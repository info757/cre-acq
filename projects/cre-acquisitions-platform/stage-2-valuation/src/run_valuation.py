"""
run_valuation.py — Run Stage 2 valuation pipeline from ScreeningResult.

Usage:
    python3 src/run_valuation.py --screening-result path/to/screening.json [--overrides path] [--skip-gate]
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def _stage_dir():
    return Path(__file__).resolve().parent.parent


def _project_root():
    return _stage_dir().parent


def _run(cmd: list, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def _python():
    return sys.executable


def main():
    parser = argparse.ArgumentParser(description="Run Stage 2 valuation from ScreeningResult")
    parser.add_argument("--screening-result", required=True, help="Path to Stage 1 output (ScreeningResult JSON)")
    parser.add_argument("--overrides", help="Path to valuation_overrides JSON (optional)")
    parser.add_argument("--skip-gate", action="store_true", help="Skip human review gate (for testing)")
    parser.add_argument("--out-dir", default=None, help="Output directory (default: stage-2-valuation/output)")
    args = parser.parse_args()

    stage_dir = _stage_dir()
    project_root = _project_root()
    criteria_path = project_root / "shared" / "buy-criteria.json"
    out_dir = Path(args.out_dir) if args.out_dir else stage_dir / "output"
    out_dir.mkdir(parents=True, exist_ok=True)

    # Load screening to get deal_id
    with open(args.screening_result, "r") as f:
        screening = json.load(f)
    deal_id = screening.get("deal_id", "deal")
    base = out_dir / deal_id

    # 1. Normalize input
    norm_out = str(base) + "_valuation_input.json"
    cmd = [
        _python(),
        "src/normalize_input.py",
        "--screening-result", args.screening_result,
        "--criteria", str(criteria_path),
        "--out", norm_out,
    ]
    if args.overrides:
        cmd.extend(["--overrides", args.overrides])
    r = _run(cmd, stage_dir)
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        sys.exit(1)

    # 2. Human review gate (skip for now in v1 — we can add later)
    if not args.skip_gate:
        pass  # TODO: display assumptions, wait for confirm

    # 3. Direct cap
    cmd = [_python(), "src/direct_cap.py", "--valuation-input", norm_out]
    r = _run(cmd, stage_dir)
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        sys.exit(1)
    direct_cap_result = json.loads(r.stdout)
    direct_cap_value = direct_cap_result["direct_cap_value"]

    # 4. DCF
    dcf_out = str(base) + "_dcf.json"
    cmd = [
        _python(), "src/dcf.py",
        "--valuation-input", norm_out,
        "--out", dcf_out,
    ]
    r = _run(cmd, stage_dir)
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        sys.exit(1)

    # 5. Flags
    flags_out = str(base) + "_flags.json"
    cmd = [
        _python(), "src/flags.py",
        "--valuation-input", norm_out,
        "--valuation-result", dcf_out,
    ]
    r = _run(cmd, stage_dir)
    with open(flags_out, "w") as f:
        f.write(r.stdout if r.returncode == 0 else "[]")

    # 6. Format output
    final_out = str(base) + "_valuation.json"
    prompt_path = stage_dir / "prompts" / "valuation-narrator.md"
    cmd = [
        _python(), "src/format_valuation_output.py",
        "--valuation-input", norm_out,
        "--direct-cap", str(direct_cap_value),
        "--dcf-result", dcf_out,
        "--flags", flags_out,
        "--out", final_out,
    ]
    r = _run(cmd, stage_dir)
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        sys.exit(1)
    print(r.stdout)
    print(f"[run_valuation] Output: {final_out}", file=sys.stderr)


if __name__ == "__main__":
    main()
