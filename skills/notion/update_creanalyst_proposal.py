#!/usr/bin/env python3
"""
Updates the CREanalyst proposal page:
1. Replaces the Architecture section with the sub-agent architecture
2. Appends an Agent as a Service section
Page ID: 317a3175-c27b-81b6-bbc1-d19f532de118
"""
import json
import urllib.request
import urllib.error
from pathlib import Path

ENV_PATH = Path(__file__).parent / ".env"
API_KEY = None
if ENV_PATH.exists():
    for line in ENV_PATH.read_text().splitlines():
        if line.startswith("NOTION_API_KEY="):
            API_KEY = line.split("=", 1)[1].strip()

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}
BASE = "https://api.notion.com/v1"
PAGE_ID = "317a3175-c27b-81b6-bbc1-d19f532de118"


def api(method, path, body=None):
    url = f"{BASE}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err = json.loads(e.read())
        print(f"ERROR {e.code}: {err.get('message', str(err))}")
        return None


def get_text(block):
    for btype in ["heading_1","heading_2","heading_3","paragraph",
                  "bulleted_list_item","callout","code","numbered_list_item"]:
        if btype in block:
            parts = block[btype].get("rich_text", [])
            return "".join(p.get("plain_text","") for p in parts)
    return ""


def get_all_blocks(block_id):
    blocks = []
    cursor = None
    while True:
        path = f"/blocks/{block_id}/children?page_size=100"
        if cursor:
            path += f"&start_cursor={cursor}"
        data = api("GET", path)
        if not data:
            break
        blocks.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")
    return blocks


# Block builders
def h1(text):
    return {"object":"block","type":"heading_1","heading_1":{
        "rich_text":[{"type":"text","text":{"content":text}}]}}

def h2(text):
    return {"object":"block","type":"heading_2","heading_2":{
        "rich_text":[{"type":"text","text":{"content":text}}]}}

def h3(text):
    return {"object":"block","type":"heading_3","heading_3":{
        "rich_text":[{"type":"text","text":{"content":text}}]}}

def p(text):
    return {"object":"block","type":"paragraph","paragraph":{
        "rich_text":[{"type":"text","text":{"content":text}}]}}

def p_empty():
    return {"object":"block","type":"paragraph","paragraph":{"rich_text":[]}}

def bullet(text, bold_prefix=None):
    if bold_prefix:
        parts = [
            {"type":"text","text":{"content":bold_prefix},"annotations":{"bold":True}},
            {"type":"text","text":{"content":text}}
        ]
    else:
        parts = [{"type":"text","text":{"content":text}}]
    return {"object":"block","type":"bulleted_list_item","bulleted_list_item":{"rich_text":parts}}

def divider():
    return {"object":"block","type":"divider","divider":{}}

def callout(text, emoji="💡"):
    return {"object":"block","type":"callout","callout":{
        "rich_text":[{"type":"text","text":{"content":text}}],
        "icon":{"type":"emoji","emoji":emoji}}}

def code_block(text):
    return {"object":"block","type":"code","code":{
        "rich_text":[{"type":"text","text":{"content":text}}],
        "language":"plain text"}}


# ─── Step 1: Find and delete old Architecture section ─────────────────────────
print("Fetching blocks...")
blocks = get_all_blocks(PAGE_ID)
print(f"Total blocks: {len(blocks)}")

in_arch = False
arch_blocks_to_delete = []

for block in blocks:
    text = get_text(block)
    btype = block.get("type","")

    if btype == "heading_1" and "Architecture" in text:
        in_arch = True

    if in_arch:
        arch_blocks_to_delete.append(block["id"])

    # Stop at divider after architecture (before Tool Stack)
    if in_arch and btype == "divider" and len(arch_blocks_to_delete) > 1:
        in_arch = False

print(f"Deleting {len(arch_blocks_to_delete)} old architecture blocks...")
for bid in arch_blocks_to_delete:
    api("DELETE", f"/blocks/{bid}")
print("✓ Old architecture section removed.")


# ─── Step 2: Find the Tool Stack section to insert before it ──────────────────
# Re-fetch blocks after deletion
blocks = get_all_blocks(PAGE_ID)
tool_stack_block_id = None
for block in blocks:
    if block.get("type") == "heading_1" and "Tool Stack" in get_text(block):
        tool_stack_block_id = block["id"]
        break

print(f"Tool Stack block ID: {tool_stack_block_id}")


# ─── Step 3: Build new Architecture blocks ────────────────────────────────────
new_arch_blocks = [
    h1("Architecture: Phase-Specific Agents + n8n"),
    callout("The key insight: agents handle the intelligence, n8n handles the plumbing. No complexity where it isn't needed.", "🧠"),
    p_empty(),

    h2("The Model"),
    p("Each Fast Track phase has its own dedicated sub-agent — pre-programmed to know exactly what to extract, what schema to return, and how to flag uncertainty. The agent does the intelligent work. n8n receives clean structured output and writes it to the Excel template. That's it."),
    p_empty(),
    code_block(
        "Student uploads document (or types / speaks assumptions)\n"
        "        ↓\n"
        "[Phase Agent]          — pre-programmed for this specific phase\n"
        "                         knows the exact fields to extract\n"
        "                         returns clean JSON only (no free-form text)\n"
        "                         flags anything it can't confirm\n"
        "        ↓\n"
        "[Human Review]         — student sees extracted data before it goes anywhere\n"
        "                         approves or corrects\n"
        "        ↓\n"
        "[n8n]                  — receives the approved JSON\n"
        "                         maps fields to Excel template cells\n"
        "                         writes to the CREanalyst template\n"
        "        ↓\n"
        "[Excel Template]       — same template students already use\n"
        "                         populated, ready to work with"
    ),
    p_empty(),

    h2("Why This Architecture"),
    bullet("Simple — each agent has one job. No sprawling multi-node pipelines."),
    bullet("Teachable — students can see exactly what each agent does and why."),
    bullet("Auditable — every extraction is structured JSON with source citations. Nothing ambiguous hits the model."),
    bullet("Familiar — students keep the Excel templates they already know. AI handles the data entry layer."),
    bullet("Extensible — agents can be updated independently as templates evolve."),
    p_empty(),

    h2("The Eight Agents"),
    bullet("Phase 1 — Valuation Agent: extracts NOI, cap rate, occupancy, rent/SF, lease terms from an OM"),
    bullet("Phase 2 — Debt Agent: takes plain-language deal description, returns structured loan scenario comparison"),
    bullet("Phase 3 — Development Agent: takes voice or text assumptions, returns development pro forma inputs"),
    bullet("Phase 4 — JV Agent: reads a JV agreement, explains waterfall structure in plain language, maps tiers (v1: explanation only — full model automation is v2)"),
    bullet("Phase 5 — Capital Markets Agent: synthesizes comp data and market inputs into a structured memo draft"),
    bullet("Phase 6 — CRE System Agent: takes natural language, returns Excel formula and dashboard structure"),
    bullet("Phase 7 — Due Diligence Agent: reviews uploaded documents against standard DD checklist, flags gaps"),
    bullet("Phase 8 — Leasing Agent: extracts key lease terms and populates standard abstraction template"),
    p_empty(),

    h2("How Students Keep the Tools"),
    p("Students receive a pre-configured agent for each phase — the same way they receive the Excel templates today. Each agent is loaded with the right instructions for that phase and mapped to the CREanalyst template structure. No setup required. Open it, drop in your document, review the output."),
    p_empty(),
    p("For class use, agents run on cloud AI (Claude or ChatGPT). For professional use, the same agents can be deployed with enterprise data agreements or private infrastructure — see Agent as a Service below."),
    divider(),
]

# ─── Step 4: Append new architecture blocks BEFORE Tool Stack ────────────────
# Notion API: append children to PAGE (they go to end), or we insert after a specific block
# We'll append to the page and then the order won't be perfect — 
# Better: append after the last block before Tool Stack

# Find block just before Tool Stack
before_tool_stack = None
for i, block in enumerate(blocks):
    if block.get("id") == tool_stack_block_id and i > 0:
        before_tool_stack = blocks[i - 1]["id"]
        break

# Append to the page after that block
# Notion doesn't support insert-at-position, only append to end or as children
# Strategy: append arch blocks, then AaaS section, then note position to user
# Actually we can use the "after" parameter in blocks append — but Notion API doesn't support reordering
# Best we can do: append to page end (will be after About Will) — we'll fix ordering by
# appending in the right logical sequence: arch → tool stack → delivery → why → about will
# Since we can't reorder, let's just append everything and note the order issue

# For now: append architecture blocks to end, they'll appear after "About Will"
# Then separately we'll note this limitation. Actually, let's check if we deleted
# the arch blocks from near end and Tool Stack is still there.
# The page order should now be: ... Solution → Module-by-Module → [arch deleted] → Tool Stack → ...
# So we just need to insert before Tool Stack.

# Workaround: use "after" block ID if supported, else just append to page
# Notion DOES support after: in blocks/children PATCH you pass after block id

def append_after(page_id, after_block_id, new_blocks, chunk_size=100):
    """Append blocks after a specific block using Notion's after parameter."""
    for i in range(0, len(new_blocks), chunk_size):
        chunk = new_blocks[i:i+chunk_size]
        body = {"children": chunk}
        if after_block_id and i == 0:
            body["after"] = after_block_id
        result = api("PATCH", f"/blocks/{page_id}/children", body)
        if result:
            # Get the last block id from this chunk to chain next append
            results = result.get("results", [])
            if results:
                after_block_id = results[-1]["id"]
    return after_block_id


print("Inserting new architecture section...")
last_arch_block_id = append_after(PAGE_ID, before_tool_stack, new_arch_blocks)
print("✓ New architecture section inserted.")


# ─── Step 5: Agent as a Service section ───────────────────────────────────────
# Find "About Will" block to insert AaaS before it
blocks = get_all_blocks(PAGE_ID)
about_will_prev = None
for i, block in enumerate(blocks):
    if block.get("type") == "heading_1" and "About Will" in get_text(block):
        if i > 0:
            about_will_prev = blocks[i-1]["id"]
        break

aaas_blocks = [
    h1("Agent as a Service: The Partnership Model"),
    callout("For review — not yet included in the external-facing version of this proposal.", "🔒"),
    p_empty(),

    h2("The Opportunity"),
    p("Students who learn with these agents during Fast Track will want to keep using them when they enter the workforce. Their firms will need a version that meets institutional data and compliance standards. That gap is a business."),
    p_empty(),
    p("CREanalyst is the distribution channel. Fast Track graduates become the user base. DataGrove provides the agents, the infrastructure, and the ongoing maintenance. Revenue flows from the firms that adopt the tools at scale."),
    p_empty(),

    h2("How It Works"),
    p("The same agents students use in class are available as a professional product — with tiered security and deployment options depending on the firm's requirements."),
    p_empty(),

    h3("Tier 1 — Individual (Cloud)"),
    bullet("Who: Individual analysts and associates, recent graduates"),
    bullet("How it works: Cloud-based agents, enterprise AI contracts (data not used for training)"),
    bullet("Pricing: Monthly subscription per user"),
    bullet("Security: OpenAI Enterprise / Anthropic Claude for Enterprise data agreements"),
    p_empty(),

    h3("Tier 2 — Team / Firm (Cloud, Managed)"),
    bullet("Who: Small to mid-size CRE firms, investment teams"),
    bullet("How it works: Multi-user access, firm-level audit logs, admin controls"),
    bullet("Pricing: Per-seat subscription with firm minimum"),
    bullet("Security: Enterprise AI contracts + data isolation per firm"),
    p_empty(),

    h3("Tier 3 — Private Deployment"),
    bullet("Who: Institutional investors, REITs, large PE firms with strict data policies"),
    bullet("How it works: Agents run on the firm's own infrastructure. No data leaves their environment."),
    bullet("Pricing: Setup fee + annual maintenance contract"),
    bullet("Security: Full air-gap option. Local AI model (Llama/Mistral via Ollama) available."),
    p_empty(),

    h2("The CREanalyst Partnership Structure"),
    p("CREanalyst introduces the tools as part of Fast Track curriculum. Students experience the value firsthand. When they join firms or refer colleagues, DataGrove handles the enterprise conversation."),
    p_empty(),
    bullet("CREanalyst receives a referral fee or revenue share on any firm-level subscriptions sourced through their graduate network"),
    bullet("CREanalyst can optionally white-label the student-facing agents as a CRE Analyst product"),
    bullet("DataGrove maintains the agents, updates them as templates evolve, and handles enterprise deployments"),
    p_empty(),

    h2("Why This Works"),
    bullet("CREanalyst gets a curriculum differentiator and a new revenue stream with zero product build required"),
    bullet("DataGrove gets a direct channel into one of the best-networked CRE training programs in the country"),
    bullet("Students get tools they can actually use in their careers, not just classroom exercises"),
    bullet("Firms get a compliance-ready solution with a clear security tier that matches their risk posture"),
    p_empty(),
    callout("The pitch to CREanalyst: you trained them. We keep them sharp. We split the upside.", "🤝"),
    divider(),
]

print("Inserting Agent as a Service section...")
append_after(PAGE_ID, about_will_prev, aaas_blocks)
print("✓ Agent as a Service section inserted.")

print("\n✅ All updates complete.")
print(f"Page: https://www.notion.so/CREanalyst-AI-Augmented-Fast-Track-Proposal-317a3175c27b81b6bbc1d19f532de118")
