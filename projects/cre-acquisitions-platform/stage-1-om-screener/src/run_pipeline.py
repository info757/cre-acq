"""
run_pipeline.py — Run the full OM Screener pipeline from a deal folder.

Use this to test the pipeline locally without n8n. For production, use the n8n workflow.

Usage:
    python3 src/run_pipeline.py --folder /path/to/deal/folder [options]
    python3 src/run_pipeline.py --config /path/to/config.json  # n8n: payload from config file

Options:
    --folder       Path to deal folder (required unless --confirm-only or --config).
    --deal-id      Deal ID for output files (default: folder basename).
    --run-id       Run/execution ID for temp path isolation (default: deal_id). Use n8n $execution.id.
    --skip-gate    Skip human review: auto-confirm extracted metrics (for testing).
    --stop-before-scoring  Run discover->merge->format_review, print review to stdout, exit. For n8n production flow.
    --confirm-only Run only apply_corrections->score->format_output (requires --deal-id, --tmp-dir, --corrections). For n8n resume.
    --config       Path to JSON config file (n8n path). Overrides CLI args. Config keys: folder, deal_id, run_id, mode, corrections.
    --tmp-dir      Temp directory for intermediate files (default: system temp). Use /tmp for n8n.
    --criteria     Path to buy-criteria.json (default: ../../shared/buy-criteria.json)
    --out-dir      Output directory for final JSON (default: ../output)
"""

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile

# Safe pattern for deal_id and run_id: alphanumeric, dash, underscore only (prevents path traversal)
_SAFE_ID_RE = re.compile(r"^[a-zA-Z0-9_-]+$")


def _stage_dir():
    return os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _project_root():
    """Project root (cre-acquisitions-platform) containing shared/, stage-1-om-screener/, etc."""
    return os.path.abspath(os.path.join(_stage_dir(), ".."))


def _run(cmd: list, cwd: str = None) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd or _stage_dir(), capture_output=True, text=True)


def _python():
    """Use same interpreter as this script (inherits venv)."""
    return sys.executable


def _validate_safe_id(val: str, name: str) -> None:
    """Reject IDs that could cause path traversal or injection."""
    if not val or not _SAFE_ID_RE.match(val):
        print(f"[run_pipeline] ERROR: {name} must be alphanumeric, dash, underscore only. Got: {val!r}", file=sys.stderr)
        sys.exit(1)


def _maybe_cleanup_config(config_path: str) -> None:
    """Remove n8n-created temp config under /tmp to avoid leaving sensitive payloads on disk."""
    if not config_path:
        return
    if (
        config_path.startswith("/tmp/")
        and "om-screener" in config_path
        and "om-screener-resume-" not in os.path.basename(config_path)
    ):
        try:
            os.unlink(config_path)
        except OSError:
            pass


def _run_confirm_only(args, validate_ids=True):
    """Run apply_corrections -> score -> format_output (n8n resume after human review)."""
    deal_id = args.deal_id
    run_id = args.run_id or deal_id
    if validate_ids:
        _validate_safe_id(deal_id, "deal_id")
        _validate_safe_id(run_id, "run_id")
    tmp = os.path.join(os.path.abspath(args.tmp_dir), f"om-screener-{run_id}")
    stage_dir = _stage_dir()
    project_root = _project_root()
    extracted_json = os.path.join(tmp, f"{deal_id}_extracted.json")
    confirmed_json = os.path.join(tmp, f"{deal_id}_confirmed.json")
    scored_json = os.path.join(tmp, f"{deal_id}_scored.json")
    prompt_narrator = os.path.join(stage_dir, "prompts", "om-narrator.md")
    out_dir = args.out_dir or os.path.join(stage_dir, "output")
    out_path = os.path.join(out_dir, f"{deal_id}.json")

    if not os.path.exists(extracted_json):
        print(f"[run_pipeline] ERROR: Extracted file not found: {extracted_json}", file=sys.stderr)
        sys.exit(1)

    py = _python()
    r = _run(
        [
            py,
            "src/apply_corrections.py",
            "--metrics",
            extracted_json,
            "--corrections",
            args.corrections,
            "--out",
            confirmed_json,
        ]
    )
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        sys.exit(1)

    r = _run(
        [
            py,
            "src/score.py",
            "--metrics",
            confirmed_json,
            "--criteria",
            args.criteria,
            "--out",
            scored_json,
        ]
    )
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        sys.exit(1)

    os.makedirs(out_dir, exist_ok=True)
    r = _run(
        [
            py,
            "src/format_output.py",
            "--scored",
            scored_json,
            "--prompt",
            prompt_narrator,
            "--out",
            out_path,
        ]
    )
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        sys.exit(1)

    print(f"\n[run_pipeline] Done. Output: {out_path}", file=sys.stderr)


def main():
    parser = argparse.ArgumentParser(description="Run OM Screener pipeline from deal folder")
    parser.add_argument("--config", help="Path to JSON config file (n8n). Overrides CLI args.")
    parser.add_argument("--folder", help="Path to deal folder with .pdf and/or .xlsx (required unless --confirm-only or --config)")
    parser.add_argument("--deal-id", help="Deal ID (default: folder basename)")
    parser.add_argument("--run-id", help="Run/execution ID for temp path isolation (default: deal_id). Use n8n $execution.id.")
    parser.add_argument("--skip-gate", action="store_true", help="Skip human review gate (auto-confirm)")
    parser.add_argument("--stop-before-scoring", action="store_true", help="Run up to format_review, print to stdout, exit (for n8n)")
    parser.add_argument("--confirm-only", action="store_true", help="Run apply_corrections->score->format_output only (for n8n resume)")
    parser.add_argument("--corrections", help="Corrections string for apply_corrections (required with --confirm-only)")
    parser.add_argument("--tmp-dir", help="Temp dir for intermediates (default: system temp). Use /tmp for n8n.")
    parser.add_argument(
        "--criteria",
        default=os.path.join(_project_root(), "shared", "buy-criteria.json"),
        help="Path to buy-criteria.json",
    )
    parser.add_argument(
        "--out-dir",
        default=os.path.join(_stage_dir(), "output"),
        help="Output directory for final JSON",
    )
    args = parser.parse_args()

    # Load from config file if provided (n8n path)
    if args.config:
        try:
            with open(args.config, "r") as f:
                cfg = json.load(f)
        except FileNotFoundError:
            print(f"[run_pipeline] ERROR: Config file not found: {args.config}", file=sys.stderr)
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"[run_pipeline] ERROR: Invalid config JSON: {e}", file=sys.stderr)
            sys.exit(1)
        mode = cfg.get("mode")
        if mode == "stop-before-scoring":
            args.folder = cfg.get("folder")
            args.deal_id = cfg.get("deal_id")
            args.run_id = cfg.get("run_id", args.deal_id)
            args.stop_before_scoring = True
            args.tmp_dir = cfg.get("tmp_dir") or "/tmp"
            if not args.folder:
                print("[run_pipeline] ERROR: Config mode 'stop-before-scoring' requires 'folder'", file=sys.stderr)
                sys.exit(1)
        elif mode == "confirm-only":
            args.deal_id = cfg.get("deal_id")
            args.corrections = cfg.get("corrections")
            args.run_id = cfg.get("run_id", args.deal_id)
            args.confirm_only = True
            args.tmp_dir = cfg.get("tmp_dir") or "/tmp"
            if args.corrections is None:
                args.corrections = ""
            if not args.deal_id:
                print("[run_pipeline] ERROR: Config mode 'confirm-only' requires 'deal_id'", file=sys.stderr)
                sys.exit(1)
        elif mode == "skip-gate":
            args.folder = cfg.get("folder")
            args.deal_id = cfg.get("deal_id")
            args.run_id = cfg.get("run_id", args.deal_id)
            args.skip_gate = True
            args.tmp_dir = cfg.get("tmp_dir") or "/tmp"
            if not args.folder:
                print("[run_pipeline] ERROR: Config mode 'skip-gate' requires 'folder'", file=sys.stderr)
                sys.exit(1)
        else:
            print(f"[run_pipeline] ERROR: Config mode must be 'stop-before-scoring', 'confirm-only', or 'skip-gate'. Got: {mode!r}", file=sys.stderr)
            sys.exit(1)

    try:
        if args.confirm_only:
            if not args.deal_id or not args.tmp_dir or args.corrections is None:
                parser.error("--confirm-only requires --deal-id, --tmp-dir, and --corrections")
            _run_confirm_only(args, validate_ids=bool(args.config))
            return

        if not args.folder:
            parser.error("--folder is required (unless using --confirm-only)")
        folder = os.path.abspath(args.folder)
        deal_id = args.deal_id or os.path.basename(folder.rstrip("/"))
        run_id = args.run_id or deal_id
        if args.config:
            _validate_safe_id(deal_id, "deal_id")
            _validate_safe_id(str(run_id), "run_id")  # run_id may be numeric from n8n
        stage_dir = _stage_dir()
        project_root = _project_root()

        if args.tmp_dir:
            tmp = os.path.join(os.path.abspath(args.tmp_dir), f"om-screener-{run_id}")
            os.makedirs(tmp, exist_ok=True)
            tmp_ctx = type("_", (), {"__enter__": lambda s: tmp, "__exit__": lambda s, *a: None})()
        else:
            tmp_ctx = tempfile.TemporaryDirectory(prefix="om-screener-")

        with tmp_ctx as tmp:
            raw_txt = os.path.join(tmp, f"{deal_id}_raw.txt")
            excel_json = os.path.join(tmp, f"{deal_id}_excel.json")
            extracted_json = os.path.join(tmp, f"{deal_id}_extracted.json")
            confirmed_json = os.path.join(tmp, f"{deal_id}_confirmed.json")
            scored_json = os.path.join(tmp, f"{deal_id}_scored.json")
            prompt_extractor = os.path.join(stage_dir, "prompts", "om-extractor.md")
            prompt_narrator = os.path.join(stage_dir, "prompts", "om-narrator.md")
    
            # 1. Discover inputs
            py = _python()
            r = _run([py, "src/discover_inputs.py", "--folder", folder])
            if r.returncode != 0:
                print(r.stderr, file=sys.stderr)
                sys.exit(1)
            discover = json.loads(r.stdout)
            has_pdf = discover.get("has_pdf", False)
            has_excel = discover.get("has_excel", False)
            pdf_path = discover.get("pdf_path")
            excel_paths = discover.get("excel_paths", [])
    
            # 2a. PDF path: extract text, optionally OCR
            raw_text_path = None
            if has_pdf and pdf_path:
                r = _run([py, "src/extract_text.py", "--pdf", pdf_path, "--out", raw_txt])
                if r.returncode != 0:
                    print(r.stderr, file=sys.stderr)
                    sys.exit(1)
                r = _run([py, "src/check_ocr_needed.py", "--txt", raw_txt])
                if r.returncode != 0:
                    print(r.stderr, file=sys.stderr)
                    sys.exit(1)
                ocr_result = json.loads(r.stdout)
                if ocr_result.get("needs_ocr"):
                    mode = ocr_result.get("mode", "full")
                    ocr_cmd = [py, "src/ocr_pdf.py", "--pdf", pdf_path, "--txt", raw_txt, "--mode", mode]
                    if mode == "targeted":
                        ocr_cmd.extend(["--pages", json.dumps(ocr_result.get("target_pages", []))])
                    r = _run(ocr_cmd)
                    if r.returncode != 0:
                        print(r.stderr, file=sys.stderr)
                        sys.exit(1)
                raw_text_path = raw_txt
    
            # 2b. Excel path: parse
            if has_excel and excel_paths:
                r = _run(
                    [py, "src/parse_excel.py", "--files", json.dumps(excel_paths), "--out", excel_json]
                )
                if r.returncode != 0:
                    print(r.stderr, file=sys.stderr)
                    sys.exit(1)
    
            # 3. Merge
            merge_cmd = [py, "src/merge_inputs.py", "--prompt", prompt_extractor, "--out", extracted_json]
            if raw_text_path:
                merge_cmd.extend(["--raw-text", raw_text_path])
            if has_excel and excel_paths:
                merge_cmd.extend(["--excel", excel_json])
            r = _run(merge_cmd)
            if r.returncode != 0:
                print(r.stderr, file=sys.stderr)
                sys.exit(1)
    
            # Set deal_id in extracted
            with open(extracted_json) as f:
                extracted = json.load(f)
            extracted["deal_id"] = deal_id
            with open(extracted_json, "w") as f:
                json.dump(extracted, f, indent=2)
    
            # 4. Human review gate (or stop before scoring for n8n)
            if args.stop_before_scoring:
                r = _run([py, "src/format_review_message.py", "--metrics", extracted_json])
                if r.returncode != 0:
                    print(r.stderr, file=sys.stderr)
                    sys.exit(1)
                print(r.stdout)
                print(f"\n[run_pipeline] Stopped before scoring. Extracted: {extracted_json}", file=sys.stderr)
                return
    
            if args.skip_gate:
                r = _run(
                    [
                        py,
                        "src/apply_corrections.py",
                        "--metrics",
                        extracted_json,
                        "--corrections",
                        "ok",
                        "--out",
                        confirmed_json,
                    ]
                )
            else:
                metrics_for_review = extracted_json
                while True:
                    r = _run([py, "src/format_review_message.py", "--metrics", metrics_for_review])
                    if r.returncode != 0:
                        print(r.stderr, file=sys.stderr)
                        sys.exit(1)
                    print(r.stdout)
                    print("\n--- Reply 'ok' to confirm, or 'fix: field value' to correct ---")
                    corrections = input().strip()
                    r = _run(
                        [
                            py,
                            "src/apply_corrections.py",
                            "--metrics",
                            metrics_for_review,
                            "--corrections",
                            corrections,
                            "--out",
                            confirmed_json,
                        ]
                    )
                    if r.returncode != 0:
                        print(r.stderr, file=sys.stderr)
                        sys.exit(1)
                    if corrections.strip().lower() == "ok":
                        break
                    metrics_for_review = confirmed_json
            if r.returncode != 0:
                print(r.stderr, file=sys.stderr)
                sys.exit(1)
    
            # 5. Score
            r = _run(
                [
                    py,
                    "src/score.py",
                    "--metrics",
                    confirmed_json,
                    "--criteria",
                    args.criteria,
                    "--out",
                    scored_json,
                ]
            )
            if r.returncode != 0:
                print(r.stderr, file=sys.stderr)
                sys.exit(1)
    
            # 6. Format output (Claude narrative + final JSON)
            os.makedirs(args.out_dir, exist_ok=True)
            out_path = os.path.join(args.out_dir, f"{deal_id}.json")
            r = _run(
                [
                    py,
                    "src/format_output.py",
                    "--scored",
                    scored_json,
                    "--prompt",
                    prompt_narrator,
                    "--out",
                    out_path,
                ]
            )
            if r.returncode != 0:
                print(r.stderr, file=sys.stderr)
                sys.exit(1)
    
            print(f"\n[run_pipeline] Done. Output: {out_path}", file=sys.stderr)
    finally:
        if args.config:
            _maybe_cleanup_config(args.config)


if __name__ == "__main__":
    main()
