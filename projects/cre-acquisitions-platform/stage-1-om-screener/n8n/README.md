# n8n Workflow — OM Screener

Orchestrates the Stage 1 OM Screener pipeline. See `../architecture.md` for the full design.

## Prerequisites

1. **n8n** running locally (e.g. `npx n8n` or Docker). Default: `http://localhost:5678`
2. **Execute Command node** enabled (disabled by default in n8n 2.0+). In self-hosted n8n, enable it in settings if needed.
3. **Python** with project dependencies installed (`pip install -r requirements.txt`)
4. **ANTHROPIC_API_KEY** in `.env` (for merge Claude extraction and format_output narrative)
5. **Telegram** env vars for production workflow: `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` (used by Send Review and Send Verdict nodes)

## Quick Test Without n8n

Run the pipeline locally (use the project venv if you have one):

```bash
cd stage-1-om-screener
# With venv: .venv/bin/python3 src/run_pipeline.py ...
python3 src/run_pipeline.py --folder /path/to/deal/folder --skip-gate
```

Use `--skip-gate` to auto-confirm extracted metrics (no human review). Omit it for interactive review. Ensure `pip install -r requirements.txt` and `ANTHROPIC_API_KEY` in `.env`.

## Workflow Overview

| Node | Type | Purpose |
|------|------|---------|
| 1 | Webhook | POST `/om-screener/run` — body: `{ deal_folder, deal_id }` |
| 2 | Execute Command | `discover_inputs.py --folder {{deal_folder}}` |
| 3 | IF | `has_pdf == true` |
| 3a | Execute Command | `extract_text.py` |
| 3b | Execute Command | `check_ocr_needed.py --txt /tmp/{{deal_id}}_raw.txt` |
| 3c | IF | `needs_ocr == true` → `ocr_pdf.py` |
| 4 | IF | `has_excel == true` |
| 4a | Execute Command | `parse_excel.py --files {{excel_paths}} --out /tmp/{{deal_id}}_excel.json` |
| 5 | Execute Command | `merge_inputs.py` (raw-text + excel) |
| 6 | Execute Command | `format_review_message.py` |
| 7 | HTTP Request | Send to Telegram |
| 8 | Wait for Webhook | POST `/om-screener/confirm/{{deal_id}}` — body: `{ corrections: "ok" \| "fix: field value" }` |
| 9 | Execute Command | `apply_corrections.py` |
| 10 | Execute Command | `score.py` |
| 11 | Execute Command | `format_output.py` |
| 12 | HTTP Request | Send final verdict to Telegram |

## Import Workflow

This folder includes two workflow files:

- `workflow.json` — **production** flow with human review gate: run_pipeline --stop-before-scoring → Wait for Webhook → run_pipeline --confirm-only
- `workflow-testing.json` — **testing-only** skip-gate runner (`run_pipeline.py --skip-gate`)

1. Open n8n → Workflows → Import from File.
2. For production, import `workflow.json`. Set `CRE_ACQ_STAGE1` or edit the path in the Execute Command nodes.
3. For local testing only, import `workflow-testing.json`.
4. **Set project path** in the testing workflow command: replace `/path/to/cre-acquisitions-platform/stage-1-om-screener` or set env var `CRE_ACQ_STAGE1`.
5. **Enable Execute Command**: n8n 2.0+ disables it by default. Settings → Blocked nodes → enable.
6. Trigger testing workflow: `curl -X POST https://your-host/webhook/om-screener/run-test -H "Content-Type: application/json" -d '{"deal_folder":"/path/to/deal/folder","deal_id":"mill-one"}'`

**Production workflow** (`workflow.json`) includes: (1) Run Pipeline Stage 1; (2) Send Review to Telegram; (3) Send Approval Instructions with the resume URL in a separate message so it cannot be truncated; (4) Wait for Confirm, POST required; (5) Run Pipeline Confirm, which fails closed if `corrections` is missing from the resume payload; (6) Build Verdict Message; (7) Send Verdict to Telegram as plain text with the actual verdict included. Set `TELEGRAM_BOT_TOKEN` and `TELEGRAM_CHAT_ID` in n8n env. When `deal_id` is missing in the webhook body, execution ID is used to avoid temp-file collisions.

## Human Review Gate

When Node 7 sends the metrics to Telegram, Will sees the extraction table. He replies:

- **"ok"** — proceed to scoring
- **"fix: noi_trailing 920000"** — apply correction, then re-send for confirmation

The confirmation must POST to the webhook with `{ "corrections": "ok" }` or `{ "corrections": "fix: ..." }`. Missing `corrections` now fails the workflow instead of defaulting to approval. This can be wired from a Telegram bot that listens for Will's reply and forwards to the webhook.

## File Paths (n8n)

All scripts run with `cwd` = `PROJECT_ROOT` (stage-1-om-screener). Temp files use `/tmp/{{deal_id}}_*.json`. Output goes to `output/{{deal_id}}.json` inside the project.

## Troubleshooting

- **Execute Command not found**: Enable it in n8n Settings → Blocked nodes
- **Python not found**: `workflow-testing.json` uses `.venv/bin/python3` when present. Ensure project path is correct and venv exists, or it falls back to system `python3`.
- **Claude errors**: Check ANTHROPIC_API_KEY in `.env` (merge_inputs and format_output load it)
- **Resume request fails immediately**: Ensure the POST body includes `corrections`. Empty or missing corrections are rejected on purpose.
