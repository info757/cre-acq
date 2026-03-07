# n8n Workflow — OM Screener

Orchestrates the Stage 1 OM Screener pipeline. See `../architecture.md` for the full design.

## Prerequisites

1. **n8n** running locally (e.g. `npx n8n` or Docker). Default: `http://localhost:5678`
2. **Execute Command node** enabled (disabled by default in n8n 2.0+). In self-hosted n8n, enable it in settings if needed.
3. **Python** with project dependencies installed (`pip install -r requirements.txt`)
4. **ANTHROPIC_API_KEY** in `.env` (for merge Claude extraction and format_output narrative)
5. **n8n Community Edition works** for this workflow.
6. Create an n8n **Telegram API** credential and keep the bot token there, not in workflow JSON.
7. After import, edit the `Workflow Config` node values:
   - `cre_acq_stage1` — absolute path to `stage-1-om-screener`
   - `telegram_chat_id` — target chat ID

## Quick Test Without n8n

Run the pipeline locally (use the project venv if you have one):

```bash
cd stage-1-om-screener
# With venv: .venv/bin/python3 src/run_pipeline.py ...
python3 src/run_pipeline.py --folder /path/to/deal/folder --skip-gate
```

Use `--skip-gate` to auto-confirm extracted metrics (no human review). Omit it for interactive review. Ensure `pip install -r requirements.txt` and `ANTHROPIC_API_KEY` in `.env`.

## Workflow Overview

The production workflow is intentionally compact because `run_pipeline.py` owns the stage orchestration:

| Node | Type | Purpose |
|------|------|---------|
| 1 | Webhook | POST `/om-screener/run` with `{ deal_folder, deal_id? }` |
| 2 | Set | `Workflow Config` node with local path + chat ID |
| 3 | Execute Command | `run_pipeline.py --stop-before-scoring` to produce the review message |
| 4 | Telegram | Send the review to Telegram |
| 5 | Telegram | Send the resume URL separately so it cannot be truncated |
| 6 | Wait | Pause for a POST resume payload containing `corrections` |
| 7 | Execute Command | `run_pipeline.py --confirm-only` to apply corrections, score, and write output |
| 8 | Execute Command | Build a plain-text verdict message from `output/{{deal_id}}.json` |
| 9 | Telegram | Send the final verdict to Telegram |

## Import Workflow

This folder includes two workflow files:

- `workflow.json` — **production** flow with human review gate: run_pipeline --stop-before-scoring → Wait for Webhook → run_pipeline --confirm-only
- `workflow-testing.json` — **testing-only** skip-gate runner (`run_pipeline.py --skip-gate`)

1. Open n8n → Workflows → Import from File.
2. For production, import `workflow.json`.
3. Attach your **Telegram API** credential to all three Telegram nodes:
   - `Send Review to Telegram`
   - `Send Approval Instructions`
   - `Send Verdict to Telegram`
4. Edit the `Workflow Config` node in the imported workflow:
   - set `cre_acq_stage1` to your absolute local path
   - set `telegram_chat_id`
5. Leave the workflow inactive until the credential and config values are set.
6. For local testing only, import `workflow-testing.json`.
7. **Enable Execute Command**: n8n 2.0+ disables it by default. Settings → Blocked nodes → enable.
8. In n8n, open the `Webhook Start` node and copy the actual **Production URL** or **Test URL** shown by the editor for your instance. Do not assume the short path is the exact live URL on every n8n build.
9. Trigger the workflow with curl (replace `YOUR_WEBHOOK_URL` and `/path/to/deal/folder`):

```bash
curl -X POST "YOUR_WEBHOOK_URL" -H "Content-Type: application/json" -d '{"deal_folder":"/path/to/deal/folder","deal_id":"mill-one"}'
```

Example for local n8n (copy the real URL from the Webhook node):
```bash
curl -X POST "http://localhost:5678/webhook/om-screener/run" -H "Content-Type: application/json" -d '{"deal_folder":"/Users/willholt/some/deal/folder","deal_id":"mill-one"}'
```

**Production workflow** (`workflow.json`) includes: (1) Webhook Start; (2) `Workflow Config`; (3) Run Pipeline Stage 1; (4) Send Review to Telegram; (5) Send Approval Instructions with the resume URL in a separate message so it cannot be truncated; (6) Wait for Confirm, POST required; (7) Run Pipeline Confirm, which fails closed if `corrections` is missing from the resume payload; (8) Build Verdict Message; (9) Send Verdict to Telegram as plain text with the actual verdict included. This version is designed for n8n Community Edition, does not rely on `$vars` or `$env` inside node expressions, and keeps the bot token in an n8n Telegram credential rather than workflow data. When `deal_id` is missing in the webhook body, execution ID is used to avoid temp-file collisions.

## Human Review Gate

When Node 7 sends the metrics to Telegram, Will sees the extraction table. He replies:

- **"ok"** — proceed to scoring
- **"fix: noi_trailing 920000"** — apply correction, then re-send for confirmation

The confirmation must POST to the webhook with `{ "corrections": "ok" }` or `{ "corrections": "fix: ..." }`. Missing `corrections` now fails the workflow instead of defaulting to approval. This can be wired from a Telegram bot that listens for Will's reply and forwards to the webhook.

## File Paths (n8n)

All scripts run with `cwd` = `PROJECT_ROOT` (stage-1-om-screener). Temp files use `/tmp/{{deal_id}}_*.json`. Output goes to `output/{{deal_id}}.json` inside the project.

## Troubleshooting

- **Execute Command not found**: Enable it in n8n Settings → Blocked nodes
- **Python not found**: `workflow-testing.json` uses `.venv/bin/python3` when present. Ensure `cre_acq_stage1` in `Workflow Config` points at the project and the venv exists, or it falls back to system `python3`.
- **Commands fail with `/path/to/...`**: Update the `Workflow Config` node after import. The workflow is meant to be configured there, not via `$env` or `$vars`.
- **Telegram nodes show missing credentials**: Attach your `Telegram API` credential to each Telegram node before activating the workflow.
- **Webhook 404 even though the workflow is active**: Copy the exact URL from the Webhook node in the n8n editor. On some n8n builds, the effective live URL is not the hand-typed short path you expect.
- **Review message fails on Telegram markdown parsing**: The workflow sends the review as plain text on purpose so extracted OM text cannot break Telegram entity parsing.
- **Claude errors**: Check ANTHROPIC_API_KEY in `.env` (merge_inputs and format_output load it)
- **Resume request fails immediately**: Ensure the POST body includes `corrections`. Empty or missing corrections are rejected on purpose.
