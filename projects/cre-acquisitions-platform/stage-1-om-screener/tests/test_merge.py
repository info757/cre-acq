"""
tests/test_merge.py — Unit tests for merge_inputs.py merge logic.

Tests the merge() function directly (no Claude calls, no file I/O).
Claude integration tested separately via manual run on Mill One sample.
"""

import json
import os
import subprocess
import sys
import tempfile
import pytest

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from merge_inputs import merge, normalize_excel_output, SCALAR_FIELDS, EMPTY_METRICS

PYTHON = os.path.join(os.path.dirname(__file__), "../.venv/bin/python3")
MERGE = os.path.join(os.path.dirname(__file__), "../src/merge_inputs.py")
PARSE_EXCEL = os.path.join(os.path.dirname(__file__), "../src/parse_excel.py")
PROMPT = os.path.join(os.path.dirname(__file__), "../prompts/om-extractor.md")
SAMPLE_DIR = os.path.join(os.path.dirname(__file__), "../../tests/sample-oms")
MILL_FILES = [
    os.path.join(SAMPLE_DIR, "Mill One 2024-2025 Financials.xlsx"),
    os.path.join(SAMPLE_DIR, "Mill One Commercial RR.xlsx"),
    os.path.join(SAMPLE_DIR, "Mill One Itemized RR (5).xlsx"),
    os.path.join(SAMPLE_DIR, "Mill One Loan Info (2 tabs).xlsx"),
]


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


class TestNormalizeExcelOutput:
    """parse_excel flat output maps correctly to nested ExtractedMetrics."""

    def test_cap_rate_trailing_mapped_from_excel(self):
        raw = {"noi_trailing_annualized": 900000, "cap_rate_trailing": 0.051, "_extraction_flags": []}
        out = normalize_excel_output(raw)
        assert out["financials"]["cap_rate_trailing"] == 0.051

    def test_noi_annualized_mapped(self):
        raw = {"noi_trailing_annualized": 873000, "_extraction_flags": []}
        out = normalize_excel_output(raw)
        assert out["financials"]["noi_trailing"] == 873000

    def test_noi_trailing_fallback_when_no_annualized(self):
        """parse_excel may output noi_trailing without noi_trailing_annualized."""
        raw = {"noi_trailing": 850000, "_extraction_flags": []}
        out = normalize_excel_output(raw)
        assert out["financials"]["noi_trailing"] == 850000

    def test_noi_annualized_preferred_over_noi_trailing(self):
        """When both present, noi_trailing_annualized wins."""
        raw = {"noi_trailing_annualized": 900000, "noi_trailing": 850000, "_extraction_flags": []}
        out = normalize_excel_output(raw)
        assert out["financials"]["noi_trailing"] == 900000


class TestMergeInputsCLI:
    """Integration: merge_inputs CLI with Excel-only (no Claude)."""

    def test_excel_only_cli_output_structure(self):
        """Run parse_excel → merge_inputs --excel only; verify ExtractedMetrics structure."""
        missing = [f for f in MILL_FILES if not os.path.exists(f)]
        if missing:
            pytest.skip(f"Missing sample files: {missing}")

        with tempfile.TemporaryDirectory() as tmpdir:
            excel_json = os.path.join(tmpdir, "excel.json")
            out_json = os.path.join(tmpdir, "extracted.json")

            # parse_excel
            r1 = subprocess.run(
                [PYTHON, PARSE_EXCEL, "--files", json.dumps(MILL_FILES), "--out", excel_json],
                capture_output=True, text=True, cwd=os.path.dirname(__file__)
            )
            assert r1.returncode == 0, r1.stderr

            # merge_inputs Excel-only
            r2 = subprocess.run(
                [PYTHON, MERGE, "--excel", excel_json, "--prompt", PROMPT, "--out", out_json],
                capture_output=True, text=True, cwd=os.path.dirname(__file__)
            )
            assert r2.returncode == 0, r2.stderr

            with open(out_json) as f:
                data = json.load(f)

            assert "property" in data
            assert "financials" in data
            assert "debt" in data
            assert "leases" in data
            assert "extraction_flags" in data
            assert "_sources" in data
            assert "extraction_timestamp" in data
            assert data["financials"]["noi_trailing"] is not None
            assert data["_sources"]["financials"]["noi_trailing"] == "excel"

    def test_raw_text_cli_with_mocked_claude(self):
        """Run merge_inputs --raw-text with mocked Claude; verify output structure."""
        stage_dir = os.path.join(os.path.dirname(__file__), "..")
        with tempfile.TemporaryDirectory() as tmpdir:
            raw_txt = os.path.join(tmpdir, "raw.txt")
            out_json = os.path.join(tmpdir, "extracted.json")
            with open(raw_txt, "w", encoding="utf-8") as f:
                f.write("Sample OM text for extraction.")

            mock_response = {
                "property": {"type": "multifamily", "market": "Charlotte, NC", "submarket": None,
                             "address": None, "vintage": 1998, "units": 142, "total_sf": None},
                "financials": {"asking_price": 18000000, "price_per_unit": None, "price_per_sf": None,
                               "noi_trailing": 873000, "noi_proforma": None, "cap_rate_trailing": 0.0485,
                               "cap_rate_proforma": None, "occupancy_current": 0.91, "occupancy_economic": None,
                               "gross_revenue": None, "total_expenses": None, "expense_ratio": None},
                "debt": {"ltv": None, "dscr": None, "interest_rate": None,
                         "maturity_date": None, "assumable": None},
                "leases": [],
                "extraction_flags": [],
            }

            wrapper = os.path.join(tmpdir, "run_merge.py")
            with open(wrapper, "w") as f:
                f.write('''import sys, os
sys.path.insert(0, os.path.join(os.getcwd(), "src"))
from unittest.mock import patch
MOCK = ''' + repr(mock_response) + '''
with patch("merge_inputs.call_claude", return_value=MOCK):
    import merge_inputs
    sys.argv = ["merge_inputs", "--raw-text", sys.argv[1], "--prompt", sys.argv[2], "--out", sys.argv[3]]
    merge_inputs.main()
''')
            prompt_path = os.path.abspath(os.path.join(stage_dir, "prompts", "om-extractor.md"))
            r = subprocess.run(
                [PYTHON, wrapper, raw_txt, prompt_path, out_json],
                capture_output=True, text=True,
                cwd=os.path.abspath(stage_dir)
            )
            assert r.returncode == 0, r.stderr
            with open(out_json) as f:
                data = json.load(f)
            assert "property" in data
            assert "financials" in data
            assert "_sources" in data
            assert data["financials"]["noi_trailing"] == 873000
            assert data["_sources"]["financials"]["noi_trailing"] == "claude"


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
