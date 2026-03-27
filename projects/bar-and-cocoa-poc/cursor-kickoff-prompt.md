# Bar & Cocoa — 10-Pack Selection Agent POC
## Cursor Kickoff Prompt

---

## Context

Bar & Cocoa is a specialty chocolate retailer. The owner, Pashmina, manually selects 10 bars for a curated gift box. This is time-consuming, error-prone, and hard to scale. The goal is to build an AI-powered selection agent that replicates and augments her judgment.

This is a real paid engagement (Triad AI, first live client). Inventory comes from the ShopiCoda CSV export (`data/inbound/Bundle_Items_List.csv` → `data/real_inventory.json`).

---

## The Problem

Selecting 10 bars from ~20–50 inventory items sounds simple. It isn't. Pashmina is solving two intertwined problems simultaneously:

**1. Inventory management:** Use the gift box to move inventory intelligently:
- Move bars that are slow-selling and approaching expiry
- Do NOT use fast-moving bars (they'll sell without the box)
- Do NOT use "hard to get" bars even if inventory looks high (that stock is a safety buffer — bars ordered only 1–2x/year from overseas)

**2. Curation quality:** The box must actually look and taste great together:
- Diversity of origin, type (dark/milk/white), and intensity
- Flavor arc from mild to bold
- Price ceiling per box
- No more than 2 bars from the same maker

---

## Architecture (Agreed)

**Phase 1 (POC — build this):** Two-stage pipeline

**Stage 1 — Inventory Scoring Engine (Python)**
- Load `data/real_inventory.json` (regenerate from inbound CSV via `scripts/import_bundle_items_csv.py` when the export updates)
- Load `rules/real_bundle_rules.json` (bundle recipes)
- Compute derived metrics per bar:
  - `days_of_supply = (current_inventory / weekly_velocity) * 7`
  - `days_until_expiry` = days from today to `expiry_date`
  - `expiry_risk_score` = urgency score (higher = more urgent)
  - `is_buffer_stock` = True if `reorder_frequency_per_year <= 2`
  - `is_fast_mover` = True if `weekly_velocity >= 4.0`
- Flag candidates: exclude fast movers, exclude buffer stock, prioritize expiry urgency + slow velocity
- Output: ranked candidate list with scores and flags

**Stage 2 — LLM Selection (Claude)**
- Take the candidate list (with scores + metadata)
- Apply each recipe's hard constraints + soft caps from `real_bundle_rules.json` (deterministic greedy on sell-out days)
- Output: 10-bar selection per active bundle recipe

**Stage 3 — Human Review Output**
- Format the selection as a clear, readable review message
- Show each bar with: name, maker, origin, price, expiry date, days_of_supply, reason for inclusion
- Show box totals: total price, origin count, intensity spread
- Flag any borderline calls for Pashmina to review

---

## Files

```
bar-and-cocoa-poc/
├── data/
│   ├── inbound/
│   │   └── Bundle_Items_List.csv   # source export from ShopiCoda
│   └── real_inventory.json     # JSON for app + bundle scripts (imported from CSV)
├── rules/
│   └── real_bundle_rules.json # ShopiCoda bundle recipes
├── src/
│   ├── score.py                # Stage 1: inventory scoring engine
│   ├── select.py               # Stage 2: LLM selection via Claude API
│   └── format_review.py        # Stage 3: human-readable review output
├── tests/
│   ├── test_score.py
│   └── test_format_review.py
├── docs/
│   └── PRD.md                  # to be generated
└── README.md
```

---

## Data Model

`score.py` maps each ShopiCoda row to legacy fields for scoring / LLM selection. Normalized fields include:

| Field | Type | Description |
|---|---|---|
| id | string | Unique bar ID |
| name | string | Display name |
| maker | string | Chocolate maker/brand |
| origin | string | Country of origin |
| type | enum | dark / milk / white / dark-inclusion / milk-inclusion / white-inclusion |
| cacao_pct | int | Cacao percentage (0 for white) |
| flavor_tags | string[] | Flavor descriptors |
| intensity | enum | mild / medium / medium-bold / bold / extra-bold |
| price_usd | float | Retail price per bar |
| dietary_flags | string[] | vegan, nut-free, etc. |
| current_inventory | int | Units on hand |
| weekly_velocity | float | Avg units sold per week |
| expiry_date | date | YYYY-MM-DD |
| reorder_frequency_per_year | int | How many times/year Pashmina can reorder |
| reorder_lead_time_weeks | int | Weeks from order to arrival |

---

## Build Order (BMAD discipline — do not skip ahead)

### Story 1: Scoring Engine
- File: `src/score.py`
- Input: `data/real_inventory.json` (list of bars; ShopiCoda schema, normalized internally)
- Output: same list with computed fields added: `days_of_supply`, `days_until_expiry`, `expiry_risk_score`, `is_buffer_stock`, `is_fast_mover`, `candidate_score`, `candidate_eligible` (bool)
- Tests: `tests/test_score.py` — cover scoring logic, buffer stock flag, fast mover flag, edge cases (zero velocity, expired already)
- Gate: all tests pass before Story 2

### Story 2: LLM Selection
- File: `src/select.py`
- Input: scored candidate list from Story 1, recipes from `real_bundle_rules.json` (or use deterministic bundle selector)
- Output: JSON object with `selected_bars` (list of 10) and `reasoning` per bar
- Use Claude API (anthropic SDK). Model: `claude-3-7-sonnet-20250219`
- Prompt must include: full candidate data, hard constraints, soft preferences, explicit instruction to respect max_per_maker, max_per_origin, min_dark, price ceiling
- Gate: selection respects all hard constraints 100% of the time (write a validator to verify — not just trust LLM output)

### Story 3: Review Formatter
- File: `src/format_review.py`
- Input: selection output from Story 2
- Output: clean formatted text (Markdown) showing the 10-bar selection with per-bar reasoning, box totals, and any flagged borderline calls
- Tests: `tests/test_format_review.py`
- Gate: output is readable and complete

---

## Constraints & Notes

- Python 3.11+, standard libs + `anthropic`, no heavy dependencies
- No database — `real_inventory.json` (from inbound CSV) is the data source for POC
- Claude API key expected in environment as `ANTHROPIC_API_KEY`
- Today's date for expiry calculations: use `datetime.date.today()`
- Do not build a UI for the POC — CLI only, stdout output is fine
- Do not connect to Coda.io yet — that's Phase 2
- BMAD gate discipline: each story must be tested before advancing

---

## Success Criteria

A successful POC:
1. Runs `python src/score.py` → outputs scored/flagged inventory
2. Runs `python src/select.py` → outputs 10-bar selection satisfying all hard constraints
3. Runs `python src/format_review.py` → outputs a readable review message Pashmina could act on
4. All tests pass
5. No fast movers or buffer stock in the selection

---

*Built for Triad AI — Bar & Cocoa engagement, March 2026*
