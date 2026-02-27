# MEMORY.md - Long-Term Memory

<!--
This file is your AI's curated long-term memory.
Unlike daily notes (memory/YYYY-MM-DD.md), this contains the important stuff
that should persist indefinitely.

SECURITY NOTE: This file may contain personal information.
It's only loaded in direct/main sessions with you, not in group chats.
-->

## First Awakening

- **Date:** 2026-02-26
- **AI Name:** _(fill from IDENTITY.md after first conversation)_
- **Human:** Will
- Initial setup completed

## About Will

<!-- Key facts about Will that the AI should always remember -->
<!-- This grows over time as the AI learns -->

_(To be filled in as we get to know each other)_

## Preferences & Decisions

<!-- Important decisions, preferences, and rules established over time -->

_(None yet - this section grows as we work together)_

## Lessons Learned

<!-- Things the AI has learned from mistakes or experience -->

_(None yet)_

## Important Dates

<!-- Birthdays, anniversaries, deadlines, etc. -->

_(None yet)_

## Agent HQ — Telegram Group

- **Chat ID:** -1003783443203
- **Topic 1:** General
- **Topic 2:** Code and Dev
- **Topic 3:** Research
- **Topic 4:** Content
- **Topic 5:** Automations
- Bot: @Holt_ai_bot (ID: 8453434126)
- Group policy: allowlist (only this group allowed)
- requireMention: false (responds without being tagged)

## Ongoing Projects

### Email Setup
- n8n send-email workflow working (webhook: localhost:5678)
- Approval queue live: `.outbound-queue/queue.sh`
- Approval bot: @Holt_ai_bot (second bot token in .env), run via `.outbound-queue/run-approval-bot.sh`
- Inbox reading: ideas saved in `memory/inbox-reading-ideas.md` — needs n8n workflow

## Cross-Session Memory Convention

Every version of me (DM, group topics) writes important decisions, context, and discoveries to:
- `memory/YYYY-MM-DD.md` — daily log
- `MEMORY.md` — long-term curated facts

This is how all sessions stay in sync. If it's worth remembering, write it down.
