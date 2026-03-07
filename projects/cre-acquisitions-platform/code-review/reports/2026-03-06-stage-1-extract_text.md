# Code Review — Story 1.2: Extract text from PDF

**Date:** 2026-03-06  
**Model:** Claude (adversarial review)  
**Story:** 1-2-extract-text-from-pdf  
**Files:** extract_text.py, check_ocr_needed.py, ocr_pdf.py, test_extract.py

---

## Git vs Story Discrepancies

Story File List matches implementation. No significant discrepancies.

---

## AC Validation

| AC | Status | Evidence |
|----|--------|----------|
| 1. pdfplumber extraction | IMPLEMENTED | extract_text.py:43-49 |
| 2. low-density detection | IMPLEMENTED | extract_text.py:48-49, meta.low_density_pages |
| 3. targeted OCR | IMPLEMENTED | ocr_pdf.py splice_ocr_into_text, --mode targeted |
| 4. full OCR | IMPLEMENTED | ocr_pdf.py:141-164, --mode full |
| 5. error file not found / not PDF | IMPLEMENTED | extract_text.py:32-38, Test 6, 8 |
| 6. page-level metadata | IMPLEMENTED | extract_text.py:62-72, .meta.json |

---

## Findings

### HIGH

1. **check_ocr_needed CLI mismatch with architecture/n8n** [check_ocr_needed.py, architecture.md]  
   Architecture and n8n workflow specify: `check_ocr_needed.py --txt /tmp/{{deal_id}}_raw.txt`  
   Implementation expects: `--meta /path/to/file.meta.json`  
   n8n Node 3b would pass `--txt` and the script would fail (unknown argument). Either add `--txt` support (infer meta path as `{txt}.meta.json`) or update architecture and n8n to use `--meta`.

### MEDIUM

2. **Full OCR path not tested** [test_extract.py]  
   Story Testing Requirements: "Test: scanned PDF → full OCR, entire doc replaced." No scanned PDF in sample-oms; no test runs `ocr_pdf.py --mode full`. AC4 (full OCR) is implemented but untested. Add a test with a synthetic low-char doc or document the gap.

3. **check_ocr_needed invalid JSON handling** [check_ocr_needed.py:71-76]  
   `json.load(f)` can raise `json.JSONDecodeError` on malformed meta file. Only `FileNotFoundError` is caught. Malformed .meta.json would produce unhandled traceback. Add `except json.JSONDecodeError` with clear error message.

### LOW

4. **ocr_pdf full mode: unused import** [ocr_pdf.py:144]  
   `from pdf2image.exceptions import PDFInfoNotInstalledError` is imported but never used. Dead code.

5. **extract_text meta file encoding** [extract_text.py:71]  
   `open(meta_path, "w")` without `encoding="utf-8"`. JSON is ASCII-safe but explicit encoding is good practice for consistency with text file writes.

6. **Test 3 assertion is fragile** [test_extract.py:106-108]  
   `"DEAL UNDERWRITING" in full_text or "NOI" in full_text or "Net Operating" in full_text` — OCR output varies; these strings may not appear. Test passed with "page 4 pro forma not found" in detail but condition still passed (one of the alternatives matched). Consider a more robust assertion (e.g. min char count for OCR sections).

---

## Verdict

**PASS WITH WARNINGS**

- All ACs implemented.
- HIGH: Fix check_ocr_needed CLI for n8n compatibility.
- MEDIUM: Add full OCR test or document; add JSON decode error handling.
- LOW: Clean up imports, encoding, test assertions.

---

## Recommendation

Address HIGH item 1 before marking story done. MEDIUM items 2 and 3 should be fixed. LOW items can be deferred.
