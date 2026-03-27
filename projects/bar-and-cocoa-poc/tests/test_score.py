"""
Tests for src/score.py — Stage 1: Inventory Scoring Engine
"""

import sys
import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from score import (
    compute_days_until_expiry,
    compute_days_of_supply,
    compute_expiry_risk_score,
    compute_candidate_score,
    score_inventory,
    load_inventory,
    BUFFER_STOCK_MAX_REORDER,
    FAST_MOVER_MIN_VELOCITY,
)

TODAY = datetime.date(2026, 3, 22)


# ---------------------------------------------------------------------------
# compute_days_until_expiry
# ---------------------------------------------------------------------------

def test_expiry_future():
    assert compute_days_until_expiry("2026-06-20", TODAY) == 90

def test_expiry_today():
    assert compute_days_until_expiry("2026-03-22", TODAY) == 0

def test_expiry_past():
    assert compute_days_until_expiry("2026-03-01", TODAY) < 0

def test_expiry_far_future():
    assert compute_days_until_expiry("2027-03-22", TODAY) == 365


# ---------------------------------------------------------------------------
# compute_days_of_supply
# ---------------------------------------------------------------------------

def test_dos_normal():
    # 70 units, 1.0/week → 70 weeks → 490 days
    assert compute_days_of_supply(70, 1.0) == 490.0

def test_dos_zero_velocity():
    assert compute_days_of_supply(50, 0) == float("inf")

def test_dos_high_velocity():
    # 20 units, 5/week → 4 weeks → 28 days
    assert compute_days_of_supply(20, 5.0) == 28.0

def test_dos_fractional():
    result = compute_days_of_supply(48, 1.2)
    assert abs(result - 280.0) < 0.1  # 48/1.2 * 7 = 280


# ---------------------------------------------------------------------------
# compute_expiry_risk_score
# ---------------------------------------------------------------------------

def test_risk_already_expired():
    assert compute_expiry_risk_score(-5, 100) == 1.0

def test_risk_zero_expiry():
    assert compute_expiry_risk_score(0, 100) == 1.0

def test_risk_sells_before_expiry():
    # 30 days supply, 60 days until expiry → will sell fine → 0 risk
    assert compute_expiry_risk_score(60, 30) == 0.0

def test_risk_wont_sell_before_expiry():
    # 200 days supply, 60 days until expiry → overhang = 140 → high risk
    score = compute_expiry_risk_score(60, 200)
    assert score > 0.5

def test_risk_zero_velocity_urgent():
    # Zero velocity → inf days supply; expiry in 30 days (< 90) → max risk
    assert compute_expiry_risk_score(30, float("inf")) == 1.0

def test_risk_zero_velocity_not_urgent():
    # Zero velocity, expiry in 200 days → moderate risk
    score = compute_expiry_risk_score(200, float("inf"))
    assert score == 0.5

def test_risk_capped_at_one():
    score = compute_expiry_risk_score(10, 10000)
    assert score == 1.0


# ---------------------------------------------------------------------------
# compute_candidate_score
# ---------------------------------------------------------------------------

def make_bar(reorder_freq=6, velocity=0.8):
    return {
        "reorder_frequency_per_year": reorder_freq,
        "weekly_velocity": velocity,
    }

def test_score_buffer_stock_is_zero():
    bar = make_bar(reorder_freq=BUFFER_STOCK_MAX_REORDER)
    score = compute_candidate_score(bar, 60, 200, 0.8)
    assert score == 0.0

def test_score_fast_mover_is_zero():
    bar = make_bar(velocity=FAST_MOVER_MIN_VELOCITY)
    score = compute_candidate_score(bar, 60, 28, 0.2)
    assert score == 0.0

def test_score_ideal_candidate():
    # Slow, high urgency, easy to restock
    bar = make_bar(reorder_freq=12, velocity=0.5)
    score = compute_candidate_score(bar, 30, 280, 0.9)
    assert score > 0.6

def test_score_range():
    bar = make_bar(reorder_freq=6, velocity=1.0)
    score = compute_candidate_score(bar, 60, 200, 0.5)
    assert 0.0 <= score <= 1.0


# ---------------------------------------------------------------------------
# score_inventory (integration)
# ---------------------------------------------------------------------------

def make_inventory():
    return [
        {
            "id": "test-fast",
            "name": "Fast Mover Bar",
            "reorder_frequency_per_year": 12,
            "weekly_velocity": 5.0,
            "current_inventory": 100,
            "expiry_date": "2026-07-01",
        },
        {
            "id": "test-buffer",
            "name": "Buffer Stock Bar",
            "reorder_frequency_per_year": 2,
            "weekly_velocity": 0.5,
            "current_inventory": 40,
            "expiry_date": "2026-07-01",
        },
        {
            "id": "test-candidate",
            "name": "Ideal Candidate Bar",
            "reorder_frequency_per_year": 6,
            "weekly_velocity": 0.8,
            "current_inventory": 60,
            "expiry_date": "2026-05-01",
        },
    ]

def test_score_inventory_fast_mover_excluded():
    scored = score_inventory(make_inventory(), today=TODAY)
    fast = next(b for b in scored if b["id"] == "test-fast")
    assert fast["_is_fast_mover"] is True
    assert fast["_candidate_eligible"] is False

def test_score_inventory_buffer_excluded():
    scored = score_inventory(make_inventory(), today=TODAY)
    buf = next(b for b in scored if b["id"] == "test-buffer")
    assert buf["_is_buffer_stock"] is True
    assert buf["_candidate_eligible"] is False

def test_score_inventory_candidate_eligible():
    scored = score_inventory(make_inventory(), today=TODAY)
    cand = next(b for b in scored if b["id"] == "test-candidate")
    assert cand["_candidate_eligible"] is True
    assert cand["_candidate_score"] > 0.0

def test_score_inventory_sorted_eligible_first():
    scored = score_inventory(make_inventory(), today=TODAY)
    eligible_seen = False
    for b in scored:
        if b["_candidate_eligible"]:
            eligible_seen = True
        elif eligible_seen:
            # Once we see an ineligible after eligible, that's fine as long
            # as all eligibles come before ineligibles
            pass
    # First bar should be eligible
    assert scored[0]["_candidate_eligible"] is True

def test_score_inventory_derived_fields_present():
    scored = score_inventory(make_inventory(), today=TODAY)
    required = [
        "_days_until_expiry", "_days_of_supply", "_expiry_risk_score",
        "_is_buffer_stock", "_is_fast_mover", "_candidate_score", "_candidate_eligible"
    ]
    for bar in scored:
        for field in required:
            assert field in bar, f"Missing field {field} on {bar['id']}"

def test_score_inventory_no_mutation():
    inventory = make_inventory()
    original_ids = [b["id"] for b in inventory]
    score_inventory(inventory, today=TODAY)
    # Original list should be unchanged
    assert [b["id"] for b in inventory] == original_ids
    assert "_candidate_score" not in inventory[0]

def test_score_real_inventory():
    """Smoke test against ShopiCoda-backed real_inventory.json."""
    base = Path(__file__).parent.parent
    inv_path = base / "data" / "real_inventory.json"
    if not inv_path.exists():
        print("Skipping real inventory test — file not found")
        return
    from score import load_app_inventory

    inventory = load_app_inventory(inv_path)
    scored = score_inventory(inventory, today=TODAY)
    assert len(scored) == len(inventory)
    eligible = [b for b in scored if b["_candidate_eligible"]]
    assert len(eligible) >= 1, "Expected at least one eligible candidate"


# ---------------------------------------------------------------------------
# Run
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = failed = 0
    for t in tests:
        try:
            t()
            print(f"  ✅ {t.__name__}")
            passed += 1
        except Exception as e:
            print(f"  ❌ {t.__name__}: {e}")
            failed += 1
    print(f"\n{passed} passed, {failed} failed")
    if failed:
        sys.exit(1)
