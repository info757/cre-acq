# Story 1.1: Discover deal folder inputs

Status: done

<!-- Note: Validation is optional. Run validate-create-story for quality check before dev-story. -->

## Story

As an acquisitions professional,
I want to point the system at a folder of deal files,
so that it figures out what's there and routes each file correctly.

## Acceptance Criteria

1. **Given** a folder path containing deal files **When** the system scans the folder **Then** it identifies all .pdf and .xlsx/.xls files
2. **And** returns has_pdf, pdf_path, has_excel, excel_paths as JSON
3. **And** if multiple PDFs found, selects the largest (most likely the OM)
4. **And** exits with error if folder is empty or contains no supported files
5. **And** neither PDF nor Excel is required — any combination is valid (at least one must be present)

## Tasks / Subtasks

- [x] Task 1: Implement discover_inputs.py (AC: 1, 2, 3, 4, 5)
  - [x] Add argparse for --folder
  - [x] Scan folder for .pdf, .xlsx, .xls (skip hidden files)
  - [x] If multiple PDFs, select largest by file size
  - [x] Exit 1 with clear error if no supported files found
  - [x] Output JSON to stdout
- [x] Task 2: Add tests (AC: all)
  - [x] tests/test_discover.py with cases: empty folder, PDF only, Excel only, both, multiple PDFs

## Dev Notes

### Architecture Compliance

- **Script location:** `stage-1-om-screener/src/discover_inputs.py`
- **CLI:** `python3 src/discover_inputs.py --folder <path>`
- **Output:** JSON to stdout: `{ has_pdf, pdf_path, has_excel, excel_paths: [] }`
- **Error handling:** Exit 1 with message if folder not found, empty, or no supported files
- **n8n integration:** Node 2 calls this script; returns JSON for downstream IF nodes

### Technical Requirements

- Use Python stdlib only (os, json, argparse) — no external deps for this script
- Supported extensions: .pdf, .xlsx, .xls (case-insensitive)
- Skip hidden files (e.g. .gitkeep)
- If multiple PDFs: use `max(files, key=os.path.getsize)` to pick largest
- Log warning to stderr when multiple PDFs found (which one selected)

### File Structure Requirements

```
stage-1-om-screener/
  src/
    discover_inputs.py    ← this story
  tests/
    test_discover.py      ← unit tests
```

### Testing Requirements

- Test: empty folder → exit 1, error message
- Test: folder with no .pdf/.xlsx/.xls → exit 1
- Test: single PDF → has_pdf true, pdf_path set, has_excel false, excel_paths []
- Test: single Excel → has_pdf false, pdf_path null, has_excel true, excel_paths [path]
- Test: PDF + Excel → both present
- Test: multiple PDFs → pdf_path is largest by size, warning to stderr
- Test: hidden files ignored
- Run: `python3 tests/test_discover.py`

### Project Structure Notes

- Code lives in `stage-1-om-screener/` subfolder (not project root)
- All paths in this story are relative to `stage-1-om-screener/`
- Implementation may already exist — dev agent should verify against AC and update if gaps found

### References

- [Source: stage-1-om-screener/architecture.md#Python Scripts] — discover_inputs spec
- [Source: stage-1-om-screener/architecture.md#n8n Workflow Design] — Node 2 integration
- [Source: _bmad-output/planning-artifacts/epics.md] — Epic 1, Story 1.1

## Change Log

- 2026-03-06: Verified existing implementation against AC; all criteria satisfied, 16 tests pass. No code changes. Marked ready for review.
- 2026-03-06: Code review fixes: added Test 6 (multiple PDFs, largest selected), Test 7 (Excel-only folder), fixed Dev Notes pytest→python3. 25 tests pass.

## Dev Agent Record

### Agent Model Used

Claude (dev-story workflow)

### Debug Log References

### Completion Notes List

- Implementation verified: discover_inputs.py and test_discover.py already exist in stage-1-om-screener
- All 5 acceptance criteria satisfied: folder scan, JSON output, largest-PDF selection, error on empty/unsupported, PDF/Excel optional
- 25 tests pass: Mill One (PDF+Excel), empty folder, unsupported files, PDF-only, non-existent folder, multiple PDFs (largest selected), Excel-only
- Code review fixes: added Test 6 (multiple PDFs), Test 7 (Excel-only), fixed Dev Notes

### File List

- stage-1-om-screener/src/discover_inputs.py (existing)
- stage-1-om-screener/tests/test_discover.py (modified: added Test 6, Test 7)
