"""
Stage 2: LLM Selection Engine
Bar & Cocoa POC — Triad AI

Takes scored candidate list from score.py, applies hard constraints,
and uses Claude to select the final 10-bar gift box with reasoning.
"""

import json
import os
import sys
from pathlib import Path

import anthropic

# Add src to path for local import
sys.path.insert(0, str(Path(__file__).parent))
from score import load_app_inventory, score_inventory

# Legacy LLM box builder — agent now uses bundle_select + real_bundle_rules.json.

MODEL = "claude-sonnet-4-6"
BOX_SIZE = 10


SYSTEM_PROMPT = """You are an expert chocolate buyer and gift curator working for Bar & Cocoa, 
a specialty chocolate retailer. Your job is to select exactly 10 bars for a curated gift box.

You have two goals that must both be achieved:
1. INVENTORY MANAGEMENT: Move bars that need to be sold before they expire. Prioritize bars 
   with high expiry urgency scores that are slow-moving.
2. CURATION QUALITY: The box must be genuinely excellent — diverse origins, a range of 
   intensities from mild to bold, interesting flavor stories, and a price point that feels 
   premium but fair.

You must ALWAYS respect the hard constraints. They are non-negotiable."""


def build_selection_prompt(candidates: list, rules: dict) -> str:
    hc = rules["hard_constraints"]
    box_ceiling = rules["box_price_ceiling_usd"]

    candidate_data = []
    for b in candidates:
        candidate_data.append({
            "id": b["id"],
            "name": b["name"],
            "maker": b["maker"],
            "origin": b["origin"],
            "type": b["type"],
            "cacao_pct": b["cacao_pct"],
            "flavor_tags": b["flavor_tags"],
            "intensity": b["intensity"],
            "price_usd": b["price_usd"],
            "dietary_flags": b["dietary_flags"],
            "candidate_score": b["_candidate_score"],
            "days_until_expiry": b["_days_until_expiry"],
            "days_of_supply": b["_days_of_supply"],
            "expiry_risk_score": b["_expiry_risk_score"],
            "weekly_velocity": b["weekly_velocity"],
            "reorder_frequency_per_year": b["reorder_frequency_per_year"],
        })

    prompt = f"""Here are the {len(candidates)} bars eligible for the gift box (pre-screened: 
fast movers and hard-to-restock buffer stock have already been excluded).

CANDIDATE BARS:
{json.dumps(candidate_data, indent=2)}

HARD CONSTRAINTS (non-negotiable — violating any of these is a failure):
- Select exactly {BOX_SIZE} bars
- Maximum {hc['max_bars_per_maker']} bars from the same maker
- Maximum {hc['max_bars_per_origin']} bars from the same origin country  
- Minimum {hc['min_dark_chocolate_bars']} dark chocolate bars (type starts with "dark")
- Minimum {hc['min_distinct_origins']} distinct origins in the box
- Total box price must not exceed ${box_ceiling} USD

SOFT PREFERENCES (optimize for these within the hard constraints):
- Prefer bars with higher candidate_score (higher expiry urgency, harder to sell)
- Include a range of intensities: mild, medium, bold
- Include variety across types: dark, milk, white, inclusions
- Aim for interesting and complementary flavor combinations
- Prefer flavor diversity (avoid too many similar flavor profiles)

Respond with a JSON object in this exact format:
{{
  "selected_bars": [
    {{
      "id": "bar-xxx",
      "reason": "1-2 sentence explanation of why this bar was chosen (both inventory and curation rationale)"
    }},
    ...10 entries total...
  ],
  "box_summary": "2-3 sentence description of the box as a whole — what makes it a great selection"
}}

Think carefully before responding. Check that all hard constraints are satisfied."""

    return prompt


def enforce_hard_constraints(selected_ids: list, all_bars_by_id: dict,
                              candidates_ranked: list, rules: dict) -> list:
    """
    Deterministically enforce hard constraints by swapping out violating bars.
    Returns a valid list of 10 bar IDs, or the best we can achieve.
    candidates_ranked: full candidate list sorted by score desc (fallback pool).
    """
    from collections import Counter

    hc = rules["hard_constraints"]
    max_per_maker = hc["max_bars_per_maker"]
    max_per_origin = hc["max_bars_per_origin"]
    box_ceiling = rules["box_price_ceiling_usd"]

    selected = list(selected_ids)
    selected_set = set(selected)

    # Build fallback pool: candidates not already selected, sorted by score desc
    fallback = [b["id"] for b in candidates_ranked if b["id"] not in selected_set]

    def swap_out(bad_id: str) -> bool:
        """Replace bad_id with the best fallback that doesn't introduce new violations."""
        nonlocal selected, selected_set, fallback

        # Temporarily remove bad_id
        temp = [x for x in selected if x != bad_id]
        temp_bars = [all_bars_by_id[x] for x in temp]

        for candidate_id in fallback:
            candidate = all_bars_by_id.get(candidate_id)
            if not candidate:
                continue
            trial = temp + [candidate_id]
            trial_bars = temp_bars + [candidate]
            maker_counts = Counter(b["maker"] for b in trial_bars)
            origin_counts = Counter(b["origin"] for b in trial_bars)
            total_price = sum(b["price_usd"] for b in trial_bars)
            if (
                all(c <= max_per_maker for c in maker_counts.values())
                and all(c <= max_per_origin for c in origin_counts.values())
                and total_price <= box_ceiling
            ):
                selected = trial
                selected_set = set(selected)
                fallback = [x for x in fallback if x != candidate_id]
                return True
        return False  # no valid swap found

    # Enforce max_per_maker
    for _ in range(10):
        maker_counts = Counter(all_bars_by_id[x]["maker"] for x in selected if x in all_bars_by_id)
        over = [m for m, c in maker_counts.items() if c > max_per_maker]
        if not over:
            break
        maker = over[0]
        # Find lowest-score bar from this maker to swap out
        maker_bars = sorted(
            [x for x in selected if all_bars_by_id.get(x, {}).get("maker") == maker],
            key=lambda x: all_bars_by_id[x].get("_candidate_score", 0)
        )
        swap_out(maker_bars[0])

    # Enforce max_per_origin
    for _ in range(10):
        origin_counts = Counter(all_bars_by_id[x]["origin"] for x in selected if x in all_bars_by_id)
        over = [o for o, c in origin_counts.items() if c > max_per_origin]
        if not over:
            break
        origin = over[0]
        origin_bars = sorted(
            [x for x in selected if all_bars_by_id.get(x, {}).get("origin") == origin],
            key=lambda x: all_bars_by_id[x].get("_candidate_score", 0)
        )
        swap_out(origin_bars[0])

    return selected


def validate_selection(selected_ids: list, all_bars_by_id: dict, rules: dict) -> list[str]:
    """Returns a list of constraint violations. Empty list = valid."""
    violations = []
    hc = rules["hard_constraints"]
    box_ceiling = rules["box_price_ceiling_usd"]

    if len(selected_ids) != BOX_SIZE:
        violations.append(f"Wrong box size: got {len(selected_ids)}, expected {BOX_SIZE}")

    bars = [all_bars_by_id[id_] for id_ in selected_ids if id_ in all_bars_by_id]
    missing = [id_ for id_ in selected_ids if id_ not in all_bars_by_id]
    if missing:
        violations.append(f"Unknown bar IDs: {missing}")

    # Maker constraint
    from collections import Counter
    maker_counts = Counter(b["maker"] for b in bars)
    for maker, count in maker_counts.items():
        if count > hc["max_bars_per_maker"]:
            violations.append(f"Too many bars from maker '{maker}': {count} > {hc['max_bars_per_maker']}")

    # Origin constraint
    origin_counts = Counter(b["origin"] for b in bars)
    for origin, count in origin_counts.items():
        if count > hc["max_bars_per_origin"]:
            violations.append(f"Too many bars from origin '{origin}': {count} > {hc['max_bars_per_origin']}")

    # Min dark chocolate
    dark_count = sum(1 for b in bars if b["type"].startswith("dark"))
    if dark_count < hc["min_dark_chocolate_bars"]:
        violations.append(f"Not enough dark chocolate: {dark_count} < {hc['min_dark_chocolate_bars']}")

    # Min distinct origins
    distinct_origins = len(set(b["origin"] for b in bars))
    if distinct_origins < hc["min_distinct_origins"]:
        violations.append(f"Not enough distinct origins: {distinct_origins} < {hc['min_distinct_origins']}")

    # Price ceiling
    total_price = sum(b["price_usd"] for b in bars)
    if total_price > box_ceiling:
        violations.append(f"Box price ${total_price:.2f} exceeds ceiling ${box_ceiling}")

    return violations


def select_bars(candidates: list, all_bars: list, rules: dict, max_retries: int = 3) -> dict:
    """
    Main selection function. Calls Claude to select 10 bars, validates hard constraints.
    Retries with explicit violation feedback if constraints are not met.
    Returns: {selected_bars: [...], box_summary: str, metadata: {...}}
    """
    client = anthropic.Anthropic()

    all_bars_by_id = {b["id"]: b for b in all_bars}
    messages = [{"role": "user", "content": build_selection_prompt(candidates, rules)}]

    print(f"Calling Claude ({MODEL}) for bar selection...")
    response = client.messages.create(
        model=MODEL,
        max_tokens=16384,
        system=SYSTEM_PROMPT,
        messages=messages,
    )

    # Handle extended thinking: find the text block (skip thinking blocks)
    raw_text = ""
    for block in response.content:
        if getattr(block, "type", None) == "text":
            raw_text = block.text.strip()
            break
    if not raw_text:
        raw_text = response.content[0].text.strip()

    # Robustly extract first valid JSON object from response
    start = raw_text.find('{')
    if start == -1:
        raise ValueError(f"No JSON object found in response: {raw_text[:200]}")
    decoder = json.JSONDecoder()
    result, _ = decoder.raw_decode(raw_text, start)

    selected_ids = [item["id"] for item in result["selected_bars"]]
    violations = validate_selection(selected_ids, all_bars_by_id, rules)

    if violations:
        print(f"⚠️  LLM selection had violations: {violations}")
        print("Applying deterministic constraint enforcer...")
        fixed_ids = enforce_hard_constraints(selected_ids, all_bars_by_id, candidates, rules)
        # Rebuild result with fixed ids, preserving reasons where possible
        reasons_by_id = {item["id"]: item["reason"] for item in result["selected_bars"]}
        result["selected_bars"] = [
            {"id": id_, "reason": reasons_by_id.get(id_, "Selected as constraint-compliant replacement.")}
            for id_ in fixed_ids
        ]
        selected_ids = fixed_ids
        violations = validate_selection(selected_ids, all_bars_by_id, rules)
        if not violations:
            print("✅ Enforcer resolved all violations.")
        else:
            print(f"❌ Could not fully resolve violations: {violations}")
    else:
        print("✅ All constraints satisfied.")

    # Enrich selected bars with full bar data
    enriched = []
    for item in result["selected_bars"]:
        bar_data = all_bars_by_id.get(item["id"], {})
        enriched.append({**bar_data, "selection_reason": item["reason"]})

    total_price = sum(b.get("price_usd", 0) for b in enriched)
    origins = list({b.get("origin") for b in enriched})
    types = list({b.get("type") for b in enriched})
    intensities = list({b.get("intensity") for b in enriched})

    return {
        "selected_bars": enriched,
        "box_summary": result.get("box_summary", ""),
        "metadata": {
            "total_price_usd": round(total_price, 2),
            "distinct_origins": origins,
            "types_included": types,
            "intensities_included": intensities,
            "constraint_violations": violations,
            "valid": len(violations) == 0,
        },
    }


def load_rules(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


if __name__ == "__main__":
    import datetime

    today = datetime.date.today()
    base = Path(__file__).parent.parent
    inventory = load_app_inventory(base / "data" / "real_inventory.json")
    scored = score_inventory(inventory, today=today)
    candidates = [b for b in scored if b["_candidate_eligible"]]
    print(
        "Legacy LLM + selection_rules path removed — use bundle rules.\n"
        "  CLI: python scripts/select_real_bundles.py\n"
        "  Agent: chainlit run app.py\n\n"
        f"Scoring smoke: {len(inventory)} bars, {len(candidates)} scoring-eligible."
    )
