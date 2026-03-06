#!/usr/bin/env python3
"""
Notion CLI wrapper for Zoé — uses urllib (no extra deps).
Usage: python3 notion.py <command> [args]

Commands:
  databases                        List all accessible databases
  query <db_id> [--status <s>]     Query a database (optional status filter)
  add <db_id> <title> [--status <s>] [--notes <n>]  Add a page to a database
  update <page_id> --status <s>    Update a page's status
  get <page_id>                    Get page details
  search <query>                   Search across all pages/databases
  complete <page_id>               Mark a task as Done
"""

import json
import sys
import os
import urllib.request
import urllib.error
from pathlib import Path

# Load API key from .env in same directory
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


def notion_request(method, path, body=None):
    url = f"{BASE}{path}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(url, data=data, headers=HEADERS, method=method)
    try:
        with urllib.request.urlopen(req) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err = json.loads(e.read())
        print(f"ERROR {e.code}: {err.get('message', str(err))}", file=sys.stderr)
        sys.exit(1)


def get_title(obj):
    """Extract plain text title from a Notion object."""
    # Database object: has top-level 'title' list
    title_parts = obj.get("title", [])
    if isinstance(title_parts, list) and title_parts:
        return "".join(t.get("plain_text", "") for t in title_parts)
    # Page object: find the property of type 'title'
    props = obj.get("properties", {})
    for key, val in props.items():
        if val.get("type") == "title":
            rich = val.get("title", [])
            return "".join(t.get("plain_text", "") for t in rich)
    return "(untitled)"


def get_status(page):
    """Extract status from a page's properties."""
    props = page.get("properties", {})
    for key in ["Status", "status"]:
        if key in props:
            s = props[key]
            if s.get("type") == "status" and s.get("status"):
                return s["status"].get("name", "")
            if s.get("type") == "select" and s.get("select"):
                return s["select"].get("name", "")
    return ""


def cmd_databases():
    data = notion_request("POST", "/search", {
        "filter": {"value": "database", "property": "object"},
        "page_size": 50
    })
    print(f"{'ID':<40} {'Title'}")
    print("-" * 70)
    for r in data.get("results", []):
        title = get_title(r)
        print(f"{r['id']:<40} {title}")
    print(f"\nTotal: {len(data.get('results', []))}")


def cmd_query(db_id, status_filter=None):
    body = {"page_size": 50, "sorts": [{"timestamp": "created_time", "direction": "descending"}]}
    if status_filter:
        body["filter"] = {
            "or": [
                {"property": "Status", "status": {"equals": status_filter}},
                {"property": "Status", "select": {"equals": status_filter}},
            ]
        }
    data = notion_request("POST", f"/databases/{db_id}/query", body)
    results = data.get("results", [])
    if not results:
        print("No items found.")
        return
    print(f"{'ID':<40} {'Status':<20} {'Title'}")
    print("-" * 90)
    for r in results:
        title = get_title(r)
        status = get_status(r)
        print(f"{r['id']:<40} {status:<20} {title}")
    print(f"\nTotal: {len(results)}")


def cmd_add(db_id, title, status=None, notes=None):
    # First, find the title property name for this database
    db = notion_request("GET", f"/databases/{db_id}")
    title_prop = "Name"
    for key, val in db.get("properties", {}).items():
        if val.get("type") == "title":
            title_prop = key
            break

    props = {
        title_prop: {"title": [{"text": {"content": title}}]}
    }
    if status:
        props["Status"] = {"status": {"name": status}}
    body = {"parent": {"database_id": db_id}, "properties": props}
    if notes:
        body["children"] = [{
            "object": "block",
            "type": "paragraph",
            "paragraph": {"rich_text": [{"text": {"content": notes}}]}
        }]
    result = notion_request("POST", "/pages", body)
    print(f"✓ Created: {result['id']} — {title}")


def cmd_update(page_id, status):
    body = {"properties": {"Status": {"status": {"name": status}}}}
    result = notion_request("PATCH", f"/pages/{page_id}", body)
    title = get_title(result)
    print(f"✓ Updated '{title}' → {status}")


def cmd_complete(page_id):
    cmd_update(page_id, "Done")


def cmd_get(page_id):
    result = notion_request("GET", f"/pages/{page_id}")
    title = get_title(result)
    status = get_status(result)
    url = result.get("url", "")
    created = result.get("created_time", "")
    edited = result.get("last_edited_time", "")
    print(f"Title:   {title}")
    print(f"Status:  {status}")
    print(f"URL:     {url}")
    print(f"Created: {created}")
    print(f"Edited:  {edited}")


def cmd_search(query):
    data = notion_request("POST", "/search", {"query": query, "page_size": 20})
    results = data.get("results", [])
    if not results:
        print("No results found.")
        return
    print(f"{'Type':<12} {'ID':<40} {'Title'}")
    print("-" * 80)
    for r in results:
        obj_type = r.get("object", "")
        title = get_title(r)
        print(f"{obj_type:<12} {r['id']:<40} {title}")
    print(f"\nTotal: {len(results)}")


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        sys.exit(0)

    cmd = args[0]

    if cmd == "databases":
        cmd_databases()

    elif cmd == "query":
        if len(args) < 2:
            print("Usage: notion.py query <db_id> [--status <s>]")
            sys.exit(1)
        status = None
        if "--status" in args:
            idx = args.index("--status")
            status = args[idx + 1]
        cmd_query(args[1], status)

    elif cmd == "add":
        if len(args) < 3:
            print("Usage: notion.py add <db_id> <title> [--status <s>] [--notes <n>]")
            sys.exit(1)
        status = None
        notes = None
        if "--status" in args:
            idx = args.index("--status")
            status = args[idx + 1]
        if "--notes" in args:
            idx = args.index("--notes")
            notes = args[idx + 1]
        cmd_add(args[1], args[2], status, notes)

    elif cmd == "update":
        if len(args) < 2 or "--status" not in args:
            print("Usage: notion.py update <page_id> --status <s>")
            sys.exit(1)
        idx = args.index("--status")
        cmd_update(args[1], args[idx + 1])

    elif cmd == "complete":
        if len(args) < 2:
            print("Usage: notion.py complete <page_id>")
            sys.exit(1)
        cmd_complete(args[1])

    elif cmd == "get":
        if len(args) < 2:
            print("Usage: notion.py get <page_id>")
            sys.exit(1)
        cmd_get(args[1])

    elif cmd == "search":
        if len(args) < 2:
            print("Usage: notion.py search <query>")
            sys.exit(1)
        cmd_search(" ".join(args[1:]))

    else:
        print(f"Unknown command: {cmd}")
        print(__doc__)
        sys.exit(1)


if __name__ == "__main__":
    main()
