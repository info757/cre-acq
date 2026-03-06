#!/usr/bin/env python3
"""
Notion nightly backup — exports all accessible databases to Markdown.
Output: ~/.openclaw/workspace/notion-backups/YYYY-MM-DD/
"""

import json
import sys
import os
import urllib.request
import urllib.error
from datetime import datetime
from pathlib import Path

# Load API key
ENV_PATH = Path(__file__).parent / ".env"
API_KEY = None
if ENV_PATH.exists():
    for line in ENV_PATH.read_text().splitlines():
        if line.startswith("NOTION_API_KEY="):
            API_KEY = line.split("=", 1)[1].strip()

if not API_KEY:
    print("ERROR: NOTION_API_KEY not found in .env", file=sys.stderr)
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Notion-Version": "2022-06-28",
    "Content-Type": "application/json",
}
BASE = "https://api.notion.com/v1"
BACKUP_ROOT = Path.home() / ".openclaw/workspace/notion-backups"


def notion_request(method, path, body=None):
    url = f"{BASE}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return {"error": str(e)}


def get_title(obj):
    title_parts = obj.get("title", [])
    if isinstance(title_parts, list) and title_parts:
        return "".join(t.get("plain_text", "") for t in title_parts)
    props = obj.get("properties", {})
    for key, val in props.items():
        if val.get("type") == "title":
            rich = val.get("title", [])
            return "".join(t.get("plain_text", "") for t in rich)
    return "(untitled)"


def get_prop_value(val):
    """Extract a human-readable value from any property type."""
    t = val.get("type", "")
    if t == "title":
        return "".join(x.get("plain_text", "") for x in val.get("title", []))
    elif t == "rich_text":
        return "".join(x.get("plain_text", "") for x in val.get("rich_text", []))
    elif t == "status":
        s = val.get("status")
        return s.get("name", "") if s else ""
    elif t == "select":
        s = val.get("select")
        return s.get("name", "") if s else ""
    elif t == "multi_select":
        return ", ".join(o.get("name", "") for o in val.get("multi_select", []))
    elif t == "date":
        d = val.get("date")
        return d.get("start", "") if d else ""
    elif t == "checkbox":
        return "✓" if val.get("checkbox") else "☐"
    elif t == "number":
        n = val.get("number")
        return str(n) if n is not None else ""
    elif t == "url":
        return val.get("url") or ""
    elif t == "email":
        return val.get("email") or ""
    elif t == "phone_number":
        return val.get("phone_number") or ""
    elif t == "people":
        return ", ".join(p.get("name", "") for p in val.get("people", []))
    elif t == "formula":
        f = val.get("formula", {})
        return str(f.get(f.get("type", ""), ""))
    return ""


def backup_database(db, out_dir):
    db_id = db["id"]
    db_title = get_title(db)
    safe_name = "".join(c if c.isalnum() or c in " -_" else "_" for c in db_title).strip()
    if not safe_name:
        safe_name = db_id

    # Query all pages
    pages = []
    cursor = None
    while True:
        body = {"page_size": 100}
        if cursor:
            body["start_cursor"] = cursor
        data = notion_request("POST", f"/databases/{db_id}/query", body)
        if "error" in data:
            return f"  ⚠️  {db_title}: query failed"
        pages.extend(data.get("results", []))
        if not data.get("has_more"):
            break
        cursor = data.get("next_cursor")

    # Write markdown
    lines = [f"# {db_title}", f"*Backed up: {datetime.now().strftime('%Y-%m-%d %H:%M')}*", f"*Total: {len(pages)} items*", ""]

    for page in pages:
        title = get_title(page)
        lines.append(f"## {title or '(untitled)'}")
        lines.append(f"- **ID:** `{page['id']}`")
        lines.append(f"- **URL:** {page.get('url', '')}")
        lines.append(f"- **Created:** {page.get('created_time', '')}")
        lines.append(f"- **Edited:** {page.get('last_edited_time', '')}")

        props = page.get("properties", {})
        for key, val in props.items():
            if val.get("type") == "title":
                continue  # already shown as heading
            value = get_prop_value(val)
            if value:
                lines.append(f"- **{key}:** {value}")
        lines.append("")

    out_file = out_dir / f"{safe_name}.md"
    out_file.write_text("\n".join(lines))
    return f"  ✓  {db_title} ({len(pages)} items)"


def main():
    today = datetime.now().strftime("%Y-%m-%d")
    out_dir = BACKUP_ROOT / today
    out_dir.mkdir(parents=True, exist_ok=True)

    print(f"🗄️  Notion backup → {out_dir}")
    print(f"📅  {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

    # Get all databases
    data = notion_request("POST", "/search", {
        "filter": {"value": "database", "property": "object"},
        "page_size": 100
    })
    databases = data.get("results", [])
    print(f"Found {len(databases)} databases\n")

    results = []
    for db in databases:
        result = backup_database(db, out_dir)
        print(result)
        results.append(result)

    # Write summary
    summary = out_dir / "_summary.md"
    summary.write_text(
        f"# Notion Backup — {today}\n\n"
        f"**Databases backed up:** {len(databases)}\n\n"
        + "\n".join(results)
    )

    print(f"\n✅  Backup complete → {out_dir}")


if __name__ == "__main__":
    main()
