"""
test_run_pipeline.py — Test run_pipeline.py --config and execution scoping.
"""

import json
import os
import subprocess
import sys
import tempfile

STAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
PYTHON = os.path.join(STAGE_DIR, ".venv/bin/python3")
RUN_PIPELINE = os.path.join(STAGE_DIR, "src/run_pipeline.py")
BUILD_VERDICT = os.path.join(STAGE_DIR, "n8n/build_verdict_message.py")
SAMPLE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../tests/sample-oms"))


def _run(args, cwd=None):
    cmd = [PYTHON if os.path.isfile(PYTHON) else "python3", RUN_PIPELINE] + args
    return subprocess.run(cmd, cwd=cwd or STAGE_DIR, capture_output=True, text=True)


class TestRunPipelineConfig:
    """Test --config payload parsing and execution scoping."""

    def test_config_stop_before_scoring_creates_run_scoped_temp(self):
        """Config mode stop-before-scoring uses run_id for temp dir."""
        if not os.path.isdir(SAMPLE_DIR):
            return  # Skip if no sample data
        deal_folder = os.path.join(SAMPLE_DIR, "Mill One")
        if not os.path.isdir(deal_folder):
            return

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            config = {
                "mode": "stop-before-scoring",
                "folder": deal_folder,
                "deal_id": "mill-one",
                "run_id": "test-run-12345",
                "tmp_dir": "/tmp",
            }
            json.dump(config, f)
            config_path = f.name

        try:
            r = _run(["--config", config_path])
            assert r.returncode == 0, r.stderr
            # Temp dir should be /tmp/om-screener-test-run-12345
            expected_tmp = "/tmp/om-screener-test-run-12345"
            assert os.path.isdir(expected_tmp), f"Expected temp dir {expected_tmp}"
            extracted = os.path.join(expected_tmp, "mill-one_extracted.json")
            assert os.path.isfile(extracted), f"Expected {extracted}"
        finally:
            os.unlink(config_path)
            # Cleanup temp dir
            import shutil
            run_tmp = "/tmp/om-screener-test-run-12345"
            if os.path.isdir(run_tmp):
                shutil.rmtree(run_tmp, ignore_errors=True)

    def test_config_confirm_only_requires_deal_id_corrections(self):
        """Config mode confirm-only fails without deal_id or corrections."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"mode": "confirm-only", "tmp_dir": "/tmp"}, f)
            config_path = f.name

        try:
            r = _run(["--config", config_path])
            assert r.returncode != 0
            assert "deal_id" in r.stderr or "ERROR" in r.stderr
        finally:
            os.unlink(config_path)

    def test_config_confirm_only_success(self):
        """Config mode confirm-only runs apply_corrections -> score -> format_output successfully."""
        with tempfile.TemporaryDirectory() as tmpdir:
            run_id = "confirm-test-999"
            run_tmp = os.path.join(tmpdir, f"om-screener-{run_id}")
            os.makedirs(run_tmp, exist_ok=True)
            deal_id = "confirm-deal"
            extracted_json = os.path.join(run_tmp, f"{deal_id}_extracted.json")
            # Minimal valid extracted metrics (apply_corrections + score expect property/financials/debt)
            extracted = {
                "deal_id": deal_id,
                "property": {"type": "Multifamily", "market": "Austin", "units": 120},
                "financials": {
                    "asking_price": 25000000,
                    "cap_rate_trailing": 0.055,
                    "occupancy_current": 0.92,
                    "expense_ratio": 0.35,
                },
                "debt": {"ltv": 0.65, "dscr": 1.25},
                "leases": [],
                "extraction_flags": [],
            }
            with open(extracted_json, "w") as f:
                json.dump(extracted, f, indent=2)

            config_path = os.path.join(tmpdir, "config.json")
            with open(config_path, "w") as f:
                json.dump({
                    "mode": "confirm-only",
                    "deal_id": deal_id,
                    "run_id": run_id,
                    "tmp_dir": tmpdir,
                    "corrections": "ok",
                }, f)

            r = _run(["--config", config_path])
            assert r.returncode == 0, r.stderr
            out_path = os.path.join(STAGE_DIR, "output", f"{deal_id}.json")
            assert os.path.isfile(out_path), f"Expected output {out_path}"
            # Cleanup
            if os.path.isfile(out_path):
                os.unlink(out_path)

    def test_resume_config_survives_confirm_until_verdict(self):
        """Resume config stays available for build_verdict_message, then gets cleaned up there."""
        with tempfile.TemporaryDirectory() as tmpdir:
            run_id = "confirm-verdict-999"
            run_tmp = os.path.join(tmpdir, f"om-screener-{run_id}")
            os.makedirs(run_tmp, exist_ok=True)
            deal_id = "confirm-verdict-deal"
            extracted_json = os.path.join(run_tmp, f"{deal_id}_extracted.json")
            extracted = {
                "deal_id": deal_id,
                "property": {"type": "Multifamily", "market": "Austin", "units": 120},
                "financials": {
                    "asking_price": 25000000,
                    "cap_rate_trailing": 0.055,
                    "occupancy_current": 0.92,
                    "expense_ratio": 0.35,
                },
                "debt": {"ltv": 0.65, "dscr": 1.25},
                "leases": [],
                "extraction_flags": [],
            }
            with open(extracted_json, "w") as f:
                json.dump(extracted, f, indent=2)

            config_path = os.path.join("/tmp", f"om-screener-resume-{os.getpid()}-{run_id}.json")
            with open(config_path, "w") as f:
                json.dump({
                    "mode": "confirm-only",
                    "deal_id": deal_id,
                    "run_id": run_id,
                    "tmp_dir": tmpdir,
                    "corrections": "ok",
                    "stage_dir": STAGE_DIR,
                }, f)

            out_path = os.path.join(STAGE_DIR, "output", f"{deal_id}.json")
            verdict_cmd = [PYTHON if os.path.isfile(PYTHON) else "python3", BUILD_VERDICT, "--config", config_path]
            try:
                r = _run(["--config", config_path])
                assert r.returncode == 0, r.stderr
                assert os.path.isfile(config_path), "Resume config should remain for downstream verdict step"

                r2 = subprocess.run(verdict_cmd, cwd=STAGE_DIR, capture_output=True, text=True)
                assert r2.returncode == 0, r2.stderr
                assert "Verdict:" in r2.stdout
                assert not os.path.exists(config_path), "Verdict builder should clean the resume config"
            finally:
                if os.path.isfile(config_path):
                    os.unlink(config_path)
                if os.path.isfile(out_path):
                    os.unlink(out_path)

    def test_config_skip_gate_runs_full_pipeline(self):
        """Config mode skip-gate runs pipeline without human review."""
        if not os.path.isdir(SAMPLE_DIR):
            return
        deal_folder = os.path.join(SAMPLE_DIR, "Mill One")
        if not os.path.isdir(deal_folder):
            return

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = os.path.join(tmpdir, "config.json")
            with open(config_path, "w") as f:
                json.dump({
                    "mode": "skip-gate",
                    "folder": deal_folder,
                    "deal_id": "mill-one-skip",
                    "run_id": "skip-test-999",
                    "tmp_dir": tmpdir,
                }, f)

            r = _run(["--config", config_path])
            assert r.returncode == 0, r.stderr
            out_path = os.path.join(STAGE_DIR, "output", "mill-one-skip.json")
            assert os.path.isfile(out_path), f"Expected output {out_path}"
            # Cleanup
            if os.path.isfile(out_path):
                os.unlink(out_path)


if __name__ == "__main__":
    tc = TestRunPipelineConfig()
    tc.test_config_stop_before_scoring_creates_run_scoped_temp()
    tc.test_config_confirm_only_requires_deal_id_corrections()
    tc.test_config_confirm_only_success()
    tc.test_resume_config_survives_confirm_until_verdict()
    tc.test_config_skip_gate_runs_full_pipeline()
    print("✓ All test_run_pipeline tests PASSED")
