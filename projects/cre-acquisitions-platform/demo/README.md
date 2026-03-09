# CRE Acquisitions Demo UI

Minimal web UI to run the pipeline and display valuation results.

## Run

```bash
# From project root
python -m venv demo/.venv   # if needed
demo/.venv/bin/pip install -r demo/requirements.txt
demo/.venv/bin/python demo/app.py
```

Open **http://localhost:5001**

## What it does

- Shows the pipeline flow (Deal Folder → Stage 1 → Stage 2 → ValuationResult)
- **Run pipeline** button runs the full pipeline on Mill One sample data (~60s)
- Displays Direct Cap, DCF, Suggested Offer, IRR, Equity Multiple, and narrative

## Requirements

- Stage 1 venv must exist at `stage-1-om-screener/.venv` (pipeline runs via that Python)
- `ANTHROPIC_API_KEY` in `stage-1-om-screener/.env`
