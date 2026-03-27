"""
Bundle selection engine — real_bundle_rules.json + ShopiCoda inventory rows.

Used by scripts/select_real_bundles.py and the Chainlit agent.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

# ── Loading ──────────────────────────────────────────────────────────────────


def load_bundle_rules(path: Path | str) -> dict[str, Any]:
    with open(path) as f:
        return json.load(f)


# ── Hard constraints ─────────────────────────────────────────────────────────


def passes_hard_constraints(bar: dict, bundle: dict) -> tuple[bool, str]:
    hc = bundle["hard_constraints"]

    if bar.get("product_type") != "Chocolate Bars":
        return False, "not a chocolate bar"

    if bar.get("net_weight_g", 0) < hc.get("min_net_weight_g", 0):
        return False, f"weight {bar.get('net_weight_g')}g < {hc['min_net_weight_g']}g"

    if bar.get("retail_price", 999) > hc.get("max_retail_price", 999):
        return False, f"price ${bar['retail_price']} > ${hc['max_retail_price']}"

    if bar.get("current_inventory", 0) < hc.get("min_inventory", 0):
        return False, f"inventory {bar['current_inventory']} < {hc['min_inventory']}"

    if bar.get("days_till_expiry", 0) < hc.get("min_days_till_expiry", 0):
        return False, f"expires in {bar['days_till_expiry']} days < {hc['min_days_till_expiry']}"

    cacaonum = bar.get("cacaonum")
    if cacaonum is not None:
        if "cacaonum_max" in hc and cacaonum > hc["cacaonum_max"]:
            return False, f"cacaonum {cacaonum} > {hc['cacaonum_max']}"
        if "cacaonum_min" in hc and cacaonum < hc["cacaonum_min"]:
            return False, f"cacaonum {cacaonum} < {hc['cacaonum_min']}"
    elif not hc.get("cacaonum_blank_ok", True):
        return False, "cacaonum blank not allowed"

    bar_types = set(bar.get("chocolate_type", []))

    if "chocolate_type_must_include" in hc:
        allowed = set(hc["chocolate_type_must_include"])
        if not bar_types.intersection(allowed):
            return False, f"chocolate type {bar_types} not in allowed {allowed}"

    if "chocolate_type_all_must_be" in hc:
        required = set(hc["chocolate_type_all_must_be"])
        if "Plain" in required and "Plain" not in bar_types:
            return False, f"must be Plain, got {bar_types}"

    if "chocolate_type_must_be" in hc:
        required_type = hc["chocolate_type_must_be"]
        if required_type not in bar_types:
            return False, f"must have type {required_type}, got {bar_types}"

    if "chocolate_type_subtype" in hc:
        subtype = hc["chocolate_type_subtype"]
        if subtype not in bar_types:
            return False, f"must include chocolate type {subtype}, got {bar_types}"

    if "diet_must_contain" in hc:
        bar_diet = set(bar.get("diet_icons", []))
        required_any = set(hc["diet_must_contain"])
        if not bar_diet.intersection(required_any):
            return False, f"diet {bar_diet} missing any of {required_any}"

    return True, "ok"


def bar_filled_or_praline(bar: dict) -> bool:
    inc = bar.get("inclusion_flavor") or []
    return "Filled" in inc or "Praline" in inc


def inclusion_limits_ok(trial: list, prefs: dict) -> bool:
    limits = prefs.get("inclusion_limits") or {}
    fallback = prefs.get("max_bars_same_inclusion_flavor", 999)
    counts: dict[str, int] = {}

    for b in trial:
        incs = b.get("inclusion_flavor") or []
        if "Filled_or_Praline" in limits and bar_filled_or_praline(b):
            counts["Filled_or_Praline"] = counts.get("Filled_or_Praline", 0) + 1
        for inc in incs:
            if "Filled_or_Praline" in limits and inc in ("Filled", "Praline"):
                continue
            lim = limits.get(inc, fallback)
            counts[inc] = counts.get(inc, 0) + 1
            if counts[inc] > lim:
                return False

    for key, lim in limits.items():
        if counts.get(key, 0) > lim:
            return False
    return True


def preference_max_ok(trial: list, prefs: dict) -> bool:
    if not prefs:
        return True

    vendors = Counter(b.get("vendor", "") for b in trial)
    mv = prefs.get("max_bars_per_vendor", 999)
    if any(c > mv for c in vendors.values()):
        return False

    max_country = prefs.get("max_bars_per_source_country", 999)
    blend_max = prefs.get("source_country_blend_max", 999)
    by_country: dict[str, int] = {}
    blend = 0
    for b in trial:
        co = (b.get("source_country") or "").strip()
        if co == "Blend":
            blend += 1
        else:
            by_country[co] = by_country.get(co, 0) + 1
    if blend > blend_max:
        return False
    if any(c > max_country for c in by_country.values()):
        return False

    cn_counts = Counter()
    for b in trial:
        c = b.get("cacaonum")
        if c is not None:
            cn_counts[c] += 1
    max_same = prefs.get("max_bars_same_cacaonum", 999)
    if any(c > max_same for c in cn_counts.values()):
        return False

    u42 = o79 = o82 = o84 = eq70 = 0
    for b in trial:
        c = b.get("cacaonum")
        if c is None:
            continue
        if c < 42:
            u42 += 1
        if c > 79:
            o79 += 1
        if c > 82:
            o82 += 1
        if c > 84:
            o84 += 1
        if c == 70:
            eq70 += 1
    if u42 > prefs.get("max_bars_cacaonum_under_42", 999):
        return False
    if o79 > prefs.get("max_bars_cacaonum_over_79", 999):
        return False
    if o82 > prefs.get("max_bars_cacaonum_over_82", 999):
        return False
    if o84 > prefs.get("max_bars_cacaonum_over_84", 999):
        return False
    if eq70 > prefs.get("max_bars_cacaonum_70", 999):
        return False

    if not inclusion_limits_ok(trial, prefs):
        return False

    salt_n = sum(1 for b in trial if "Salt" in (b.get("chocolate_type") or []))
    if salt_n > prefs.get("max_bars_chocolate_type_salt", 999):
        return False

    def typeset(b):
        return set(b.get("chocolate_type") or [])

    plain = sum(1 for b in trial if "Plain" in typeset(b))
    white = sum(1 for b in trial if "White" in typeset(b))
    white_plain = sum(
        1 for b in trial if "White" in typeset(b) and "Plain" in typeset(b)
    )
    dark_plain = sum(
        1 for b in trial if "Dark" in typeset(b) and "Plain" in typeset(b)
    )
    milk_dm_plain = sum(
        1
        for b in trial
        if "Plain" in typeset(b)
        and ("Milk" in typeset(b) or "Dark Milk" in typeset(b))
    )
    milk_dm_white = sum(
        1
        for b in trial
        if typeset(b) & {"Milk", "Dark Milk", "White"}
    )

    if plain > prefs.get("plain_bars_max", 999):
        return False
    if white > prefs.get("white_bars_max", 999):
        return False
    if dark_plain > prefs.get("dark_plain_max", 999):
        return False
    if milk_dm_plain > prefs.get("milk_dark_milk_plain_max", 999):
        return False
    if milk_dm_white > prefs.get("milk_dark_milk_white_combined_max", 999):
        return False

    wlim = prefs.get("white_plain_max_if_2_white")
    if wlim is not None and white >= 2 and white_plain > wlim:
        return False

    return True


def preference_mins_ok(selected: list, prefs: dict) -> bool:
    def typeset(b):
        return set(b.get("chocolate_type") or [])

    plain = sum(1 for b in selected if "Plain" in typeset(b))
    white = sum(1 for b in selected if "White" in typeset(b))
    dark_plain = sum(
        1 for b in selected if "Dark" in typeset(b) and "Plain" in typeset(b)
    )
    milk_dm_plain = sum(
        1
        for b in selected
        if "Plain" in typeset(b)
        and ("Milk" in typeset(b) or "Dark Milk" in typeset(b))
    )

    if plain < prefs.get("plain_bars_min", 0):
        return False
    if white < prefs.get("white_bars_min", 0):
        return False
    if dark_plain < prefs.get("dark_plain_min", 0):
        return False
    if milk_dm_plain < prefs.get("milk_dark_milk_plain_min", 0):
        return False
    return True


def select_bundle(bundle: dict, candidates: list) -> dict:
    prefs = bundle.get("preferences", {})
    bar_count = bundle["bar_count"]
    sorted_candidates = sorted(candidates, key=lambda b: b.get("sell_out_days", 9999))

    selected = []
    for bar in sorted_candidates:
        if len(selected) >= bar_count:
            break
        trial = selected + [bar]
        if not preference_max_ok(trial, prefs):
            continue
        selected.append(bar)

    total_value = sum(b["retail_price"] for b in selected)
    hc = bundle["hard_constraints"]
    value_ok = hc["min_box_retail_value"] <= total_value <= hc["max_box_retail_value"]
    mins_ok = preference_mins_ok(selected, prefs)
    full_count_ok = len(selected) >= bar_count

    return {
        "bundle_id": bundle["bundle_id"],
        "bundle_name": bundle["name"],
        "box_sku": bundle["box_sku"],
        "box_name": bundle.get("box_name", ""),
        "bars_selected": len(selected),
        "bars_needed": bar_count,
        "total_retail_value": round(total_value, 2),
        "value_in_range": value_ok,
        "preferences_satisfied": mins_ok,
        "selection_ok": full_count_ok and value_ok and mins_ok,
        "selected_bars": [
            {
                "sku": b["sku"],
                "name": b["name"],
                "vendor": b["vendor"],
                "source_country": b["source_country"],
                "chocolate_type": b["chocolate_type"],
                "cacaonum": b["cacaonum"],
                "retail_price": b["retail_price"],
                "net_weight_g": b["net_weight_g"],
                "current_inventory": b["current_inventory"],
                "days_till_expiry": b["days_till_expiry"],
                "sell_out_days": b["sell_out_days"],
                "inclusion_flavor": b["inclusion_flavor"],
            }
            for b in selected
        ],
    }


def get_bundle_by_id(rules: dict, bundle_id: str) -> dict | None:
    for b in rules.get("bundles") or []:
        if b.get("bundle_id") == bundle_id:
            return b
    return None


def run_one_bundle(
    inventory_raw: list[dict],
    bundle: dict,
) -> tuple[dict, list[tuple[str, str]], int]:
    """Returns (selection result, rejection samples, candidate count)."""
    candidates = []
    rejected: list[tuple[str, str]] = []
    for bar in inventory_raw:
        ok, reason = passes_hard_constraints(bar, bundle)
        if ok:
            candidates.append(bar)
        else:
            rejected.append((bar["sku"], reason))
    result = select_bundle(bundle, candidates)
    return result, rejected, len(candidates)


def _intensity_from_cacao(cacao: int | None) -> str:
    if cacao is None or cacao == 0:
        return "mild"
    if cacao >= 88:
        return "extra-bold"
    if cacao >= 80:
        return "bold"
    if cacao >= 55:
        return "medium"
    return "mild"


def normalize_bundle_selection_for_agent(
    result: dict,
    inventory_by_sku: dict[str, dict],
    bundle: dict,
) -> dict:
    """Shape compatible with explain_bar / format_review-style consumers."""
    reason = (
        "Passed this bundle's hard filters; chosen by greedy priority on lowest sell-out days "
        "within soft caps (vendor, origin, inclusions, etc.)."
    )
    selected = []
    for row in result["selected_bars"]:
        raw = inventory_by_sku.get(row["sku"], {})
        types = row.get("chocolate_type") or []
        cacao = row.get("cacaonum")
        ctype = str(types[0]).lower() if types else "dark"
        inv = int(row.get("current_inventory", 0))
        vel = float(raw.get("weekly_velocity", 0) or 0)
        dos = (inv / vel) * 7 if vel > 0 else None
        selected.append(
            {
                **row,
                "id": row["sku"],
                "maker": row["vendor"],
                "origin": row["source_country"],
                "type": ctype,
                "cacao_pct": int(cacao) if cacao is not None else 0,
                "flavor_tags": list(row.get("inclusion_flavor") or []) or [str(t) for t in types],
                "intensity": _intensity_from_cacao(cacao),
                "price_usd": float(row["retail_price"]),
                "expiry_date": raw.get("expiry_date", ""),
                "weekly_velocity": vel,
                "dietary_flags": list(raw.get("diet_icons") or []),
                "_days_until_expiry": row.get("days_till_expiry", 0),
                "_days_of_supply": round(dos, 1) if dos is not None else None,
                "_candidate_score": 0.0,
                "selection_reason": reason,
            }
        )

    lo = bundle["hard_constraints"].get("min_box_retail_value", 0)
    hi = bundle["hard_constraints"].get("max_box_retail_value", 9999)
    violations = []
    if not result.get("selection_ok"):
        if result["bars_selected"] < result["bars_needed"]:
            violations.append(
                f"Incomplete box: {result['bars_selected']}/{result['bars_needed']} bars filled"
            )
        if not result.get("value_in_range"):
            violations.append(
                f"Retail total ${result['total_retail_value']:.2f} outside ${lo}–${hi} target band"
            )
        if not result.get("preferences_satisfied"):
            violations.append("Soft preference minimums (e.g. plain/white counts) not met")

    return {
        "selected_bars": selected,
        "box_summary": (
            f"{result['bundle_name']} ({result['bundle_id']}) — "
            f"{result['bars_selected']} bars, ${result['total_retail_value']:.2f} retail "
            f"(target ${lo}–${hi})."
        ),
        "metadata": {
            "total_price_usd": result["total_retail_value"],
            "distinct_origins": sorted(
                {b["origin"] for b in selected if b.get("origin")}
            ),
            "types_included": sorted(
                {t for b in selected for t in (b.get("chocolate_type") or [])}
            ),
            "intensities_included": [],
            "constraint_violations": violations,
            "valid": len(violations) == 0,
            "bundle_id": result["bundle_id"],
            "box_sku": result["box_sku"],
            "source": "real_bundle_rules",
        },
    }
