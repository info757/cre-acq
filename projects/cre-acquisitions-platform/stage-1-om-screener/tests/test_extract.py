"""
test_extract.py — Tests for extract_text.py, check_ocr_needed.py, ocr_pdf.py

US-01a Acceptance Criteria covered:
  - Text extraction from clean PDF
  - Low-density page detection
  - Targeted OCR on image pages
  - Error on missing/invalid file
  - Metadata written alongside text

Run: python3 tests/test_extract.py
"""

import json
import os
import subprocess
import sys
import tempfile

PYTHON = os.path.join(os.path.dirname(__file__), "../.venv/bin/python3")
EXTRACT = os.path.join(os.path.dirname(__file__), "../src/extract_text.py")
CHECK_OCR = os.path.join(os.path.dirname(__file__), "../src/check_ocr_needed.py")
OCR = os.path.join(os.path.dirname(__file__), "../src/ocr_pdf.py")
SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "../../tests/sample-oms")

NAVAHO = os.path.join(SAMPLE_DIR, "Navaho Drive Properties, LLC - Pref Equity Raise.pdf")
MILL_ONE_PDF = os.path.join(SAMPLE_DIR, "Mill-One-2025 (1) (1).pdf")

PASS = "✅"
FAIL = "❌"
results = []


def run(script, args):
    result = subprocess.run(
        [PYTHON, script] + args,
        capture_output=True, text=True
    )
    return result.returncode, result.stdout, result.stderr


def check(name, condition, detail=""):
    status = PASS if condition else FAIL
    results.append((status, name, detail))
    print(f"  {status} {name}" + (f" — {detail}" if detail else ""))


# ---------------------------------------------------------------------------

print("\n=== test_extract.py ===\n")

with tempfile.TemporaryDirectory() as tmpdir:

    # Test 1: Extract text from Navaho Drive (mixed text + image PDF)
    print("Test 1: extract_text — Navaho Drive (mixed text/image)")
    navaho_txt = os.path.join(tmpdir, "navaho_raw.txt")
    code, out, err = run(EXTRACT, ["--pdf", NAVAHO, "--out", navaho_txt])
    check("exit code 0", code == 0, err[:100] if code != 0 else "")
    check("text file created", os.path.isfile(navaho_txt))
    check("meta file created", os.path.isfile(navaho_txt + ".meta.json"))

    if os.path.isfile(navaho_txt + ".meta.json"):
        with open(navaho_txt + ".meta.json") as f:
            meta = json.load(f)
        check("page_count = 17", meta["page_count"] == 17, f"got {meta['page_count']}")
        check("total_chars > 10000", meta["total_chars"] > 10000, f"got {meta['total_chars']}")
        check("low_density_pages detected", len(meta["low_density_pages"]) > 0,
              f"got {meta['low_density_pages']}")
        check("pages 4, 9, 10 flagged as low-density",
              set([4, 9, 10]).issubset(set(meta["low_density_pages"])),
              f"got {meta['low_density_pages']}")

    # Test 2: check_ocr_needed — should flag targeted OCR for Navaho
    print("\nTest 2: check_ocr_needed — Navaho Drive")
    meta_path = navaho_txt + ".meta.json"
    code, out, err = run(CHECK_OCR, ["--meta", meta_path])
    check("exit code 0", code == 0)
    try:
        ocr_decision = json.loads(out)
        check("needs_ocr = true", ocr_decision["needs_ocr"] is True)
        check("mode = targeted", ocr_decision["mode"] == "targeted",
              f"got '{ocr_decision['mode']}'")
        check("target_pages includes 4", 4 in ocr_decision["target_pages"])
        check("target_pages includes 9", 9 in ocr_decision["target_pages"])
        check("target_pages includes 10", 10 in ocr_decision["target_pages"])
    except (json.JSONDecodeError, KeyError) as e:
        check("valid JSON from check_ocr_needed", False, str(e))

    # Test 3: OCR targeted pages on Navaho Drive
    print("\nTest 3: ocr_pdf — targeted OCR pages 4, 9, 10")
    pages = json.dumps(ocr_decision.get("target_pages", [4, 9, 10]))
    code, out, err = run(OCR, [
        "--pdf", NAVAHO,
        "--txt", navaho_txt,
        "--mode", "targeted",
        "--pages", pages
    ])
    check("exit code 0", code == 0, err[:100] if code != 0 else "")

    if os.path.isfile(navaho_txt):
        with open(navaho_txt) as f:
            full_text = f.read()
        check("OCR marker present in output", "[OCR]" in full_text)
        ocred_sections = full_text.split("[OCR]")[1:]
        ocred_content_len = sum(len(s.strip()) for s in ocred_sections)
        check("OCR sections have substantial content", ocred_content_len > 500,
              f"OCR content length: {ocred_content_len}")
        total_chars_after = len(full_text)
        check("text grew after OCR", total_chars_after > 16000,
              f"chars after OCR: {total_chars_after}")

    # Test 4: Extract text from Mill One PDF (clean text-layer PDF)
    print("\nTest 4: extract_text — Mill One PDF (clean text-layer)")
    mill_txt = os.path.join(tmpdir, "mill_raw.txt")
    code, out, err = run(EXTRACT, ["--pdf", MILL_ONE_PDF, "--out", mill_txt])
    check("exit code 0", code == 0, err[:100] if code != 0 else "")
    if os.path.isfile(mill_txt + ".meta.json"):
        with open(mill_txt + ".meta.json") as f:
            meta = json.load(f)
        check("Mill One has multiple pages", meta["page_count"] > 1,
              f"got {meta['page_count']}")
        check("Mill One has text content", meta["total_chars"] > 1000,
              f"got {meta['total_chars']}")

    # Test 5: check_ocr_needed — Mill One should be text-rich, no OCR needed
    print("\nTest 5: check_ocr_needed — Mill One (expect no OCR or minimal)")
    code, out, err = run(CHECK_OCR, ["--meta", mill_txt + ".meta.json"])
    check("exit code 0", code == 0)
    try:
        ocr_decision_mill = json.loads(out)
        # Mill One is a proper PDF — either no OCR or targeted only
        check("mode is not full OCR",
              ocr_decision_mill["mode"] != "full",
              f"got mode={ocr_decision_mill['mode']}")
    except (json.JSONDecodeError, KeyError) as e:
        check("valid JSON from check_ocr_needed", False, str(e))

    # Test 6: Error on missing file
    print("\nTest 6: extract_text — error on missing file")
    code, out, err = run(EXTRACT, ["--pdf", "/tmp/does_not_exist.pdf", "--out", "/tmp/out.txt"])
    check("exit code 1 on missing file", code == 1)
    check("error on stderr", "ERROR" in err)

    # Test 6b: check_ocr_needed --txt (n8n-compatible CLI)
    print("\nTest 6b: check_ocr_needed — --txt flag (infer meta path)")
    code, out, err = run(CHECK_OCR, ["--txt", navaho_txt])
    check("exit code 0 with --txt", code == 0)
    try:
        ocr_txt_decision = json.loads(out)
        check("--txt produces same result as --meta", ocr_txt_decision["mode"] == "targeted",
              f"got '{ocr_txt_decision['mode']}'")
    except (json.JSONDecodeError, KeyError) as e:
        check("valid JSON from check_ocr_needed --txt", False, str(e))

    # Test 7: Error on missing meta file for check_ocr_needed
    print("\nTest 7: check_ocr_needed — error on missing meta file")
    code, out, err = run(CHECK_OCR, ["--meta", "/tmp/no_such_file.meta.json"])
    check("exit code 1 on missing meta", code == 1)

    # Test 7b: check_ocr_needed — error on invalid JSON
    print("\nTest 7b: check_ocr_needed — error on invalid JSON meta")
    bad_meta = os.path.join(tmpdir, "bad.meta.json")
    with open(bad_meta, "w") as f:
        f.write("{ invalid json }")
    code, out, err = run(CHECK_OCR, ["--meta", bad_meta])
    check("exit code 1 on invalid JSON", code == 1)
    check("error mentions invalid JSON", "invalid" in err.lower() or "JSON" in err)

    # Test 8: extract_text — error on not a PDF (AC5)
    print("\nTest 8: extract_text — error on not a PDF")
    not_pdf = os.path.join(tmpdir, "notes.txt")
    with open(not_pdf, "w") as f:
        f.write("not a pdf")
    code, out, err = run(EXTRACT, ["--pdf", not_pdf, "--out", os.path.join(tmpdir, "out.txt")])
    check("exit code 1 on not a PDF", code == 1)
    check("error mentions not a PDF", "not a PDF" in err or "PDF" in err)

    # Test 9: ocr_pdf — full OCR mode (AC4 path)
    print("\nTest 9: ocr_pdf — full OCR mode")
    full_ocr_txt = os.path.join(tmpdir, "full_ocr.txt")
    with open(full_ocr_txt, "w") as f:
        f.write("[Page 1]\nplaceholder")
    code, out, err = run(OCR, [
        "--pdf", NAVAHO,
        "--txt", full_ocr_txt,
        "--mode", "full",
    ])
    check("full OCR exit code 0", code == 0, err[:100] if code != 0 else "")
    if os.path.isfile(full_ocr_txt):
        with open(full_ocr_txt) as f:
            full_ocr_content = f.read()
        check("full OCR overwrote file", "[Page 1] [OCR]" in full_ocr_content)
        check("full OCR has page breaks", "--- PAGE BREAK ---" in full_ocr_content)
        check("full OCR has 17 pages", full_ocr_content.count("[Page ") == 17,
              f"got {full_ocr_content.count('[Page ')} pages")

# ---------------------------------------------------------------------------
print()
passed = sum(1 for r in results if r[0] == PASS)
failed = sum(1 for r in results if r[0] == FAIL)
print(f"Results: {passed} passed, {failed} failed")
if failed:
    print("\nFAILED TESTS:")
    for r in results:
        if r[0] == FAIL:
            print(f"  {r[1]}" + (f" — {r[2]}" if r[2] else ""))
    sys.exit(1)
else:
    print("All tests passed.")
    sys.exit(0)
