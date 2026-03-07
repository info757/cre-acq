# Story 6.2: Wire pipeline in n8n

Status: review

<!-- Note: Created after n8n work was done. Story retrofitted to capture scope. -->

## Story

As the developer (Will + Zoé),
we want the OM Screener pipeline orchestrated in n8n,
so that we can run it end-to-end from a webhook and demo it on real deals.

## Acceptance Criteria

1. **Given** a deal folder path **When** we POST to the n8n webhook **Then** the pipeline runs: discover → extract/parse → merge → score → format_output
2. **And** a CLI runner (`run_pipeline.py`) exists to test the pipeline without n8n
3. **And** n8n workflow JSON is importable and documented
4. **And** the human review gate cannot be bypassed in production (architecture principle)
5. **And** a minimal workflow with --skip-gate exists for local testing only; production must use the full flow with Wait for Webhook

## Tasks / Subtasks

- [x] Task 1: CLI runner (AC: 2)
  - [x] run_pipeline.py: --folder, --deal-id, --skip-gate, --criteria, --out-dir
  - [x] Orchestrates: discover_inputs → extract_text/check_ocr/ocr_pdf (if PDF) → parse_excel (if Excel) → merge_inputs → apply_corrections → score → format_output
  - [x] --skip-gate: auto-confirm for testing
  - [x] Without --skip-gate: format_review_message to stdout, read corrections from stdin
- [x] Task 2: n8n workflow (AC: 1, 3, 4)
  - [x] n8n/workflow.json: production workflow with human review gate (safe, no bypass path)
  - [x] n8n/workflow-testing.json: Webhook → Execute Command (run_pipeline --skip-gate, testing-only)
  - [x] n8n/README.md: setup, import, configure paths, trigger
  - [x] Document Execute Command node enablement (disabled by default in n8n 2.0+)
- [x] Task 3: Production path documentation (AC: 5)
  - [x] README references architecture.md for full flow (Nodes 1–13, Telegram, Wait for Webhook)
  - [x] Minimal workflow is for testing; `workflow.json` carries the full gated production flow

## Dev Notes

### Architecture Compliance

- **Source:** stage-1-om-screener/architecture.md#n8n Workflow Design
- **Pipeline order:** discover → extract/parse (parallel) → merge → format_review → [wait] → apply_corrections → score → format_output → Telegram
- **Temp paths:** /tmp/{{deal_id}}_*.json
- **Output:** output/{{deal_id}}.json

### Technical Requirements

- **run_pipeline.py:** Must run from stage-1-om-screener cwd; uses relative paths to src/, prompts/, shared/
- **n8n Community config:** `workflow.json` and `workflow-testing.json` use a `Workflow Config` Set node so Community Edition does not require `$vars`
- **Webhook body:** `{ "deal_folder": "/abs/path/to/folder", "deal_id": "mill-one" }`

### File Structure

```
stage-1-om-screener/
  src/
    run_pipeline.py     ← CLI runner (this story)
  n8n/
    workflow.json         ← production workflow (gated)
    workflow-testing.json ← testing-only skip-gate runner
    README.md             ← setup, import, trigger
```

### Testing Requirements

- Run: `python3 src/run_pipeline.py --folder /path/to/sample-oms --skip-gate`
- Requires: pip install -r requirements.txt, ANTHROPIC_API_KEY in .env
- Sample data: tests/sample-oms/ (Mill One Excel files)

### References

- [Source: stage-1-om-screener/architecture.md] — n8n Workflow Design, pipeline stages
- [Source: _bmad-output/planning-artifacts/epics.md] — NFR6: One n8n node = one responsibility

## Change Log

- 2026-03-07: Review fixes. Moved Telegram bot auth out of workflow config and into n8n Telegram credentials, updated README to require credential attachment before activation, and reset checked-in `workflow.json` to inactive-by-default so import/configure/activate happens in that order.
- 2026-03-07: Community Edition pass. Replaced `$vars` dependency with a `Workflow Config` Set node in both workflows, documented Community setup, switched review delivery to plain text to avoid Telegram markdown parse failures, and validated the production-gated path end-to-end on local n8n using Mill One sample files: webhook trigger → review delivery → POST resume payload → confirmed/scored/output JSON → final verdict delivery. Status: review.
- 2026-03-06: Code review fixes: split workflows (`workflow.json` production scaffold, `workflow-testing.json` testing-only); fixed testing command syntax and python fallback; run_pipeline uses sys.executable (venv); fix loop re-displays and waits for ok.
- 2026-03-06: Story created (retrofitted). run_pipeline.py, n8n/workflow.json, n8n/README.md added. Status: in-progress.
