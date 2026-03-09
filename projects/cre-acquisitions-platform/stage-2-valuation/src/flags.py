"""
flags.py — Flag outlier assumptions and comp inconsistencies.

Usage:
    python3 src/flags.py --valuation-input path --valuation-result path
"""

import argparse
import json
import sys


# Asset-class expense ratio norms (min, max) — flag if outside
EXPENSE_RATIO_NORMS = {
    "multifamily": (0.35, 0.50),
    "industrial": (0.25, 0.40),
    "office": (0.40, 0.55),
    "retail": (0.35, 0.50),
    "mixed_use": (0.38, 0.52),
}

RENT_GROWTH_CONSERVATIVE = 0.03  # Flag if above 4%


def run_flags(valuation_input: dict, valuation_result: dict) -> list[dict]:
    flags = []
    overrides = valuation_input.get("valuation_overrides", {})
    screening = valuation_input.get("screening_result", {})
    fin = screening.get("extracted_metrics", {}).get("financials", {})
    prop = screening.get("extracted_metrics", {}).get("property", {})
    prop_type = (prop.get("type") or "multifamily").lower()

    # Expense ratio
    exp_ratio = fin.get("expense_ratio")
    if exp_ratio is not None:
        norms = EXPENSE_RATIO_NORMS.get(prop_type, (0.35, 0.55))
        if exp_ratio < norms[0]:
            flags.append({
                "flag": "expense_ratio_low",
                "explanation": f"Expense ratio {exp_ratio:.1%} is below {prop_type} norm ({norms[0]:.0%}-{norms[1]:.0%}). Verify operating expense completeness.",
            })
        elif exp_ratio > norms[1]:
            flags.append({
                "flag": "expense_ratio_high",
                "explanation": f"Expense ratio {exp_ratio:.1%} is above {prop_type} norm ({norms[0]:.0%}-{norms[1]:.0%}). May indicate deferred maintenance or above-market expenses.",
            })

    # Rent growth
    rent_growth = overrides.get("rent_growth_rate")
    if rent_growth is not None and rent_growth > 0.04:
        flags.append({
            "flag": "rent_growth_aggressive",
            "explanation": f"Rent growth assumption {rent_growth:.1%}/yr is above conservative 3-4% range. Consider sensitivity at 2.5-3%.",
        })

    # Cap rate spread (if we had comps we'd check; for now skip)
    return flags


def main():
    parser = argparse.ArgumentParser(description="Flag valuation assumption outliers")
    parser.add_argument("--valuation-input", required=True, help="Path to valuation_input.json")
    parser.add_argument("--valuation-result", required=True, help="Path to valuation result JSON (from dcf)")
    args = parser.parse_args()

    with open(args.valuation_input, "r") as f:
        vi = json.load(f)
    with open(args.valuation_result, "r") as f:
        vr = json.load(f)

    flags = run_flags(vi, vr)
    print(json.dumps(flags))


if __name__ == "__main__":
    main()
