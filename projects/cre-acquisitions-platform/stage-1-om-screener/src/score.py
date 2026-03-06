"""
score.py — Screen extracted metrics against buy criteria.

Takes confirmed_metrics.json (output from apply_corrections.py) and buy-criteria.json,
runs rule-based screening, outputs ScreeningResult with GO/NO-GO/CONDITIONAL verdict.

Usage:
    python3 src/score.py \
        --metrics /tmp/deal_confirmed.json \
        --criteria shared/buy-criteria.json \
        --out /tmp/deal_scored.json
"""

import argparse
import json
import sys
from datetime import datetime, timezone
from decimal import Decimal


class Screener:
    """Rule-based CRE deal screening engine."""
    
    # Plausibility bounds for CRE metrics (industry-standard ranges, not just "not garbage")
    # Bounds are intentionally tight to catch unrealistic extractions
    PLAUSIBLE_RANGES = {
        "cap_rate_trailing": (0.02, 0.15),       # 2% to 15% (realistic range; >15% is speculative)
        "cap_rate_proforma": (0.02, 0.15),
        "occupancy_current": (0.50, 1.0),        # 50% to 100% (below 50% is distressed)
        "occupancy_economic": (0.50, 1.0),
        "dscr": (0.8, 3.0),                      # 0.8x to 3.0x (below 1.0 is negative CF; >3.0 is conservative)
        "ltv": (0.0, 0.90),                      # 0% to 90% (above 90% is aggressive)
        "expense_ratio": (0.15, 0.70),           # 15% to 70% (below 15% is suspicious; above 70% is poorly managed)
        "interest_rate": (0.01, 0.15),           # 1% to 15% (realistic lending rates)
    }
    
    def __init__(self, metrics: dict, criteria: dict):
        self.metrics = metrics
        self.criteria = criteria
        self.criteria_results = []
        self.red_flags = []
        self.verdict = None
    
    def _validate_metrics_plausibility(self, metrics: dict) -> list:
        """
        Validate extracted metrics are within plausible CRE ranges.
        Returns list of errors (empty if valid).
        """
        errors = []
        
        # Check financials
        fin = metrics.get("financials", {})
        for field, (min_val, max_val) in self.PLAUSIBLE_RANGES.items():
            val = fin.get(field)
            if val is not None and (val < min_val or val > max_val):
                errors.append(
                    f"Metric {field} = {val} is outside plausible range [{min_val}, {max_val}]"
                )
        
        # Check debt
        debt = metrics.get("debt", {})
        dscr = debt.get("dscr")
        if dscr is not None and (dscr < 0.5 or dscr > 5.0):
            errors.append(f"DSCR {dscr:.2f}x outside plausible range [0.5x, 5.0x]")
        
        ltv = debt.get("ltv")
        if ltv is not None and (ltv < 0.0 or ltv > 1.0):
            errors.append(f"LTV {ltv:.1%} outside plausible range [0%, 100%]")
        
        return errors
    
    def run(self) -> dict:
        """Run all screening rules and return ScreeningResult."""
        
        # FIRST: Validate extracted metrics are plausible
        plausibility_errors = self._validate_metrics_plausibility(self.metrics)
        if plausibility_errors:
            # Return FAIL verdict with explanation
            self.verdict = "NO-GO"
            self._add_flag("Data Integrity", "Extracted metrics failed plausibility checks: " + "; ".join(plausibility_errors))
            return self._build_result()
        
        # Extract convenience variables
        prop_type = self.metrics.get("property", {}).get("type")
        prop_market = self.metrics.get("property", {}).get("market")
        vintage = self.metrics.get("property", {}).get("vintage")
        asking_price = self.metrics.get("financials", {}).get("asking_price")
        noi_trailing = self.metrics.get("financials", {}).get("noi_trailing")
        noi_proforma = self.metrics.get("financials", {}).get("noi_proforma")
        cap_rate_trailing = self.metrics.get("financials", {}).get("cap_rate_trailing")
        occupancy = self.metrics.get("financials", {}).get("occupancy_current")
        expense_ratio = self.metrics.get("financials", {}).get("expense_ratio")
        ltv = self.metrics.get("debt", {}).get("ltv")
        dscr = self.metrics.get("debt", {}).get("dscr")
        gross_revenue = self.metrics.get("financials", {}).get("gross_revenue")
        total_expenses = self.metrics.get("financials", {}).get("total_expenses")
        property_tax = self.metrics.get("financials", {}).get("property_tax")
        
        # === HARD GATES (NO-GO if failed) ===
        
        # Property type whitelist
        if prop_type:
            allowed_types = self.criteria.get("property_types", [])
            if allowed_types and prop_type not in allowed_types:
                self._add_result(
                    "property_type_whitelist",
                    prop_type,
                    allowed_types,
                    "FAIL",
                    f"Property type '{prop_type}' not in whitelist: {allowed_types}"
                )
                self._add_flag("Property Type", f"Not in acquisition whitelist: {prop_type}")
            else:
                self._add_result("property_type_whitelist", prop_type, allowed_types, "PASS")
        
        # Markets whitelist (empty = no filter). Matches exact or city substring
        # (e.g. "Phoenix" matches "Phoenix, AZ" per om-extractor format).
        allowed_markets = self.criteria.get("markets", [])
        if allowed_markets and prop_market is not None:
            def _market_matches(market: str, allowed: list) -> bool:
                if market in allowed:
                    return True
                return any(am in market or market in am for am in allowed)
            if not _market_matches(prop_market, allowed_markets):
                self._add_result(
                    "markets_whitelist",
                    prop_market,
                    allowed_markets,
                    "FAIL",
                    f"Market '{prop_market}' not in whitelist: {allowed_markets}"
                )
                self._add_flag("Market", f"Not in acquisition whitelist: {prop_market}")
            else:
                self._add_result("markets_whitelist", prop_market, allowed_markets, "PASS")
        
        # Max asking price (null/missing = no filter)
        max_asking_price = self.criteria.get("max_asking_price")
        if max_asking_price is not None and asking_price is not None:
            if asking_price > max_asking_price:
                self._add_result(
                    "max_asking_price",
                    asking_price,
                    max_asking_price,
                    "FAIL",
                    f"Asking price ${asking_price:,.0f} exceeds max ${max_asking_price:,.0f}"
                )
                self._add_flag("Asking Price", f"Exceeds max: ${asking_price:,.0f} > ${max_asking_price:,.0f}")
            else:
                self._add_result("max_asking_price", asking_price, max_asking_price, "PASS")
        
        # DSCR hard minimum (null/missing = no filter)
        hard_min_dscr = self.criteria.get("debt", {}).get("hard_min_dscr")
        if hard_min_dscr is not None:
            if dscr is not None:
                if dscr < hard_min_dscr:
                    self._add_result(
                        "dscr_hard_min",
                        dscr,
                        hard_min_dscr,
                        "FAIL",
                        f"DSCR {dscr} below hard minimum {hard_min_dscr}"
                    )
                    self._add_flag("DSCR", f"Hard minimum failed: {dscr} < {hard_min_dscr}")
                else:
                    self._add_result("dscr_hard_min", dscr, hard_min_dscr, "PASS")
            else:
                self._add_result("dscr_hard_min", None, hard_min_dscr, "FLAG", "DSCR not available")
        
        # === SOFT GATES (FLAG if failed, but not automatic NO-GO) ===
        
        # DSCR minimum (null = no filter)
        min_dscr = self.criteria.get("debt", {}).get("min_dscr")
        if min_dscr is not None and dscr is not None:
            if dscr < min_dscr:
                self._add_result(
                    "dscr_min",
                    dscr,
                    min_dscr,
                    "FLAG",
                    f"Below target DSCR: {dscr} < {min_dscr}"
                )
                self._add_flag("DSCR", f"Below target minimum: {dscr} < {min_dscr}")
            else:
                self._add_result("dscr_min", dscr, min_dscr, "PASS")
        
        # LTV maximum (null = no filter)
        max_ltv = self.criteria.get("debt", {}).get("max_ltv")
        if max_ltv is not None and ltv is not None:
            if ltv > max_ltv:
                self._add_result(
                    "ltv_max",
                    ltv,
                    max_ltv,
                    "FLAG",
                    f"LTV exceeds target: {ltv} > {max_ltv}"
                )
                self._add_flag("LTV", f"Exceeds target: {ltv:.1%} > {max_ltv:.1%}")
            else:
                self._add_result("ltv_max", ltv, max_ltv, "PASS")
        
        # Cap rate minimum (null = no filter)
        min_cap = self.criteria.get("income", {}).get("min_cap_rate_trailing")
        if min_cap is not None and cap_rate_trailing is not None:
            if cap_rate_trailing < min_cap:
                self._add_result(
                    "cap_rate_min",
                    cap_rate_trailing,
                    min_cap,
                    "FLAG",
                    f"Cap rate below minimum: {cap_rate_trailing} < {min_cap}"
                )
                self._add_flag("Cap Rate", f"Below minimum: {cap_rate_trailing:.2%} < {min_cap:.2%}")
            else:
                self._add_result("cap_rate_min", cap_rate_trailing, min_cap, "PASS")
        
        # Occupancy minimum (null = no filter)
        min_occ = self.criteria.get("income", {}).get("min_occupancy")
        if min_occ is not None and occupancy is not None:
            if occupancy < min_occ:
                self._add_result(
                    "occupancy_min",
                    occupancy,
                    min_occ,
                    "FLAG",
                    f"Occupancy below minimum: {occupancy} < {min_occ}"
                )
                self._add_flag("Occupancy", f"Below minimum: {occupancy:.1%} < {min_occ:.1%}")
            else:
                self._add_result("occupancy_min", occupancy, min_occ, "PASS")
        
        # Expense ratio maximum (null = no filter)
        max_exp = self.criteria.get("expenses", {}).get("max_expense_ratio")
        if max_exp is not None and expense_ratio is not None:
            if expense_ratio > max_exp:
                self._add_result(
                    "expense_ratio_max",
                    expense_ratio,
                    max_exp,
                    "FLAG",
                    f"Expense ratio above maximum: {expense_ratio} > {max_exp}"
                )
                self._add_flag("Expense Ratio", f"Exceeds maximum: {expense_ratio:.1%} > {max_exp:.1%}")
            else:
                self._add_result("expense_ratio_max", expense_ratio, max_exp, "PASS")
        
        # Vintage range (null/missing = no filter)
        vintage_min = self.criteria.get("vintage_min")
        vintage_max = self.criteria.get("vintage_max")
        if vintage is not None:
            if vintage_min is not None and vintage < vintage_min:
                self._add_result(
                    "vintage_min",
                    vintage,
                    vintage_min,
                    "FLAG",
                    f"Vintage {vintage} below minimum {vintage_min}"
                )
                self._add_flag("Vintage", f"Below minimum: {vintage} < {vintage_min}")
            elif vintage_min is not None:
                self._add_result("vintage_min", vintage, vintage_min, "PASS")
            if vintage_max is not None and vintage > vintage_max:
                self._add_result(
                    "vintage_max",
                    vintage,
                    vintage_max,
                    "FLAG",
                    f"Vintage {vintage} above maximum {vintage_max}"
                )
                self._add_flag("Vintage", f"Above maximum: {vintage} > {vintage_max}")
            elif vintage_max is not None:
                self._add_result("vintage_max", vintage, vintage_max, "PASS")
        
        # === SOFT FLAGS (not pass/fail, just informational) ===
        
        # Proforma NOI premium (null = no filter)
        max_premium = self.criteria.get("income", {}).get("max_proforma_noi_premium")
        if max_premium is not None and noi_trailing and noi_proforma:
            premium = (noi_proforma - noi_trailing) / noi_trailing if noi_trailing > 0 else 0.0
            if premium > max_premium:
                self._add_flag(
                    "Proforma NOI Premium",
                    f"Proforma {premium:.1%} above trailing — verify underwriting assumptions"
                )
        
        # Property tax discrepancy (only flag if explicitly stated in extraction_flags)
        # This prevents false positives from estimation logic
        # The real check happens in the extraction layer when comparing stated vs. estimated
        
        # Extraction flags from the OM itself
        extraction_flags = self.metrics.get("extraction_flags", [])
        for flag_msg in extraction_flags:
            self._add_flag("Extraction", flag_msg)
        
        # === DETERMINE VERDICT ===
        
        # Hard fails = NO-GO
        hard_fails = [r for r in self.criteria_results if r["result"] == "FAIL"]
        
        # Any FLAGs = CONDITIONAL
        soft_flags = [r for r in self.criteria_results if r["result"] == "FLAG"]
        
        if hard_fails:
            self.verdict = "NO-GO"
        elif soft_flags or self.red_flags:
            self.verdict = "CONDITIONAL"
        else:
            self.verdict = "GO"
        
        return self._build_result()
    
    def _add_result(self, criterion: str, value, threshold, result: str, note: str = None):
        """Add a screening criterion result."""
        self.criteria_results.append({
            "criterion": criterion,
            "value": self._json_safe(value),
            "threshold": self._json_safe(threshold),
            "result": result,
            "note": note,
        })
    
    def _add_flag(self, category: str, explanation: str):
        """Add a red flag."""
        self.red_flags.append({
            "flag": category,
            "explanation": explanation,
        })
    
    def _json_safe(self, val):
        """Convert value to JSON-safe type."""
        if isinstance(val, Decimal):
            return float(val)
        if isinstance(val, (list, tuple)):
            return [self._json_safe(v) for v in val]
        if isinstance(val, dict):
            return {k: self._json_safe(v) for k, v in val.items()}
        return val
    
    def _build_result(self) -> dict:
        """Build final ScreeningResult dict."""
        return {
            "deal_id": self.metrics.get("deal_id"),
            "screened_at": datetime.now(timezone.utc).isoformat(),
            "criteria_used": "shared/buy-criteria.json",
            "verdict": self.verdict,
            "criteria_results": self.criteria_results,
            "red_flags": self.red_flags,
            "extracted_metrics": self.metrics,
        }


def main():
    parser = argparse.ArgumentParser(description="Screen metrics against buy criteria")
    parser.add_argument("--metrics", required=True, help="Path to confirmed_metrics.json")
    parser.add_argument("--criteria", required=True, help="Path to buy-criteria.json")
    parser.add_argument("--out", required=True, help="Output path for scoring_results.json")
    args = parser.parse_args()
    
    # Load metrics
    try:
        with open(args.metrics, "r") as f:
            metrics = json.load(f)
    except FileNotFoundError:
        print(f"[score] ERROR: Metrics file not found: {args.metrics}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[score] ERROR: Metrics JSON parsing failed at line {e.lineno}, col {e.colno}: {e.msg}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[score] ERROR loading metrics: {e}", file=sys.stderr)
        sys.exit(1)

    # Gate enforcement (AC5): reject metrics not confirmed by human review
    if not metrics.get("_human_confirmed"):
        print("[score] ERROR: Metrics must pass human review gate before scoring. Run apply_corrections.py first.", file=sys.stderr)
        sys.exit(1)

    # Load criteria
    try:
        with open(args.criteria, "r") as f:
            criteria = json.load(f)
    except FileNotFoundError:
        print(f"[score] ERROR: Criteria file not found: {args.criteria}", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"[score] ERROR: Criteria JSON parsing failed at line {e.lineno}, col {e.colno}: {e.msg}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[score] ERROR loading criteria: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Screen
    try:
        screener = Screener(metrics, criteria)
        result = screener.run()
    except ValueError as e:
        # Criteria validation failed
        print(f"[score] ERROR: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"[score] ERROR screening: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Output
    try:
        with open(args.out, "w") as f:
            json.dump(result, f, indent=2, cls=DecimalEncoder)
        print(f"[score] Verdict: {result['verdict']}", file=sys.stderr)
        print(f"[score] Screening results written to {args.out}", file=sys.stderr)
    except Exception as e:
        print(f"[score] ERROR writing output: {e}", file=sys.stderr)
        sys.exit(1)


class DecimalEncoder(json.JSONEncoder):
    """JSON encoder for Decimal types."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return float(obj)
        return super().default(obj)


if __name__ == "__main__":
    main()
