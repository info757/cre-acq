"""
CLI wrapper — run bundle selection against data/real_inventory.json.

Logic lives in src/bundle_select.py (shared with the Chainlit agent).

Usage: python scripts/select_real_bundles.py [bundle_id]
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

from bundle_select import load_bundle_rules, passes_hard_constraints, select_bundle  # noqa: E402

BASE = Path(__file__).parent.parent
INV_PATH = BASE / "data" / "real_inventory.json"
RULES_PATH = BASE / "rules" / "real_bundle_rules.json"


def load_data():
    with open(INV_PATH) as f:
        inventory = json.load(f)
    rules = load_bundle_rules(RULES_PATH)
    return inventory, rules


def run(bundle_id_filter=None):
    inventory, rules = load_data()

    for bundle in rules["bundles"]:
        if bundle_id_filter and bundle["bundle_id"] != bundle_id_filter:
            continue

        print(f"\n{'='*60}")
        print(f"Bundle: {bundle['bundle_id']} — {bundle['name']}")
        print(f"Box: {bundle['box_name']} ({bundle['box_sku']})")
        print(f"{'='*60}")

        candidates = []
        rejected = []
        for bar in inventory:
            ok, reason = passes_hard_constraints(bar, bundle)
            if ok:
                candidates.append(bar)
            else:
                rejected.append((bar["sku"], reason))

        print(f"Candidates passing hard constraints: {len(candidates)} / {len(inventory)}")

        if len(candidates) < bundle["bar_count"]:
            print(f"⚠️  Only {len(candidates)} candidates, need {bundle['bar_count']} bars")
            if len(candidates) < 5:
                print("Sample rejections:")
                for sku, reason in rejected[:10]:
                    print(f"  {sku}: {reason}")

        result = select_bundle(bundle, candidates)

        print(f"\nSelected {result['bars_selected']}/{result['bars_needed']} bars")
        print(
            f"Total retail value: ${result['total_retail_value']:.2f} | "
            f"In range: {'✅' if result['value_in_range'] else '❌'} | "
            f"Prefs min: {'✅' if result.get('preferences_satisfied', True) else '❌'} | "
            f"Overall: {'✅' if result.get('selection_ok') else '❌'}"
        )
        print("\nSelected bars:")
        for i, bar in enumerate(result["selected_bars"], 1):
            inc = ", ".join(bar["inclusion_flavor"]) if bar["inclusion_flavor"] else "—"
            print(f"  {i:2}. [{bar['sku']}] {bar['name'][:45]}")
            print(
                f"      ${bar['retail_price']} | {bar['cacaonum']}% | "
                f"{', '.join(bar['chocolate_type'])} | {bar['source_country']} | {bar['vendor']}"
            )
            print(
                f"      Inv: {bar['current_inventory']} | Expires: {bar['days_till_expiry']}d | "
                f"Sellout: {bar['sell_out_days']}d | Inc: {inc}"
            )


if __name__ == "__main__":
    bundle_filter = sys.argv[1] if len(sys.argv) > 1 else None
    run(bundle_filter)
