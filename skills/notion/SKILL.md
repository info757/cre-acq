# Notion Skill

Manage Will's Notion workspace via the Notion API.

## Script
```
python3 ~/.openclaw/workspace/skills/notion/notion.py <command>
```

## Key Databases
| Name | ID |
|------|-----|
| Goals Tracker | 210a3175-c27b-8019-9167-fece4f7484f6 |
| Projects | 210a3175-c27b-800c-b965-e71b48fd638b |
| DataGrove.ai | 2f3a3175-c27b-8001-a173-dfc7a7c47653 |

Run `databases` to get a fresh list anytime.

## Commands

```bash
# List all databases accessible to the integration
python3 notion.py databases

# Query a database (optionally filter by status)
python3 notion.py query <db_id>
python3 notion.py query <db_id> --status "In progress"

# Add a page to a database
python3 notion.py add <db_id> "Title" --status "Not started" --notes "Optional notes"

# Update a page's status
python3 notion.py update <page_id> --status "In progress"

# Mark a page as Done
python3 notion.py complete <page_id>

# Get page details
python3 notion.py get <page_id>

# Search across workspace
python3 notion.py search "query"
```

## Safety Rules
- NEVER connect or modify portfolio pages
- ALL writes require Will's explicit approval before executing
- When in doubt, query first — never assume database structure
- Before bulk updates, query to confirm you have the right pages

## API Key
Stored in: `skills/notion/.env` (chmod 600)
Never echo or log the key.
