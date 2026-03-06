"""
tests/test_merge.py — Unit tests for merge_inputs.py merge logic.

Tests the merge() function directly (no Claude calls, no file I/O).
Claude integration tested separately via manual run on Mill One sample.
"""

import sys
import os
import json
import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from merge_inputs import merge, SCALAR_FIELDS, EMPTY_METRICS


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

EXCEL_PARTIAL = {
    "property": {
        "type": "multifamily",
        "market": "Charlotte, NC",
        "vintage": 1998,
        "units": 142,
    },
    "financials": {
        "asking_price": 18200000,
        "noi_trailing": 873000,
        "expense_ratio": 0.48,
    },
    "debt": {
        "dscr": 1.18,
        "ltv": 0.75,
    },
    "leases": [],
    "extraction_flags": ["parsed from Mill One financials tab"],
}

CLAUDE_FULL = {
    "property": {
        "type": "multifamily",
        "market": "Charlotte, NC",
        "submarket": "South End",
        "address": "123 Main St, Charlotte, NC 28202",
        "vintage": 1999,  # different from Excel — Excel should win
        "units": 142,
        "total_sf": 120000,
    },
    "financials": {
        "asking_price": 18200000,
        "price_per_unit": 128169,
        "price_per_sf": 151.67,
        "noi_trailing": 850000,  # different — Excel should win
        "noi_proforma": 1100000,
        "cap_rate_trailing": 0.048,
        "cap_rate_proforma": 0.060,
        "occupancy_current": 0.91,
        "occupancy_economic": 0.88,
        "gross_revenue": 1680000,
        "total_expenses": 807000,
        "expense_ratio": 0.50,  # different — Excel should win
    },
    "debt": {
        "ltv": 0.70,  # different — Excel should win
        "dscr": 1.22,  # different — Excel should win
        "interest_rate": 0.065,
        "maturity_date": "2031-06-01",
        "assumable": False,
    },
    "leases": [
        {"tenant": "Acme Corp", "sf": 5000, "expiration": "2027-03-31", "rent_per_sf": 24.0}
    ],
    "extraction_flags": ["noi_proforma present — verify underwriting assumptions"],
}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

class TestMergeExcelWins:
    """Excel values take priority over Claude values."""

    def test_vintage_excel_wins(self):
        merged, sources = merge(EXCEL_PARTIAL, CLAUDE_FULL)
        assert merged["property"]["vintage"] == 1998  # Excel
        assert sources["property"]["vintage"] == "excel"

    def test_noi_trailing_excel_wins(self):
        merged, sources = merge(EXCEL_PARTIAL, CLAUDE_FULL)
        assert merged["financials"]["noi_trailing"] == 873000  # Excel
        assert sources["financials"]["noi_trailing"] == "excel"

    def test_dscr_excel_wins(self):
        merged, sources = merge(EXCEL_PARTIAL, CLAUDE_FULL)
        assert merged["debt"]["dscr"] == 1.18  # Excel
        assert sources["debt"]["dscr"] == "excel"

    def test_ltv_excel_wins(self):
        merged, sources = merge(EXCEL_PARTIAL, CLAUDE_FULL)
        assert merged["debt"]["ltv"] == 0.75  # Excel
        assert sources["debt"]["ltv"] == "excel"

    def test_expense_ratio_excel_wins(self):
        merged, sources = merge(EXCEL_PARTIAL, CLAUDE_FULL)
        assert merged["financials"]["expense_ratio"] == 0.48  # Excel
        assert sources["financials"]["expense_ratio"] == "excel"


class TestClaudeFillsGaps:
    """Claude fills fields that Excel did not provide."""

    def test_submarket_from_claude(self):
        merged, sources = merge(EXCEL_PARTIAL, CLAUDE_FULL)
        assert merged["property"]["submarket"] == "South End"
        assert sources["property"]["submarket"] == "claude"

    def test_address_from_claude(self):
        merged, sources = merge(EXCEL_PARTIAL, CLAUDE_FULL)
        assert merged["property"]["address"] == "123 Main St, Charlotte, NC 28202"
        assert sources["property"]["address"] == "claude"

    def test_noi_proforma_from_claude(self):
        merged, sources = merge(EXCEL_PARTIAL, CLAUDE_FULL)
        assert merged["financials"]["noi_proforma"] == 1100000
        assert sources["financials"]["noi_proforma"] == "claude"

    def test_cap_rate_trailing_from_claude(self):
        merged, sources = merge(EXCEL_PARTIAL, CLAUDE_FULL)
        assert merged["financials"]["cap_rate_trailing"] == 0.048
        assert sources["financials"]["cap_rate_trailing"] == "claude"

    def test_interest_rate_from_claude(self):
        merged, sources = merge(EXCEL_PARTIAL, CLAUDE_FULL)
        assert merged["debt"]["interest_rate"] == 0.065
        assert sources["debt"]["interest_rate"] == "claude"

    def test_total_sf_from_claude(self):
        merged, sources = merge(EXCEL_PARTIAL, CLAUDE_FULL)
        assert merged["property"]["total_sf"] == 120000
        assert sources["property"]["total_sf"] == "claude"


class TestNullHandling:
    """Fields with no data in either source should be null."""

    def test_null_field_source_is_none(self):
        # Excel has no price_per_unit, Claude doesn't have it either
        excel_only = {"property": {}, "financials": {}, "debt": {}, "leases": [], "extraction_flags": []}
        merged, sources = merge(excel_only, None)
        assert merged["financials"]["price_per_unit"] is None
        assert sources["financials"]["price_per_unit"] is None

    def test_all_nulls_when_no_inputs_have_data(self):
        empty_excel = {"property": {}, "financials": {}, "debt": {}, "leases": [], "extraction_flags": []}
        merged, sources = merge(empty_excel, None)
        for section, field in SCALAR_FIELDS:
            assert merged[section][field] is None


class TestExcelOnly:
    """Works correctly with Excel input and no Claude."""

    def test_excel_only_fills_available_fields(self):
        merged, sources = merge(EXCEL_PARTIAL, None)
        assert merged["financials"]["noi_trailing"] == 873000
        assert sources["financials"]["noi_trailing"] == "excel"

    def test_excel_only_leaves_gaps_null(self):
        merged, sources = merge(EXCEL_PARTIAL, None)
        assert merged["financials"]["noi_proforma"] is None
        assert sources["financials"]["noi_proforma"] is None


class TestClaudeOnly:
    """Works correctly with Claude input and no Excel."""

    def test_claude_only_fills_available_fields(self):
        merged, sources = merge(None, CLAUDE_FULL)
        assert merged["financials"]["noi_trailing"] == 850000
        assert sources["financials"]["noi_trailing"] == "claude"

    def test_claude_only_source_tags(self):
        merged, sources = merge(None, CLAUDE_FULL)
        assert sources["property"]["submarket"] == "claude"
        assert sources["debt"]["assumable"] == "claude"


class TestLeasesMerge:
    """Lease data: Excel wins if present, otherwise Claude."""

    def test_claude_leases_used_when_excel_has_none(self):
        merged, _ = merge(EXCEL_PARTIAL, CLAUDE_FULL)
        # EXCEL_PARTIAL has empty leases list → Claude's leases used
        assert len(merged["leases"]) == 1
        assert merged["leases"][0]["tenant"] == "Acme Corp"

    def test_excel_leases_win_when_present(self):
        excel_with_leases = {**EXCEL_PARTIAL, "leases": [
            {"tenant": "Excel Tenant", "sf": 3000, "expiration": "2026-12-31", "rent_per_sf": 20.0}
        ]}
        merged, _ = merge(excel_with_leases, CLAUDE_FULL)
        assert merged["leases"][0]["tenant"] == "Excel Tenant"


class TestFlagsMerge:
    """Extraction flags are combined from both sources."""

    def test_flags_combined(self):
        merged, _ = merge(EXCEL_PARTIAL, CLAUDE_FULL)
        flags = merged["extraction_flags"]
        assert any("Mill One" in f for f in flags)
        assert any("proforma" in f for f in flags)

    def test_flags_deduplicated(self):
        excel = {**EXCEL_PARTIAL, "extraction_flags": ["duplicate flag"]}
        claude = {**CLAUDE_FULL, "extraction_flags": ["duplicate flag"]}
        merged, _ = merge(excel, claude)
        assert merged["extraction_flags"].count("duplicate flag") == 1


class TestOutputStructure:
    """Merged output has correct top-level structure."""

    def test_all_sections_present(self):
        merged, sources = merge(EXCEL_PARTIAL, CLAUDE_FULL)
        assert "property" in merged
        assert "financials" in merged
        assert "debt" in merged
        assert "leases" in merged
        assert "extraction_flags" in merged

    def test_sources_covers_all_fields(self):
        _, sources = merge(EXCEL_PARTIAL, CLAUDE_FULL)
        for section, field in SCALAR_FIELDS:
            assert section in sources
            assert field in sources[section]
