#!/usr/bin/env python3
"""
Restructures the CRE Analyst AI Agents teaser page:
1. Deletes 'The Idea' section (redundant)
2. Moves 'Two Ways to Engage' to the top (after callout)
3. Cleans up trailing dividers and empty paragraphs
Page ID: 317a3175-c27b-81c6-8a38-f36759f03d3c
"""
import json, urllib.request, urllib.error
from pathlib import Path

API_KEY = None
for line in Path(".env").read_text().splitlines():
    if line.startswith("NOTION_API_KEY="):
        API_KEY = line.split("=",1)[1].strip()

HEADERS = {"Authorization": f"Bearer {API_KEY}", "Notion-Version": "2022-06-28", "Content-Type": "application/json"}
BASE = "https://api.notion.com/v1"
PAGE_ID = "317a3175-c27b-81c6-8a38-f36759f03d3c"

def api(method, path, body=None):
    url = f"{BASE}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"ERROR: {json.loads(e.read()).get('message')}")
        return None

def get_text(block):
    btype = block.get("type","")
    inner = block.get(btype, {})
    rt = inner.get("rich_text", [])
    return "".join(p.get("plain_text","") for p in rt)

def get_blocks():
    blocks, cursor = [], None
    while True:
        path = f"/blocks/{PAGE_ID}/children?page_size=100" + (f"&start_cursor={cursor}" if cursor else "")
        data = api("GET", path)
        if not data: break
        blocks.extend(data.get("results", []))
        if not data.get("has_more"): break
        cursor = data.get("next_cursor")
    return blocks

def delete(bid):
    api("DELETE", f"/blocks/{bid}")

def p(text):
    return {"object":"block","type":"paragraph","paragraph":{
        "rich_text":[{"type":"text","text":{"content":text}}]}}

def p_empty():
    return {"object":"block","type":"paragraph","paragraph":{"rich_text":[]}}

def h1(text):
    return {"object":"block","type":"heading_1","heading_1":{
        "rich_text":[{"type":"text","text":{"content":text}}]}}

def divider():
    return {"object":"block","type":"divider","divider":{}}


# ── Step 1: Snapshot current blocks ──────────────────────────────────────────
blocks = get_blocks()
print(f"Current blocks: {len(blocks)}")

callout_id = blocks[0]["id"]  # Keep this — it's the opener

# IDs to delete: blocks 1-7 (empty + The Idea section)
idea_ids = [blocks[i]["id"] for i in range(1, 8)]

# Two Ways to Engage content (blocks 19-25): capture text, then delete
two_ways_ids = [blocks[i]["id"] for i in range(18, 26)]  # divider + Two Ways section + closing divider

# Extra trailing dividers (blocks 31-34)
trailing_ids = [blocks[i]["id"] for i in range(31, 35)]

# Empty paragraph after bullet list (block 17)
trailing_ids.append(blocks[17]["id"])

# ── Step 2: Delete The Idea section ──────────────────────────────────────────
print("Deleting 'The Idea' section...")
for bid in idea_ids:
    delete(bid)
    print(f"  ✓ {bid[:8]}")

# ── Step 3: Delete Two Ways section (we'll re-add it at top) ─────────────────
print("Removing 'Two Ways to Engage' from current position...")
for bid in two_ways_ids:
    delete(bid)
    print(f"  ✓ {bid[:8]}")

# ── Step 4: Delete trailing clutter ──────────────────────────────────────────
print("Cleaning trailing dividers...")
for bid in trailing_ids:
    delete(bid)
    print(f"  ✓ {bid[:8]}")

# ── Step 5: Re-insert Two Ways to Engage right after callout ─────────────────
print("Inserting 'Two Ways to Engage' after callout...")

two_ways_blocks = [
    p_empty(),
    h1("Two Ways to Engage"),
    p("The first is a lighter integration woven into Fast Track as it exists today. Students get a pre-built agent for each phase and use it to handle the data entry layer on their coursework. One session takes a look inside how it works, using n8n to connect the pieces, so students leave with a working understanding of what they are using, not just that it works."),
    p_empty(),
    p("The second is a standalone course for graduates or working professionals who want to go further. Students build and deploy their own agents in a sandboxed environment, guided step by step by an Education Agent that knows where they are in the process and what usually goes wrong there. If someone gets stuck and cannot deploy in time, a working version is always available so the coursework keeps moving. The goal is that every student finishes knowing how to configure and maintain these tools, not just use them."),
    p_empty(),
    p("The two tracks can run independently or together. Happy to talk through either."),
    divider(),
]

result = api("PATCH", f"/blocks/{PAGE_ID}/children", {
    "children": two_ways_blocks,
    "after": callout_id
})
if result:
    print(f"  ✓ Two Ways section inserted after callout")

print("\n✅ Done.")
print(f"Page: https://www.notion.so/CRE-Analyst-AI-Agents-317a3175c27b81c68a38f36759f03d3c")
