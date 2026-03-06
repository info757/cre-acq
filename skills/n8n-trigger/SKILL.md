---
name: n8n-trigger
description: Run deterministic actions via n8n (email, calendar, etc.). Use when the user asks to send an email, create a calendar event, or perform any action that is implemented as an n8n workflow. Do not use for general web search or file operations — use built-in tools for those.
---

# n8n-trigger

Trigger n8n workflows from OpenClaw. Sensitive actions (email, calendar, sheets, etc.) run in n8n with credentials stored only in n8n; OpenClaw never holds service tokens.

## When to use

- User asks to send an email, create a calendar event, or perform another action that you have implemented as an n8n workflow.
- Do **not** use for web search, reading files, or operations that are not exposed as n8n workflows.

## How to use

1. Build the JSON payload the n8n workflow expects (e.g. for send-email: `to`, `subject`, `body`).
2. Run the script with the **workflow name** and the **JSON payload** as the second argument.
3. Do **not** invent workflow names; only use workflows listed in "Available workflows" below or in TOOLS.md.
4. Per SOUL and DESIGN_PRINCIPLES: **Never trigger without Will's explicit approval.** Propose the action and payload; wait for confirmation before running the script.

**Email and iMessage:** Use the **outbound-queue** skill only. Add the draft, run post_draft_for_approval.sh; Will approves in the approval bot. You must **never** run n8n_trigger.sh with send-email — the script will reject it. Only the approval bot handler can trigger send-email.

**Command shape (from skill directory):**

```bash
./scripts/n8n_trigger.sh <workflow-name> '<json-payload>'
```

Example (for other workflows only — do not use send-email):

```bash
./scripts/n8n_trigger.sh some-other-workflow '{"key":"value"}'
```

The script reads webhook URLs from environment variables (or from `.env` in this skill directory). Do not put webhook URLs or secrets in SKILL.md; see TOOLS.md for where they are configured.

## Available workflows

Add workflows here as Will creates them in n8n. Each workflow name maps to an env var (e.g. `N8N_WEBHOOK_SEND_EMAIL`).

| Workflow name | Env var | Agent may trigger? |
|---------------|---------|---------------------|
| send-email    | N8N_WEBHOOK_SEND_EMAIL | **No** — only the approval bot (via queue.sh). Use outbound-queue skill. |
| email-to-trash | N8N_WEBHOOK_EMAIL_TO_TRASH | No — only queue delete uses this. |
| fetch-email   | N8N_WEBHOOK_FETCH_EMAIL | **Yes** — Zoé may trigger to fetch full email body by message ID. POST `{"messageId":"<id>"}`. Returns parsed email with `from`, `subject`, `text`, `html`, `date`, `replyTo`. |

When Will adds a new workflow in n8n, he will add the webhook URL to `skills/n8n-trigger/.env` and can add a row here.

**send-email:** Webhook → Gmail only. No Wait, no form, no approval step in n8n. The approval bot handler runs send when Will taps Approve in Telegram; Zoé never triggers send-email.

**email-to-trash:** Optional. When Will deletes an email draft, queue delete POSTs here so the draft is saved to Gmail Trash and he can recover.

## Credentials

Webhook URLs and optional secret live in `skills/n8n-trigger/.env` (gitignored). Never commit that file or paste URLs into this skill or TOOLS.md.
