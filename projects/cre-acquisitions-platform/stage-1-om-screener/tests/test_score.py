"""
test_score.py — Test deal screening logic.
"""

import json
import sys
import os
import tempfile
from copy import deepcopy
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from score import Screener


# Test criteria (simplified version of buy-criteria.json)
BASE_CRITERIA = {
    "property_types": ["multifamily", "industrial"],
    "markets": [],
    "debt": {
        "max_ltv": 0.70,
        "min_dscr": 1.20,
        "hard_min_dscr": 1.10,
    },
    "income": {
        "min_cap_rate_trailing": 0.050,
        "min_occupancy": 0.88,
        "max_proforma_noi_premium": 0.15,
    },
    "expenses": {
        "max_expense_ratio": 0.50,
        "min_property_tax_pct_of_price": 0.005,
        "tax_assessment_pct": 0.60,
        "tax_rate": 0.012775,
    },
}

# Test metrics fixture (strong deal)
STRONG_METRICS = {
    "_human_confirmed": True,  # Gate marker (apply_corrections output)
    "deal_id": "test-strong",
    "extraction_timestamp": "2026-03-05T15:30:00+00:00",
    "property": {
        "type": "multifamily",
        "market": "Phoenix",
        "units": 185,
    },
    "financials": {
        "asking_price": 38900000,
        "noi_trailing": 1982813,
        "noi_proforma": 2181094,  # ~10% premium, within max 15%
        "cap_rate_trailing": 0.051,
        "occupancy_current": 0.92,
        "expense_ratio": 0.37,
        "gross_revenue": 3150000,
    },
    "debt": {
        "ltv": 0.59,
        "dscr": 1.447,
    },
    "leases": [],
    "extraction_flags": [],
}


class TestScreenerBasicMetrics:
    """Test screening of individual metrics."""
    
    def test_dscr_passes(self):
        """DSCR 1.447 should pass minimum 1.20."""
        metrics = deepcopy(STRONG_METRICS)
        screener = Screener(metrics, BASE_CRITERIA)
        result = screener.run()
        
        dscr_result = [r for r in result["criteria_results"] if r["criterion"] == "dscr_min"]
        assert len(dscr_result) == 1
        assert dscr_result[0]["result"] == "PASS"
        print("✓ test_dscr_passes PASSED")
    
    def test_dscr_flags(self):
        """DSCR 1.15 should flag (below 1.20 min but above 1.10 hard min)."""
        metrics = deepcopy(STRONG_METRICS)
        metrics["debt"]["dscr"] = 1.15
        screener = Screener(metrics, BASE_CRITERIA)
        result = screener.run()
        
        dscr_result = [r for r in result["criteria_results"] if r["criterion"] == "dscr_min"]
        assert len(dscr_result) == 1
        assert dscr_result[0]["result"] == "FLAG"
        print("✓ test_dscr_flags PASSED")
    
    def test_dscr_hard_fail(self):
        """DSCR 1.08 should hard fail (below 1.10 hard min)."""
        metrics = deepcopy(STRONG_METRICS)
        metrics["debt"]["dscr"] = 1.08
        screener = Screener(metrics, BASE_CRITERIA)
        result = screener.run()
        
        dscr_result = [r for r in result["criteria_results"] if r["criterion"] == "dscr_hard_min"]
        assert len(dscr_result) == 1
        assert dscr_result[0]["result"] == "FAIL"
        assert result["verdict"] == "NO-GO"
        print("✓ test_dscr_hard_fail PASSED")
    
    def test_ltv_passes(self):
        """LTV 0.59 should pass maximum 0.70."""
        metrics = deepcopy(STRONG_METRICS)
        screener = Screener(metrics, BASE_CRITERIA)
        result = screener.run()
        
        ltv_result = [r for r in result["criteria_results"] if r["criterion"] == "ltv_max"]
        assert len(ltv_result) == 1
        assert ltv_result[0]["result"] == "PASS"
        print("✓ test_ltv_passes PASSED")
    
    def test_ltv_flags(self):
        """LTV 0.72 should flag (above 0.70 max)."""
        metrics = deepcopy(STRONG_METRICS)
        metrics["debt"]["ltv"] = 0.72
        screener = Screener(metrics, BASE_CRITERIA)
        result = screener.run()
        
        ltv_result = [r for r in result["criteria_results"] if r["criterion"] == "ltv_max"]
        assert len(ltv_result) == 1
        assert ltv_result[0]["result"] == "FLAG"
        print("✓ test_ltv_flags PASSED")
    
    def test_cap_rate_passes(self):
        """Cap rate 0.051 should pass minimum 0.050."""
        metrics = deepcopy(STRONG_METRICS)
        screener = Screener(metrics, BASE_CRITERIA)
        result = screener.run()
        
        cap_result = [r for r in result["criteria_results"] if r["criterion"] == "cap_rate_min"]
        assert len(cap_result) == 1
        assert cap_result[0]["result"] == "PASS"
        print("✓ test_cap_rate_passes PASSED")
    
    def test_occupancy_passes(self):
        """Occupancy 0.92 should pass minimum 0.88."""
        metrics = deepcopy(STRONG_METRICS)
        screener = Screener(metrics, BASE_CRITERIA)
        result = screener.run()
        
        occ_result = [r for r in result["criteria_results"] if r["criterion"] == "occupancy_min"]
        assert len(occ_result) == 1
        assert occ_result[0]["result"] == "PASS"
        print("✓ test_occupancy_passes PASSED")
    
    def test_expense_ratio_passes(self):
        """Expense ratio 0.37 should pass maximum 0.50."""
        metrics = deepcopy(STRONG_METRICS)
        screener = Screener(metrics, BASE_CRITERIA)
        result = screener.run()
        
        exp_result = [r for r in result["criteria_results"] if r["criterion"] == "expense_ratio_max"]
        assert len(exp_result) == 1
        assert exp_result[0]["result"] == "PASS"
        print("✓ test_expense_ratio_passes PASSED")


class TestScreenerVerdicts:
    """Test verdict determination (GO, CONDITIONAL, NO-GO)."""
    
    def test_verdict_go(self):
        """All criteria pass → GO."""
        screener = Screener(STRONG_METRICS, BASE_CRITERIA)
        result = screener.run()
        assert result["verdict"] == "GO"
        print("✓ test_verdict_go PASSED")
    
    def test_verdict_conditional_soft_flag(self):
        """Soft flag (but no hard fail) → CONDITIONAL."""
        metrics = deepcopy(STRONG_METRICS)
        metrics["debt"]["dscr"] = 1.15  # Below 1.20 min, above 1.10 hard min = FLAG
        screener = Screener(metrics, BASE_CRITERIA)
        result = screener.run()
        assert result["verdict"] == "CONDITIONAL"
        print("✓ test_verdict_conditional_soft_flag PASSED")
    
    def test_verdict_no_go_hard_fail(self):
        """Hard fail (DSCR below 1.10) → NO-GO."""
        metrics = deepcopy(STRONG_METRICS)
        metrics["debt"]["dscr"] = 1.08
        screener = Screener(metrics, BASE_CRITERIA)
        result = screener.run()
        assert result["verdict"] == "NO-GO"
        print("✓ test_verdict_no_go_hard_fail PASSED")
    
    def test_verdict_no_go_property_type(self):
        """Property type not in whitelist → NO-GO."""
        metrics = deepcopy(STRONG_METRICS)
        metrics["property"]["type"] = "office"  # Not in ["multifamily", "industrial"]
        screener = Screener(metrics, BASE_CRITERIA)
        result = screener.run()
        assert result["verdict"] == "NO-GO"
        print("✓ test_verdict_no_go_property_type PASSED")


class TestScreenerFlags:
    """Test red flag generation."""
    
    def test_extraction_flags_propagated(self):
        """Extraction flags from metrics should be in red_flags."""
        metrics = deepcopy(STRONG_METRICS)
        metrics["extraction_flags"] = [
            "Property tax discrepancy: stated $24.6k vs. calc $298k",
            "Pro forma NOI not found",
        ]
        screener = Screener(metrics, BASE_CRITERIA)
        result = screener.run()
        
        extraction_flags = [f for f in result["red_flags"] if f["flag"] == "Extraction"]
        assert len(extraction_flags) == 2
        print("✓ test_extraction_flags_propagated PASSED")
    
    def test_proforma_premium_flag(self):
        """Proforma NOI >15% above trailing should flag in criteria_results and red_flags."""
        metrics = deepcopy(STRONG_METRICS)
        metrics["financials"]["noi_trailing"] = 1000000
        metrics["financials"]["noi_proforma"] = 1200000  # 20% premium > 15% max
        screener = Screener(metrics, BASE_CRITERIA)
        result = screener.run()
        
        proforma_result = [r for r in result["criteria_results"] if r["criterion"] == "max_proforma_noi_premium"]
        assert len(proforma_result) == 1
        assert proforma_result[0]["result"] == "FLAG"
        proforma_flags = [f for f in result["red_flags"] if "Proforma" in f["flag"]]
        assert len(proforma_flags) > 0
        print("✓ test_proforma_premium_flag PASSED")
    
    def test_proforma_premium_pass_in_criteria_results(self):
        """Proforma NOI within max premium → PASS in criteria_results."""
        metrics = deepcopy(STRONG_METRICS)
        # STRONG_METRICS has noi_proforma 2181094, noi_trailing 1982813 (~10% < 15%)
        screener = Screener(metrics, BASE_CRITERIA)
        result = screener.run()
        proforma_result = [r for r in result["criteria_results"] if r["criterion"] == "max_proforma_noi_premium"]
        assert len(proforma_result) == 1
        assert proforma_result[0]["result"] == "PASS"
        print("✓ test_proforma_premium_pass_in_criteria_results PASSED")
    
    def test_proforma_premium_trailing_zero_flags(self):
        """Trailing NOI zero or negative → FLAG (cannot compute premium)."""
        metrics = deepcopy(STRONG_METRICS)
        metrics["financials"]["noi_trailing"] = 0
        metrics["financials"]["noi_proforma"] = 1000000
        screener = Screener(metrics, BASE_CRITERIA)
        result = screener.run()
        proforma_result = [r for r in result["criteria_results"] if r["criterion"] == "max_proforma_noi_premium"]
        assert len(proforma_result) == 1
        assert proforma_result[0]["result"] == "FLAG"
        assert "positive" in (proforma_result[0].get("note") or "").lower()
        print("✓ test_proforma_premium_trailing_zero_flags PASSED")
    
    def test_missing_metric_flags(self):
        """Criterion set but metric missing → FLAG in criteria_results."""
        metrics = deepcopy(STRONG_METRICS)
        metrics["financials"]["asking_price"] = None
        criteria = deepcopy(BASE_CRITERIA)
        criteria["max_asking_price"] = 50_000_000
        screener = Screener(metrics, criteria)
        result = screener.run()
        price_result = [r for r in result["criteria_results"] if r["criterion"] == "max_asking_price"]
        assert len(price_result) == 1
        assert price_result[0]["result"] == "FLAG"
        assert "not available" in (price_result[0].get("note") or "").lower()
        print("✓ test_missing_metric_flags PASSED")


# Minimal criteria: all required sections, null optional filters (AC4: no filter)
MINIMAL_CRITERIA = {
    "property_types": [],
    "markets": [],
    "debt": {"hard_min_dscr": None, "min_dscr": None, "max_ltv": None},
    "income": {"min_cap_rate_trailing": None, "min_occupancy": None, "max_proforma_noi_premium": None},
    "expenses": {"max_expense_ratio": None},
}

# Minimal criteria with MISSING nested keys (AC4: missing = no filter)
MINIMAL_CRITERIA_MISSING_KEYS = {
    "property_types": [],
    "markets": [],
    "debt": {},  # No nested keys
    "income": {},
    "expenses": {},
}


class TestBuyCriteriaDefaults:
    """AC4: Missing/null criteria default to no filter."""

    def test_minimal_criteria_runs(self):
        """Minimal criteria (all null filters) → score runs, deal passes."""
        metrics = deepcopy(STRONG_METRICS)
        screener = Screener(metrics, MINIMAL_CRITERIA)
        result = screener.run()
        assert result["verdict"] in ("GO", "CONDITIONAL")
        print("✓ test_minimal_criteria_runs PASSED")

    def test_property_types_empty_passes_all(self):
        """property_types=[] → all property types pass."""
        metrics = deepcopy(STRONG_METRICS)
        metrics["property"]["type"] = "office"  # Not in BASE_CRITERIA whitelist
        screener = Screener(metrics, MINIMAL_CRITERIA)
        result = screener.run()
        assert result["verdict"] != "NO-GO"
        pt_result = [r for r in result["criteria_results"] if r["criterion"] == "property_type_whitelist"]
        assert len(pt_result) == 1
        assert pt_result[0]["result"] == "PASS"
        print("✓ test_property_types_empty_passes_all PASSED")

    def test_null_dscr_filter_skipped(self):
        """hard_min_dscr=null → DSCR check skipped, low DSCR does not fail."""
        metrics = deepcopy(STRONG_METRICS)
        metrics["debt"]["dscr"] = 1.0  # Would fail if hard_min_dscr were 1.10
        screener = Screener(metrics, MINIMAL_CRITERIA)
        result = screener.run()
        dscr_results = [r for r in result["criteria_results"] if "dscr" in r["criterion"]]
        assert len(dscr_results) == 0  # No DSCR checks when null
        assert result["verdict"] != "NO-GO"
        print("✓ test_null_dscr_filter_skipped PASSED")

    def test_missing_keys_default_to_no_filter(self):
        """Missing nested keys (e.g. debt: {}) → validation passes, scoring runs."""
        metrics = deepcopy(STRONG_METRICS)
        screener = Screener(metrics, MINIMAL_CRITERIA_MISSING_KEYS)
        result = screener.run()
        assert result["verdict"] in ("GO", "CONDITIONAL")
        # No debt/income/expense checks when sections are empty
        assert result["verdict"] != "NO-GO"
        print("✓ test_missing_keys_default_to_no_filter PASSED")

    def test_missing_sections_default_to_no_filter(self):
        """AC4: Missing top-level sections (property_types, debt, etc.) → no filter, scoring runs."""
        metrics = deepcopy(STRONG_METRICS)
        criteria = {}  # No sections at all
        screener = Screener(metrics, criteria)
        result = screener.run()
        assert result["verdict"] in ("GO", "CONDITIONAL")
        assert result["verdict"] != "NO-GO"
        print("✓ test_missing_sections_default_to_no_filter PASSED")


class TestMarketsMaxPriceVintage:
    """Tests for markets, max_asking_price, vintage filters."""

    def test_markets_whitelist_fail(self):
        """Market not in whitelist → NO-GO."""
        criteria = deepcopy(BASE_CRITERIA)
        criteria["markets"] = ["Charlotte", "Dallas"]
        metrics = deepcopy(STRONG_METRICS)
        metrics["property"]["market"] = "Phoenix"  # Not in whitelist
        screener = Screener(metrics, criteria)
        result = screener.run()
        mkt_result = [r for r in result["criteria_results"] if r["criterion"] == "markets_whitelist"]
        assert len(mkt_result) == 1
        assert mkt_result[0]["result"] == "FAIL"
        assert result["verdict"] == "NO-GO"
        print("✓ test_markets_whitelist_fail PASSED")

    def test_markets_whitelist_pass(self):
        """Market in whitelist → PASS."""
        criteria = deepcopy(BASE_CRITERIA)
        criteria["markets"] = ["Phoenix", "Charlotte"]
        metrics = deepcopy(STRONG_METRICS)
        screener = Screener(metrics, criteria)
        result = screener.run()
        mkt_result = [r for r in result["criteria_results"] if r["criterion"] == "markets_whitelist"]
        assert len(mkt_result) == 1
        assert mkt_result[0]["result"] == "PASS"
        print("✓ test_markets_whitelist_pass PASSED")

    def test_markets_city_match_phoenix_az(self):
        """City in criteria matches 'Phoenix, AZ' in property.market (om-extractor format)."""
        criteria = deepcopy(BASE_CRITERIA)
        criteria["markets"] = ["Phoenix"]
        metrics = deepcopy(STRONG_METRICS)
        metrics["property"]["market"] = "Phoenix, AZ"
        screener = Screener(metrics, criteria)
        result = screener.run()
        mkt_result = [r for r in result["criteria_results"] if r["criterion"] == "markets_whitelist"]
        assert len(mkt_result) == 1
        assert mkt_result[0]["result"] == "PASS"
        assert result["verdict"] != "NO-GO"
        print("✓ test_markets_city_match_phoenix_az PASSED")

    def test_max_asking_price_fail(self):
        """Asking price above max → NO-GO."""
        criteria = deepcopy(BASE_CRITERIA)
        criteria["max_asking_price"] = 30_000_000
        metrics = deepcopy(STRONG_METRICS)
        metrics["financials"]["asking_price"] = 38_900_000
        screener = Screener(metrics, criteria)
        result = screener.run()
        price_result = [r for r in result["criteria_results"] if r["criterion"] == "max_asking_price"]
        assert len(price_result) == 1
        assert price_result[0]["result"] == "FAIL"
        assert result["verdict"] == "NO-GO"
        print("✓ test_max_asking_price_fail PASSED")

    def test_max_asking_price_pass(self):
        """Asking price at or below max → PASS."""
        criteria = deepcopy(BASE_CRITERIA)
        criteria["max_asking_price"] = 50_000_000
        metrics = deepcopy(STRONG_METRICS)
        screener = Screener(metrics, criteria)
        result = screener.run()
        price_result = [r for r in result["criteria_results"] if r["criterion"] == "max_asking_price"]
        assert len(price_result) == 1
        assert price_result[0]["result"] == "PASS"
        print("✓ test_max_asking_price_pass PASSED")

    def test_vintage_outside_range_flags(self):
        """Vintage outside min/max range → FLAG."""
        criteria = deepcopy(BASE_CRITERIA)
        criteria["vintage_min"] = 2000
        criteria["vintage_max"] = 2015
        metrics = deepcopy(STRONG_METRICS)
        metrics["property"]["vintage"] = 1998
        screener = Screener(metrics, criteria)
        result = screener.run()
        vmin_result = [r for r in result["criteria_results"] if r["criterion"] == "vintage_min"]
        assert len(vmin_result) == 1
        assert vmin_result[0]["result"] == "FLAG"
        print("✓ test_vintage_outside_range_flags PASSED")


class TestScreenerIntegration:
    """Integration tests via main()."""
    
    def test_score_strong_deal(self):
        """Run score.py on a strong deal."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(STRONG_METRICS, f)
            metrics_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(BASE_CRITERIA, f)
            criteria_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            out_file = f.name
        
        try:
            from score import main
            import sys
            sys.argv = [
                "score.py",
                "--metrics", metrics_file,
                "--criteria", criteria_file,
                "--out", out_file,
            ]
            main()
            
            with open(out_file, "r") as f:
                result = json.load(f)
            
            assert result["verdict"] == "GO"
            assert "criteria_results" in result
            assert "red_flags" in result
            print("✓ test_score_strong_deal PASSED")
        finally:
            os.unlink(metrics_file)
            os.unlink(criteria_file)
            os.unlink(out_file)
    
    def test_score_weak_deal(self):
        """Run score.py on a weak deal with multiple soft flags."""
        weak_metrics = deepcopy(STRONG_METRICS)
        weak_metrics["debt"]["dscr"] = 1.15  # FLAG
        weak_metrics["debt"]["ltv"] = 0.72   # FLAG
        weak_metrics["financials"]["occupancy_current"] = 0.80  # FLAG
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(weak_metrics, f)
            metrics_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(BASE_CRITERIA, f)
            criteria_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            out_file = f.name
        
        try:
            from score import main
            import sys
            sys.argv = [
                "score.py",
                "--metrics", metrics_file,
                "--criteria", criteria_file,
                "--out", out_file,
            ]
            main()
            
            with open(out_file, "r") as f:
                result = json.load(f)
            
            assert result["verdict"] == "CONDITIONAL"
            # Should have at least 3 FLAGs
            flags = [r for r in result["criteria_results"] if r["result"] == "FLAG"]
            assert len(flags) >= 3
            print("✓ test_score_weak_deal PASSED")
        finally:
            os.unlink(metrics_file)
            os.unlink(criteria_file)
            os.unlink(out_file)


if __name__ == "__main__":
    # TestBuyCriteriaDefaults
    tbd = TestBuyCriteriaDefaults()
    tbd.test_minimal_criteria_runs()
    tbd.test_property_types_empty_passes_all()
    tbd.test_null_dscr_filter_skipped()
    tbd.test_missing_keys_default_to_no_filter()
    tbd.test_missing_sections_default_to_no_filter()

    # TestMarketsMaxPriceVintage
    tmv = TestMarketsMaxPriceVintage()
    tmv.test_markets_whitelist_fail()
    tmv.test_markets_whitelist_pass()
    tmv.test_markets_city_match_phoenix_az()
    tmv.test_max_asking_price_fail()
    tmv.test_max_asking_price_pass()
    tmv.test_vintage_outside_range_flags()

    # TestScreenerBasicMetrics
    tc = TestScreenerBasicMetrics()
    tc.test_dscr_passes()
    tc.test_dscr_flags()
    tc.test_dscr_hard_fail()
    tc.test_ltv_passes()
    tc.test_ltv_flags()
    tc.test_cap_rate_passes()
    tc.test_occupancy_passes()
    tc.test_expense_ratio_passes()
    
    # TestScreenerVerdicts
    tv = TestScreenerVerdicts()
    tv.test_verdict_go()
    tv.test_verdict_conditional_soft_flag()
    tv.test_verdict_no_go_hard_fail()
    tv.test_verdict_no_go_property_type()
    
    # TestScreenerFlags
    tf = TestScreenerFlags()
    tf.test_extraction_flags_propagated()
    tf.test_proforma_premium_flag()
    tf.test_proforma_premium_pass_in_criteria_results()
    tf.test_proforma_premium_trailing_zero_flags()
    tf.test_missing_metric_flags()
    
    # TestScreenerIntegration
    ti = TestScreenerIntegration()
    ti.test_score_strong_deal()
    ti.test_score_weak_deal()
    
    print("\n✅ All tests passed")
