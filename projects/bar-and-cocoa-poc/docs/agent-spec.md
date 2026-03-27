# Bar & Cocoa Selection Agent — Spec
*Triad AI | Draft 2026-03-23*

---

## Goal

Convert the existing batch POC into a conversational LangGraph agent that Pashmina can interact with directly. She asks questions, adjusts rules, and re-runs selections. The agent explains its reasoning at every step. Synthetic inventory expands to 100 bars for demo realism.

---

## What Pashmina Can Do

Pashmina can ask anything she'd ask a knowledgeable employee who had her full inventory in front of them. The examples below are illustrative, not exhaustive.

**Selection:**
- "Show me this month's box."
- "Make me a vegan-only box."
- "What would change if I raised the price ceiling to $175?"
- "Show me everything that was excluded and why."

**Explaining decisions:**
- "Why is [bar name] not in the box?"
- "Why did you pick [bar name]?"

**Adjusting rules:**
- "Change the velocity threshold to 3 and re-run."
- "Stop including bars from USA."
- "I want at least 5 dark bars in every box."

**Inventory queries — anything, natural language:**
- "What bars are expiring in the next 30 days?"
- "How many bars do I have from Madagascar?"
- "What's my total inventory value right now?"
- "Which makers do I carry the most of?"
- "Show me my slowest moving bars."
- "What's my most expensive bar?"
- "Which bars have less than 20 units left?"
- Anything else she'd want to know about her stock.

---

## Architecture

### Stack
- **LangGraph** — agent graph + state management
- **Claude (claude-sonnet-4-6)** — reasoning and conversation (drop Opus for cost)
- **Python** — existing scoring engine wrapped as tools
- **LangGraph Studio** — visual graph trace for demo
- **Simple CLI or Chainlit** — chat interface (see Interface section)

### Agent Graph Nodes

```
[user_input]
     │
     ▼
[intent_router]          ← classifies: select / explain / adjust_rules / query_inventory / general
     │
     ├──► [run_selection]     ← scores inventory, calls LLM selector, validates constraints
     │         │
     │         ▼
     │    [format_response]   ← assembles human-readable box summary + reasoning
     │
     ├──► [explain_bar]       ← explains why a specific bar was included or excluded
     │
     ├──► [adjust_rules]      ← parses rule change, updates rules in state, confirms with user
     │         │
     │         ▼
     │    [run_selection]     ← re-runs after rule change
     │
     ├──► [query_inventory]   ← answers questions about inventory without running a full selection
     │
     └──► [general_response]  ← handles anything else conversationally
```

### State Object

```python
class AgentState(TypedDict):
    messages: list                  # full conversation history
    inventory: list                 # raw inventory (loaded once)
    scored_inventory: list          # scored inventory (updated after rule changes)
    rules: dict                     # current rules (mutable — Pashmina can change these)
    last_selection: dict | None     # most recent selection result
    pending_rule_change: dict | None  # rule change awaiting confirmation
```

### Tools (wrapping existing scoring engine)

| Tool | Description |
|------|-------------|
| `score_inventory(inventory, rules)` | Runs scoring engine, returns scored + flagged bars |
| `select_bars(candidates, scored, rules)` | Calls LLM selector + constraint enforcer |
| `explain_bar(bar_id, scored_inventory, last_selection)` | Returns why a bar was included/excluded |
| `query_inventory(question, scored_inventory)` | Answers inventory questions (expiry risk, velocity, etc.) |
| `update_rules(field, value, current_rules)` | Applies a rule change, returns updated rules |
| `format_box_output(selection_result)` | Formats selection as readable summary |

All tools are thin wrappers over the existing `score.py` / `llm_select.py` / `format_review.py` logic. No rewrite.

---

## Rules Are First-Class

Rules live in agent state, not a static file. When Pashmina changes a rule, the agent:
1. Confirms what it heard ("Got it — changing velocity threshold from 4.0 to 3.0. Re-running the selection.")
2. Updates the rules in state
3. Re-runs scoring + selection
4. Returns the new box with a diff ("These 2 bars are new, these 2 dropped out.")

This is the core demo moment. She sees the system respond to her judgment in real time.

---

## Chat Interface

**Chainlit.** Clean web UI, runs locally, shareable via ngrok. Pashmina opens a URL, no install required. Shows conversation with the agent; LangGraph Studio runs alongside for the visual graph trace.

---

## LangGraph Studio

Run alongside the chat interface during demo/review. Pashmina (or Will) can watch the graph nodes light up as the agent works. Scoring → filtering → selecting → explaining — all visible.

This is the transparency layer. Not a dashboard we had to build — it comes free with LangGraph.

---

## Synthetic Inventory Expansion (100 bars)

Expand from 20 → 100 bars. Distribution should be realistic:
- ~30% fast movers (excluded from selection)
- ~15% buffer stock (excluded)
- ~55% eligible candidates (~55 bars competing for 10 spots)
- Spread across 15+ origins, 10+ makers
- Mix of types: dark (~50%), dark-inclusion (~20%), milk (~15%), white (~10%), other (~5%)
- Realistic expiry spread: some urgent (< 60 days), most mid-range, some safe (> 180 days)

The expanded inventory should stress-test the constraint logic and make the selection feel genuinely competitive.

---

## What We Are NOT Building

- No Coda.io integration (Phase 2)
- No authentication / multi-user
- No persistent database
- No deployment / hosting
- No mobile UI
- No automated scheduling

This is a demo. Clean, focused, impressive. Not a product.

---

## Build Order

1. Inventory is ShopiCoda CSV → `real_inventory.json` (no synthetic fixture)
2. Wrap existing scoring engine as LangGraph tools
3. Build agent graph (nodes + state + routing)
4. Add Chainlit chat interface
5. Wire LangGraph Studio
6. End-to-end test: all Pashmina conversation examples work
7. Polish: intro message, error handling, rule change confirmation flow

---

## Success Criteria

Pashmina opens the URL, types "Show me this month's box," and gets a complete, explained selection. She then asks "why isn't [bar] in there?" and gets a clear answer. She says "change the velocity threshold to 3" and watches the box update. She's convinced the system understands her business.

---

*Spec by Zoé 🌹 — ready for Will's review*
