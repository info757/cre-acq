# Code Review — Story 1.1: Discover deal folder inputs

**Date:** 2026-03-06  
**Model:** Claude (adversarial review)  
**Story:** 1-1-discover-deal-folder-inputs  
**Files:** discover_inputs.py, test_discover.py

---

## Git vs Story Discrepancies

**0 found.** Story File List matches implementation. No uncommitted changes to reviewed files (implementation pre-existed; dev-story verified, did not modify).

---

## AC Validation

| AC | Status | Evidence |
|----|--------|----------|
| 1. Scan folder, identify .pdf/.xlsx/.xls | IMPLEMENTED | discover_inputs.py:36-45, ext in SUPPORTED_*_EXTS |
| 2. Return has_pdf, pdf_path, has_excel, excel_paths as JSON | IMPLEMENTED | discover_inputs.py:65-70, json.dumps |
| 3. Multiple PDFs → select largest | IMPLEMENTED | discover_inputs.py:57-58, max(..., key=os.path.getsize) |
| 4. Exit 1 if empty or no supported files | IMPLEMENTED | discover_inputs.py:47-53, sys.exit(1) |
| 5. PDF/Excel optional, at least one required | IMPLEMENTED | discover_inputs.py:47, `if not pdf_files and not excel_files` |

---

## Task Audit

All tasks marked [x] are implemented. No false claims.

---

## Findings

### MEDIUM

1. **Multiple-PDF selection not explicitly tested** [test_discover.py]  
   AC3 requires "if multiple PDFs found, selects the largest." Test 1 uses Mill One (1 PDF + 4 Excel). No test creates a folder with 2+ PDFs and asserts pdf_path is the largest by size. The logic exists in code but is untested.

2. **Excel-only folder not tested** [test_discover.py]  
   Story Testing Requirements: "Test: single Excel → has_pdf false, pdf_path null, has_excel true, excel_paths [path]". Test 4 is PDF-only. No dedicated Excel-only test. Test 1 covers PDF+Excel but not Excel-only.

3. **Test sample path vs architecture** [test_discover.py:23]  
   SAMPLE_DIR = `../../tests/sample-oms` resolves to project-root `tests/sample-oms`. Architecture file layout shows `stage-1-om-screener/tests/sample-oms/`. Two sample-oms dirs exist; test uses project-root. Works but diverges from documented layout.

### LOW

4. **Hidden-files test is indirect** [test_discover.py]  
   Story: "Test: hidden files ignored." Test 1 checks "no .gitkeep in excel_paths" — .gitkeep has no .xlsx ext so it's excluded. No explicit test that creates `.hidden.pdf` and verifies it's ignored.

5. **Hardcoded venv path** [test_discover.py:21]  
   `PYTHON = "../.venv/bin/python3"` — fails if venv missing or elsewhere. Reduces portability.

6. **Dev Notes typo** [1-1-discover-deal-folder-inputs.md:69]  
   "Run: `python -m pytest tests/test_discover.py -v`" but tests use custom runner (`python3 tests/test_discover.py`). Doc/implementation mismatch.

---

## Verdict

**PASS** (after fixes)

- All ACs implemented.
- No BLOCKERs.
- MEDIUM items 1 and 2 fixed: Test 6 (multiple PDFs), Test 7 (Excel-only) added. 25 tests pass.
- Dev Notes typo fixed (pytest → python3).
- LOW items deferred.

---

## Post-Fix

2026-03-06: Applied automatic fixes. Story marked done.
