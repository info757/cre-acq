# RESTORE.md - How to Restore This OpenClaw Instance

If you lose the Mac Mini or need to rebuild from scratch, use this as the restore checklist.

## Prerequisites

- Fresh macOS (or same machine after wipe)
- Apple ID and Gmail (infrastructure) ready
- API keys and bot tokens in password manager

## Steps

1. **Install system prerequisites**  
   Xcode CLI tools, Homebrew, Node.js 22+, pnpm. See the [OpenClaw on Mac Mini guide](https://open.substack.com/pub/robertheubanks/p/openclaw-on-mac-mini-the-complete).

2. **Install OpenClaw**  
   `curl -fsSL https://openclaw.ai/install.sh | bash`  
   Then: `openclaw onboard --install-daemon` (re-enter API keys, Telegram/Discord tokens as prompted).

3. **Restore workspace**  
   - Clone or copy this workspace repo to `~/.openclaw/workspace/` (overwriting the default workspace created by onboarding).  
   - Ensure `SOUL.md`, `MEMORY.md`, `USER.md`, `IDENTITY.md`, `AGENTS.md`, `TOOLS.md`, `HEARTBEAT.md`, and `memory/` are present.

4. **Restore config**  
   - Copy your backed-up `openclaw.json` to `~/.openclaw/openclaw.json` if you have one (or re-run `openclaw configure` for web search, etc.).  
   - Ensure `agents.defaults.heartbeat` is set (e.g. Haiku, every 1h) to avoid cost overruns.

5. **Lock permissions**  
   `chmod 700 ~/.openclaw`  
   `chmod 600 ~/.openclaw/openclaw.json`  
   `chmod -R 600 ~/.openclaw/credentials/`

6. **Verify**  
   `openclaw gateway restart`  
   `openclaw health`  
   `openclaw security audit --deep`

## Backup strategy

- **Workspace (code/config):** This directory in a private Git repo (e.g. GitHub). Push regularly.  
- **Data:** If you use databases or large data, back those up separately (e.g. Google Drive, as in the guide).  
- **openclaw.json:** Back up separately or keep in a private repo; it contains tokens and should never be committed to a public repo.

---

_Update this file when you add integrations or change restore steps._
