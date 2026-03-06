# Story 2.1: Merge inputs and extract metrics from OM

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an acquisitions professional,
I want the agent to pull key metrics from the OM and combine them with Excel data,
so that I don't have to read the full document to find the numbers.

## Acceptance Criteria

1. **Given** raw text from PDF (optional) and/or partial metrics from Excel (optional) **When** at least one input is provided **Then** the system merges inputs: Excel values take priority field-by-field, Claude fills remaining nulls from PDF text
2. **And** extracts: property type, market, asking price, NOI (trailing + pro-forma), cap rate, occupancy, expense ratio, debt terms, vintage, units/SF, lease info
3. **And** uses null if not found — never hallucinates
4. **And** each field carries a source tag (excel | claude | null)
5. **And** output is full ExtractedMetrics JSON matching the data-model schema
6. **And** if a field is ambiguous, agent flags it for human review rather than guessing

## Tasks / Subtasks

- [x] Task 1: Implement merge_inputs.py (AC: 1, 2, 3, 4, 5, 6)
  - [x] Add argparse for --raw-text (optional), --excel (optional), --prompt (required), --out (required)
  - [x] Exit 1 if neither --raw-text nor --excel provided
  - [x] Load Excel JSON if provided; normalize via normalize_excel_output() to nested ExtractedMetrics
  - [x] If raw-text provided: call Claude with om-extractor.md prompt; parse JSON response
  - [x] Merge: Excel wins field-by-field; Claude fills nulls
  - [x] Write _sources dict per field: "excel" | "claude" | null
  - [x] Output full ExtractedMetrics (deal_id, extraction_timestamp, property, financials, debt, leases, extraction_flags, _sources)
  - [x] om-extractor prompt instructs Claude: null if not found; add to extraction_flags if ambiguous
- [x] Task 2: Add tests (AC: all)
  - [x] tests/test_merge.py: Excel wins, Claude fills gaps, null handling, Excel-only, Claude-only, leases merge, flags merge
  - [x] Test normalize_excel_output maps parse_excel flat keys correctly
  - [x] Integration: run merge on Mill One (PDF + Excel) and verify output structure

## Dev Notes

### Architecture Compliance

- **Script:** `stage-1-om-screener/src/merge_inputs.py`
- **CLI:** `python3 src/merge_inputs.py [--raw-text /tmp/deal_raw.txt] [--excel /tmp/deal_excel.json] --prompt prompts/om-extractor.md --out /tmp/deal_extracted.json`
- **n8n flow:** Node 5 runs merge_inputs. Receives raw-text (from Node 3a/3c) and/or excel (from Node 4a). At least one required.
- **Output:** full ExtractedMetrics JSON with _sources. Consumed by format_review_message.py (Story 2.2).

### Technical Requirements

- **Stack:** anthropic (Claude), dotenv for ANTHROPIC_API_KEY
- **Merge rule:** For each scalar field in SCALAR_FIELDS: excel_val wins if non-null; else claude_val; else null
- **Leases:** Excel leases used if non-empty; else Claude leases
- **Flags:** Combine excel + claude extraction_flags (dedupe)
- **Claude prompt:** prompts/om-extractor.md. Schema embedded. Instructs: null if not found; extraction_flags for ambiguities
- **normalize_excel_output:** Maps parse_excel flat keys (noi_trailing_annualized, gross_income, etc.) to nested ExtractedMetrics. Must stay in sync with parse_excel output keys.

### File Structure Requirements

```
stage-1-om-screener/
  src/
    merge_inputs.py      ← this story
  prompts/
    om-extractor.md     ← Claude prompt (schema, rules)
  tests/
    test_merge.py       ← unit tests
```

### Testing Requirements

- Test: Excel wins over Claude on overlapping fields (vintage, noi_trailing, expense_ratio, dscr, ltv)
- Test: Claude fills fields Excel did not provide (submarket, address, noi_proforma, cap_rate, interest_rate)
- Test: Null when neither source has data
- Test: Excel-only path (no raw-text) → no Claude call, Excel values only
- Test: Claude-only path (no excel) → Claude extraction only
- Test: Leases merge (Excel wins if present)
- Test: extraction_flags combined from both sources
- Test: normalize_excel_output maps cap_rate_trailing, noi_trailing_annualized, etc.
- Run: `python3 -m pytest tests/test_merge.py -v`

### Previous Story Intelligence (1.1, 1.2, 1.3)

- Tests use pytest. SAMPLE_DIR = `../../tests/sample-oms`
- parse_excel outputs flat keys; merge_inputs.normalize_excel_output maps to nested
- normalize_excel_output maps: unit_count, gross_income, total_expenses, noi_trailing_annualized, expense_ratio, cap_rate_trailing, occupancy_pct, loan_rate_weighted_avg, _extraction_flags
- Implementation may already exist — dev agent should verify against AC and update if gaps found

### References

- [Source: stage-1-om-screener/architecture.md#merge_inputs] — merge_inputs spec
- [Source: stage-1-om-screener/architecture.md#n8n Workflow Design] — Node 5 integration
- [Source: shared/data-model.md] — ExtractedMetrics schema
- [Source: stage-1-om-screener/prompts/om-extractor.md] — Claude prompt
- [Source: _bmad-output/planning-artifacts/epics.md] — Epic 2, Story 2.1

## Change Log

- 2026-03-06: Code review fixes: noi_trailing fallback in normalize_excel_output, raw-text CLI test with mocked Claude. 29 tests pass. Story done.
- 2026-03-06: Dev-story complete. Verified merge_inputs.py against AC; added TestMergeInputsCLI (Excel-only integration); output encoding utf-8. 26 tests pass.
- 2026-03-06: Story created via create-story workflow. Ready for dev.

## Dev Agent Record

### Agent Model Used

Claude (dev-story workflow)

### Debug Log References

### Completion Notes List

- Implementation verified: merge_inputs.py already existed and satisfies all ACs
- All 6 ACs satisfied: merge (Excel priority), extraction fields, null handling, source tags, ExtractedMetrics schema, ambiguous-flag via om-extractor
- Added TestMergeInputsCLI: parse_excel → merge_inputs --excel only, verifies output structure and _sources
- Added encoding="utf-8" to output file write
- 26 tests pass

### File List

- stage-1-om-screener/src/merge_inputs.py (existing, modified: output encoding, noi_trailing fallback)
- stage-1-om-screener/tests/test_merge.py (modified: TestMergeInputsCLI, noi_trailing tests, raw-text CLI test)
