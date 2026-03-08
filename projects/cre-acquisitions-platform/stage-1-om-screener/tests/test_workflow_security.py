"""
test_workflow_security.py — Assert workflow.json does not interpolate untrusted input into shell commands.
"""

import json
import os


def test_workflow_does_not_interpolate_webhook_body_into_command():
    """Execute Command nodes must not concatenate deal_folder, deal_id, or corrections into shell."""
    workflow_path = os.path.join(
        os.path.dirname(__file__), "..", "n8n", "workflow.json"
    )
    with open(workflow_path) as f:
        wf = json.load(f)

    unsafe_patterns = [
        ".body.deal_folder",
        ".body.deal_id",
        ".body.corrections",
        "json.body.deal_folder",
        "json.body.corrections",
    ]

    for node in wf.get("nodes", []):
        if node.get("type") != "n8n-nodes-base.executeCommand":
            continue
        cmd = node.get("parameters", {}).get("command", "")
        for pattern in unsafe_patterns:
            assert pattern not in cmd, (
                f"Node {node.get('name')} interpolates untrusted input: {pattern}"
            )


def test_workflow_uses_config_path_instead():
    """Execute Command nodes should use --config with a file path."""
    workflow_path = os.path.join(
        os.path.dirname(__file__), "..", "n8n", "workflow.json"
    )
    with open(workflow_path) as f:
        wf = json.load(f)

    run_nodes = [
        n for n in wf.get("nodes", [])
        if n.get("type") == "n8n-nodes-base.executeCommand"
        and "src/run_pipeline.py" in n.get("parameters", {}).get("command", "")
    ]
    assert len(run_nodes) >= 2, "Expected at least 2 run_pipeline Execute Command nodes"
    for node in run_nodes:
        cmd = node.get("parameters", {}).get("command", "")
        assert "--config" in cmd, f"Node {node.get('name')} should use --config"
        assert "configPath" in cmd or "config" in cmd, (
            f"Node {node.get('name')} should reference config path"
        )
