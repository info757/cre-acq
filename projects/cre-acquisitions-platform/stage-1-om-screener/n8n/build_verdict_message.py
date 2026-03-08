#!/usr/bin/env python3
"""
build_verdict_message.py — Build plain-text verdict message from screening output.

Called by n8n with --config <path>. Config JSON must contain:
  - deal_id: str
  - stage_dir: str (absolute path to stage-1-om-screener)

Reads output/{deal_id}.json and prints a trimmed message to stdout.
"""

import argparse
import json
import os
import sys


def _maybe_cleanup_config(config_path: str) -> None:
    """Remove n8n-created temp config after the last consumer reads it."""
    if not config_path:
        return
    if config_path.startswith("/tmp/") and "om-screener" in config_path:
        try:
            os.unlink(config_path)
        except OSError:
            pass


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", required=True, help="Path to JSON config with deal_id, stage_dir")
    args = parser.parse_args()

    try:
        try:
            with open(args.config, "r") as f:
                cfg = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[build_verdict_message] ERROR: {e}", file=sys.stderr)
            sys.exit(1)

        deal_id = cfg.get("deal_id")
        stage_dir = cfg.get("stage_dir")
        if not deal_id or not stage_dir:
            print("[build_verdict_message] ERROR: config must contain deal_id and stage_dir", file=sys.stderr)
            sys.exit(1)
        if "/" in str(deal_id) or ".." in str(deal_id):
            print("[build_verdict_message] ERROR: invalid deal_id", file=sys.stderr)
            sys.exit(1)

        out_path = f"{stage_dir.rstrip('/')}/output/{deal_id}.json"
        try:
            with open(out_path, "r") as f:
                d = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"[build_verdict_message] ERROR reading output: {e}", file=sys.stderr)
            sys.exit(1)

        verdict = d.get("verdict", "UNKNOWN")
        narrative = d.get("narrative", "Screening complete.")
        red_flags = d.get("red_flags", [])
        extra = []
        if red_flags:
            extra = ["", "Red flags:"]
            for flag in red_flags[:5]:
                fcat = flag.get("flag", "flag")
                expl = flag.get("explanation", "")
                extra.append(f"- {fcat}: {expl}")

        message = "\n".join(
            [f"Screening complete for {deal_id}", f"Verdict: {verdict}", "", narrative] + extra
        )
        print(message[:3900])
    finally:
        _maybe_cleanup_config(args.config)


if __name__ == "__main__":
    main()
