"""
test_review_gate_integration.py — Integration: merge → format_review_message → apply_corrections → score.

Verifies Story 2.2 AC: human review gate displays metrics, accepts corrections, scoring uses confirmed values.
"""

import json
import os
import subprocess
import sys
import tempfile
import pytest

PYTHON = os.path.join(os.path.dirname(__file__), "../.venv/bin/python3")
MERGE = os.path.join(os.path.dirname(__file__), "../src/merge_inputs.py")
PARSE_EXCEL = os.path.join(os.path.dirname(__file__), "../src/parse_excel.py")
FORMAT_REVIEW = os.path.join(os.path.dirname(__file__), "../src/format_review_message.py")
APPLY_CORRECTIONS = os.path.join(os.path.dirname(__file__), "../src/apply_corrections.py")
SCORE = os.path.join(os.path.dirname(__file__), "../src/score.py")
PROMPT = os.path.join(os.path.dirname(__file__), "../prompts/om-extractor.md")
SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "../../tests/sample-oms")
CRITERIA = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../shared/buy-criteria.json"))
MILL_FILES = [
    os.path.join(SAMPLE_DIR, "Mill One 2024-2025 Financials.xlsx"),
    os.path.join(SAMPLE_DIR, "Mill One Commercial RR.xlsx"),
    os.path.join(SAMPLE_DIR, "Mill One Itemized RR (5).xlsx"),
    os.path.join(SAMPLE_DIR, "Mill One Loan Info (2 tabs).xlsx"),
]


class TestReviewGateIntegration:
    """Full pipeline: merge → format_review_message → apply_corrections → score."""

    def test_full_pipeline_with_ok_confirmation(self):
        """merge → format_review_message → apply_corrections(ok) → score."""
        missing = [f for f in MILL_FILES if not os.path.exists(f)]
        if missing:
            pytest.skip(f"Missing sample files: {missing}")
        if not os.path.exists(CRITERIA):
            pytest.skip(f"Missing buy-criteria: {CRITERIA}")

        stage_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        with tempfile.TemporaryDirectory() as tmpdir:
            excel_json = os.path.join(tmpdir, "excel.json")
            extracted_json = os.path.join(tmpdir, "extracted.json")
            confirmed_json = os.path.join(tmpdir, "confirmed.json")
            scored_json = os.path.join(tmpdir, "scored.json")

            # 1. parse_excel → merge
            r1 = subprocess.run(
                [PYTHON, PARSE_EXCEL, "--files", json.dumps(MILL_FILES), "--out", excel_json],
                capture_output=True, text=True, cwd=stage_dir
            )
            assert r1.returncode == 0, r1.stderr

            r2 = subprocess.run(
                [PYTHON, MERGE, "--excel", excel_json, "--prompt", PROMPT, "--out", extracted_json],
                capture_output=True, text=True, cwd=stage_dir
            )
            assert r2.returncode == 0, r2.stderr

            # 2. format_review_message (display)
            r3 = subprocess.run(
                [PYTHON, FORMAT_REVIEW, "--metrics", extracted_json],
                capture_output=True, text=True, cwd=stage_dir
            )
            assert r3.returncode == 0, r3.stderr
            assert "EXTRACTION REVIEW" in r3.stdout
            assert "Reply 'ok'" in r3.stdout or "Reply \"ok\"" in r3.stdout

            # 3. apply_corrections (user says "ok")
            r4 = subprocess.run(
                [PYTHON, APPLY_CORRECTIONS, "--metrics", extracted_json, "--corrections", "ok", "--out", confirmed_json],
                capture_output=True, text=True, cwd=stage_dir
            )
            assert r4.returncode == 0, r4.stderr

            with open(extracted_json) as f:
                extracted = json.load(f)
            with open(confirmed_json) as f:
                confirmed = json.load(f)
            assert confirmed["financials"]["noi_trailing"] == extracted["financials"]["noi_trailing"]

            # 4. score (uses confirmed, not extracted)
            r5 = subprocess.run(
                [PYTHON, SCORE, "--metrics", confirmed_json, "--criteria", CRITERIA, "--out", scored_json],
                capture_output=True, text=True, cwd=stage_dir
            )
            assert r5.returncode == 0, r5.stderr

            with open(scored_json) as f:
                scored = json.load(f)
            assert "verdict" in scored
            assert scored["verdict"] in ("GO", "CONDITIONAL", "NO-GO")

    def test_full_pipeline_with_correction(self):
        """merge → format_review_message → apply_corrections(fix: noi_trailing 920000) → score uses corrected value."""
        missing = [f for f in MILL_FILES if not os.path.exists(f)]
        if missing:
            pytest.skip(f"Missing sample files: {missing}")
        if not os.path.exists(CRITERIA):
            pytest.skip(f"Missing buy-criteria: {CRITERIA}")

        stage_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        with tempfile.TemporaryDirectory() as tmpdir:
            excel_json = os.path.join(tmpdir, "excel.json")
            extracted_json = os.path.join(tmpdir, "extracted.json")
            confirmed_json = os.path.join(tmpdir, "confirmed.json")
            scored_json = os.path.join(tmpdir, "scored.json")

            r1 = subprocess.run(
                [PYTHON, PARSE_EXCEL, "--files", json.dumps(MILL_FILES), "--out", excel_json],
                capture_output=True, text=True, cwd=stage_dir
            )
            assert r1.returncode == 0, r1.stderr

            r2 = subprocess.run(
                [PYTHON, MERGE, "--excel", excel_json, "--prompt", PROMPT, "--out", extracted_json],
                capture_output=True, text=True, cwd=stage_dir
            )
            assert r2.returncode == 0, r2.stderr

            with open(extracted_json) as f:
                extracted = json.load(f)
            original_noi = extracted["financials"].get("noi_trailing")

            # User corrects noi_trailing
            r3 = subprocess.run(
                [PYTHON, APPLY_CORRECTIONS, "--metrics", extracted_json, "--corrections", "fix: noi_trailing 920000", "--out", confirmed_json],
                capture_output=True, text=True, cwd=stage_dir
            )
            assert r3.returncode == 0, r3.stderr

            with open(confirmed_json) as f:
                confirmed = json.load(f)
            assert confirmed["financials"]["noi_trailing"] == 920000
            if original_noi is not None:
                assert confirmed["financials"]["noi_trailing"] != original_noi

            # Score uses corrected value (AC4: corrected values used in scoring)
            r4 = subprocess.run(
                [PYTHON, SCORE, "--metrics", confirmed_json, "--criteria", CRITERIA, "--out", scored_json],
                capture_output=True, text=True, cwd=stage_dir
            )
            assert r4.returncode == 0, r4.stderr

            with open(scored_json) as f:
                scored = json.load(f)
            assert scored["extracted_metrics"]["financials"]["noi_trailing"] == 920000

    def test_score_rejects_unconfirmed_metrics(self):
        """AC5: score.py rejects metrics that bypass human review gate."""
        if not os.path.exists(CRITERIA):
            pytest.skip(f"Missing buy-criteria: {CRITERIA}")

        stage_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
        with tempfile.TemporaryDirectory() as tmpdir:
            # Extracted metrics without _human_confirmed (bypass attempt)
            extracted = {
                "deal_id": "test",
                "extraction_timestamp": "2026-03-06T00:00:00Z",
                "property": {"type": "multifamily", "market": "Test", "submarket": None, "address": None, "vintage": 2000, "units": 100, "total_sf": None},
                "financials": {"asking_price": 10000000, "noi_trailing": 500000, "expense_ratio": 0.40, "occupancy_current": 0.90},
                "debt": {"ltv": 0.65, "dscr": 1.25},
                "leases": [],
                "extraction_flags": [],
            }
            extracted_json = os.path.join(tmpdir, "extracted.json")
            scored_json = os.path.join(tmpdir, "scored.json")
            with open(extracted_json, "w") as f:
                json.dump(extracted, f, indent=2)

            r = subprocess.run(
                [PYTHON, SCORE, "--metrics", extracted_json, "--criteria", CRITERIA, "--out", scored_json],
                capture_output=True, text=True, cwd=stage_dir
            )
            assert r.returncode != 0
            assert "human review" in r.stderr.lower() or "apply_corrections" in r.stderr.lower()
