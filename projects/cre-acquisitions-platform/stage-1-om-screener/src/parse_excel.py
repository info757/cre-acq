"""
parse_excel.py — Extract CRE metrics from Excel files in a deal folder.

Detects file type from filename keywords and sheet names, then routes to
the appropriate parser. Outputs a partial ExtractedMetrics JSON containing
only the fields actually found — no nulls for fields not in Excel.

All numeric extraction uses Decimal. Never float for money.

Usage:
    python3 src/parse_excel.py --files '["path1.xlsx","path2.xlsx"]' --out /tmp/deal_excel.json

Output: partial ExtractedMetrics JSON written to --out path.
"""

import argparse
import json
import os
import sys
from datetime import datetime, date
from decimal import Decimal, InvalidOperation

import openpyxl
import pandas as pd


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def to_decimal(value) -> Decimal | None:
    """Convert a cell value to Decimal. Returns None if not a valid number."""
    if value is None:
        return None
    try:
        d = Decimal(str(value))
        # Reject obviously bogus values (headers, formula artifacts)
        if d == 0:
            return Decimal("0")
        return d
    except (InvalidOperation, TypeError):
        return None


def to_date_str(value) -> str | None:
    """Convert a datetime or date cell value to ISO string."""
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    return None


def decimal_default(obj):
    """JSON serializer for Decimal and date types."""
    if isinstance(obj, Decimal):
        return float(obj)
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def classify_file(path: str, sheet_names: list[str]) -> str:
    """
    Classify an Excel file as: financials | rent_roll | commercial_rent_roll | loan_info | unknown.
    Uses filename keywords first, then sheet name fallback.
    """
    name_lower = os.path.basename(path).lower()

    if any(k in name_lower for k in ("financial", "finance", "income", "p&l")):
        return "financials"
    if "commercial" in name_lower and ("rr" in name_lower or "rent" in name_lower):
        return "commercial_rent_roll"
    if any(k in name_lower for k in ("itemized", "rent roll", " rr", "_rr")):
        return "rent_roll"
    if any(k in name_lower for k in ("loan", "debt", "mortgage")):
        return "loan_info"

    # Fall back to sheet name inspection
    sheets_lower = [s.lower() for s in sheet_names]
    if any("financial" in s or "income" in s or "noi" in s for s in sheets_lower):
        return "financials"
    if any("commercial" in s and ("rent" in s or "rr" in s or "lease" in s) for s in sheets_lower):
        return "commercial_rent_roll"
    if any("rent roll" in s or "rr" in s for s in sheets_lower):
        return "rent_roll"
    if any("loan" in s or "debt" in s for s in sheets_lower):
        return "loan_info"

    return "unknown"


# ---------------------------------------------------------------------------
# Financials parser
# ---------------------------------------------------------------------------

def parse_financials(path: str) -> dict:
    """
    Extract from an income statement / financials Excel file.

    Looks for:
    - Annualized NOI (labeled 'Annualized' adjacent to NOI row)
    - Total Operating Income
    - Total Operating Expense
    - 2025 Forecast NOI
    - Implied cap rate (if present)
    """
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb.active
    result = {}
    flags = []

    rows = list(ws.iter_rows(values_only=True))

    for i, row in enumerate(rows):
        if not row or row[0] is None:
            continue

        label = str(row[0]).strip().lower()

        # NOI row — look for annualized value in adjacent column
        if "noi" in label or "net operating income" in label:
            # Check the next row for 'Annualized' label and value
            if i + 1 < len(rows):
                next_row = rows[i + 1]
                if next_row:
                    for j, cell in enumerate(next_row):
                        if cell and "annualized" in str(cell).lower():
                            # Annualized value is one column to the right
                            if j + 1 < len(next_row):
                                val = to_decimal(next_row[j + 1])
                                if val:
                                    result["noi_trailing_annualized"] = val
                                    flags.append("noi_trailing: annualized from financials file")

            # Also capture the trailing total (last non-None numeric in row)
            numerics = [to_decimal(c) for c in row[1:] if to_decimal(c) is not None and to_decimal(c) != 0]
            if numerics:
                result["noi_trailing"] = numerics[-1]

        # Total Operating Income
        if "total operating income" in label:
            numerics = [to_decimal(c) for c in row[1:] if to_decimal(c) is not None and to_decimal(c) != 0]
            if numerics:
                result["gross_income"] = numerics[-1]

        # Total Operating Expense
        if "total operating expense" in label:
            numerics = [to_decimal(c) for c in row[1:] if to_decimal(c) is not None and to_decimal(c) != 0]
            if numerics:
                result["total_expenses"] = numerics[-1]

        # Implied cap rate (e.g. "Price @ 5.1% Cap")
        if "price @" in label and "cap" in label:
            # Extract the cap rate percentage from the label string
            import re
            match = re.search(r"(\d+\.?\d*)\s*%", label)
            if match:
                result["cap_rate_trailing"] = Decimal(match.group(1)) / Decimal("100")
                flags.append("cap_rate_trailing: extracted from financials implied price row")

    wb.close()

    if result:
        # Compute expense ratio if we have both income and expenses
        income = result.get("gross_income")
        expenses = result.get("total_expenses")
        if income and expenses and income != 0:
            result["expense_ratio"] = (expenses / income).quantize(Decimal("0.0001"))

        result["_extraction_flags"] = flags
        result["_source_file"] = os.path.basename(path)

    return result


# ---------------------------------------------------------------------------
# Residential rent roll parser
# ---------------------------------------------------------------------------

def parse_rent_roll(path: str) -> dict:
    """
    Extract from an itemized residential rent roll.

    Extracts:
    - Unit count (residential only — units with BD/BA)
    - Occupied unit count → occupancy %
    - Unit mix (bedroom type counts)
    - Avg rent per unit
    - Lease expiration distribution (roll risk)
    - Total monthly rent income
    """
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb.active
    result = {}
    flags = []

    rows = list(ws.iter_rows(values_only=True))

    # Find the header row (contains 'Status', 'Lease To', 'Unit', 'BD/BA')
    header_row_idx = None
    for i, row in enumerate(rows):
        if row and any(c and str(c).strip() == "Status" for c in row):
            if any(c and "BD" in str(c) for c in row):
                header_row_idx = i
                break

    if header_row_idx is None:
        wb.close()
        flags.append("rent_roll: could not find header row")
        return {"_extraction_flags": flags, "_source_file": os.path.basename(path)}

    header = [str(c).strip() if c else "" for c in rows[header_row_idx]]

    # Column index lookup
    def col(name):
        for i, h in enumerate(header):
            if name.lower() in h.lower():
                return i
        return None

    status_col = col("Status")
    bd_ba_col = col("BD/BA")
    sqft_col = col("Sqft")
    rent_col = col("Rent Income")
    lease_to_col = col("Lease To")
    unit_col = col("Unit")

    residential_units = []
    today = datetime.today().date()

    for row in rows[header_row_idx + 1:]:
        if not row or row[0] is None:
            continue

        status = str(row[status_col]).strip() if status_col is not None and row[status_col] else ""
        bd_ba = str(row[bd_ba_col]).strip() if bd_ba_col is not None and row[bd_ba_col] else ""

        # Skip commercial units (BD/BA is '--/--') and blank rows
        if not status or bd_ba in ("--/--", "", "BD/BA"):
            continue
        if status not in ("Current", "Notice", "Vacant", "Eviction"):
            continue

        rent = to_decimal(row[rent_col]) if rent_col is not None else None
        sqft = to_decimal(row[sqft_col]) if sqft_col is not None else None
        lease_to = to_date_str(row[lease_to_col]) if lease_to_col is not None else None

        # Parse BD count from "2/2.00" → 2
        bedrooms = None
        if "/" in bd_ba:
            try:
                bedrooms = int(bd_ba.split("/")[0])
            except ValueError:
                pass

        residential_units.append({
            "status": status,
            "bedrooms": bedrooms,
            "sqft": sqft,
            "rent": rent,
            "lease_to": lease_to,
        })

    wb.close()

    if not residential_units:
        flags.append("rent_roll: no residential units found")
        return {"_extraction_flags": flags, "_source_file": os.path.basename(path)}

    total_units = len(residential_units)
    occupied = [u for u in residential_units if u["status"] in ("Current", "Notice")]
    occupied_count = len(occupied)

    # Occupancy %
    occupancy_pct = (Decimal(occupied_count) / Decimal(total_units) * 100).quantize(Decimal("0.1"))
    result["occupancy_pct"] = occupancy_pct
    result["unit_count"] = total_units

    # Unit mix: count by bedroom type
    unit_mix = {}
    for u in residential_units:
        bd = u["bedrooms"]
        key = f"{bd}br" if bd is not None else "unknown"
        unit_mix[key] = unit_mix.get(key, 0) + 1
    result["unit_mix"] = unit_mix

    # Average rent (occupied units with rent data)
    rents = [u["rent"] for u in occupied if u["rent"] and u["rent"] > 0]
    if rents:
        result["avg_rent"] = (sum(rents) / Decimal(len(rents))).quantize(Decimal("0.01"))
        result["total_monthly_residential_rent"] = sum(rents)

    # Lease roll risk: % of leases expiring within 12 months
    leases_expiring_12mo = 0
    leases_with_dates = 0
    for u in occupied:
        if u["lease_to"]:
            leases_with_dates += 1
            exp_date = date.fromisoformat(u["lease_to"])
            months_out = (exp_date.year - today.year) * 12 + (exp_date.month - today.month)
            if months_out <= 12:
                leases_expiring_12mo += 1

    if leases_with_dates > 0:
        result["lease_roll_12mo_pct"] = (
            Decimal(leases_expiring_12mo) / Decimal(leases_with_dates) * 100
        ).quantize(Decimal("0.1"))
        flags.append(
            f"lease_roll: {leases_expiring_12mo} of {leases_with_dates} leases expire within 12 months"
        )

    result["_extraction_flags"] = flags
    result["_source_file"] = os.path.basename(path)
    return result


# ---------------------------------------------------------------------------
# Commercial rent roll parser
# ---------------------------------------------------------------------------

def parse_commercial_rent_roll(path: str) -> dict:
    """
    Extract from a commercial rent roll.

    Extracts:
    - Commercial tenant count
    - Total commercial monthly rent
    - Avg rent per SF
    - Lease expiration info
    """
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    ws = wb.active
    result = {}
    flags = []
    rows = list(ws.iter_rows(values_only=True))

    # Find header row
    header_row_idx = None
    for i, row in enumerate(rows):
        if row and any(c and "monthly rent" in str(c).lower() for c in row):
            header_row_idx = i
            break

    if header_row_idx is None:
        wb.close()
        return {"_extraction_flags": ["commercial_rr: no header row found"], "_source_file": os.path.basename(path)}

    header = [str(c).strip().lower() if c else "" for c in rows[header_row_idx]]

    def col(name):
        for i, h in enumerate(header):
            if name.lower() in h:
                return i
        return None

    rent_col = col("monthly rent")
    sqft_col = col("square footage")
    lease_exp_col = col("lease exp")

    tenants = []
    today = datetime.today().date()

    for row in rows[header_row_idx + 1:]:
        if not row or row[0] is None:
            continue
        # Skip CAM rows (unit number is None, label says 'CAM')
        if row[0] is None and row[1] and "cam" in str(row[1]).lower():
            continue
        rent = to_decimal(row[rent_col]) if rent_col is not None else None
        sqft = to_decimal(row[sqft_col]) if sqft_col is not None else None
        lease_exp = to_date_str(row[lease_exp_col]) if lease_exp_col is not None else None

        if rent and rent > 0:
            tenants.append({"rent": rent, "sqft": sqft, "lease_exp": lease_exp})

    wb.close()

    if tenants:
        result["commercial_tenant_count"] = len(tenants)
        result["total_monthly_commercial_rent"] = sum(t["rent"] for t in tenants)

        sqft_tenants = [t for t in tenants if t["sqft"] and t["sqft"] > 0]
        if sqft_tenants:
            total_sqft = sum(t["sqft"] for t in sqft_tenants)
            annual_rent = sum(t["rent"] * 12 for t in sqft_tenants)
            result["commercial_avg_rent_psf"] = (annual_rent / total_sqft).quantize(Decimal("0.01"))

        # Commercial lease roll risk
        leases_expiring_12mo = 0
        leases_with_dates = 0
        for t in tenants:
            if t["lease_exp"]:
                leases_with_dates += 1
                exp_date = date.fromisoformat(t["lease_exp"])
                months_out = (exp_date.year - today.year) * 12 + (exp_date.month - today.month)
                if months_out <= 12:
                    leases_expiring_12mo += 1
        if leases_with_dates > 0 and leases_expiring_12mo > 0:
            flags.append(
                f"commercial_lease_roll: {leases_expiring_12mo} of {leases_with_dates} commercial leases expire within 12 months"
            )

    result["_extraction_flags"] = flags
    result["_source_file"] = os.path.basename(path)
    return result


# ---------------------------------------------------------------------------
# Loan info parser
# ---------------------------------------------------------------------------

def parse_loan_info(path: str) -> dict:
    """
    Extract from a loan amortization file.

    Each sheet = one loan. Extracts:
    - Current outstanding balance (row 2, Balance column)
    - Interest rate
    - Monthly payment
    - Annual debt service (across all loans)
    - Computed DSCR (if NOI available — left for merge step)
    """
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    result = {}
    flags = []

    loans = []

    for sheet_name in wb.sheetnames:
        ws = wb[sheet_name]
        rows = list(ws.iter_rows(max_row=5, values_only=True))

        # Header row: Date Due | Date Paid | #days | Rate | Per Diem | Payment | Interest | Principal | Balance
        header = None
        balance_col = payment_col = rate_col = None

        for row in rows:
            if row and row[0] and "date" in str(row[0]).lower():
                header = [str(c).strip().lower() if c else "" for c in row]
                for i, h in enumerate(header):
                    if h == "balance":
                        balance_col = i
                    if h == "payment":
                        payment_col = i
                    if h == "rate":
                        rate_col = i
                break

        if header is None:
            flags.append(f"loan_info: could not parse sheet '{sheet_name}'")
            continue

        # Row 2 (index 1) has the opening balance, no payment yet
        # Row 3 (index 2) has the first scheduled payment with rate
        data_rows = list(ws.iter_rows(min_row=2, max_row=4, values_only=True))

        balance = None
        rate = None
        monthly_payment = None

        for row in data_rows:
            if not row:
                continue
            if balance is None and balance_col is not None:
                b = to_decimal(row[balance_col])
                if b and b > 0:
                    balance = b
            if rate is None and rate_col is not None:
                r = to_decimal(row[rate_col])
                if r and r > 0:
                    rate = r
            if monthly_payment is None and payment_col is not None:
                p = to_decimal(row[payment_col])
                if p and p > 0:
                    monthly_payment = p

        if balance:
            loans.append({
                "loan_id": sheet_name,
                "balance": balance,
                "rate": rate,
                "monthly_payment": monthly_payment,
            })

    wb.close()

    if loans:
        result["loan_count"] = len(loans)
        result["total_loan_balance"] = sum(l["balance"] for l in loans)

        # Annual debt service
        monthly_payments = [l["monthly_payment"] for l in loans if l["monthly_payment"]]
        if monthly_payments:
            result["annual_debt_service"] = (sum(monthly_payments) * 12).quantize(Decimal("0.01"))
            result["monthly_debt_service"] = sum(monthly_payments).quantize(Decimal("0.01"))
            flags.append(
                f"debt_service: computed from {len(monthly_payments)} loan(s), "
                f"${sum(monthly_payments):,.2f}/month"
            )

        # Weighted average rate
        rated_loans = [l for l in loans if l["rate"]]
        if rated_loans:
            total_balance = sum(l["balance"] for l in rated_loans)
            weighted_rate = sum(l["rate"] * l["balance"] for l in rated_loans) / total_balance
            result["loan_rate_weighted_avg"] = weighted_rate.quantize(Decimal("0.00001"))

        result["loans"] = [
            {
                "loan_id": l["loan_id"],
                "balance": l["balance"],
                "rate": l["rate"],
                "monthly_payment": l["monthly_payment"],
            }
            for l in loans
        ]

    result["_extraction_flags"] = flags
    result["_source_file"] = os.path.basename(path)
    return result


# ---------------------------------------------------------------------------
# Merge partial results (across multiple Excel files of same type)
# ---------------------------------------------------------------------------

def merge_partials(partials: list[dict]) -> dict:
    """
    Merge multiple partial metric dicts into one.
    First non-None value per key wins (earlier files take priority).
    _extraction_flags and loans lists are concatenated.
    """
    merged = {}
    all_flags = []
    all_loans = []

    for partial in partials:
        for key, value in partial.items():
            if key == "_extraction_flags":
                all_flags.extend(value)
            elif key == "loans":
                all_loans.extend(value)
            elif key == "_source_file":
                pass  # don't merge this
            elif key not in merged:
                merged[key] = value

    if all_flags:
        merged["_extraction_flags"] = all_flags
    if all_loans:
        merged["loans"] = all_loans

    return merged


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Parse Excel files and extract CRE metrics.")
    parser.add_argument("--files", required=True, help="JSON array of Excel file paths")
    parser.add_argument("--out", required=True, help="Output path for partial metrics JSON")
    args = parser.parse_args()

    try:
        file_paths = json.loads(args.files)
    except json.JSONDecodeError:
        print("ERROR: --files must be a valid JSON array of paths", file=sys.stderr)
        sys.exit(1)

    if not file_paths:
        print("ERROR: no files provided", file=sys.stderr)
        sys.exit(1)

    partials = []

    for path in file_paths:
        if not os.path.isfile(path):
            print(f"WARNING: file not found, skipping: {path}", file=sys.stderr)
            continue

        # Get sheet names for classification
        wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
        sheet_names = wb.sheetnames
        wb.close()

        file_type = classify_file(path, sheet_names)
        print(f"  {os.path.basename(path)} → {file_type}", file=sys.stderr)

        if file_type == "financials":
            partial = parse_financials(path)
        elif file_type == "rent_roll":
            partial = parse_rent_roll(path)
        elif file_type == "commercial_rent_roll":
            partial = parse_commercial_rent_roll(path)
        elif file_type == "loan_info":
            partial = parse_loan_info(path)
        else:
            print(f"  WARNING: unrecognized file type for {os.path.basename(path)}, skipping", file=sys.stderr)
            continue

        if partial:
            partials.append(partial)

    if not partials:
        print("WARNING: no data extracted from any Excel file", file=sys.stderr)
        result = {}
    else:
        result = merge_partials(partials)

    # Write output
    os.makedirs(os.path.dirname(args.out) if os.path.dirname(args.out) else ".", exist_ok=True)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, default=decimal_default)

    print(f"  Excel extraction complete → {args.out}", file=sys.stderr)
    print(f"  Fields extracted: {[k for k in result if not k.startswith('_')]}", file=sys.stderr)


if __name__ == "__main__":
    main()
