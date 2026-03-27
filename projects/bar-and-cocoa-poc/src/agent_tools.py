"""
agent_tools.py — Tool functions for the Bar & Cocoa agent.

Each function is a pure callable that the LangGraph nodes invoke.
No LangGraph imports here — keeps tools testable in isolation.
"""

import json
import os
import sys
from pathlib import Path
from typing import Optional

import anthropic

# Local imports
_src = Path(__file__).parent
sys.path.insert(0, str(_src))
from score import score_inventory, load_app_inventory, load_inventory
from bundle_select import (
    get_bundle_by_id,
    load_bundle_rules,
    normalize_bundle_selection_for_agent,
    run_one_bundle,
)
from format_review import format_review

BOX_SIZE = 10  # legacy prompts; bundle recipes define bar_count

BASE = _src.parent
MODEL_FAST = "claude-haiku-4-5-20251001"   # routing + simple Q&A
MODEL_HEAVY = "claude-sonnet-4-6"           # explanations + rule parsing


def _client() -> anthropic.Anthropic:
    return anthropic.Anthropic()


# ── Core selection pipeline (bundle rules + real inventory rows) ─────────────

def run_bundle_selection_pipeline(
    inventory_raw: list,
    rules: dict,
    bundle_id: str,
) -> dict:
    """
    Deterministic 10-bar (or recipe bar_count) selection from real_bundle_rules.json.
    Returns {result, review_md, num_candidates, num_total, bundle}.
    """
    bundle = get_bundle_by_id(rules, bundle_id)
    if not bundle:
        bundle = rules["bundles"][0]
        bundle_id = bundle["bundle_id"]

    result_raw, _, num_candidates = run_one_bundle(inventory_raw, bundle)
    by_sku = {b["sku"]: b for b in inventory_raw}
    result = normalize_bundle_selection_for_agent(result_raw, by_sku, bundle)
    review_md = format_review(result)
    return {
        "result": result,
        "review_md": review_md,
        "num_candidates": num_candidates,
        "num_total": len(inventory_raw),
        "bundle": bundle,
        "bundle_pick": result_raw,
    }


# ── Inventory queries ─────────────────────────────────────────────────────────

def query_inventory(inventory: list, rules: dict, user_query: str,
                    last_selection: Optional[dict] = None) -> str:
    """
    Answer a natural-language inventory question.
    Uses scored inventory for accuracy.
    """
    import datetime
    scored = score_inventory(inventory, today=datetime.date.today())

    # Build compact context for the model
    summary_rows = []
    for b in scored:
        summary_rows.append({
            "id": b["id"],
            "name": b["name"],
            "maker": b["maker"],
            "origin": b["origin"],
            "type": b["type"],
            "cacao_pct": b["cacao_pct"],
            "intensity": b["intensity"],
            "price_usd": b["price_usd"],
            "weekly_velocity": b["weekly_velocity"],
            "current_inventory": b["current_inventory"],
            "expiry_date": b["expiry_date"],
            "days_until_expiry": b["_days_until_expiry"],
            "days_of_supply": b["_days_of_supply"],
            "candidate_score": b["_candidate_score"],
            "candidate_eligible": b["_candidate_eligible"],
            "is_fast_mover": b["_is_fast_mover"],
            "is_buffer_stock": b["_is_buffer_stock"],
            "dietary_flags": b["dietary_flags"],
            "reorder_frequency_per_year": b["reorder_frequency_per_year"],
        })

    selection_context = ""
    if last_selection:
        selected_names = [b["name"] for b in last_selection.get("selected_bars", [])]
        meta = last_selection.get("metadata") or {}
        bid = meta.get("bundle_id", "")
        selection_context = f"\nLAST SELECTION (bundle {bid}): {', '.join(selected_names)}"

    bundle_rules_note = (
        "Box building uses recipes in rules/real_bundle_rules.json (bundle IDs, hard constraints, "
        "retail value bands). Scoring below is for Q&A only."
    )
    recipe_index = [
        {"bundle_id": b.get("bundle_id"), "name": b.get("name")}
        for b in rules.get("bundles", [])
    ]

    prompt = f"""You are the inventory intelligence layer for Bar & Cocoa, a specialty chocolate retailer.
Answer the following question about the inventory concisely and accurately.

INVENTORY ({len(summary_rows)} bars):
{json.dumps(summary_rows, indent=2)}

{bundle_rules_note}
(Recipe catalog summary — bundle_id + name only:)
{json.dumps(recipe_index, indent=2)}
{selection_context}

QUESTION: {user_query}

Answer directly and specifically. Use numbers and bar names. Keep it under 250 words."""

    response = _client().messages.create(
        model=MODEL_FAST,
        max_tokens=500,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


# ── Bar explanation ───────────────────────────────────────────────────────────

def explain_bar(user_query: str, inventory: list, rules: dict,
                last_selection: Optional[dict] = None) -> str:
    """
    Explain why a bar was selected, excluded, or describe it in detail.
    """
    import datetime
    scored = score_inventory(inventory, today=datetime.date.today())
    scored_by_id = {b["id"]: b for b in scored}
    scored_by_name_lower = {b["name"].lower(): b for b in scored}

    # Try to find the referenced bar
    query_lower = user_query.lower()
    matched_bar = None
    for b in scored:
        if b["name"].lower() in query_lower or b["id"] in query_lower:
            matched_bar = b
            break

    selection_context = ""
    if last_selection:
        selected_ids = {b["id"] for b in last_selection.get("selected_bars", [])}
        selection_reasons = {
            b["id"]: b.get("selection_reason", "")
            for b in last_selection.get("selected_bars", [])
        }
        if matched_bar:
            is_selected = matched_bar["id"] in selected_ids
            reason = selection_reasons.get(matched_bar["id"], "")
            selection_context = f"\nThis bar IS {'selected' if is_selected else 'NOT selected'} in the current box.{' Reason: ' + reason if reason else ''}"
        else:
            selected_names = [b["name"] for b in last_selection.get("selected_bars", [])]
            selection_context = f"\nCurrently selected bars: {', '.join(selected_names)}"

    bar_data_str = ""
    if matched_bar:
        bar_data_str = f"\nBAR IN QUESTION:\n{json.dumps(matched_bar, indent=2)}"
    else:
        # Provide top-20 bars by score so the model can reason
        top = sorted(scored, key=lambda x: -x["_candidate_score"])[:20]
        bar_data_str = f"\nTOP CANDIDATES BY SCORE:\n{json.dumps(top, indent=2)}"

    recipe_index = [
        {"bundle_id": b.get("bundle_id"), "name": b.get("name")}
        for b in rules.get("bundles", [])
    ]

    prompt = f"""You are the expert curator and inventory manager for Bar & Cocoa.
Answer the following question about a specific bar or selection decision.

{bar_data_str}

BUNDLE RECIPES (real_bundle_rules.json):
{json.dumps(recipe_index, indent=2)}
{selection_context}

QUESTION: {user_query}

Be specific about inventory metrics (days till expiry, velocity, stock). Note: the live box uses bundle recipe constraints, not legacy gift-box rules. Keep it under 300 words."""

    response = _client().messages.create(
        model=MODEL_HEAVY,
        max_tokens=600,
        messages=[{"role": "user", "content": prompt}],
    )
    return response.content[0].text.strip()


# ── Bundle recipe focus (which real_bundle_rules bundle to run) ─────────────

def parse_bundle_focus(user_query: str, rules: dict, active_bundle_id: str) -> dict:
    """
    Parse which bundle recipe the user wants. Constraint edits belong in real_bundle_rules.json.
    Returns { "active_bundle_id", "changes", "summary" } for compatibility with adjust_rules_node.
    """
    catalog = [
        {"bundle_id": b["bundle_id"], "name": b["name"], "box_name": b.get("box_name", "")}
        for b in (rules.get("bundles") or [])
    ]
    valid_ids = {b["bundle_id"] for b in catalog}

    prompt = f"""The user may want to switch which gift-box RECIPE to build (bundle rules).

ACTIVE BUNDLE NOW: {active_bundle_id}

AVAILABLE RECIPES:
{json.dumps(catalog, indent=2)}

USER MESSAGE: {user_query}

Decide if they are selecting a different recipe (by id, box name, or obvious nickname).
Return ONLY valid JSON:
{{
  "bundle_id": "<exact bundle_id from list>" | null,
  "summary": "short explanation"
}}

If they are asking to change numeric constraints/thresholds inside a recipe, set bundle_id to null and explain in summary that recipe constraints are edited in the rules file by the team — they should name which box recipe to use instead."""

    response = _client().messages.create(
        model=MODEL_FAST,
        max_tokens=300,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text.strip()
    start = raw.find("{")
    if start == -1:
        return {
            "active_bundle_id": active_bundle_id,
            "changes": [],
            "summary": "Could not parse. Name a bundle id (e.g. ST-BAR-401-3) or describe the box recipe.",
        }

    import json as _json
    decoder = _json.JSONDecoder()
    try:
        parsed, _ = decoder.raw_decode(raw, start)
    except Exception:
        return {
            "active_bundle_id": active_bundle_id,
            "changes": [],
            "summary": "Parse error. Try: 'use bundle ST-BAR-404-3'.",
        }

    new_id = parsed.get("bundle_id")
    summary = parsed.get("summary", "")
    if isinstance(new_id, str) and new_id in valid_ids:
        return {
            "active_bundle_id": new_id,
            "changes": [
                {
                    "path": "active_bundle_id",
                    "old_value": active_bundle_id,
                    "new_value": new_id,
                    "description": f"Active recipe → {new_id}",
                }
            ],
            "summary": summary or f"Switched to {new_id}",
        }

    return {
        "active_bundle_id": active_bundle_id,
        "changes": [],
        "summary": summary or "No recipe change. Edit real_bundle_rules.json for constraint updates, or name a bundle id.",
    }




# ── General response ──────────────────────────────────────────────────────────

def general_response(user_query: str, inventory: list, rules: dict,
                     last_selection: Optional[dict], conversation_history: list) -> str:
    """
    Handle general questions, greetings, or off-topic messages.
    """
    import datetime
    scored = score_inventory(inventory, today=datetime.date.today())
    candidates = [b for b in scored if b["_candidate_eligible"]]

    context = f"""You are Pashmina's AI assistant for Bar & Cocoa, a specialty chocolate retailer.
You help curate monthly gift boxes by balancing inventory management with chocolate curation quality.

SYSTEM STATUS:
- Total inventory: {len(inventory)} bars
- Eligible candidates: {len(candidates)} bars
- Fast movers (excluded): {sum(1 for b in scored if b["_is_fast_mover"])} bars
- Buffer stock (excluded): {sum(1 for b in scored if b["_is_buffer_stock"])} bars
- Box size: {BOX_SIZE} bars
- Today: {datetime.date.today().isoformat()}

{"Selection has been run. " + str(len(last_selection.get("selected_bars", []))) + " bars selected." if last_selection else "No selection run yet."}

Answer helpfully and concisely. If asked to select a box, explain you can do that — they should ask you to "select" or "run the box"."""

    messages = []
    # Add recent conversation for context (last 4 messages)
    for msg in conversation_history[-4:]:
        if hasattr(msg, 'type'):
            role = "assistant" if msg.type == "ai" else "user"
        else:
            role = "user"
        messages.append({"role": role, "content": str(msg.content)})

    messages.append({"role": "user", "content": user_query})

    response = _client().messages.create(
        model=MODEL_FAST,
        max_tokens=400,
        system=context,
        messages=messages,
    )
    return response.content[0].text.strip()


# ── Intent classification ─────────────────────────────────────────────────────

def classify_intent(user_message: str, last_selection_exists: bool) -> str:
    """
    Classify user intent. Returns one of:
    select | adjust | explain | query | general
    """
    prompt = f"""Classify the user's intent for a chocolate inventory management system.

USER MESSAGE: "{user_message}"

Context: {"A box selection has already been run." if last_selection_exists else "No selection has been run yet."}

Intent categories:
- "select": User wants to run/generate/build/show the box selection (e.g. "select the box", "run selection", "pick the bars", "what's the box?", "generate", "run it")
- "adjust": User wants to switch which box RECIPE to run (e.g. "use the vegan dark box", "switch to ST-BAR-404-3", "orange box milk dark milk") OR asks to change constraints (you'll route to recipe switch / file note)
- "explain": User asks why a specific bar was/wasn't chosen, or wants details about a specific bar (e.g. "why is bar X selected?", "tell me about the Ghana bar", "explain this pick")
- "query": User asks a factual inventory question (e.g. "how many bars expire before June?", "show me vegan bars", "what's our highest risk bar?", "how many candidates do we have?")
- "general": Greetings, help requests, meta questions, or anything else

Respond with ONLY the intent word (select, adjust, explain, query, or general)."""

    response = _client().messages.create(
        model=MODEL_FAST,
        max_tokens=10,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text.strip().lower()
    valid = {"select", "adjust", "explain", "query", "general"}
    for word in raw.split():
        if word in valid:
            return word
    return "general"


# ── Data loaders ──────────────────────────────────────────────────────────────

def load_initial_inventory() -> list:
    return load_app_inventory(BASE / "data" / "real_inventory.json")


def load_raw_inventory() -> list:
    """ShopiCoda rows (before legacy scoring adapter)."""
    return load_inventory(BASE / "data" / "real_inventory.json")


def load_initial_rules() -> dict:
    return load_bundle_rules(BASE / "rules" / "real_bundle_rules.json")
