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
        "noi_proforma": None,
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
        """Proforma NOI >15% above trailing should flag."""
        metrics = deepcopy(STRONG_METRICS)
        metrics["financials"]["noi_trailing"] = 1000000
        metrics["financials"]["noi_proforma"] = 1200000  # 20% premium > 15% max
        screener = Screener(metrics, BASE_CRITERIA)
        result = screener.run()
        
        proforma_flags = [f for f in result["red_flags"] if "Proforma" in f["flag"]]
        assert len(proforma_flags) > 0
        print("✓ test_proforma_premium_flag PASSED")


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
    
    # TestScreenerIntegration
    ti = TestScreenerIntegration()
    ti.test_score_strong_deal()
    ti.test_score_weak_deal()
    
    print("\n✅ All tests passed")
