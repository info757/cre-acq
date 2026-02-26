---
name: outbound-queue
description: Manage the outbound message queue (email and iMessage). Add drafts and post them for approval via the approval bot. You never run queue send or queue delete.
---

# outbound-queue

Drafts live in the queue. You add, update, list, and get them. To show a draft for approval you run the post-draft script. Only the approval button handler can send or delete; you must never run `queue.sh send` or `queue.sh delete`.

## When to use

- Will asks to draft an email or iMessage, or to add something to the queue.
- You add the draft with `queue.sh add`, then **immediately** run `post_draft_for_approval.sh <id>` so Will sees the draft in the **Telegram approval bot** chat with [Approve] [Edit] [Delete] buttons. There is no form in n8n; approval is only in that approval bot.
- When Will taps **Edit**, he will reply in the main chat with edit instructions; you run `queue.sh update <id> '...'` then run `post_draft_for_approval.sh <id>` again. You never run send or delete.

## Queue script (you may only use these)

From the **workspace root**:

```bash
.outbound-queue/queue.sh list [--type email|imessage]
.outbound-queue/queue.sh add <type> '<payload-json>'
.outbound-queue/queue.sh get <id>
.outbound-queue/queue.sh update <id> '<partial-payload-json>'
```

You must never run `queue.sh send` or `queue.sh delete`. Only the Telegram approval button handler can.

## Post draft for approval

To show a draft so Will can tap Approve, Edit, or Delete:

```bash
.outbound-queue/post_draft_for_approval.sh <draft-id>
```

Run this after adding a draft (use the id returned by `queue.sh add`). After Will taps Edit and replies with instructions, run `queue.sh update <id> '...'` then run this script again with the same id.

## Payload shapes

- **email:** `{"to":"addr@example.com","subject":"...","body":"..."}`
- **imessage:** `{"to":"+1234567890 or handle","body":"..."}`

## Flow (no n8n form)

1. Add draft: `queue.sh add email '{"to":"...","subject":"...","body":"..."}'` → note the id.
2. **Right away** run `post_draft_for_approval.sh <id>`. Will sees the draft in the **approval bot** Telegram chat with [Approve] [Edit] [Delete]. There is no n8n form; do not tell Will to use n8n for approval.
3. Will taps Approve or Delete in the approval bot → the handler runs send or delete. You do nothing.
4. If Will taps Edit, he will reply in the main chat with what to change. You run `queue.sh update <id> '...'` then `post_draft_for_approval.sh <id>` again.

## Related

- n8n-trigger: send-email and email-to-trash are called by queue.sh when the approval handler runs send/delete. You never run send or delete.
