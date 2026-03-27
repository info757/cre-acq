"""
agent_graph.py — LangGraph agent for Bar & Cocoa inventory curation.

Graph:
  START → intent_router
    → select   → run_selection → END
    → adjust   → adjust_rules  → run_selection → END
    → explain  → explain_bar   → END
    → query    → query_inv     → END
    → general  → general_resp  → END
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages
from typing_extensions import Annotated, TypedDict

# Load .env relative to this file's project root
_base = Path(__file__).parent.parent
_env_candidates = [
    _base / ".env",
    _base.parent / "cre-acquisitions-platform" / "stage-1-om-screener" / ".env",
]
for _env in _env_candidates:
    if _env.exists():
        load_dotenv(str(_env))
        break

# Local imports
sys.path.insert(0, str(Path(__file__).parent))
from agent_tools import (
    classify_intent,
    explain_bar,
    general_response,
    load_initial_inventory,
    load_initial_rules,
    load_raw_inventory,
    parse_bundle_focus,
    query_inventory,
    run_bundle_selection_pipeline,
)


# ── State ─────────────────────────────────────────────────────────────────────

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]
    inventory: list
    inventory_raw: list
    rules: dict
    active_bundle_id: str
    last_selection: Optional[dict]
    routing_intent: str   # set by intent_router, read by conditional edge


# ── Node: Intent Router ───────────────────────────────────────────────────────

def intent_router_node(state: AgentState) -> dict:
    """Classify the last user message and set routing_intent."""
    last_msg = state["messages"][-1]
    user_text = last_msg.content if hasattr(last_msg, "content") else str(last_msg)
    intent = classify_intent(
        user_text,
        last_selection_exists=state.get("last_selection") is not None,
    )
    return {"routing_intent": intent}


def route_after_intent(state: AgentState) -> str:
    """Conditional edge: route based on routing_intent."""
    return state.get("routing_intent", "general")


# ── Node: Run Selection ───────────────────────────────────────────────────────

def run_selection_node(state: AgentState) -> dict:
    """Run deterministic bundle selection (real_bundle_rules + inventory rows)."""
    print("[agent] Running bundle selection pipeline...")
    raw = state.get("inventory_raw")
    if not raw:
        raw = load_raw_inventory()
    rules = state["rules"]
    bid = state.get("active_bundle_id") or rules["bundles"][0]["bundle_id"]
    data = run_bundle_selection_pipeline(raw, rules, bid)
    result = data["result"]
    review_md = data["review_md"]
    bundle = data["bundle"]

    header = (
        f"**Recipe:** {bundle['name']} (`{bundle['bundle_id']}`)\n"
        f"**Box:** {bundle.get('box_name', '')} ({bundle['box_sku']})\n"
        f"**Hard-filter candidates:** {data['num_candidates']} / {data['num_total']} SKUs\n\n"
    )

    response = header + review_md
    return {
        "messages": [AIMessage(content=response)],
        "last_selection": result,
    }


# ── Node: Adjust Rules ────────────────────────────────────────────────────────

def adjust_rules_node(state: AgentState) -> dict:
    """Switch active bundle recipe when the user asks; selection follows."""
    last_msg = state["messages"][-1]
    user_text = last_msg.content if hasattr(last_msg, "content") else str(last_msg)

    print("[agent] Parsing bundle focus...")
    cur = state.get("active_bundle_id") or state["rules"]["bundles"][0]["bundle_id"]
    parsed = parse_bundle_focus(user_text, state["rules"], cur)
    new_id = parsed["active_bundle_id"]
    summary = parsed.get("summary", "")
    changes = parsed.get("changes", [])

    if changes:
        change_lines = "\n".join(
            f"  • {c.get('description', c.get('path', '?'))}: "
            f"{c.get('old_value')} → {c.get('new_value')}"
            for c in changes
        )
        ack = f"⚙️ **Bundle recipe:**\n{change_lines}\n\n*Re-running selection...*"
    else:
        ack = f"⚙️ {summary}\n\n*Re-running selection with the same recipe...*"

    return {
        "messages": [AIMessage(content=ack)],
        "active_bundle_id": new_id,
    }


# ── Node: Explain Bar ─────────────────────────────────────────────────────────

def explain_bar_node(state: AgentState) -> dict:
    """Explain a specific bar or selection decision."""
    last_msg = state["messages"][-1]
    user_text = last_msg.content if hasattr(last_msg, "content") else str(last_msg)

    print("[agent] Generating bar explanation...")
    explanation = explain_bar(
        user_query=user_text,
        inventory=state["inventory"],
        rules=state["rules"],
        last_selection=state.get("last_selection"),
    )
    return {"messages": [AIMessage(content=explanation)]}


# ── Node: Query Inventory ─────────────────────────────────────────────────────

def query_inv_node(state: AgentState) -> dict:
    """Answer an inventory data question."""
    last_msg = state["messages"][-1]
    user_text = last_msg.content if hasattr(last_msg, "content") else str(last_msg)

    print("[agent] Answering inventory query...")
    answer = query_inventory(
        inventory=state["inventory"],
        rules=state["rules"],
        user_query=user_text,
        last_selection=state.get("last_selection"),
    )
    return {"messages": [AIMessage(content=answer)]}


# ── Node: General Response ────────────────────────────────────────────────────

def general_resp_node(state: AgentState) -> dict:
    """Handle general questions, greetings, or off-topic messages."""
    last_msg = state["messages"][-1]
    user_text = last_msg.content if hasattr(last_msg, "content") else str(last_msg)

    print("[agent] Generating general response...")
    answer = general_response(
        user_query=user_text,
        inventory=state["inventory"],
        rules=state["rules"],
        last_selection=state.get("last_selection"),
        conversation_history=state["messages"][:-1],
    )
    return {"messages": [AIMessage(content=answer)]}


# ── Build Graph ───────────────────────────────────────────────────────────────

def build_graph() -> StateGraph:
    builder = StateGraph(AgentState)

    # Nodes
    builder.add_node("intent_router", intent_router_node)
    builder.add_node("run_selection", run_selection_node)
    builder.add_node("adjust_rules", adjust_rules_node)
    builder.add_node("explain_bar", explain_bar_node)
    builder.add_node("query_inv", query_inv_node)
    builder.add_node("general_resp", general_resp_node)

    # Entry point
    builder.add_edge(START, "intent_router")

    # Route after intent classification
    builder.add_conditional_edges(
        "intent_router",
        route_after_intent,
        {
            "select": "run_selection",
            "adjust": "adjust_rules",
            "explain": "explain_bar",
            "query": "query_inv",
            "general": "general_resp",
        },
    )

    # After adjust_rules, always run selection
    builder.add_edge("adjust_rules", "run_selection")

    # Terminal edges
    builder.add_edge("run_selection", END)
    builder.add_edge("explain_bar", END)
    builder.add_edge("query_inv", END)
    builder.add_edge("general_resp", END)

    return builder


# Export the builder so callers can compile with their own checkpointer.
# - LangGraph Studio: uses `graph` (no checkpointer, platform handles it)
# - Chainlit app.py: builds `graph_with_memory` using MemorySaver
_builder = build_graph()
graph = _builder.compile()          # for LangGraph Studio / langgraph dev
compiled_builder = _builder         # for app.py to re-compile with MemorySaver


# ── Initial state factory ─────────────────────────────────────────────────────

def make_initial_state() -> dict:
    """Return the initial state dict (inventory + rules loaded from disk)."""
    rules = load_initial_rules()
    first_id = rules["bundles"][0]["bundle_id"]
    return {
        "inventory": load_initial_inventory(),
        "inventory_raw": load_raw_inventory(),
        "rules": rules,
        "active_bundle_id": first_id,
        "last_selection": None,
        "routing_intent": "",
        "messages": [
            SystemMessage(content=(
                "You are Bar & Cocoa's bundle curator. Gift boxes follow recipes in "
                "real_bundle_rules.json (hard constraints + soft caps). Selection is "
                "deterministic on ShopiCoda inventory: prioritize bars with shortest sell-out days "
                "that still satisfy the active recipe."
            ))
        ],
    }


if __name__ == "__main__":
    # Quick smoke test
    import uuid
    state = make_initial_state()
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    print("=== Intent router smoke test ===")
    result = graph.invoke(
        {**state, "messages": [HumanMessage(content="How many bars do we have?")]},
        config=config,
    )
    last = result["messages"][-1]
    print(f"Intent: {result['routing_intent']}")
    print(f"Response: {last.content[:300]}")
