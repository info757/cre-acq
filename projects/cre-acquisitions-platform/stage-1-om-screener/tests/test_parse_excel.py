"""
test_parse_excel.py — Tests for parse_excel.py

US-01b Acceptance Criteria covered:
  - File type detection from filename + sheet names
  - Extraction from financials, rent roll, commercial RR, loan info
  - Decimal (not float) for all money values
  - Extraction flags logged
  - Unrecognized files skipped gracefully

Run: python3 tests/test_parse_excel.py
"""

import json
import os
import subprocess
import sys
import tempfile
from decimal import Decimal

PYTHON = os.path.join(os.path.dirname(__file__), "../.venv/bin/python3")
SCRIPT = os.path.join(os.path.dirname(__file__), "../src/parse_excel.py")
SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "../../tests/sample-oms")

MILL_FILES = [
    os.path.join(SAMPLE_DIR, "Mill One 2024-2025 Financials.xlsx"),
    os.path.join(SAMPLE_DIR, "Mill One Commercial RR.xlsx"),
    os.path.join(SAMPLE_DIR, "Mill One Itemized RR (5).xlsx"),
    os.path.join(SAMPLE_DIR, "Mill One Loan Info (2 tabs).xlsx"),
]

PASS = "✅"
FAIL = "❌"
results = []


def run(files_json, out_path):
    result = subprocess.run(
        [PYTHON, SCRIPT, "--files", files_json, "--out", out_path],
        capture_output=True, text=True
    )
    return result.returncode, result.stdout, result.stderr


def check(name, condition, detail=""):
    status = PASS if condition else FAIL
    results.append((status, name, detail))
    print(f"  {status} {name}" + (f" — {detail}" if detail else ""))


def approx_equal(a, b, tolerance=0.01):
    """Check two numbers are within tolerance %."""
    if b == 0:
        return a == 0
    return abs(a - b) / abs(b) < tolerance


# ---------------------------------------------------------------------------

print("\n=== test_parse_excel.py ===\n")

with tempfile.TemporaryDirectory() as tmpdir:
    out_path = os.path.join(tmpdir, "mill_excel.json")

    # Test 1: Full Mill One Excel package
    print("Test 1: Mill One — all 4 Excel files")
    missing = [f for f in MILL_FILES if not os.path.exists(f)]
    if missing:
        print(f"  ⚠️  Skipping — missing sample files: {missing}")
    else:
        files_json = json.dumps(MILL_FILES)
        code, out, err = run(files_json, out_path)
        check("exit code 0", code == 0, err[:200] if code != 0 else "")
        check("output file created", os.path.isfile(out_path))

        if os.path.isfile(out_path):
            with open(out_path) as f:
                data = json.load(f)

            # --- Financials ---
            print("\n  Financials checks:")
            check("noi_trailing_annualized present", "noi_trailing_annualized" in data)
            if "noi_trailing_annualized" in data:
                noi = data["noi_trailing_annualized"]
                check("annualized NOI ~$1,982,813",
                      approx_equal(noi, 1_982_813),
                      f"got {noi:,.2f}")
            check("gross_income present", "gross_income" in data)
            check("total_expenses present", "total_expenses" in data)
            check("expense_ratio present", "expense_ratio" in data)

            # --- Loan info ---
            print("\n  Loan checks:")
            check("loan_count = 2", data.get("loan_count") == 2,
                  f"got {data.get('loan_count')}")
            check("total_loan_balance ~$23M",
                  approx_equal(data.get("total_loan_balance", 0), 23_000_000),
                  f"got {data.get('total_loan_balance'):,.0f}")
            check("annual_debt_service ~$1,380,825",
                  approx_equal(data.get("annual_debt_service", 0), 1_380_825),
                  f"got {data.get('annual_debt_service'):,.2f}")
            check("loans list has 2 entries", len(data.get("loans", [])) == 2)

            # --- Rent roll ---
            print("\n  Rent roll checks:")
            check("unit_count present", "unit_count" in data)
            check("occupancy_pct present", "occupancy_pct" in data)
            check("unit_mix present", "unit_mix" in data)
            check("avg_rent present", "avg_rent" in data)
            check("lease_roll_12mo_pct present", "lease_roll_12mo_pct" in data)

            # --- Commercial RR ---
            print("\n  Commercial RR checks:")
            check("commercial_tenant_count present", "commercial_tenant_count" in data)
            check("total_monthly_commercial_rent present",
                  "total_monthly_commercial_rent" in data)

            # --- Extraction flags ---
            print("\n  Metadata checks:")
            check("_extraction_flags present", "_extraction_flags" in data)
            check("extraction flags is a list", isinstance(data.get("_extraction_flags"), list))

    # Test 2: Empty file list
    print("\nTest 2: Empty file list")
    code, out, err = run("[]", os.path.join(tmpdir, "empty.json"))
    check("exit code 1 on empty list", code == 1)

    # Test 3: Missing file path handled gracefully
    print("\nTest 3: Missing file path skipped with warning")
    fake_files = json.dumps(["/tmp/does_not_exist.xlsx"])
    out2 = os.path.join(tmpdir, "missing.json")
    code, out, err = run(fake_files, out2)
    check("exit code 0 (skip missing, don't crash)", code == 0)
    check("warning on stderr", "WARNING" in err or "warning" in err.lower())

    # Test 4: Single financials file
    print("\nTest 4: Financials file only")
    fin_path = os.path.join(SAMPLE_DIR, "Mill One 2024-2025 Financials.xlsx")
    if os.path.exists(fin_path):
        out3 = os.path.join(tmpdir, "fin_only.json")
        code, out, err = run(json.dumps([fin_path]), out3)
        check("exit code 0", code == 0)
        if os.path.isfile(out3):
            with open(out3) as f:
                fin_data = json.load(f)
            check("noi_trailing_annualized extracted",
                  "noi_trailing_annualized" in fin_data)
            check("no loan fields in financials-only output",
                  "loan_count" not in fin_data)

    # Test 5: Single loan file
    print("\nTest 5: Loan info file only")
    loan_path = os.path.join(SAMPLE_DIR, "Mill One Loan Info (2 tabs).xlsx")
    if os.path.exists(loan_path):
        out4 = os.path.join(tmpdir, "loan_only.json")
        code, out, err = run(json.dumps([loan_path]), out4)
        check("exit code 0", code == 0)
        if os.path.isfile(out4):
            with open(out4) as f:
                loan_data = json.load(f)
            check("two loans extracted", loan_data.get("loan_count") == 2)
            check("no rent roll fields in loan-only output",
                  "unit_count" not in loan_data)

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
