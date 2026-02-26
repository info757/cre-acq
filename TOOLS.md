# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

## Examples

```markdown
### Cameras

- living-room → Main area, 180° wide angle
- front-door → Entrance, motion-triggered

### SSH

- home-server → 192.168.1.100, user: admin

### TTS

- Preferred voice: "Nova" (warm, slightly British)
- Default speaker: Kitchen HomePod
```

## n8n

Sensitive actions (email, calendar, etc.) run via n8n. OpenClaw triggers n8n workflows via the `n8n-trigger` workspace skill; credentials (Gmail, Google Calendar, etc.) live only in n8n. Webhook URLs for each workflow live in `skills/n8n-trigger/.env`. Do not commit that file.

**send-email:** The workflow should be Webhook → Gmail only (no Wait, no form). Zoé sends only when you approve in Telegram.

## Outbound queue (Telegram approval)

- **Queue:** `.outbound-queue/queue.sh` — list, add, get, update (Zoé). send, delete only by the approval bot handler.
- **Approval bot:** Second Telegram bot. Create via BotFather, add token to `skills/n8n-trigger/.env` as `TELEGRAM_APPROVAL_BOT_TOKEN`. Start the bot (from anywhere): `~/.openclaw/workspace/.outbound-queue/run-approval-bot.sh` or from workspace `./.outbound-queue/run-approval-bot.sh`. Do /start with that bot once so it stores your chat_id. Drafts appear there with [Approve] [Edit] [Delete] buttons; only your tap triggers send/delete.
- **Post draft:** Zoé runs `.outbound-queue/post_draft_for_approval.sh <draft-id>` to show a draft in the approval bot. She never runs queue send or delete.

## Why Separate?

Skills are shared. Your setup is yours. Keeping them apart means you can update skills without losing your notes, and share skills without leaking your infrastructure.

---

Add whatever helps you do your job. This is your cheat sheet.
