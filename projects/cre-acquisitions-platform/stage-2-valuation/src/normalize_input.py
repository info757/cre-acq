"""
normalize_input.py — Merge ScreeningResult + valuation overrides + buy-criteria defaults.

Produces full ValuationInput for Stage 2 valuation pipeline.

Usage:
    python3 src/normalize_input.py --screening-result output/deal.json [--overrides path] [--criteria path] [--out path]
"""

import argparse
import json
import os
import sys
from decimal import Decimal
from pathlib import Path


def _project_root():
    return Path(__file__).resolve().parent.parent.parent


def _default_criteria_path():
    return _project_root() / "shared" / "buy-criteria.json"


def load_screening_result(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def load_overrides(path: str | None) -> dict:
    if not path:
        return {}
    with open(path, "r") as f:
        return json.load(f)


def load_buy_criteria(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)


def merge_valuation_input(
    screening_result: dict,
    overrides: dict,
    criteria: dict,
) -> dict:
    """Build full ValuationInput with defaults from buy-criteria."""
    returns = criteria.get("returns", {})
    debt = criteria.get("debt", {})

    defaults = {
        "market_cap_rate": None,  # Filled from deal trailing cap or exit_cap below
        "exit_cap_rate": returns.get("exit_cap_rate", 0.0665),
        "hold_period_years": returns.get("hold_period_years", 10),
        "rent_growth_rate": returns.get("rent_growth_pct", 0.03),
        "expense_growth_rate": criteria.get("capex", {}).get("expense_inflation", 0.02),
        "discount_rate": returns.get("discount_rate", 0.07),
        "vacancy_rate": None,
        "capex_reserve_per_unit": None,
        "debt_terms": {
            "ltv": debt.get("max_ltv", 0.70),
            "interest_rate": None,
            "amortization_years": 30,
        },
    }

    # Override with user-provided values
    if overrides:
        for k, v in overrides.items():
            if v is not None and k in defaults:
                if k == "debt_terms" and isinstance(v, dict):
                    defaults["debt_terms"] = {**defaults["debt_terms"], **v}
                else:
                    defaults[k] = v

    # market_cap_rate: prefer override, else trailing cap from deal, else exit_cap from criteria
    fin = screening_result.get("extracted_metrics", {}).get("financials", {})
    if defaults.get("market_cap_rate") is None:
        defaults["market_cap_rate"] = (
            float(fin["cap_rate_trailing"])
            if fin.get("cap_rate_trailing")
            else defaults.get("exit_cap_rate", 0.0665)
        )

    return {
        "screening_result": screening_result,
        "valuation_overrides": defaults,
    }


def main():
    parser = argparse.ArgumentParser(description="Normalize valuation input from ScreeningResult + overrides")
    parser.add_argument("--screening-result", required=True, help="Path to Stage 1 ScreeningResult JSON")
    parser.add_argument("--overrides", help="Path to valuation_overrides JSON (optional)")
    parser.add_argument("--criteria", default=str(_default_criteria_path()), help="Path to buy-criteria.json")
    parser.add_argument("--out", help="Output path (default: stdout)")
    args = parser.parse_args()

    if not os.path.exists(args.screening_result):
        print(f"[normalize_input] ERROR: Screening result not found: {args.screening_result}", file=sys.stderr)
        sys.exit(1)

    screening = load_screening_result(args.screening_result)
    overrides = load_overrides(args.overrides) if args.overrides and os.path.exists(args.overrides) else {}

    if not os.path.exists(args.criteria):
        print(f"[normalize_input] WARNING: buy-criteria not found, using fallback defaults", file=sys.stderr)
        criteria = {}
    else:
        criteria = load_buy_criteria(args.criteria)

    result = merge_valuation_input(screening, overrides, criteria)
    out_json = json.dumps(result, indent=2, default=lambda x: float(x) if isinstance(x, Decimal) else x)

    if args.out:
        os.makedirs(os.path.dirname(args.out) or ".", exist_ok=True)
        with open(args.out, "w") as f:
            f.write(out_json)
        print(f"[normalize_input] Wrote {args.out}", file=sys.stderr)
    else:
        print(out_json)


if __name__ == "__main__":
    main()
