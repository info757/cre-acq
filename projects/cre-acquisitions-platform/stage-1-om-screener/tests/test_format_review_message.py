"""
test_format_review_message.py — Test Telegram message formatting.
"""

import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from format_review_message import format_extracted_metrics, format_money, format_percent


def test_format_money():
    assert format_money(1500000) == "$1,500,000"
    assert format_money(None) == "—"
    assert format_money(0) == "$0"


def test_format_percent():
    assert format_percent(0.88) == "88.0%"
    assert format_percent(0.055) == "5.5%"
    assert format_percent(88) == "88.0%"
    assert format_percent(None) == "—"


def test_format_extracted_metrics_with_sources():
    """Test formatting with source tags."""
    metrics = {
        "deal_id": "mill-one-2025",
        "extraction_timestamp": "2026-03-05T15:30:00+00:00",
        "property": {
            "type": "multifamily",
            "market": "Phoenix",
            "submarket": "North Phoenix",
            "address": "123 Mill Drive",
            "vintage": 2005,
            "units": 185,
            "total_sf": 142500,
        },
        "financials": {
            "asking_price": 38900000,
            "price_per_unit": 210270,
            "price_per_sf": 273,
            "gross_revenue": 3150000,
            "total_expenses": 1167000,
            "noi_trailing": 1982813,
            "noi_proforma": None,
            "cap_rate_trailing": 0.051,
            "cap_rate_proforma": None,
            "occupancy_current": 0.88,
            "occupancy_economic": 0.92,
            "expense_ratio": 0.37,
        },
        "debt": {
            "ltv": 0.59,
            "dscr": 1.447,
            "interest_rate": 0.055,
            "maturity_date": "2035-03-15",
            "assumable": False,
        },
        "leases": [
            {"tenant": "TenantA", "sf": 42000, "expiration": "2027-06-30", "rent_per_sf": 25.50},
            {"tenant": "TenantB", "sf": 28500, "expiration": "2026-12-31", "rent_per_sf": 24.00},
        ],
        "extraction_flags": [
            "Property tax discrepancy: stated $24.6k vs. calc $298k",
            "Pro forma NOI not found in OM",
        ],
        "_sources": {
            "property": {
                "type": "excel",
                "market": "claude",
                "submarket": "claude",
                "address": "claude",
                "vintage": "excel",
                "units": "excel",
                "total_sf": "excel",
            },
            "financials": {
                "asking_price": "claude",
                "price_per_unit": "excel",
                "price_per_sf": "claude",
                "gross_revenue": "excel",
                "total_expenses": "excel",
                "noi_trailing": "excel",
                "noi_proforma": None,
                "cap_rate_trailing": "claude",
                "cap_rate_proforma": None,
                "occupancy_current": "excel",
                "occupancy_economic": "claude",
                "expense_ratio": "excel",
            },
            "debt": {
                "ltv": "claude",
                "dscr": "claude",
                "interest_rate": "claude",
                "maturity_date": "claude",
                "assumable": None,
            },
        },
    }

    msg = format_extracted_metrics(metrics)

    # Check key sections exist
    assert "PROPERTY" in msg
    assert "FINANCIALS" in msg
    assert "DEBT" in msg
    assert "LEASES" in msg
    assert "EXTRACTION FLAGS" in msg

    # Check source tags are included
    assert "[EXCEL]" in msg
    assert "[CLAUDE]" in msg
    assert "[?]" in msg

    # Check specific values formatted correctly
    assert "$38,900,000" in msg
    assert "185" in msg or "185.0" in msg
    assert "Phoenix" in msg
    assert "North Phoenix" in msg
    assert "TenantA" in msg
    assert "Property tax discrepancy" in msg

    # Check formatting for percentages
    assert "88.0%" in msg or "88%" in msg  # occupancy_current

    # AC: User instructions for confirmation/correction
    assert "Reply 'ok'" in msg or "Reply \"ok\"" in msg
    assert "fix:" in msg

    print("✓ test_format_extracted_metrics_with_sources PASSED")


def test_format_empty_metrics():
    """Test formatting with minimal/empty metrics."""
    metrics = {
        "deal_id": "test-empty",
        "extraction_timestamp": "2026-03-05T15:30:00+00:00",
        "property": {},
        "financials": {},
        "debt": {},
        "leases": [],
        "extraction_flags": [],
        "_sources": {},
    }

    msg = format_extracted_metrics(metrics)

    # Should still have headers and structure
    assert "EXTRACTION REVIEW" in msg
    assert "PROPERTY" in msg
    assert "FINANCIALS" in msg
    assert "DEBT" in msg

    print("✓ test_format_empty_metrics PASSED")


def test_format_zero_values_displayed():
    """Zero-valued metrics are displayed (not hidden by truthy check)."""
    metrics = {
        "deal_id": "test-zero",
        "extraction_timestamp": "2026-03-05T15:30:00+00:00",
        "property": {"type": "multifamily", "market": "Test", "units": 0},
        "financials": {"asking_price": 0, "noi_trailing": 0, "occupancy_current": 0.0},
        "debt": {"ltv": 0, "dscr": 0},
        "leases": [],
        "extraction_flags": [],
        "_sources": {},
    }

    msg = format_extracted_metrics(metrics)

    assert "$0" in msg
    assert "0" in msg
    assert "0.0%" in msg or "0%" in msg

    print("✓ test_format_zero_values_displayed PASSED")


def test_format_no_sources():
    """Test formatting when _sources is missing."""
    metrics = {
        "deal_id": "test-no-sources",
        "extraction_timestamp": "2026-03-05T15:30:00+00:00",
        "property": {
            "type": "industrial",
            "market": "Dallas",
        },
        "financials": {
            "asking_price": 25000000,
        },
        "debt": {},
        "leases": [],
        "extraction_flags": [],
        # No _sources key
    }

    msg = format_extracted_metrics(metrics)

    # Should format without error
    assert "industrial" in msg
    assert "Dallas" in msg
    assert "$25,000,000" in msg

    print("✓ test_format_no_sources PASSED")


if __name__ == "__main__":
    test_format_money()
    test_format_percent()
    test_format_extracted_metrics_with_sources()
    test_format_empty_metrics()
    test_format_zero_values_displayed()
    test_format_no_sources()
    print("\n✅ All tests passed")
