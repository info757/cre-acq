#!/usr/bin/env python3
"""
CRE Acquisitions Pipeline — Demo UI

Minimal web UI to run the pipeline and display valuation results.
Run: python demo/app.py
Open: http://localhost:5000
"""

import json
import os
import subprocess
import sys
from pathlib import Path

from flask import Flask, jsonify, render_template, request

app = Flask(__name__, static_folder="static", template_folder="templates")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PIPELINE_PY = PROJECT_ROOT / "pipeline" / "run-full.py"
SAMPLE_FOLDER = PROJECT_ROOT / "tests" / "sample-oms" / "Mill One"
# Use stage-1 venv for pipeline (has anthropic, pdfplumber, etc.)
VENV_PYTHON = PROJECT_ROOT / "stage-1-om-screener" / ".venv" / "bin" / "python"
PYTHON = str(VENV_PYTHON) if VENV_PYTHON.exists() else sys.executable


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/api/run", methods=["POST"])
def run_pipeline():
    """Run the full pipeline and return valuation result."""
    folder = request.json.get("folder") if request.is_json else None
    folder_path = Path(folder) if folder else SAMPLE_FOLDER
    if not folder_path.is_absolute():
        folder_path = (PROJECT_ROOT / folder_path).resolve()
    deal_id = request.json.get("deal_id", "mill-one") if request.is_json else "mill-one"

    if not folder_path.exists():
        return jsonify({"error": f"Folder not found: {folder_path}"}), 400

    cmd = [
        PYTHON,
        str(PIPELINE_PY),
        "--folder", str(folder_path),
        "--deal-id", deal_id,
        "--skip-gate",
    ]
    try:
        r = subprocess.run(
            cmd,
            cwd=PROJECT_ROOT,
            capture_output=True,
            text=True,
            timeout=120,
        )
    except subprocess.TimeoutExpired:
        return jsonify({"error": "Pipeline timed out (120s)"}), 500

    if r.returncode != 0:
        return jsonify({
            "error": "Pipeline failed",
            "stderr": r.stderr,
        }), 500

    # Load Stage 1 screening result (OM extraction)
    stage1_out = PROJECT_ROOT / "stage-1-om-screener" / "output" / f"{deal_id}.json"
    extraction = None
    if stage1_out.exists():
        with open(stage1_out, "r") as f:
            screening = json.load(f)
        extraction = screening.get("extracted_metrics", {})

    # Load valuation result + inputs for math breakdown
    out_dir = PROJECT_ROOT / "stage-2-valuation" / "output"
    valuation_path = out_dir / f"{deal_id}_valuation.json"
    if not valuation_path.exists():
        return jsonify({"error": "Valuation output not found", "stdout": r.stdout}), 500

    with open(valuation_path, "r") as f:
        valuation = json.load(f)

    # Add math breakdown from valuation_input and dcf output
    vi_path = out_dir / f"{deal_id}_valuation_input.json"
    dcf_path = out_dir / f"{deal_id}_dcf.json"
    if vi_path.exists() and dcf_path.exists():
        with open(vi_path, "r") as f:
            vi = json.load(f)
        with open(dcf_path, "r") as f:
            dcf = json.load(f)
        fin = vi.get("screening_result", {}).get("extracted_metrics", {}).get("financials", {})
        overrides = vi.get("valuation_overrides", {})
        noi = float(fin.get("noi_trailing") or fin.get("noi_proforma") or 0)
        cap_rate = float(overrides.get("market_cap_rate") or 0.0665)
        valuation["math"] = {
            "direct_cap": {
                "formula": "Value = NOI ÷ cap_rate",
                "inputs": {"noi": noi, "cap_rate": cap_rate, "cap_rate_pct": cap_rate * 100},
                "calculation": f"{noi:,.0f} ÷ {cap_rate:.4f} = {valuation['direct_cap_value']:,.0f}",
            },
            "dcf": {
                "formula": "DCF = PV(cash flows) + PV(reversion)",
                "inputs": {
                    "noi_yr1": noi,
                    "hold_years": overrides.get("hold_period_years", 10),
                    "rent_growth": overrides.get("rent_growth_rate", 0.03),
                    "exit_cap": overrides.get("exit_cap_rate", 0.0665),
                    "discount_rate": overrides.get("discount_rate", 0.07),
                },
                "noi_projection": "NOI_t = NOI_yr1 × (1 + g)^t",
                "reversion_formula": "Reversion = NOI_yr11 ÷ exit_cap",
                "pv_formula": "PV = Σ[CF_t ÷ (1+r)^(t+1)] + Reversion ÷ (1+r)^11",
                "cash_flows": dcf.get("cash_flows", []),
                "reversion": dcf.get("reversion"),
            },
            "irr": {
                "formula": "IRR: solve for r where NPV = -Initial + Σ[CF_t ÷ (1+r)^(t+1)] = 0",
                "initial": float(fin.get("asking_price") or 0),
                "cash_flows_plus_reversion": (dcf.get("cash_flows", []) or []) + [dcf.get("reversion", 0)],
            },
            "equity_multiple": {
                "formula": "EM = Total Proceeds ÷ Initial Investment",
                "total_proceeds": sum(dcf.get("cash_flows", [])) + dcf.get("reversion", 0),
                "initial": float(fin.get("asking_price") or 0),
            },
        }

    if extraction:
        valuation["extraction"] = extraction

    return jsonify(valuation)


if __name__ == "__main__":
    port = 5001  # 5000 often used by macOS AirPlay Receiver
    print(f"CRE Acquisitions Demo — http://localhost:{port}")
    app.run(debug=True, port=port)
