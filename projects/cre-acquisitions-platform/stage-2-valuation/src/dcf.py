"""
dcf.py — 10-year DCF with reversion, IRR, equity multiple.

Usage:
    python3 src/dcf.py --valuation-input path/to/valuation_input.json [--out path]
"""

import argparse
import json
import sys
from decimal import Decimal


def project_noi_simple(noi_yr1: float, hold_years: int, rent_growth: float) -> list[float]:
    """Project NOI with simple growth (NOI * (1+g)^t)."""
    return [noi_yr1 * ((1 + rent_growth) ** t) for t in range(hold_years)]


def pv_cash_flows(cash_flows: list[float], discount_rate: float) -> float:
    """Compute PV of cash flow stream."""
    return sum(cf / ((1 + discount_rate) ** (i + 1)) for i, cf in enumerate(cash_flows))


def irr_newton(initial: float, cash_flows: list[float], tol: float = 1e-6) -> float:
    """Compute IRR via Newton iteration."""
    def npv(r):
        return -initial + sum(cf / ((1 + r) ** (i + 1)) for i, cf in enumerate(cash_flows))

    def npv_prime(r):
        return sum(-(i + 1) * cf / ((1 + r) ** (i + 2)) for i, cf in enumerate(cash_flows))

    r = 0.07
    for _ in range(100):
        n = npv(r)
        if abs(n) < tol:
            return r
        d = npv_prime(r)
        if abs(d) < 1e-10:
            break
        r = r - n / d
    return r


def irr_simple(initial: float, cash_flows: list[float]) -> float:
    """IRR via scipy."""
    try:
        from scipy.optimize import newton
        def npv(r):
            return -initial + sum(cf / ((1 + r) ** (i + 1)) for i, cf in enumerate(cash_flows))
        return float(newton(npv, 0.07))
    except ImportError:
        return irr_newton(initial, cash_flows)


def main():
    parser = argparse.ArgumentParser(description="10-year DCF valuation")
    parser.add_argument("--valuation-input", required=True, help="Path to valuation_input.json")
    parser.add_argument("--out", help="Output path (default: stdout)")
    args = parser.parse_args()

    with open(args.valuation_input, "r") as f:
        vi = json.load(f)

    screening = vi.get("screening_result", {})
    overrides = vi.get("valuation_overrides", {})
    fin = screening.get("extracted_metrics", {}).get("financials", {})

    noi_yr1 = float(fin.get("noi_trailing") or fin.get("noi_proforma")
        or screening.get("extracted_metrics", {}).get("financials", {}).get("noi_trailing", 0))
    if noi_yr1 <= 0:
        print("[dcf] ERROR: No NOI in input", file=sys.stderr)
        sys.exit(1)

    hold_years = int(overrides.get("hold_period_years", 10))
    rent_growth = float(overrides.get("rent_growth_rate", 0.03))
    expense_growth = float(overrides.get("expense_growth_rate", 0.02))
    exit_cap = float(overrides.get("exit_cap_rate", 0.0665))
    discount_rate = float(overrides.get("discount_rate", 0.07))

    cash_flows = project_noi_simple(noi_yr1, hold_years, rent_growth)
    noi_yr11 = cash_flows[-1] * (1 + rent_growth)
    reversion = noi_yr11 / exit_cap
    pv_cf = pv_cash_flows(cash_flows, discount_rate)
    pv_rev = reversion / ((1 + discount_rate) ** (hold_years + 1))
    dcf_value = pv_cf + pv_rev

    # Asking price as initial outlay for IRR
    asking = float(fin.get("asking_price") or 0) or dcf_value
    total_cf = cash_flows + [reversion]
    irr_val = irr_simple(asking, total_cf)


    def equity_multiple(initial: float, cfs: list[float], rev: float) -> float:
        total_proceeds = sum(cfs) + rev
        return total_proceeds / initial if initial > 0 else 0.0

    eq_mult = equity_multiple(asking, cash_flows, reversion)

    result = {
        "dcf_value": round(dcf_value, 2),
        "returns": {
            "irr": round(irr_val, 4),
            "equity_multiple": round(eq_mult, 2),
        },
        "sensitivity": {
            "cap_rate_range": [
                {"cap_rate": round(exit_cap - 0.005, 4), "value": round(noi_yr11 / (exit_cap - 0.005), 2)},
                {"cap_rate": round(exit_cap, 4), "value": round(reversion, 2)},
                {"cap_rate": round(exit_cap + 0.005, 4), "value": round(noi_yr11 / (exit_cap + 0.005), 2)},
            ],
        },
        "cash_flows": cash_flows,
        "reversion": round(reversion, 2),
    }

    out = json.dumps(result, indent=2)
    if args.out:
        with open(args.out, "w") as f:
            f.write(out)
    else:
        print(out)


if __name__ == "__main__":
    main()
