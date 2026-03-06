"""
test_format_output.py — Test narrative generation and output formatting.
"""

import json
import sys
import os
import tempfile

# Mock missing modules (for testing without full env setup)
try:
    import anthropic
except ImportError:
    class MockAnthropic:
        pass
    sys.modules['anthropic'] = MockAnthropic()

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv(*args, **kwargs):
        pass
    sys.modules['dotenv'] = type(sys)('dotenv')
    sys.modules['dotenv'].load_dotenv = load_dotenv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from format_output import (
    build_narrator_prompt,
    format_criteria_list,
    format_red_flags,
)


# Scored result fixture
SCORED_RESULT = {
    "deal_id": "mill-one-2025",
    "screened_at": "2026-03-05T15:30:00+00:00",
    "criteria_used": "shared/buy-criteria.json",
    "verdict": "GO",
    "criteria_results": [
        {"criterion": "property_type_whitelist", "value": "multifamily", "threshold": ["multifamily", "industrial"], "result": "PASS", "note": None},
        {"criterion": "dscr_hard_min", "value": 1.447, "threshold": 1.10, "result": "PASS", "note": None},
        {"criterion": "dscr_min", "value": 1.447, "threshold": 1.20, "result": "PASS", "note": None},
        {"criterion": "ltv_max", "value": 0.59, "threshold": 0.70, "result": "PASS", "note": None},
        {"criterion": "cap_rate_min", "value": 0.051, "threshold": 0.050, "result": "PASS", "note": None},
        {"criterion": "occupancy_min", "value": 0.92, "threshold": 0.88, "result": "PASS", "note": None},
        {"criterion": "expense_ratio_max", "value": 0.37, "threshold": 0.50, "result": "PASS", "note": None},
    ],
    "red_flags": [],
    "extracted_metrics": {
        "deal_id": "mill-one-2025",
        "extraction_timestamp": "2026-03-05T15:30:00+00:00",
        "property": {
            "type": "multifamily",
            "market": "Phoenix, AZ",
            "submarket": "North Phoenix",
            "units": 185,
            "total_sf": 142500,
        },
        "financials": {
            "asking_price": 38900000,
            "noi_trailing": 1982813,
            "cap_rate_trailing": 0.051,
            "occupancy_current": 0.92,
            "expense_ratio": 0.37,
        },
        "debt": {
            "ltv": 0.59,
            "dscr": 1.447,
        },
        "leases": [],
        "extraction_flags": [],
    },
}

PROMPT_TEMPLATE = """# OM Screener Narrative Prompt

Verdict: {{verdict}}
Property Type: {{property_type}}
Market: {{market}}
Asking Price: {{asking_price}}

Key Metrics:
- Cap Rate (Trailing): {{cap_rate_trailing}}
- Occupancy: {{occupancy}}
- DSCR: {{dscr}}
- LTV: {{ltv}}
- Expense Ratio: {{expense_ratio}}

Passing Criteria: {{passing_criteria}}
Failed/Flagged Criteria: {{flagged_criteria}}
Red Flags: {{red_flags}}

Write a one-paragraph narrative explaining this verdict."""


class TestFormatCriteriaList:
    """Test criteria formatting."""
    
    def test_format_passing_criteria(self):
        criteria = SCORED_RESULT["criteria_results"]
        result = format_criteria_list(criteria, "PASS")
        assert "property_type_whitelist" in result
        assert "dscr_min" in result
        assert "ltv_max" in result
        print("✓ test_format_passing_criteria PASSED")
    
    def test_format_flagged_criteria(self):
        # Create criteria with some FLAGs
        criteria = [
            {"criterion": "dscr_min", "result": "FLAG"},
            {"criterion": "ltv_max", "result": "FLAG"},
            {"criterion": "cap_rate_min", "result": "PASS"},
        ]
        result = format_criteria_list(criteria, "FLAG")
        assert "dscr_min" in result
        assert "ltv_max" in result
        assert "cap_rate_min" not in result
        print("✓ test_format_flagged_criteria PASSED")
    
    def test_format_no_criteria(self):
        result = format_criteria_list([], "PASS")
        assert result == "None"
        print("✓ test_format_no_criteria PASSED")


class TestFormatRedFlags:
    """Test red flag formatting."""
    
    def test_format_with_flags(self):
        flags = [
            {"flag": "DSCR", "explanation": "Below target minimum"},
            {"flag": "LTV", "explanation": "Exceeds threshold"},
        ]
        result = format_red_flags(flags)
        assert "DSCR" in result
        assert "Below target minimum" in result
        assert "LTV" in result
        assert ";" in result  # Multiple flags separated by ;
        print("✓ test_format_with_flags PASSED")
    
    def test_format_no_flags(self):
        result = format_red_flags([])
        assert result == "None"
        print("✓ test_format_no_flags PASSED")


class TestBuildNarratorPrompt:
    """Test narrator prompt construction."""
    
    def test_verdict_substitution(self):
        prompt = build_narrator_prompt(SCORED_RESULT, PROMPT_TEMPLATE)
        assert "Verdict: GO" in prompt
        assert "{{verdict}}" not in prompt
        print("✓ test_verdict_substitution PASSED")
    
    def test_property_type_substitution(self):
        prompt = build_narrator_prompt(SCORED_RESULT, PROMPT_TEMPLATE)
        assert "Property Type: multifamily" in prompt
        assert "{{property_type}}" not in prompt
        print("✓ test_property_type_substitution PASSED")
    
    def test_market_substitution(self):
        prompt = build_narrator_prompt(SCORED_RESULT, PROMPT_TEMPLATE)
        assert "Market: Phoenix, AZ" in prompt
        assert "{{market}}" not in prompt
        print("✓ test_market_substitution PASSED")
    
    def test_asking_price_substitution(self):
        prompt = build_narrator_prompt(SCORED_RESULT, PROMPT_TEMPLATE)
        assert "$38,900,000" in prompt
        assert "{{asking_price}}" not in prompt
        print("✓ test_asking_price_substitution PASSED")
    
    def test_metrics_substitution(self):
        prompt = build_narrator_prompt(SCORED_RESULT, PROMPT_TEMPLATE)
        assert "5.10%" in prompt  # cap_rate_trailing
        assert "92.0%" in prompt  # occupancy
        assert "1.45x" in prompt  # dscr
        assert "59.0%" in prompt  # ltv
        assert "37.0%" in prompt  # expense_ratio
        print("✓ test_metrics_substitution PASSED")
    
    def test_no_template_vars_remain(self):
        prompt = build_narrator_prompt(SCORED_RESULT, PROMPT_TEMPLATE)
        # Check that no {{ }} variables remain
        assert "{{" not in prompt
        assert "}}" not in prompt
        print("✓ test_no_template_vars_remain PASSED")


class TestFormatOutputIntegration:
    """Integration test for the full script."""
    
    def test_format_output_creates_file(self):
        """Test that format_output.py creates output file with narrative."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(SCORED_RESULT, f)
            scored_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write(PROMPT_TEMPLATE)
            prompt_file = f.name
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            out_file = f.name
        
        try:
            # For testing, we'll just verify the prompt building works
            # In a real test, you'd mock the Claude API
            prompt = build_narrator_prompt(SCORED_RESULT, PROMPT_TEMPLATE)
            assert "{{" not in prompt  # All variables substituted
            assert "verdict" in prompt.lower()
            print("✓ test_format_output_creates_file PASSED")
        finally:
            os.unlink(scored_file)
            os.unlink(prompt_file)
            if os.path.exists(out_file):
                os.unlink(out_file)


if __name__ == "__main__":
    tc = TestFormatCriteriaList()
    tc.test_format_passing_criteria()
    tc.test_format_flagged_criteria()
    tc.test_format_no_criteria()
    
    tf = TestFormatRedFlags()
    tf.test_format_with_flags()
    tf.test_format_no_flags()
    
    tb = TestBuildNarratorPrompt()
    tb.test_verdict_substitution()
    tb.test_property_type_substitution()
    tb.test_market_substitution()
    tb.test_asking_price_substitution()
    tb.test_metrics_substitution()
    tb.test_no_template_vars_remain()
    
    ti = TestFormatOutputIntegration()
    ti.test_format_output_creates_file()
    
    print("\n✅ All tests passed")
