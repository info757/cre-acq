"""Tests for ShopiCoda CSV → real_inventory.json import."""

from datetime import date
from pathlib import Path

import pytest

import sys

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from bundle_csv import (  # noqa: E402
    load_bundle_items_csv,
    parse_int_maybe,
    parse_money,
    row_to_bar,
    weekly_velocity_from_qty_sellout,
)


def test_parse_money():
    assert parse_money("$11.50") == 11.5
    assert parse_money("12") == 12.0
    assert parse_money("") == 0.0


def test_parse_int_maybe():
    assert parse_int_maybe("46") == 46
    assert parse_int_maybe("") is None
    assert parse_int_maybe("70") == 70


def test_weekly_velocity():
    v = weekly_velocity_from_qty_sellout(49, 39.0)
    assert abs(v - 8.794871794871794) < 0.01


def test_row_to_bar_subtypes():
    row = {
        "SKU": "X-1",
        "Product Title": "Test Bar",
        "QTY": "10",
        "Days till Expiration": "100",
        "Sell Out in Days": "50",
        "Retail Price": "$9.00",
        "Net Weight": "80",
        "Vendor-L": "Maker",
        "Product Type": "Chocolate Bars",
        "Cacaonum": "",
        "Chocolate Type": "Dark,Plain",
        "Diet Icons": "Vegan",
        "Source Country": "Peru",
        "Inclusion or Flavor": "",
        "Tags-L": "a,b",
    }
    as_of = date(2026, 1, 1)
    bar = row_to_bar(row, as_of=as_of)
    assert bar["sku"] == "X-1"
    assert bar["cacaonum"] is None
    assert bar["chocolate_type"] == ["Dark", "Plain"]
    assert bar["source_country"] == "Peru"
    assert bar["expiry_date"] == "2026-04-11"
    assert bar["weekly_velocity"] == pytest.approx(10 / (50 / 7.0))


def test_load_real_inventory_csv_matches_json_count():
    base = Path(__file__).resolve().parent.parent
    csv_path = base / "data" / "inbound" / "Bundle_Items_List.csv"
    json_path = base / "data" / "real_inventory.json"
    if not csv_path.exists() or not json_path.exists():
        pytest.skip("fixture data not present")

    import json

    expected_n = len(json.loads(json_path.read_text()))
    bars = load_bundle_items_csv(csv_path, as_of=date(2026, 3, 27))
    assert len(bars) == expected_n
