# OpenClaw community token reduction (Discord-adjacent)

*Compiled from Rezha Julio, OpenClaw Pulse, Learn OpenClaw, ClawHosters, and similar community guides. Discord wasn’t queried directly; these are the strategies those sources and forums consistently recommend.*

---

## Where your tokens go (community breakdown)

| Category | Share of cost | What to do |
|----------|----------------|------------|
| **Context accumulation** | 40–50% | History limits, compaction, `/clear` / `/new` often |
| **Tool output** | 20–30% | Pruning (cache-TTL), trim tool results, avoid huge reads |
| **System prompt** | 10–15% | Shorter SOUL.md, AGENTS.md, fewer/smaller bootstrap files |
| **Heartbeats** | Significant | Longer interval, cheaper model, slim HEARTBEAT.md, or disable |
| **Cron / scheduled** | Depends | Use Haiku/Flash for cron; restrict to useful hours |
| **Multi-round / thinking** | 10–15% | Fewer rounds per task; watch thinking token usage |

---

## 1. Heartbeat (biggest “silent” lever)

- **Increase interval**  
  You’re at 55m; community often suggests **60m or 2h** if you don’t need frequent check-ins. Each doubling roughly halves heartbeat token use.
- **Use a cheap model**  
  You already use `anthropic/claude-haiku-4-5` for heartbeat; keep it. Don’t use Sonnet/Opus for heartbeat.
- **Slim HEARTBEAT.md**  
  It’s read on every heartbeat. Keep it to a few bullets (e.g. “Ensure memory/YYYY-MM-DD.md exists; check DMs if due”). Move recurring tasks to **cron** instead of HEARTBEAT.md so they run in isolated, low-context sessions.
- **Option: disable heartbeat**  
  If you’re mostly cron + webhooks + when-you-message, set `heartbeat.enabled: false` and avoid background token burn. Agent still wakes for cron, webhooks, and direct messages.

---

## 2. Model routing (same idea as “tiered model” in Discord)

- **Primary (Sonnet)** for real conversation and hard tasks.
- **Haiku (or Flash / mini)** for: heartbeats, cron, sub-agents, simple classification, “anything that doesn’t need Sonnet.”
- Community reports: routing cheap tasks to cheap models is the single biggest cost cut (often 50–80%). You’ve added Haiku to the allowlist for cron; ensure every cron job that can use Haiku actually specifies it in the payload.

---

## 3. System prompt and bootstrap

- **Shorten SOUL.md / AGENTS.md**  
  Every line is sent on every call. Aim for “under 2,000 tokens” for SOUL; cut redundancy and long examples.
- **Conditional / on-demand context**  
  Prefer “agent reads file when needed” over “inject huge file into every prompt.” Keep bootstrap and skill list lean.
- **bootstrapMaxChars / bootstrapTotalMaxChars**  
  If you have large workspace files, consider lowering these (e.g. 16k / 120k) so less is auto-injected.

---

## 4. Context and history

- **History limits**  
  You already have Telegram `historyLimit: 20`, `dmHistoryLimit: 30`, and `groupChat.historyLimit: 20`. Good. If usage is still high, try 10–15 for a few days and see.
- **Compaction**  
  You have `safeguard` with `reserveTokensFloor` and `keepRecentTokens`. Ensure compaction is actually running (check `/status` for compaction count). Use `/compact` on heavy sessions.
- **Session reset**  
  Use `/clear` or `/new` when switching topics or finishing a long thread so the next conversation doesn’t carry 50k+ tokens of history.

---

## 5. Cron and scheduled work

- **Cheap model only**  
  All cron jobs should use Haiku (or Flash/mini) unless there’s a strong reason not to. You added Haiku to the allowlist; confirm each job’s `model` is set and that the runner respects it.
- **Fewer runs**  
  If something runs every hour “just in case,” consider 2–3x/day or only during hours you care (e.g. 8am–10pm).
- **One batched cron vs many**  
  One “morning briefing” cron that does weather + calendar + email is cheaper than three separate crons doing the same.

---

## 6. Gmail / inbound triggers

- **One run per event**  
  Ensure the n8n Gmail trigger fires only on *new* INBOX messages (label filter `INBOX`), not on drafts or label changes. See `docs/n8n-gmail-trigger-verification.md`.
- **Throttle or filter**  
  If you get a lot of mail, filter in n8n (e.g. only unread, or only certain senders) before POSTing to OpenClaw so you don’t start an agent run for every single email.

---

## 7. Monitoring and guardrails

- **See where tokens go**  
  Use `openclaw status --usage`, `/context detail`, `/usage cost`, and gateway logs. Focus on: heartbeat, cron, hook sessions, and the heaviest chat sessions.
- **Timeouts**  
  Set timeouts on automated tasks so a stuck loop can’t burn unbounded tokens.
- **Spend alerts**  
  Set Anthropic/OpenAI/Google spend alerts at 50% and 80% of your monthly budget.

---

## 8. Community “nuclear” options (if you’re still way over)

- **Disable heartbeat**  
  `heartbeat.enabled: false` — no periodic check-ins; only cron, webhooks, and your messages.
- **Run heartbeats less often**  
  e.g. `every: "2h"` or `"4h"`.
- **Local model for routine work**  
  Use Ollama (or similar) for simple Q&A and file ops; keep cloud models for conversation and hard tasks.
- **Fewer sessions**  
  Fewer Telegram topics or channels means fewer sessions, each with their own heartbeat and history.

---

## Summary checklist

- [ ] Heartbeat: 60m or 2h; keep Haiku; slim HEARTBEAT.md; or disable.
- [ ] Cron: every job uses Haiku (or cheapest acceptable model); add to allowlist (done); consider fewer runs or batched jobs.
- [ ] System prompt: shorten SOUL/AGENTS; smaller bootstrap caps if needed.
- [ ] History: keep limits (20/30); use `/compact` and `/clear`/`/new` often.
- [ ] Gmail trigger: INBOX only; verify in n8n; throttle/filter if high volume.
- [ ] Monitor: `openclaw status --usage`, `/context detail`, `/usage cost`; set provider spend alerts.

These are the same levers the community (including Discord-adjacent posts and guides) consistently recommends. Applying them should get you into the “$15–40/month” band unless you’re running very heavy 24/7 automation.
