"""Tests for bundle preference helpers and hard constraints."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import bundle_select as srb  # noqa: E402


def _bundle_404_3():
    base = Path(__file__).resolve().parent.parent
    rules = json.loads((base / "rules" / "real_bundle_rules.json").read_text())
    return next(b for b in rules["bundles"] if b["bundle_id"] == "ST-BAR-404-3")


def test_chocolate_type_subtype_hard_constraint():
    bundle = _bundle_404_3()
    bar_ok = {
        "product_type": "Chocolate Bars",
        "net_weight_g": 60,
        "retail_price": 12,
        "current_inventory": 20,
        "days_till_expiry": 100,
        "cacaonum": 70,
        "chocolate_type": ["Dark", "Plain"],
        "diet_icons": ["Vegan"],
    }
    bar_bad = {**bar_ok, "chocolate_type": ["Dark", "Inclusions"]}
    assert srb.passes_hard_constraints(bar_ok, bundle)[0] is True
    assert srb.passes_hard_constraints(bar_bad, bundle)[0] is False


def test_preference_max_plain_cap():
    prefs = {"plain_bars_max": 2}
    b_plain = {"chocolate_type": ["Milk", "Plain"], "vendor": "a", "source_country": "X"}
    trial = [b_plain, b_plain, b_plain]
    assert srb.preference_max_ok(trial, prefs) is False
    assert srb.preference_max_ok(trial[:2], prefs) is True


def test_filled_praline_combined_limit():
    prefs = {
        "inclusion_limits": {"Filled_or_Praline": 1, "Fruit": 3},
        "max_bars_same_inclusion_flavor": 99,
    }
    b1 = {
        "chocolate_type": ["Milk"],
        "inclusion_flavor": ["Filled"],
        "vendor": "v1",
        "source_country": "France",
    }
    b2 = {
        "chocolate_type": ["Milk"],
        "inclusion_flavor": ["Praline"],
        "vendor": "v2",
        "source_country": "Italy",
    }
    assert srb.preference_max_ok([b1, b2], prefs) is False
    assert srb.preference_max_ok([b1], prefs) is True


def test_preference_mins():
    prefs = {"plain_bars_min": 2, "white_bars_min": 0}
    b_plain = {"chocolate_type": ["Dark", "Plain"]}
    assert srb.preference_mins_ok([b_plain], prefs) is False
    assert srb.preference_mins_ok([b_plain, b_plain], prefs) is True
