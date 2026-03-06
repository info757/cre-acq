# Story 1.3: Ingest Excel files and extract structured metrics

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an acquisitions professional,
I want the system to read any Excel files provided with an OM,
so that financial data from rent rolls, operating statements, and loan files is used directly rather than extracted by Claude from PDFs.

## Acceptance Criteria

1. **Given** one or more Excel file paths **When** the system parses each file **Then** it detects file type from filename keywords and sheet names (financials, rent_roll, commercial_rent_roll, loan_info)
2. **And** extracts partial ExtractedMetrics JSON from each recognized file type
3. **And** all numeric extraction uses Decimal — never float
4. **And** Excel values take priority over Claude-extracted values at merge step
5. **And** unrecognized files are skipped with a warning, not a failure
6. **And** extraction flags logged per field (source file, any anomalies)

## Tasks / Subtasks

- [x] Task 1: Implement parse_excel.py (AC: 1, 2, 3, 5, 6)
  - [x] Add argparse for --files (JSON array of paths), --out
  - [x] Implement classify_file(): filename keywords + sheet names → financials | rent_roll | commercial_rent_roll | loan_info | unknown
  - [x] Implement parse_financials(), parse_rent_roll(), parse_commercial_rent_roll(), parse_loan_info()
  - [x] Use Decimal for all numeric values (never float)
  - [x] Skip unrecognized files with warning to stderr; do not fail
  - [x] Write partial ExtractedMetrics to --out (only fields found, no nulls for absent fields)
  - [x] Include _extraction_flags list (source file, anomalies)
- [x] Task 2: Add tests (AC: all)
  - [x] tests/test_parse_excel.py: Mill One package (all 4 file types), empty list, missing file, single-file cases
  - [x] Verify Decimal in output (not float)
  - [x] Verify unrecognized file skipped with warning

## Dev Notes

### Architecture Compliance

- **Script:** `stage-1-om-screener/src/parse_excel.py`
- **CLI:** `python3 src/parse_excel.py --files '["path1.xlsx","path2.xlsx"]' --out /tmp/deal_excel.json`
- **n8n flow:** Node 4a runs parse_excel when has_excel is true; receives excel_paths from Node 2 (discover_inputs)
- **Output:** partial ExtractedMetrics JSON written to --out. merge_inputs.py maps flat keys (noi_trailing_annualized, gross_income, etc.) to nested ExtractedMetrics schema via normalize_excel_output().
- **Merge rule:** Excel values take priority at merge step (Story 2.1). This story only produces the partial Excel output.

### Technical Requirements

- **Stack:** pandas + openpyxl (already in requirements.txt)
- **File type detection keywords:**
  - financials: "financial", "finance", "income", "p&l" (filename) OR sheet names containing "financial", "income", "noi"
  - rent_roll: "itemized", "rent roll", " rr", "_rr" (filename) OR sheet "rent roll", "rr"
  - commercial_rent_roll: "commercial" + ("rr" or "rent") in filename
  - loan_info: "loan", "debt", "mortgage" (filename) OR sheet "loan", "debt"
- **Numeric:** Use `from decimal import Decimal`. Never float for money.
- **Output schema:** Partial ExtractedMetrics — only include fields actually extracted. merge_inputs expects flat keys (noi_trailing_annualized, gross_income, total_expenses, expense_ratio, occupancy_pct, unit_count, loan_count, total_loan_balance, annual_debt_service, loans[], _extraction_flags) and maps to nested structure.
- **First value wins:** When merging multiple Excel files, later files do NOT overwrite earlier ones per architecture.

### File Structure Requirements

```
stage-1-om-screener/
  src/
    parse_excel.py      ← this story
  tests/
    test_parse_excel.py ← unit tests
```

### Testing Requirements

- Test: Mill One full package (financials + rent roll + commercial RR + loan info) → all fields extracted
- Test: Empty file list → exit 1
- Test: Missing file path → skip with warning, exit 0 (do not fail)
- Test: Single financials file → NOI, gross income, expenses, expense ratio
- Test: Single loan file → loan count, balances, debt service
- Test: Unrecognized Excel file → skipped with warning
- Run: `python3 tests/test_parse_excel.py`
- Sample files: SAMPLE_DIR = `../../tests/sample-oms` (project-root tests/sample-oms). Mill One files: "Mill One 2024-2025 Financials.xlsx", "Mill One Commercial RR.xlsx", "Mill One Itemized RR (5).xlsx", "Mill One Loan Info (2 tabs).xlsx"

### Previous Story Intelligence (1.1, 1.2)

- Tests use PYTHON = `../.venv/bin/python3`, SAMPLE_DIR = `../../tests/sample-oms`
- Run: `python3 tests/test_parse_excel.py` (not pytest)
- Implementation may already exist — dev agent should verify against AC and update if gaps found
- merge_inputs.py already has normalize_excel_output() mapping parse_excel flat output to ExtractedMetrics nested schema. Ensure parse_excel output keys match what normalize_excel_output expects.

### References

- [Source: stage-1-om-screener/architecture.md#parse_excel] — parse_excel spec, file type detection, output rules
- [Source: stage-1-om-screener/architecture.md#n8n Workflow Design] — Node 4a integration
- [Source: shared/data-model.md] — ExtractedMetrics schema
- [Source: stage-1-om-screener/src/merge_inputs.py] — normalize_excel_output() mapping
- [Source: _bmad-output/planning-artifacts/epics.md] — Epic 1, Story 1.3

## Change Log

- 2026-03-06: Code review fixes: cap_rate_trailing mapping in normalize_excel_output (merge_inputs), commercial_rent_roll sheet-name fallback (parse_excel), TestNormalizeExcelOutput in test_merge. Story done.
- 2026-03-06: Dev-story complete. Verified parse_excel.py against AC; added Test 6 (unrecognized file); output encoding utf-8. 31 tests pass.
- 2026-03-06: Story created via create-story workflow. Ready for dev.

## Dev Agent Record

### Agent Model Used

Claude (dev-story workflow)

### Debug Log References

### Completion Notes List

- Implementation verified: parse_excel.py and test_parse_excel.py already existed
- All 6 ACs satisfied: file type detection, partial ExtractedMetrics extraction, Decimal for numerics, unrecognized skip with warning, extraction flags
- Added Test 6: unrecognized Excel file (GenericDataExport.xlsx) skipped with warning
- Added encoding="utf-8" to output file write
- 31 tests pass. merge_inputs.normalize_excel_output() maps flat keys correctly.

### File List

- stage-1-om-screener/src/parse_excel.py (existing, modified: output encoding, commercial_rent_roll sheet fallback)
- stage-1-om-screener/tests/test_parse_excel.py (modified: added Test 6)
- stage-1-om-screener/src/merge_inputs.py (modified: cap_rate_trailing in normalize_excel_output)
- stage-1-om-screener/tests/test_merge.py (modified: TestNormalizeExcelOutput)
