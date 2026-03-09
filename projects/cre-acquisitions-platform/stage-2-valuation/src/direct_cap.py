"""
direct_cap.py — Compute value via direct capitalization.

Usage:
    python3 src/direct_cap.py --noi 1983900 --cap-rate 0.051
    python3 src/direct_cap.py --valuation-input path/to/valuation_input.json
"""

import argparse
import json
import sys
from decimal import Decimal


def direct_cap(noi: float | Decimal, cap_rate: float | Decimal) -> Decimal:
    """Value = NOI / cap_rate."""
    if cap_rate <= 0:
        raise ValueError("cap_rate must be positive")
    return Decimal(str(noi)) / Decimal(str(cap_rate))


def main():
    parser = argparse.ArgumentParser(description="Direct cap valuation")
    parser.add_argument("--noi", type=float, help="Net operating income")
    parser.add_argument("--cap-rate", type=float, help="Market cap rate (e.g. 0.051 for 5.1%%)")
    parser.add_argument("--valuation-input", help="Path to valuation_input.json (extracts NOI and cap from ScreeningResult)")
    args = parser.parse_args()

    if args.valuation_input:
        with open(args.valuation_input, "r") as f:
            vi = json.load(f)
        screening = vi.get("screening_result", {})
        overrides = vi.get("valuation_overrides", {})
        fin = screening.get("extracted_metrics", {}).get("financials", {})
        noi = fin.get("noi_trailing") or fin.get("noi_proforma")
        cap_rate = overrides.get("market_cap_rate") or fin.get("cap_rate_trailing") or fin.get("cap_rate_proforma") or 0.0665
        if noi is None:
            print("[direct_cap] ERROR: No NOI in input (noi_trailing or noi_proforma required)", file=sys.stderr)
            sys.exit(1)
    else:
        if args.noi is None or args.cap_rate is None:
            parser.error("--noi and --cap-rate required, or use --valuation-input")
        noi = args.noi
        cap_rate = args.cap_rate

    value = direct_cap(noi, cap_rate)
    result = {"direct_cap_value": round(float(value), 2)}
    print(json.dumps(result))


if __name__ == "__main__":
    main()
