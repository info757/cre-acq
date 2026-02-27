# Inbox Reading — Ideas for Later

## Goal
Give Zoé access to Will's Gmail inbox so she can flag important emails.

## n8n side (Will builds)
- Schedule Trigger (e.g. every 15 min) OR Gmail Trigger (fires on new email)
- Gmail node — fetch unread emails (subject, sender, body snippet)
- HTTP Request node — POST email data to an OpenClaw webhook

## OpenClaw side
- New webhook endpoint to receive the email data
- Zoé summarizes and pings Will in Telegram with anything important

## Flow
Schedule Trigger → Gmail (get messages) → HTTP Request → OpenClaw webhook

## Notes
- Gmail credential likely already configured in n8n
- Simple first version: poll every 15 min, flag anything urgent
- Zoé needs a new n8n workflow entry + webhook URL in skills/n8n-trigger/.env
