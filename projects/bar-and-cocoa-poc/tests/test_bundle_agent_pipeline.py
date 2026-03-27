"""Agent-facing bundle pipeline (real rules + raw JSON rows)."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from agent_tools import (  # noqa: E402
    load_bundle_rules,
    load_raw_inventory,
    run_bundle_selection_pipeline,
)


def test_run_bundle_selection_pipeline_smoke():
    base = Path(__file__).resolve().parent.parent
    inv_path = base / "data" / "real_inventory.json"
    rules_path = base / "rules" / "real_bundle_rules.json"
    if not inv_path.exists() or not rules_path.exists():
        import pytest

        pytest.skip("fixture files missing")

    raw = load_raw_inventory()
    rules = load_bundle_rules(rules_path)
    bid = rules["bundles"][0]["bundle_id"]
    data = run_bundle_selection_pipeline(raw, rules, bid)
    assert data["num_total"] == len(raw)
    assert data["num_candidates"] >= 0
    result = data["result"]
    assert "selected_bars" in result
    assert result["metadata"].get("source") == "real_bundle_rules"
    assert result["selected_bars"][0]["id"] == result["selected_bars"][0]["sku"]
