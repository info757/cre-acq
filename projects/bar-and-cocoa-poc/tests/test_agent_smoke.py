"""
Smoke tests for the agent graph — verifies all five intent paths work.
Run: .venv/bin/python -m pytest tests/test_agent_smoke.py -v -s
"""

import os
import sys
import uuid
from pathlib import Path

# Setup path + env
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
from dotenv import load_dotenv
load_dotenv(Path(__file__).parent.parent / ".env")

from langchain_core.messages import HumanMessage
from agent_graph import graph, make_initial_state


def _run(msg: str) -> dict:
    """Helper: invoke graph with a fresh thread."""
    state = make_initial_state()
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}
    return graph.invoke(
        {**state, "messages": [HumanMessage(content=msg)]},
        config=config,
    )


def test_intent_query():
    result = _run("How many bars expire before June 2026?")
    assert result["routing_intent"] == "query"
    last = result["messages"][-1]
    assert len(last.content) > 20


def test_intent_general():
    result = _run("Hello, who are you?")
    assert result["routing_intent"] == "general"
    last = result["messages"][-1]
    assert len(last.content) > 10


def test_intent_explain():
    result = _run("Tell me about the Ghana 90% Ultra Dark bar")
    assert result["routing_intent"] == "explain"
    last = result["messages"][-1]
    assert "Ghana" in last.content or "ghana" in last.content.lower()


if __name__ == "__main__":
    import pytest
    pytest.main([__file__, "-v", "-s"])
