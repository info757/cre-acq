"""Tests for normalize_input.py"""
import json
import tempfile
import pytest
from pathlib import Path

import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from normalize_input import merge_valuation_input


def test_merge_uses_trailing_cap():
    screening = {
        "extracted_metrics": {
            "financials": {
                "noi_trailing": 1983900,
                "cap_rate_trailing": 0.051,
            },
        },
    }
    criteria = {"returns": {"hold_period_years": 10, "exit_cap_rate": 0.0665, "discount_rate": 0.07}}
    result = merge_valuation_input(screening, {}, criteria)
    assert result["valuation_overrides"]["market_cap_rate"] == 0.051


def test_merge_overrides_win():
    screening = {"extracted_metrics": {"financials": {}}}
    criteria = {"returns": {"exit_cap_rate": 0.0665}}
    overrides = {"market_cap_rate": 0.055}
    result = merge_valuation_input(screening, overrides, criteria)
    assert result["valuation_overrides"]["market_cap_rate"] == 0.055
