#!/usr/bin/env python3
"""
Scans the CREanalyst proposal page for em dashes and replaces them
with commas or rewrites the phrase per Will's grammar preferences.
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

EM = "\u2014"  # —


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


def clean(text):
    """Replace em dashes with commas or clean phrasing."""
    if EM not in text:
        return text
    # " — " (spaced em dash) → ", "
    text = text.replace(f" {EM} ", ", ")
    # Any remaining em dashes
    text = text.replace(EM, ", ")
    return text


def fix_rich_text(rich_text_list):
    changed = False
    for part in rich_text_list:
        if part.get("type") == "text":
            original = part["text"]["content"]
            fixed = clean(original)
            if fixed != original:
                part["text"]["content"] = fixed
                changed = True
        # Also fix plain_text if present (read-only in Notion but clean for safety)
    return changed


BLOCK_TYPES = [
    "heading_1", "heading_2", "heading_3",
    "paragraph", "bulleted_list_item", "numbered_list_item",
    "callout", "quote", "code"
]

print("Fetching blocks...")
blocks = get_all_blocks(PAGE_ID)
print(f"Total blocks: {len(blocks)}")

fixed_count = 0

for block in blocks:
    btype = block.get("type")
    if btype not in BLOCK_TYPES:
        continue

    inner = block.get(btype, {})
    rich_text = inner.get("rich_text", [])

    if fix_rich_text(rich_text):
        # Patch the block
        patch_body = {btype: {"rich_text": rich_text}}
        result = api("PATCH", f"/blocks/{block['id']}", patch_body)
        if result:
            # Show what was fixed
            plain = "".join(p.get("text", {}).get("content", "") for p in rich_text)
            print(f"  ✓ Fixed [{btype}]: {plain[:70]}...")
            fixed_count += 1

print(f"\n✅ Done. Fixed {fixed_count} blocks with em dashes.")
