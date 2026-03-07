# Code Review — Story 1.3: Ingest Excel files and extract structured metrics

**Date:** 2026-03-06  
**Story:** 1-3-ingest-excel-files-and-extract-structured-metrics  
**Files:** parse_excel.py, test_parse_excel.py, merge_inputs.py, test_merge.py

---

## AC Validation

| AC | Status | Evidence |
|----|--------|----------|
| 1. File type detection (filename + sheet names) | IMPLEMENTED | classify_file(), Test 1, 6 |
| 2. Partial ExtractedMetrics extraction | IMPLEMENTED | parse_financials, parse_rent_roll, parse_commercial_rent_roll, parse_loan_info |
| 3. Decimal for numerics | IMPLEMENTED | to_decimal(), Decimal throughout |
| 4. Excel values take priority at merge | IMPLEMENTED | merge_inputs.normalize_excel_output maps parse_excel output |
| 5. Unrecognized files skipped with warning | IMPLEMENTED | main() line 450-451, Test 6 |
| 6. Extraction flags logged | IMPLEMENTED | _extraction_flags in all parsers |

---

## Findings (Fixes Applied)

### HIGH — cap_rate_trailing not mapped at merge

**Issue:** parse_excel.py emits `cap_rate_trailing` from financials (implied price row). normalize_excel_output() in merge_inputs.py did not map it. Excel cap rate would be dropped; Claude could fill it instead, violating AC4.

**Fix applied:** Added `cap_rate_trailing` mapping to normalize_excel_output() in merge_inputs.py. Added TestNormalizeExcelOutput in test_merge.py.

### MEDIUM — commercial_rent_roll sheet-name fallback missing

**Issue:** classify_file() supported commercial_rent_roll only via filename keywords. Sheet-name fallback had financials, rent_roll, loan_info but not commercial_rent_roll. A commercial RR file with generic filename would be misclassified.

**Fix applied:** Added sheet-name check for commercial_rent_roll (sheet contains "commercial" and "rent"/"rr"/"lease") before rent_roll fallback in parse_excel.py.

---

## Verdict

**PASS** — All ACs satisfied. Fixes applied for HIGH and MEDIUM findings. 31 parse_excel tests + 25 merge tests pass.
