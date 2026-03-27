"""
Stage 1: Inventory Scoring Engine
Bar & Cocoa POC — Triad AI

Loads data/real_inventory.json (ShopiCoda export, via CSV import), maps rows to
legacy scoring fields, computes derived metrics per bar, and outputs a scored
candidate list for the LLM selection stage.
"""

import json
import datetime
from pathlib import Path

# Thresholds (could be moved to rules_config later)
BUFFER_STOCK_MAX_REORDER = 2       # reorder_frequency_per_year <= this → buffer stock
FAST_MOVER_MIN_VELOCITY = 4.0      # weekly_velocity >= this → fast mover (exclude)
LOW_VELOCITY_THRESHOLD = 1.5       # weekly_velocity < this → slow mover (candidate)
EXPIRY_URGENCY_DAYS = 90           # bars expiring within this many days are urgent


def compute_days_until_expiry(expiry_date_str: str, today: datetime.date = None) -> int:
    """Days from today until expiry. Negative means already expired."""
    if today is None:
        today = datetime.date.today()
    expiry = datetime.date.fromisoformat(expiry_date_str)
    return (expiry - today).days


def compute_days_of_supply(current_inventory: int, weekly_velocity: float) -> float:
    """How many days of stock on hand at current sales rate. Returns inf if velocity is 0."""
    if weekly_velocity <= 0:
        return float("inf")
    return (current_inventory / weekly_velocity) * 7


def compute_expiry_risk_score(days_until_expiry: int, days_of_supply: float) -> float:
    """
    Score from 0.0 to 1.0 indicating how urgently a bar needs to be moved.
    High score = bar will expire before it naturally sells through.
    0.0 = no risk (plenty of time), 1.0 = maximum urgency.
    """
    if days_until_expiry <= 0:
        return 1.0  # already expired
    if days_of_supply == float("inf"):
        # Zero velocity — if expiry is within urgency window, max risk
        return 1.0 if days_until_expiry <= EXPIRY_URGENCY_DAYS else 0.5

    # Risk = how much days_of_supply exceeds days_until_expiry
    # If days_of_supply > days_until_expiry, bar will expire before selling through
    overhang = days_of_supply - days_until_expiry
    if overhang <= 0:
        return 0.0  # will sell before expiry — no urgency
    # Normalize: full score if overhang >= expiry window
    return min(1.0, overhang / EXPIRY_URGENCY_DAYS)


def compute_candidate_score(bar: dict, days_until_expiry: int, days_of_supply: float,
                             expiry_risk_score: float) -> float:
    """
    Composite candidate score (higher = better candidate for the box).
    Factors: expiry urgency, low velocity, restockability.
    Excludes fast movers and buffer stock entirely.
    """
    is_buffer = bar["reorder_frequency_per_year"] <= BUFFER_STOCK_MAX_REORDER
    is_fast_mover = bar["weekly_velocity"] >= FAST_MOVER_MIN_VELOCITY

    if is_buffer or is_fast_mover:
        return 0.0

    # Expiry urgency (0–1): most important factor
    urgency_component = expiry_risk_score

    # Slow mover bonus: lower velocity → higher score
    velocity_component = max(0.0, 1.0 - (bar["weekly_velocity"] / LOW_VELOCITY_THRESHOLD))

    # Restock ease bonus: more reorders/year = easier to restock = safer to include
    restock_component = min(1.0, bar["reorder_frequency_per_year"] / 12)

    # Weighted composite
    score = (urgency_component * 0.5) + (velocity_component * 0.3) + (restock_component * 0.2)
    return round(score, 4)


def score_inventory(inventory: list, today: datetime.date = None) -> list:
    """
    Main scoring function. Returns a new list of bars with derived fields appended.
    Does not mutate input dicts.
    """
    if today is None:
        today = datetime.date.today()

    scored = []
    for bar in inventory:
        b = dict(bar)  # shallow copy

        days_until_expiry = compute_days_until_expiry(b["expiry_date"], today)
        days_of_supply = compute_days_of_supply(b["current_inventory"], b["weekly_velocity"])
        expiry_risk_score = compute_expiry_risk_score(days_until_expiry, days_of_supply)
        is_buffer_stock = b["reorder_frequency_per_year"] <= BUFFER_STOCK_MAX_REORDER
        is_fast_mover = b["weekly_velocity"] >= FAST_MOVER_MIN_VELOCITY
        candidate_score = compute_candidate_score(b, days_until_expiry, days_of_supply, expiry_risk_score)
        candidate_eligible = (
            not is_buffer_stock
            and not is_fast_mover
            and candidate_score > 0.0
        )

        b["_days_until_expiry"] = days_until_expiry
        b["_days_of_supply"] = round(days_of_supply, 1) if days_of_supply != float("inf") else None
        b["_expiry_risk_score"] = round(expiry_risk_score, 4)
        b["_is_buffer_stock"] = is_buffer_stock
        b["_is_fast_mover"] = is_fast_mover
        b["_candidate_score"] = candidate_score
        b["_candidate_eligible"] = candidate_eligible

        scored.append(b)

    # Sort: eligible candidates first (by score desc), then ineligible
    scored.sort(key=lambda x: (-x["_candidate_eligible"], -x["_candidate_score"]))
    return scored


def load_inventory(path: Path) -> list:
    with open(path) as f:
        return json.load(f)


# Real feed has no reorder cadence; neutral default so scoring uses velocity vs buffer heuristic.
DEFAULT_REORDER_FREQ = 6


def real_bar_to_scoring_record(bar: dict) -> dict:
    """Map ShopiCoda JSON row to fields expected by score_inventory / llm_select."""
    types = bar.get("chocolate_type") or []
    tl = {str(t).lower() for t in types}
    inc = bar.get("inclusion_flavor") or []

    if "white" in tl:
        typ = "white-inclusion" if (inc or "inclusions" in tl) else "white"
    elif "milk" in tl or "dark milk" in tl:
        typ = "milk-inclusion" if (inc or "inclusions" in tl) else "milk"
    elif "dark" in tl:
        typ = "dark-inclusion" if (inc or "inclusions" in tl) else "dark"
    else:
        typ = "dark-inclusion" if inc else "dark"

    cacao = bar.get("cacaonum")
    cacao_pct = int(cacao) if cacao is not None else 0

    if cacao_pct >= 88:
        intensity = "extra-bold"
    elif cacao_pct >= 80:
        intensity = "bold"
    elif cacao_pct >= 55:
        intensity = "medium"
    elif cacao_pct > 0:
        intensity = "mild"
    else:
        intensity = "mild"

    flavor_tags: list[str] = []
    for x in inc:
        if x not in flavor_tags:
            flavor_tags.append(x)
    for x in types:
        if str(x) != "Plain" and x not in flavor_tags:
            flavor_tags.append(str(x))
    tags = bar.get("tags") or []
    for t in tags[:12]:
        if t not in flavor_tags:
            flavor_tags.append(t)
    if not flavor_tags:
        flavor_tags = ["general"]

    origin = (bar.get("source_country") or "").strip() or "Unknown"

    return {
        "id": bar["sku"],
        "name": bar["name"],
        "maker": bar["vendor"],
        "origin": origin,
        "type": typ,
        "cacao_pct": cacao_pct,
        "flavor_tags": flavor_tags,
        "intensity": intensity,
        "price_usd": float(bar["retail_price"]),
        "dietary_flags": list(bar.get("diet_icons") or []),
        "current_inventory": int(bar["current_inventory"]),
        "weekly_velocity": float(bar["weekly_velocity"]),
        "expiry_date": bar["expiry_date"],
        "reorder_frequency_per_year": DEFAULT_REORDER_FREQ,
        "sku": bar["sku"],
    }


def load_app_inventory(path: Path | None = None) -> list:
    """Load real_inventory.json and normalize for the agent + scoring pipeline."""
    base = Path(__file__).resolve().parent.parent
    p = path or (base / "data" / "real_inventory.json")
    raw = load_inventory(p)
    return [real_bar_to_scoring_record(b) for b in raw]


def print_scored_inventory(scored: list):
    print(f"\n{'='*80}")
    print("BAR & COCOA — SCORED INVENTORY")
    print(f"{'='*80}\n")

    eligible = [b for b in scored if b["_candidate_eligible"]]
    ineligible = [b for b in scored if not b["_candidate_eligible"]]

    print(f"✅ CANDIDATES ({len(eligible)} bars eligible for selection)\n")
    print(f"{'Score':>6}  {'Risk':>5}  {'DoS':>6}  {'Exp':>5}  {'Vel':>5}  {'Name'}")
    print(f"{'-'*6}  {'-'*5}  {'-'*6}  {'-'*5}  {'-'*5}  {'-'*40}")
    for b in eligible:
        dos = f"{b['_days_of_supply']:.0f}d" if b["_days_of_supply"] is not None else "∞"
        print(
            f"{b['_candidate_score']:>6.3f}  "
            f"{b['_expiry_risk_score']:>5.3f}  "
            f"{dos:>6}  "
            f"{b['_days_until_expiry']:>5}d  "
            f"{b['weekly_velocity']:>5.1f}  "
            f"{b['name']}"
        )

    print(f"\n❌ EXCLUDED ({len(ineligible)} bars — fast mover or buffer stock)\n")
    for b in ineligible:
        reason = []
        if b["_is_fast_mover"]:
            reason.append("fast mover")
        if b["_is_buffer_stock"]:
            reason.append("buffer stock")
        print(f"  [{', '.join(reason):20}]  {b['name']}")

    print()


if __name__ == "__main__":
    base = Path(__file__).parent.parent
    inventory = load_app_inventory(base / "data" / "real_inventory.json")
    scored = score_inventory(inventory)
    print_scored_inventory(scored)
