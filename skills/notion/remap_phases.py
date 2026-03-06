#!/usr/bin/env python3
"""
Replaces the Module-by-Module and Eight Agents sections with the actual
7 Fast Track phases from CREanalyst.
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


def append_after(page_id, after_block_id, new_blocks, chunk_size=100):
    for i in range(0, len(new_blocks), chunk_size):
        chunk = new_blocks[i:i+chunk_size]
        body = {"children": chunk}
        if after_block_id and i == 0:
            body["after"] = after_block_id
        result = api("PATCH", f"/blocks/{page_id}/children", body)
        if result:
            results = result.get("results", [])
            if results:
                after_block_id = results[-1]["id"]
    return after_block_id


# ─── Step 1: Fetch all blocks ─────────────────────────────────────────────────
print("Fetching blocks...")
blocks = get_all_blocks(PAGE_ID)
print(f"Total blocks: {len(blocks)}")


# ─── Step 2: Delete Module-by-Module section ──────────────────────────────────
in_section = False
to_delete = []
anchor_before = None  # block just before "Module-by-Module"

for i, block in enumerate(blocks):
    text = get_text(block)
    btype = block.get("type","")

    if btype == "heading_1" and "Module-by-Module" in text:
        in_section = True
        if i > 0:
            anchor_before = blocks[i-1]["id"]

    if in_section:
        to_delete.append(block["id"])

    if in_section and btype == "divider" and len(to_delete) > 1:
        in_section = False

print(f"Deleting {len(to_delete)} Module-by-Module blocks...")
for bid in to_delete:
    api("DELETE", f"/blocks/{bid}")
print("✓ Module-by-Module section removed.")


# ─── Step 3: Delete Eight Agents list from Architecture section ───────────────
# Re-fetch after deletion
blocks = get_all_blocks(PAGE_ID)
in_agents = False
agents_to_delete = []

for block in blocks:
    text = get_text(block)
    btype = block.get("type","")

    if btype == "heading_2" and "Eight Agents" in text:
        in_agents = True

    if in_agents:
        agents_to_delete.append(block["id"])

    # Stop at next h2 or divider
    if in_agents and (btype in ["heading_2","divider"]) and len(agents_to_delete) > 1:
        # Don't delete the stopping block
        agents_to_delete.pop()
        in_agents = False

print(f"Deleting {len(agents_to_delete)} old agent list blocks...")
for bid in agents_to_delete:
    api("DELETE", f"/blocks/{bid}")
print("✓ Old Eight Agents section removed.")


# ─── Step 4: Build new Module-by-Module section (7 real phases) ───────────────
new_modules = [
    h1("Module-by-Module Breakdown"),
    p("The 7 Fast Track phases, each mapped to a purpose-built AI agent:"),
    p_empty(),

    h3("Phase 1 — CRE System and Capital Markets"),
    p("AI Workflow: Natural language or data → deal tracking dashboard + market analysis memo"),
    bullet("Agent builds an Excel deal tracking structure from plain-language description (deal name, asset type, stage, NOI, yield, contact)"),
    bullet("Agent synthesizes market comp data into a structured capital markets memo — supply/demand dynamics, cap rate trends, buyer profiles"),
    bullet("Students learn to use AI as a formula engine and research synthesizer"),
    p_empty(),

    h3("Phase 2 — Commercial Leases"),
    p("AI Workflow: Lease document → structured abstraction table"),
    bullet("Agent extracts base rent, rent escalations, lease term, TI allowance, options, co-tenancy clauses, and exclusivity provisions"),
    bullet("Output populates the CREanalyst lease abstraction template"),
    bullet("Multiple leases processed and compared side by side"),
    bullet("Lease abstraction is one of the most proven AI use cases in CRE — direct day-one value for students entering the workforce"),
    p_empty(),

    h3("Phase 3 — Valuation and Return Measures"),
    p("AI Workflow: Deal document → valuation model inputs"),
    bullet("Agent extracts NOI, in-place cap rate, occupancy, rent/SF, lease term summary, and operating expense assumptions from an OM or broker package"),
    bullet("Validated output populates the valuation and return model (unlevered IRR, equity multiple, cap rate)"),
    bullet("Agent flags any figures it cannot confirm with a source citation — student reviews before anything hits the model"),
    p_empty(),

    h3("Phase 4 — Acquisitions and Due Diligence"),
    p("AI Workflow: Due diligence documents → checklist population and issue flagging"),
    bullet("Agent reviews uploaded DD documents against a standard checklist"),
    bullet("Marks completed items, summarizes key findings, flags gaps or missing items"),
    bullet("v1 scope: one document type at a time (e.g. title report, survey, or environmental)"),
    bullet("v2: multi-document cross-reference and consolidated risk summary"),
    p_empty(),

    h3("Phase 5 — Debt"),
    p("AI Workflow: Natural language deal description → loan comparison table"),
    bullet("Student describes a deal and financing parameters in plain text"),
    bullet("Agent returns structured loan scenarios across LTV, rate, and amortization variables"),
    bullet("Output populates a debt comparison template — coverage ratios, debt yield, cash-on-cash"),
    bullet("Cleanest build in the curriculum — loan math is deterministic, easy to validate"),
    p_empty(),

    h3("Phase 6 — CRE Development"),
    p("AI Workflow: Voice or text assumptions → development pro forma inputs"),
    bullet("Student dictates or types a development scenario (unit count, avg SF, rent assumptions, construction cost, stabilized cap rate)"),
    bullet("Agent structures the inputs and populates the development pro forma (construction budget, equity/debt stack, stabilized yield, return measures)"),
    bullet("Voice workflow: record a site tour memo, return to a draft pro forma"),
    p_empty(),

    h3("Phase 7 — Joint Ventures"),
    p("AI Workflow: JV agreement → waterfall explanation and model mapping"),
    bullet("Agent reads a JV agreement excerpt and identifies the waterfall structure"),
    bullet("Explains each tier in plain language — preferred return, promote thresholds, catch-up provisions"),
    bullet("v1: AI-assisted understanding and explanation. Students learn to read the structure with AI support."),
    bullet("v2: Full waterfall model mapping (JV structures vary too significantly for reliable automation at v1)"),
    divider(),
]


# ─── Step 5: Build new Seven Agents section (for Architecture) ────────────────
new_agents = [
    h2("The Seven Agents"),
    bullet("Phase 1 — CRE System + Capital Markets Agent: builds deal tracking dashboard from natural language; synthesizes market data into memo"),
    bullet("Phase 2 — Leasing Agent: extracts key lease terms, populates standard abstraction template, enables multi-lease comparison"),
    bullet("Phase 3 — Valuation Agent: extracts NOI, cap rate, occupancy, rent/SF, and expense data from OM; populates valuation and return model"),
    bullet("Phase 4 — Acquisitions & DD Agent: reviews DD documents against standard checklist, flags gaps and summarizes findings"),
    bullet("Phase 5 — Debt Agent: takes plain-language deal description, returns structured loan scenario comparison table"),
    bullet("Phase 6 — Development Agent: takes voice or text assumptions, returns development pro forma inputs"),
    bullet("Phase 7 — JV Agent: reads JV agreement, explains waterfall structure in plain language; v1 explanation only, v2 model mapping"),
    p_empty(),
]


# ─── Step 6: Insert new modules where old ones were ───────────────────────────
# Re-fetch blocks to find current anchor point
blocks = get_all_blocks(PAGE_ID)

# Find anchor: block before Architecture h1
arch_prev = None
for i, block in enumerate(blocks):
    if block.get("type") == "heading_1" and "Architecture" in get_text(block):
        if i > 0:
            arch_prev = blocks[i-1]["id"]
        break

print(f"Inserting new Module-by-Module section before Architecture...")
last_id = append_after(PAGE_ID, arch_prev, new_modules)
print("✓ New Module-by-Module section inserted.")


# ─── Step 7: Insert Seven Agents into Architecture section ────────────────────
# Re-fetch and find "Why Each Step Matters" h2 (insert Seven Agents after "How Students Keep the Tools" section)
blocks = get_all_blocks(PAGE_ID)
students_keep_prev = None
for i, block in enumerate(blocks):
    if block.get("type") == "heading_2" and "How Students Keep" in get_text(block):
        # Find the next divider after this
        for j in range(i+1, len(blocks)):
            if blocks[j].get("type") == "divider":
                students_keep_prev = blocks[j-1]["id"]
                break
        break

if students_keep_prev:
    print(f"Inserting Seven Agents section...")
    append_after(PAGE_ID, students_keep_prev, new_agents)
    print("✓ Seven Agents section inserted.")
else:
    print("WARNING: Could not find insertion point for Seven Agents — appending to page end.")
    api("PATCH", f"/blocks/{PAGE_ID}/children", {"children": new_agents})

print("\n✅ All updates complete.")
print(f"Page: https://www.notion.so/CREanalyst-AI-Augmented-Fast-Track-Proposal-317a3175c27b81b6bbc1d19f532de118")
