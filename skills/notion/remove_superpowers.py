#!/usr/bin/env python3
"""
Remove the "Three Superpowers" section from the CREanalyst proposal page.
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
    """Extract plain text from any block type."""
    for btype in ["heading_1", "heading_2", "heading_3", "paragraph",
                  "bulleted_list_item", "callout", "code"]:
        if btype in block:
            parts = block[btype].get("rich_text", [])
            return "".join(p.get("plain_text", "") for p in parts)
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


# Get all blocks
print("Fetching blocks...")
blocks = get_all_blocks(PAGE_ID)
print(f"Total blocks: {len(blocks)}")

# Find the superpowers section
# It starts at "The Three Superpowers" h1 and ends at the next divider (which precedes "Module-by-Module")
in_superpowers = False
to_delete = []

for block in blocks:
    text = get_text(block)
    btype = block.get("type", "")

    if btype == "heading_1" and "Three Superpowers" in text:
        in_superpowers = True

    if in_superpowers:
        to_delete.append(block["id"])

    # Stop at the divider that follows the superpowers section
    # (the divider before "Module-by-Module Breakdown")
    if in_superpowers and btype == "divider" and len(to_delete) > 1:
        in_superpowers = False

print(f"\nBlocks to delete ({len(to_delete)}):")
for bid in to_delete:
    # Find the block text for display
    for b in blocks:
        if b["id"] == bid:
            print(f"  [{b.get('type')}] {get_text(b)[:60]}")

print("\nDeleting...")
for bid in to_delete:
    result = api("DELETE", f"/blocks/{bid}")
    if result:
        print(f"  ✓ Deleted {bid[:8]}...")

print(f"\n✅ Done — removed {len(to_delete)} blocks from the Superpowers section.")
