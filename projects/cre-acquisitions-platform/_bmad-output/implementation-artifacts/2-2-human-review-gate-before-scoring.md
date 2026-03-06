# Story 2.2: Human review gate before scoring

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an acquisitions professional,
I want to see the extracted metrics before scoring fires,
so that I can catch any extraction errors before they affect the verdict.

## Acceptance Criteria

1. **Given** extracted metrics from the merge step **When** the system displays the metrics table **Then** it pauses and waits for user confirmation
2. **And** user can confirm (proceed to scoring) or flag any incorrect fields
3. **And** if user flags a field, they can correct it inline (e.g., "fix: noi_trailing 920000") before scoring
4. **And** corrected values are used in scoring, not the extracted values
5. **And** this gate cannot be bypassed — scoring always waits for confirmation

## Tasks / Subtasks

- [x] Task 1: Verify format_review_message.py against AC (AC: 1, 2)
  - [x] Reads ExtractedMetrics JSON from merge step (--metrics path)
  - [x] Outputs formatted Telegram message with source tags [EXCEL] [CLAUDE] [?]
  - [x] Includes instructions: "Reply 'ok' to run scoring" and "Reply 'fix: field_name new_value' to correct"
  - [x] Prints to stdout (n8n Node 6 captures and sends to Telegram)
- [x] Task 2: Verify apply_corrections.py against AC (AC: 3, 4)
  - [x] Accepts --metrics (extracted), --corrections (user reply string or JSON), --out (confirmed path)
  - [x] Parses "ok" → pass-through; "fix: field value" → apply correction
  - [x] Supports nested field paths (property.type, financials.noi_trailing, debt.dscr)
  - [x] Coerces values (numeric, boolean, string) per field type
  - [x] Writes confirmed_metrics.json; score.py consumes this, never extracted
- [x] Task 3: Gate cannot be bypassed (AC: 5)
  - [x] n8n flow: Node 8 Wait for Webhook blocks until user confirms
  - [x] score.py must receive confirmed_metrics.json (output of apply_corrections), never extracted directly
  - [x] Document: no code path allows scoring without human confirmation
- [x] Task 4: Tests (AC: all)
  - [x] test_format_review_message.py: output structure, source tags, all ExtractedMetrics fields
  - [x] test_apply_corrections.py: "ok" pass-through, "fix: X Y" application, nested paths, coercion
  - [x] Integration: merge → format_review_message → (simulate user) apply_corrections → score

## Dev Notes

### Architecture Compliance

- **Scripts:** `stage-1-om-screener/src/format_review_message.py`, `src/apply_corrections.py`
- **CLI format_review_message:** `python3 src/format_review_message.py --metrics /tmp/{{deal_id}}_extracted.json`
- **CLI apply_corrections:** `python3 src/apply_corrections.py --metrics /tmp/{{deal_id}}_extracted.json --corrections "<user reply>" --out /tmp/{{deal_id}}_confirmed.json`
- **n8n flow:** Node 6 runs format_review_message → Node 7 sends to Telegram → Node 8 Wait for Webhook (human reply) → Node 9 runs apply_corrections → Node 10 runs score.py with confirmed_metrics
- **Data flow:** merge_inputs (extracted.json) → format_review_message (display) → [user confirms] → apply_corrections (confirmed.json) → score.py

### Technical Requirements

- **format_review_message:** Reads ExtractedMetrics with _sources; outputs Telegram Markdown (bold, line breaks). Must handle nulls gracefully (display "—").
- **apply_corrections:** FIELD_MAPPING maps flat names (noi_trailing, dscr) to (section, key). Coerce: int, float, bool, string. "ok" or empty → pass-through.
- **Gate enforcement:** score.py takes --metrics path; n8n must pass confirmed path. No CLI flag to skip gate.

### File Structure Requirements

```
stage-1-om-screener/
  src/
    format_review_message.py   ← this story
    apply_corrections.py       ← this story
  tests/
    test_format_review_message.py
    test_apply_corrections.py
```

### Testing Requirements

- format_review_message: Output contains deal_id, property section, financials, debt, source tags, "Reply 'ok'" instruction
- apply_corrections: "ok" → identical output; "fix: noi_trailing 920000" → noi_trailing updated; nested paths work
- Run: `python3 tests/test_format_review_message.py` and `pytest tests/test_apply_corrections.py -v`

### Previous Story Intelligence (2.1)

- merge_inputs outputs ExtractedMetrics with _sources (excel | claude | null)
- Output path: /tmp/{{deal_id}}_extracted.json
- format_review_message consumes this; apply_corrections outputs confirmed.json
- Implementation may already exist — dev agent should verify against AC and update if gaps found

### References

- [Source: stage-1-om-screener/architecture.md#Human Review Gate — UX] — Telegram message format
- [Source: stage-1-om-screener/architecture.md#n8n Workflow Design] — Nodes 6, 7, 8, 9
- [Source: shared/data-model.md] — ExtractedMetrics schema
- [Source: _bmad-output/planning-artifacts/epics.md] — Epic 2, Story 2.2

## Change Log

- 2026-03-06: Code review fixes: dotted field paths in apply_corrections; _human_confirmed gate enforcement in score.py; zero values displayed in format_review_message; integration test asserts corrected NOI in scored output; test_score_rejects_unconfirmed_metrics. 64 tests pass. Story done.
- 2026-03-06: Dev-story complete. Verified format_review_message.py and apply_corrections.py against AC; added test for "Reply 'ok'" instruction; added test_review_gate_integration.py (merge → format_review_message → apply_corrections → score). 61 tests pass. Story ready for review.
- 2026-03-06: Story created via create-story workflow. Ready for dev.

## Dev Agent Record

### Agent Model Used

Claude (dev-story workflow)

### Debug Log References

### Completion Notes List

- Code review fixes applied: dotted paths, gate enforcement, zero display, integration assertions
- Implementation verified: format_review_message.py and apply_corrections.py already existed and satisfy all ACs
- Added test_format_review_message assertion for "Reply 'ok'" and "fix:" instructions (AC 1, 2)
- Added test_review_gate_integration.py: full pipeline merge → format_review_message → apply_corrections(ok) → score and merge → apply_corrections(fix: noi_trailing 920000) → score
- score.py has no bypass: --metrics required, consumes confirmed path only
- 61 tests pass (format_review_message, apply_corrections, review_gate_integration, merge)

### File List

- stage-1-om-screener/src/format_review_message.py (modified: zero values displayed via is not None)
- stage-1-om-screener/src/apply_corrections.py (modified: dotted paths, _human_confirmed)
- stage-1-om-screener/src/score.py (modified: gate enforcement, reject unconfirmed)
- stage-1-om-screener/tests/test_format_review_message.py (modified: Reply 'ok' assertions, test_format_zero_values_displayed)
- stage-1-om-screener/tests/test_apply_corrections.py (modified: test_dotted_field_path)
- stage-1-om-screener/tests/test_review_gate_integration.py (modified: AC4 assertion, test_score_rejects_unconfirmed_metrics)
