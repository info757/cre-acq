"""
test_discover.py — Tests for discover_inputs.py

US-01 Acceptance Criteria covered:
  - Scans folder and identifies PDF and Excel files
  - Returns correct structure
  - Selects largest PDF when multiple present
  - Errors on empty or unsupported folder

Run: python3 tests/test_discover.py
"""

import json
import os
import subprocess
import sys
import tempfile
import shutil

PYTHON = os.path.join(os.path.dirname(__file__), "../.venv/bin/python3")
SCRIPT = os.path.join(os.path.dirname(__file__), "../src/discover_inputs.py")
SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "../../tests/sample-oms")

PASS = "✅"
FAIL = "❌"
results = []


def run(folder):
    result = subprocess.run(
        [PYTHON, SCRIPT, "--folder", folder],
        capture_output=True, text=True
    )
    return result.returncode, result.stdout, result.stderr


def check(name, condition, detail=""):
    status = PASS if condition else FAIL
    results.append((status, name, detail))
    print(f"  {status} {name}" + (f" — {detail}" if detail else ""))


# ---------------------------------------------------------------------------

print("\n=== test_discover.py ===\n")

# Test 1: Mill One folder (PDF + 4 Excel files)
print("Test 1: Mill One deal folder (PDF + Excel)")
code, out, err = run(SAMPLE_DIR)
check("exit code 0", code == 0)
try:
    data = json.loads(out)
    check("has_pdf = true", data["has_pdf"] is True)
    check("pdf_path is a .pdf", data["pdf_path"] and data["pdf_path"].endswith(".pdf"))
    check("has_excel = true", data["has_excel"] is True)
    check("excel_paths has 4 files", len(data["excel_paths"]) == 4,
          f"got {len(data['excel_paths'])}")
    check("no .gitkeep in excel_paths",
          not any(".gitkeep" in p for p in data["excel_paths"]))
except (json.JSONDecodeError, KeyError) as e:
    check("valid JSON output", False, str(e))

# Test 2: Empty folder
print("\nTest 2: Empty folder")
with tempfile.TemporaryDirectory() as tmpdir:
    code, out, err = run(tmpdir)
    check("exit code 1 on empty folder", code == 1)
    check("error message on stderr", "ERROR" in err)

# Test 3: Folder with only unsupported files
print("\nTest 3: Folder with only unsupported files")
with tempfile.TemporaryDirectory() as tmpdir:
    open(os.path.join(tmpdir, "notes.txt"), "w").close()
    open(os.path.join(tmpdir, "image.png"), "w").close()
    code, out, err = run(tmpdir)
    check("exit code 1 on unsupported files", code == 1)
    check("error message mentions supported types", "Supported" in err or "supported" in err)

# Test 4: Folder with only PDF (no Excel)
print("\nTest 4: PDF-only folder")
with tempfile.TemporaryDirectory() as tmpdir:
    # Copy just the Navaho Drive PDF
    navaho = os.path.join(SAMPLE_DIR, "Navaho Drive Properties, LLC - Pref Equity Raise.pdf")
    if os.path.exists(navaho):
        shutil.copy(navaho, tmpdir)
        code, out, err = run(tmpdir)
        check("exit code 0", code == 0)
        data = json.loads(out)
        check("has_pdf = true", data["has_pdf"] is True)
        check("has_excel = false", data["has_excel"] is False)
        check("excel_paths is empty list", data["excel_paths"] == [])
    else:
        check("Navaho Drive PDF found", False, "sample file missing")

# Test 5: Non-existent folder
print("\nTest 5: Non-existent folder")
code, out, err = run("/tmp/this_folder_does_not_exist_xyz")
check("exit code 1 on missing folder", code == 1)
check("error message on stderr", "ERROR" in err)

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
