"""
app.py — Chainlit UI for Bar & Cocoa Inventory Curation Agent.

Run with:
  chainlit run app.py --watch

Or with the venv:
  .venv/bin/chainlit run app.py --watch
"""

from __future__ import annotations

import os
import sys
import uuid
from pathlib import Path

# Ensure src is on the path
sys.path.insert(0, str(Path(__file__).parent / "src"))

# Load env before importing the graph
from dotenv import load_dotenv
_base = Path(__file__).parent
for _env in [_base / ".env", _base.parent / "cre-acquisitions-platform" / "stage-1-om-screener" / ".env"]:
    if _env.exists():
        load_dotenv(str(_env))
        break

import chainlit as cl

# Startup key check — helps diagnose Railway env issues
_api_key = os.environ.get("ANTHROPIC_API_KEY", "")
if not _api_key:
    raise RuntimeError(
        "ANTHROPIC_API_KEY is not set. "
        "Add it as an environment variable in Railway and redeploy."
    )
print(f"[startup] ANTHROPIC_API_KEY found (length={len(_api_key)})")
from langchain_core.messages import HumanMessage
from langgraph.checkpoint.memory import MemorySaver

from src.agent_graph import compiled_builder, make_initial_state

# Compile with MemorySaver for Chainlit (Studio handles persistence via its own platform)
graph = compiled_builder.compile(checkpointer=MemorySaver())


# ── Chat lifecycle ────────────────────────────────────────────────────────────

@cl.on_chat_start
async def on_chat_start():
    """Initialize a new conversation session."""
    thread_id = str(uuid.uuid4())
    cl.user_session.set("thread_id", thread_id)

    # Seed the graph with initial state (inventory + rules loaded from disk)
    initial = make_initial_state()
    config = {"configurable": {"thread_id": thread_id}}
    # We prime the graph by setting state directly (no message yet)
    graph.update_state(config, initial)

    await cl.Message(
        content=(
            "# 🍫 Bar & Cocoa — Curation Agent\n\n"
            "Hi Pashmina! I'm your inventory curation assistant.\n\n"
            "**What I can do:**\n"
            "- **Build the box** — `select the box` / `run selection` (uses **Bundle Rules** + live CSV → JSON inventory)\n"
            "- **Switch recipe** — e.g. `use bundle ST-BAR-404-3` or describe the orange / crane / vegan box\n"
            "- **Explain a pick** — `why is this bar in the box?` (SKU or product name)\n"
            "- **Query inventory** — stock, vegan bars, expiry, etc.\n\n"
            f"**Active recipe:** `{initial.get('active_bundle_id', '?')}` — **{len(initial['inventory'])}** bars loaded.\n"
            "Ready when you are."
        )
    ).send()


@cl.on_message
async def on_message(message: cl.Message):
    """Handle an incoming user message."""
    thread_id = cl.user_session.get("thread_id")
    if not thread_id:
        thread_id = str(uuid.uuid4())
        cl.user_session.set("thread_id", thread_id)

    config = {"configurable": {"thread_id": thread_id}}

    # Show spinner for heavy operations
    user_text_lower = message.content.lower()
    is_heavy = any(
        kw in user_text_lower
        for kw in ["select", "run", "pick", "generate", "box", "adjust", "change", "lower", "raise", "modify"]
    )

    thinking_msg = None
    if is_heavy:
        thinking_msg = cl.Message(content="⏳ Working on it...")
        await thinking_msg.send()

    try:
        # Invoke graph — graph restores state from MemorySaver automatically
        result = await graph.ainvoke(
            {"messages": [HumanMessage(content=message.content)]},
            config=config,
        )

        # Extract the last AI message
        ai_messages = [m for m in result["messages"] if hasattr(m, "type") and m.type == "ai"]
        if ai_messages:
            response_content = ai_messages[-1].content
        else:
            response_content = "_No response generated._"

        # Report what intent was detected (debug/transparency)
        intent = result.get("routing_intent", "")
        intent_badge = {
            "select": "📦 Selection",
            "adjust": "⚙️ Rule Adjustment",
            "explain": "🔍 Explanation",
            "query": "📊 Inventory Query",
            "general": "💬 General",
        }.get(intent, "")

        footer = f"\n\n---\n*Intent: {intent_badge}*" if intent_badge else ""

        if thinking_msg:
            # Replace spinner with actual response
            await thinking_msg.remove()

        await cl.Message(content=response_content + footer).send()

    except Exception as e:
        if thinking_msg:
            await thinking_msg.remove()
        await cl.Message(
            content=f"❌ **Error:** {type(e).__name__}: {e}\n\nPlease try again."
        ).send()
        raise


# ── Sidebar actions ───────────────────────────────────────────────────────────

@cl.action_callback("view_rules")
async def view_rules(action: cl.Action):
    """Show current rules."""
    thread_id = cl.user_session.get("thread_id")
    if not thread_id:
        return
    config = {"configurable": {"thread_id": thread_id}}
    state = graph.get_state(config)
    if state and state.values:
        rules = state.values.get("rules", {})
        import json
        await cl.Message(
            content=f"**Current Rules:**\n```json\n{json.dumps(rules, indent=2)}\n```"
        ).send()


@cl.action_callback("reset_rules")
async def reset_rules(action: cl.Action):
    """Reset rules to defaults."""
    thread_id = cl.user_session.get("thread_id")
    if not thread_id:
        return
    config = {"configurable": {"thread_id": thread_id}}
    from src.agent_tools import load_initial_rules, load_raw_inventory, load_initial_inventory

    default_rules = load_initial_rules()
    first = default_rules["bundles"][0]["bundle_id"]
    graph.update_state(
        config,
        {
            "rules": default_rules,
            "active_bundle_id": first,
            "inventory": load_initial_inventory(),
            "inventory_raw": load_raw_inventory(),
            "last_selection": None,
        },
    )
    await cl.Message(
        content=f"✅ Reset to defaults — active recipe `{first}`. Run selection again for a fresh box."
    ).send()
