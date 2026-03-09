#!/usr/bin/env python3
"""
run-full.py — Stage 1 (OM Screener) → Stage 2 (Valuation) end-to-end.

Usage:
    python3 pipeline/run-full.py --folder /path/to/deal/folder [--deal-id ID] [--skip-gate]

Runs Stage 1, then Stage 2 on the screening result. Requires both stages to be built.
"""

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def _project_root():
    return Path(__file__).resolve().parent.parent


def _run(cmd: list, cwd: Path) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)


def main():
    parser = argparse.ArgumentParser(description="Stage 1 → Stage 2 full pipeline")
    parser.add_argument("--folder", required=True, help="Path to deal folder (PDF/Excel)")
    parser.add_argument("--deal-id", default=None, help="Deal ID (default: folder basename)")
    parser.add_argument("--skip-gate", action="store_true", help="Skip Stage 1 human review gate")
    args = parser.parse_args()

    root = _project_root()
    stage1_dir = root / "stage-1-om-screener"
    stage2_dir = root / "stage-2-valuation"
    deal_id = args.deal_id or os.path.basename(os.path.normpath(args.folder))

    # Resolve folder to absolute path (relative paths are from project root)
    folder_path = Path(args.folder)
    if not folder_path.is_absolute():
        folder_path = (root / folder_path).resolve()
    folder_str = str(folder_path)

    # Stage 1
    cmd = [
        sys.executable,
        "src/run_pipeline.py",
        "--folder", folder_str,
        "--deal-id", deal_id,
    ]
    if args.skip_gate:
        cmd.append("--skip-gate")
    r = _run(cmd, stage1_dir)
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        sys.exit(1)

    screening_path = stage1_dir / "output" / f"{deal_id}.json"
    if not screening_path.exists():
        print(f"[run-full] ERROR: Stage 1 output not found: {screening_path}", file=sys.stderr)
        sys.exit(1)

    # Stage 2
    cmd = [
        sys.executable,
        "src/run_valuation.py",
        "--screening-result", str(screening_path),
        "--skip-gate",
    ]
    r = _run(cmd, stage2_dir)
    if r.returncode != 0:
        print(r.stderr, file=sys.stderr)
        sys.exit(1)
    print(r.stdout)
    print("[run-full] Done. Stage 1 output:", screening_path, file=sys.stderr)
    print("[run-full] Stage 2 output:", stage2_dir / "output" / f"{deal_id}_valuation.json", file=sys.stderr)


if __name__ == "__main__":
    main()
