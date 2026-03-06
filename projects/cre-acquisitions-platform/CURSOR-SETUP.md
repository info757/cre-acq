# Cursor ↔ Zoé Setup

## What this does
Points Cursor's AI at Zoé (via OpenClaw's OpenAI-compatible endpoint) so you're
talking to the same AI with the same memory and project context — not a generic model.

## OpenClaw endpoint details
- **URL:** `http://127.0.0.1:18789/v1/chat/completions`
- **API Key (bearer token):** `ee8e618f1c6cfb83ea5fb11536b61434be8ac6baf045d758`
- **Model:** `openclaw:main`

## Cursor setup steps

### 1. Open this workspace in Cursor
File → Open Folder → `/Users/willholt/.openclaw/workspace`

### 2. Add OpenClaw as a custom model
Cursor Settings (Cmd+Shift+J) → Models → Add Model:
- **Provider:** OpenAI-compatible
- **Base URL:** `http://127.0.0.1:18789/v1`
- **API Key:** (token above)
- **Model name:** `openclaw:main`

### 3. Set as default for this project (optional)
In `.cursor/settings.json` at the workspace root:
```json
{
  "defaultModel": "openclaw:main"
}
```

### 4. Cursorignore is already set
`.cursorignore` in this project dir blocks .env files and credentials from
being included in AI context. Don't remove it.

## How to use
- Open any file in the workspace, ask Cursor a question → it routes to Zoé
- Zoé has the same memory, specs, and project context as in Telegram
- For code-heavy work, use Cursor. For planning/research, use Telegram.
  Either way it's the same brain.

## Note
This endpoint is localhost-only. The gateway must be running for it to work.
Check: `openclaw gateway status`
