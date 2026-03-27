"""
Import ShopiCoda / bundle-items CSV into real_inventory.json schema.

Expected columns (exact header row names):
  SKU, Product Title, QTY, Expiring QTY, Days till Expiration, Sell Out in Days,
  Unit Cost, Retail Price, Net Weight, Unit Gross Weight (g), Vendor-L, Farm Level,
  Product Type, Cacaonum, Allergens, Awards, Chocolate Type, Diet Icons,
  Exceeds Sellout, Source Country, Inclusion or Flavor, Tags-L

By default only rows with Product Type \"Chocolate Bars\" are imported (bundle SKU set).
Pass product_type_filter=None to keep all rows.
"""

from __future__ import annotations

import csv
import json
import re
from datetime import date, timedelta
from pathlib import Path
from typing import Any

MIN_HEADERS = frozenset(
    {
        "SKU",
        "Product Title",
        "QTY",
        "Days till Expiration",
        "Sell Out in Days",
        "Retail Price",
        "Net Weight",
        "Vendor-L",
        "Product Type",
        "Chocolate Type",
        "Diet Icons",
        "Source Country",
        "Inclusion or Flavor",
        "Tags-L",
    }
)


def parse_money(raw: str) -> float:
    s = (raw or "").strip()
    if not s:
        return 0.0
    s = s.replace("$", "").replace(",", "")
    return float(s)


def parse_int_maybe(raw: str) -> int | None:
    s = (raw or "").strip()
    if not s:
        return None
    try:
        return int(float(s))
    except ValueError:
        return None


def parse_float_maybe(raw: str) -> float | None:
    s = (raw or "").strip()
    if not s:
        return None
    try:
        return float(s)
    except ValueError:
        return None


def split_list(raw: str) -> list[str]:
    if not raw or not str(raw).strip():
        return []
    parts = re.split(r"\s*,\s*", str(raw).strip())
    return [p.strip() for p in parts if p.strip()]


def weekly_velocity_from_qty_sellout(qty: int, sell_out_days: float) -> float:
    if sell_out_days and sell_out_days > 0:
        return qty / (sell_out_days / 7.0)
    return 0.0


def row_to_bar(row: dict[str, str], *, as_of: date) -> dict[str, Any]:
    sku = row["SKU"].strip()
    title = row["Product Title"].strip()
    qty = int(parse_float_maybe(row.get("QTY", "0")) or 0)
    days_till = int(parse_float_maybe(row.get("Days till Expiration", "0")) or 0)
    sell_raw = parse_float_maybe(row.get("Sell Out in Days", ""))
    sell_out_days = float(sell_raw) if sell_raw is not None else 9999.0

    net_w = int(parse_float_maybe(row.get("Net Weight", "0")) or 0)
    cacaonum = parse_int_maybe(row.get("Cacaonum", ""))

    choc = split_list(row.get("Chocolate Type", ""))
    diet = split_list(row.get("Diet Icons", ""))
    inc_raw = split_list(row.get("Inclusion or Flavor", ""))
    tags = split_list(row.get("Tags-L", ""))

    expiry = (as_of + timedelta(days=days_till)).isoformat()

    return {
        "sku": sku,
        "name": title,
        "vendor": (row.get("Vendor-L") or "").strip(),
        "source_country": (row.get("Source Country") or "").strip(),
        "product_type": (row.get("Product Type") or "").strip(),
        "chocolate_type": choc,
        "cacaonum": cacaonum,
        "net_weight_g": net_w,
        "retail_price": round(parse_money(row.get("Retail Price", "")), 4),
        "diet_icons": diet,
        "inclusion_flavor": inc_raw,
        "current_inventory": qty,
        "days_till_expiry": days_till,
        "expiry_date": expiry,
        "sell_out_days": sell_out_days,
        "weekly_velocity": round(weekly_velocity_from_qty_sellout(qty, sell_out_days), 6),
        "tags": tags,
    }


def normalize_header(h: str) -> str:
    return (h or "").strip().lstrip("\ufeff")


def load_bundle_items_csv(
    path: Path | str,
    *,
    as_of: date | None = None,
    product_type_filter: str | None = "Chocolate Bars",
) -> list[dict[str, Any]]:
    path = Path(path)
    as_of = as_of or date.today()

    with path.open(newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        if not reader.fieldnames:
            raise ValueError(f"No header row in {path}")

        fields = [normalize_header(h) for h in reader.fieldnames]

        missing = sorted(MIN_HEADERS.difference(fields))
        if missing:
            raise ValueError(
                f"{path}: missing columns {missing}. Found: {sorted(fields)}"
            )

        out: list[dict[str, Any]] = []
        for raw in reader:
            row = {
                normalize_header(k): (v if v is not None else "")
                for k, v in raw.items()
            }
            if not row.get("SKU", "").strip():
                continue
            ptype = (row.get("Product Type") or "").strip()
            if product_type_filter and ptype != product_type_filter:
                continue
            out.append(row_to_bar(row, as_of=as_of))
        return out


def write_real_inventory_json(
    bars: list[dict[str, Any]],
    out_path: Path | str,
) -> None:
    out_path = Path(out_path)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(bars, f, indent=2, ensure_ascii=False)
        f.write("\n")


def main(argv: list[str] | None = None) -> None:
    import sys

    argv = argv if argv is not None else sys.argv[1:]
    base = Path(__file__).resolve().parent.parent
    default_in = base / "data" / "inbound" / "Bundle_Items_List.csv"
    if not default_in.exists():
        default_in = base / "data" / "bundle_items_list.csv"
    default_out = base / "data" / "real_inventory.json"

    in_path = Path(argv[0]) if argv else default_in
    out_path = Path(argv[1]) if len(argv) > 1 else default_out

    if not in_path.exists():
        print(
            f"Input not found: {in_path}\n"
            f"Copy your export to this path or pass: "
            f"python scripts/import_bundle_items_csv.py <input.csv> [output.json]",
            file=sys.stderr,
        )
        sys.exit(1)

    bars = load_bundle_items_csv(in_path)
    write_real_inventory_json(bars, out_path)
    print(f"Wrote {len(bars)} bars → {out_path}")
