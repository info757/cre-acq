# Design Principles — Security and Constraints

This document is the default stance for all design and planning of OpenClaw, n8n, skills, and tools. Agent and human should check new skills, tools, and n8n workflows against it.

## Two Pillars

1. **Direct account takeover is off the table.** Credentials and broad access to accounts and apps live outside OpenClaw (e.g. in n8n). OpenClaw never holds Gmail, calendar, or other service tokens. Actions that touch those accounts are executed by other systems (n8n workflows) that hold the credentials; OpenClaw only triggers them with structured payloads.

2. **Misuse of automated actions is constrained by design and policy.** We limit what the agent can trigger and require approval where appropriate. We do not expose "do anything" endpoints; each exposed action is intentional and bounded.

## Three Mitigations

Whenever we add skills, tools, or n8n workflows:

1. **SOUL/AGENTS rules** — e.g. never send email or trigger sensitive workflows without Will's explicit approval. The agent proposes the action and payload and waits for confirmation before invoking.

2. **Human-approval or confirmation in n8n (or other execution layers) where possible** — e.g. workflow pauses and waits for approval before sending email or creating calendar events.

3. **Expose only skills, tools, and workflows we're comfortable the agent could trigger** — no catch-all or unbounded actions; each is scoped and auditable.

## Outbound queue (email, iMessage)

Outbound messages use a **unified queue** and **approval in Telegram**:

- Zoé adds drafts and posts them in Telegram. She sends (queue send) only when Will replies **Approve** for that draft.
- **Edit** → Zoé updates the draft and shows it again; Will can then Approve or Delete.
- **Delete** → queue delete; for email, the draft is saved to Gmail Trash (via n8n) so Will can recover. Then move on to the next draft.
- The queue is the single source of truth; the payload sent is exactly what was approved.

## Application

All new skills, tools, and n8n workflows must follow this. When in doubt, add approval and reduce scope.
