# Story 1.2: Extract text from PDF

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an acquisitions professional,
I want to provide an OM PDF,
so that the system can process its text content.

## Acceptance Criteria

1. **Given** a valid PDF file path **When** the system extracts text **Then** it extracts readable text from a clean (text-layer) PDF using pdfplumber
2. **And** detects low-density pages (image-embedded financials)
3. **And** falls back to targeted OCR (Tesseract) on low-density pages only
4. **And** falls back to full OCR for scanned documents (avg <100 chars/page)
5. **And** returns error if file not found or not a valid PDF
6. **And** page-level metadata written alongside text (char counts, OCR flags)

## Tasks / Subtasks

- [x] Task 1: Implement extract_text.py (AC: 1, 2, 5, 6)
  - [x] Add argparse for --pdf, --out
  - [x] Use pdfplumber to extract text page by page
  - [x] Flag low-density pages (<150 chars/page)
  - [x] Write raw text to --out, metadata to --out.meta.json
  - [x] Exit 1 if file not found or not a PDF
- [x] Task 2: Implement check_ocr_needed.py (AC: 3, 4)
  - [x] Read .meta.json from extract_text
  - [x] If avg <100 chars/page → needs_ocr true, mode "full"
  - [x] If low_density_pages exist → needs_ocr true, mode "targeted"
  - [x] Output JSON to stdout: needs_ocr, mode, target_pages, reason
- [x] Task 3: Implement ocr_pdf.py (AC: 3, 4)
  - [x] Support --mode full and --mode targeted --pages
  - [x] Use pdf2image + Tesseract for OCR
  - [x] Full mode: replace entire text file
  - [x] Targeted mode: splice OCR text into low-density pages only
- [x] Task 4: Add tests (AC: all)
  - [x] tests/test_extract.py: clean PDF, mixed PDF (low-density), scanned PDF (full OCR), error cases

## Dev Notes

### Architecture Compliance

- **Scripts:** extract_text.py, check_ocr_needed.py, ocr_pdf.py
- **Pipeline:** extract_text → check_ocr_needed → ocr_pdf (if needs_ocr)
- **n8n flow:** Node 3a runs extract_text, Node 3b runs check_ocr_needed, Node 3c runs ocr_pdf if needed
- **Output:** raw_text.txt (consumed by merge_inputs.py)

### Technical Requirements

- **extract_text.py:** pdfplumber, --pdf, --out. Writes text + .meta.json. LOW_DENSITY_THRESHOLD = 150.
- **check_ocr_needed.py:** --meta or --txt (n8n uses --txt /tmp/{{deal_id}}_raw.txt), reads extract_text output. FULL_OCR_THRESHOLD = 100, PAGE_OCR_THRESHOLD = 150.
- **ocr_pdf.py:** pdf2image, pytesseract. --pdf, --txt, --mode targeted|full, --pages '[1,2,3]' for targeted.
- **Deps:** pdfplumber, pdf2image, pytesseract, Pillow. System: tesseract, poppler (brew install).

### File Structure Requirements

```
stage-1-om-screener/
  src/
    extract_text.py
    check_ocr_needed.py
    ocr_pdf.py
  tests/
    test_extract.py
```

### Testing Requirements

- Test: clean PDF (Mill One) → text extracted, no OCR needed
- Test: mixed PDF (Navaho) → low-density pages detected, targeted OCR on pages 4, 9, 10
- Test: scanned PDF → full OCR, entire doc replaced
- Test: file not found → exit 1
- Test: not a PDF → exit 1
- Test: check_ocr_needed error on missing meta

### Previous Story Intelligence (1.1)

- Tests use PYTHON = ../.venv/bin/python3, SAMPLE_DIR = ../../tests/sample-oms
- Run: python3 tests/test_extract.py (not pytest)
- Implementation may already exist — dev agent should verify against AC

### References

- [Source: stage-1-om-screener/architecture.md#Python Scripts] — extract_text, check_ocr_needed, ocr_pdf specs
- [Source: stage-1-om-screener/architecture.md#Pipeline] — Stage 1a PDF→Text flow
- [Source: _bmad-output/planning-artifacts/epics.md] — Epic 1, Story 1.2

## Change Log

- 2026-03-06: Code review fixes applied: --txt support in check_ocr_needed (n8n-compatible), JSON decode handling, full OCR test, meta encoding, Test 3 robustness. 35 tests pass.
- 2026-03-06: Verified existing implementation against AC; added Test 8 (not a PDF). 27 tests pass. Marked ready for review.

## Dev Agent Record

### Agent Model Used

Claude (dev-story workflow)

### Debug Log References

### Completion Notes List

- Implementation verified: extract_text.py, check_ocr_needed.py, ocr_pdf.py already exist
- All 6 ACs satisfied: pdfplumber extraction, low-density detection, targeted OCR, full OCR, error handling, metadata
- 27 tests pass: Navaho (mixed), Mill One (clean), targeted OCR, check_ocr_needed, error cases (missing file, not PDF, missing meta)
- Added Test 8: error on not a PDF (AC5)

### File List

- stage-1-om-screener/src/extract_text.py (existing)
- stage-1-om-screener/src/check_ocr_needed.py (existing)
- stage-1-om-screener/src/ocr_pdf.py (existing)
- stage-1-om-screener/tests/test_extract.py (modified: added Test 8)
