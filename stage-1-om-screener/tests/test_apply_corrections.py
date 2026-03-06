"""
test_apply_corrections.py — Test human correction application.
"""

import json
import sys
import os
import tempfile
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from apply_corrections import (
    parse_corrections_input,
    apply_text_correction,
    apply_json_corrections,
    coerce_value,
    resolve_field_path,
)


# Test metrics fixture
BASE_METRICS = {
    "deal_id": "mill-one-2025",
    "extraction_timestamp": "2026-03-05T15:30:00+00:00",
    "property": {
        "type": "multifamily",
        "market": "Phoenix, AZ",
        "units": 185,
        "total_sf": 142500,
    },
    "financials": {
        "asking_price": 38900000,
        "noi_trailing": 1982813,
        "occupancy_current": 0.88,
        "expense_ratio": 0.37,
    },
    "debt": {
        "ltv": 0.59,
        "dscr": 1.447,
        "assumable": False,
    },
    "leases": [],
    "extraction_flags": [],
}


class TestCoerceValue:
    """Test value type coercion."""
    
    def test_coerce_boolean_true(self):
        assert coerce_value("assumable", "true") is True
        assert coerce_value("assumable", "yes") is True
    
    def test_coerce_boolean_false(self):
        assert coerce_value("assumable", "false") is False
        assert coerce_value("assumable", "no") is False
    
    def test_coerce_float(self):
        assert coerce_value("occupancy_current", "0.92") == 0.92
        assert coerce_value("cap_rate_trailing", "0.055") == 0.055
    
    def test_coerce_int(self):
        assert coerce_value("units", "200") == 200
        assert coerce_value("vintage", "2005") == 2005
    
    def test_coerce_string(self):
        assert coerce_value("market", "Dallas, TX") == "Dallas, TX"


class TestResolveFieldPath:
    """Test field name to (section, key) resolution."""
    
    def test_simple_field_names(self):
        assert resolve_field_path("units") == ("property", "units")
        assert resolve_field_path("asking_price") == ("financials", "asking_price")
        assert resolve_field_path("ltv") == ("debt", "ltv")
    
    def test_prefixed_field_names(self):
        assert resolve_field_path("property_units") == ("property", "units")
        assert resolve_field_path("financials_asking_price") == ("financials", "asking_price")
        assert resolve_field_path("debt_ltv") == ("debt", "ltv")
    
    def test_invalid_field(self):
        try:
            resolve_field_path("invalid_field_name")
            assert False, "Should raise ValueError"
        except ValueError as e:
            assert "Unknown field" in str(e)


class TestParseCorrectionsInput:
    """Test parsing various correction input formats."""
    
    def test_no_corrections(self):
        assert parse_corrections_input("ok") is None
        assert parse_corrections_input("") is None
        assert parse_corrections_input("  ") is None
    
    def test_single_text_correction(self):
        result = parse_corrections_input("fix: asking_price 42500000")
        assert isinstance(result, list)
        assert len(result) == 1
        assert "asking_price" in result[0]
    
    def test_multiple_text_corrections(self):
        result = parse_corrections_input("""
        fix: asking_price 42500000
        fix: units 200
        """)
        assert isinstance(result, list)
        assert len(result) == 2
    
    def test_json_corrections(self):
        result = parse_corrections_input('{"asking_price": 42500000, "units": 200}')
        assert isinstance(result, dict)
        assert result["asking_price"] == 42500000
        assert result["units"] == 200


class TestApplyTextCorrection:
    """Test applying single text-based corrections."""
    
    def test_correct_asking_price(self):
        corrected = apply_text_correction(BASE_METRICS, "fix: asking_price 42500000")
        assert corrected["financials"]["asking_price"] == 42500000
        # Original should be unchanged
        assert BASE_METRICS["financials"]["asking_price"] == 38900000
    
    def test_correct_units(self):
        corrected = apply_text_correction(BASE_METRICS, "fix: units 200")
        assert corrected["property"]["units"] == 200
    
    def test_correct_occupancy(self):
        corrected = apply_text_correction(BASE_METRICS, "fix: occupancy_current 0.92")
        assert corrected["financials"]["occupancy_current"] == 0.92
    
    def test_correct_boolean(self):
        corrected = apply_text_correction(BASE_METRICS, "fix: assumable true")
        assert corrected["debt"]["assumable"] is True
    
    def test_without_fix_prefix(self):
        # Should also accept format without "fix:" prefix
        result = apply_text_correction(BASE_METRICS, "asking_price 42500000")
        assert result["financials"]["asking_price"] == 42500000
    
    def test_invalid_format(self):
        try:
            apply_text_correction(BASE_METRICS, "invalid")
            assert False, "Should raise ValueError"
        except ValueError as e:
            assert "Invalid correction format" in str(e)
    
    def test_invalid_field(self):
        try:
            apply_text_correction(BASE_METRICS, "fix: nonexistent_field value")
            assert False, "Should raise ValueError"
        except ValueError as e:
            assert "Invalid field" in str(e)


class TestApplyJsonCorrections:
    """Test applying dict-based corrections."""
    
    def test_single_correction(self):
        corrected = apply_json_corrections(BASE_METRICS, {"asking_price": 42500000})
        assert corrected["financials"]["asking_price"] == 42500000
    
    def test_multiple_corrections(self):
        corrections = {
            "asking_price": 42500000,
            "units": 200,
            "occupancy_current": 0.95,
        }
        corrected = apply_json_corrections(BASE_METRICS, corrections)
        assert corrected["financials"]["asking_price"] == 42500000
        assert corrected["property"]["units"] == 200
        assert corrected["financials"]["occupancy_current"] == 0.95
    
    def test_unknown_field_skipped(self):
        # Invalid fields should be skipped with warning, not error
        corrections = {
            "asking_price": 42500000,
            "unknown_field": "value",
        }
        corrected = apply_json_corrections(BASE_METRICS, corrections)
        assert corrected["financials"]["asking_price"] == 42500000


class TestApplyCorrectionsIntegration:
    """Test the full apply_corrections.py script via main()."""
    
    def test_no_corrections_pass_through(self):
        """When corrections='ok', output should equal input."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(BASE_METRICS, f)
            metrics_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            out_file = f.name
        
        try:
            from apply_corrections import main
            import sys
            sys.argv = [
                "apply_corrections.py",
                "--metrics", metrics_file,
                "--corrections", "ok",
                "--out", out_file,
            ]
            main()
            
            with open(out_file, "r") as f:
                result = json.load(f)
            
            assert result["financials"]["asking_price"] == BASE_METRICS["financials"]["asking_price"]
            print("✓ test_no_corrections_pass_through PASSED")
        finally:
            os.unlink(metrics_file)
            os.unlink(out_file)
    
    def test_single_correction_via_main(self):
        """Test applying a single correction through the script."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(BASE_METRICS, f)
            metrics_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            out_file = f.name
        
        try:
            from apply_corrections import main
            import sys
            sys.argv = [
                "apply_corrections.py",
                "--metrics", metrics_file,
                "--corrections", "fix: asking_price 42500000",
                "--out", out_file,
            ]
            main()
            
            with open(out_file, "r") as f:
                result = json.load(f)
            
            assert result["financials"]["asking_price"] == 42500000
            print("✓ test_single_correction_via_main PASSED")
        finally:
            os.unlink(metrics_file)
            os.unlink(out_file)
    
    def test_json_corrections_via_main(self):
        """Test applying JSON corrections through the script."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(BASE_METRICS, f)
            metrics_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            out_file = f.name
        
        try:
            from apply_corrections import main
            import sys
            sys.argv = [
                "apply_corrections.py",
                "--metrics", metrics_file,
                "--corrections", '{"asking_price": 42500000, "units": 200}',
                "--out", out_file,
            ]
            main()
            
            with open(out_file, "r") as f:
                result = json.load(f)
            
            assert result["financials"]["asking_price"] == 42500000
            assert result["property"]["units"] == 200
            print("✓ test_json_corrections_via_main PASSED")
        finally:
            os.unlink(metrics_file)
            os.unlink(out_file)


if __name__ == "__main__":
    # Run all tests manually (pytest not available in system Python)
    tc = TestCoerceValue()
    tc.test_coerce_boolean_true()
    tc.test_coerce_boolean_false()
    tc.test_coerce_float()
    tc.test_coerce_int()
    tc.test_coerce_string()
    print("✓ TestCoerceValue PASSED\n")
    
    tfp = TestResolveFieldPath()
    tfp.test_simple_field_names()
    tfp.test_prefixed_field_names()
    tfp.test_invalid_field()
    print("✓ TestResolveFieldPath PASSED\n")
    
    tpci = TestParseCorrectionsInput()
    tpci.test_no_corrections()
    tpci.test_single_text_correction()
    tpci.test_multiple_text_corrections()
    tpci.test_json_corrections()
    print("✓ TestParseCorrectionsInput PASSED\n")
    
    tatc = TestApplyTextCorrection()
    tatc.test_correct_asking_price()
    tatc.test_correct_units()
    tatc.test_correct_occupancy()
    tatc.test_correct_boolean()
    tatc.test_without_fix_prefix()
    tatc.test_invalid_format()
    tatc.test_invalid_field()
    print("✓ TestApplyTextCorrection PASSED\n")
    
    tajc = TestApplyJsonCorrections()
    tajc.test_single_correction()
    tajc.test_multiple_corrections()
    tajc.test_unknown_field_skipped()
    print("✓ TestApplyJsonCorrections PASSED\n")
    
    tai = TestApplyCorrectionsIntegration()
    tai.test_no_corrections_pass_through()
    tai.test_single_correction_via_main()
    tai.test_json_corrections_via_main()
    
    print("\n✅ All tests passed")
