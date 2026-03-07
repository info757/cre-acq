# Code Review — Story 2.1: Merge inputs and extract metrics from OM

**Date:** 2026-03-06  
**Story:** 2-1-merge-inputs-and-extract-metrics-from-om  
**Files:** merge_inputs.py, test_merge.py

---

## AC Validation

| AC | Status | Evidence |
|----|--------|----------|
| 1. Merge: Excel priority, Claude fills nulls | IMPLEMENTED | merge(), normalize_excel_output |
| 2. Extract property, market, NOI, cap rate, etc. | IMPLEMENTED | SCALAR_FIELDS, om-extractor prompt |
| 3. null if not found, never hallucinate | IMPLEMENTED | om-extractor rules, merge null handling |
| 4. Source tag per field (excel \| claude \| null) | IMPLEMENTED | _sources dict |
| 5. Full ExtractedMetrics JSON | IMPLEMENTED | output schema |
| 6. Ambiguous field → flag for human review | IMPLEMENTED | om-extractor extraction_flags |

---

## Findings (Fixes Applied)

### HIGH — noi_trailing fallback in normalize_excel_output

**Issue:** parse_excel may output `noi_trailing` without `noi_trailing_annualized` (when no "Annualized" row). normalize_excel_output only mapped `noi_trailing_annualized`, so Excel NOI was dropped and Claude could overwrite.

**Fix applied:** Use `noi_trailing_annualized or noi_trailing`; prefer annualized when both present. Added tests: test_noi_trailing_fallback_when_no_annualized, test_noi_annualized_preferred_over_noi_trailing.

### MEDIUM — Raw-text CLI path untested

**Issue:** Integration test only covered Excel-only path. Raw-text path (prompt load, Claude call, response parse) was untested.

**Fix applied:** Added test_raw_text_cli_with_mocked_claude: runs merge_inputs --raw-text with mocked call_claude, verifies output structure and _sources.

---

## Verdict

**PASS** — All ACs satisfied. Fixes applied. 29 tests pass.
