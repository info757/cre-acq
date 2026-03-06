# n8n Gmail trigger verification (reduce token use)

When the Gmail trigger fires, n8n POSTs to OpenClaw’s hooks URL and starts one full agent run per event. If it fires too often (wrong filters or polling), token use goes up. Use this checklist to confirm it’s not firing in a loop or on every Gmail event.

## 1. Open the workflow in n8n

- Open n8n (e.g. http://localhost:5678).
- Find the workflow that sends email notifications to Zoé (the one that uses the Gmail trigger and POSTs to `OPENCLAW_HOOKS_URL` / `http://127.0.0.1:18789/hooks/agent`).

## 2. Check the Gmail trigger node

- Click the **Gmail trigger** node (first node in the flow).
- **Trigger type:** It should be “New Email” or “Email received” (one event per new message), not “On interval” or “Every X minutes” for the same mailbox without a “new message” condition.
- **Filters / Labels:**
  - Confirm **Label IDs** (or equivalent) is set to **`INBOX`** only: `["INBOX"]`.
  - This avoids firing on draft saves, sent mail, or other labels. Drafts use `DRAFT`, not `INBOX`.
- **Polling interval (if applicable):** If the trigger polls (e.g. “Check every 5 min”), that’s normal, but each **new** message should produce **one** run. If you see “Check every 10 sec” or very short intervals, consider 1–5 minutes to reduce load.

## 3. Confirm it’s not firing on other events

- In the trigger config, ensure you’re not listening to “All mail” or “Message updated” or “Label changed” unless you intend to. For “new email to Zoé,” you want **new message in INBOX only**.
- If the node has a “Simple” or “Full” mode, “Simple” is usually enough (subject, from, snippet). Full mode can make payloads (and downstream agent context) larger.

## 4. Check recent executions in n8n

- In n8n, open **Executions** (or **History**).
- Filter by the Gmail → OpenClaw workflow.
- Look at the last 24–48 hours: **how many executions** do you see?
  - Rough sanity check: if you get ~10–50 emails/day, you’d expect on the order of 10–50 runs/day for that workflow. If you see hundreds or thousands, the trigger or filters are likely wrong (e.g. firing on every poll instead of only on new message, or no INBOX filter).

## 5. Optional: narrow who can trigger the agent

- To cut token use further, you can add a filter in n8n **after** the Gmail node (e.g. “Only unread” or “Only from these senders”) so only some emails invoke OpenClaw.
- Or temporarily disable the workflow in n8n and see how much your OpenClaw token usage drops; that confirms this flow is a major contributor.

## Summary

- **Goal:** One agent run per new email in INBOX, not per draft, not per label change, not per short poll.
- **Key setting:** Gmail trigger **Label IDs = `["INBOX"]`**, and trigger type = new message / email received.
- **Re-check after changes:** Restart or save the workflow, then watch n8n Executions and OpenClaw usage for a few hours.
