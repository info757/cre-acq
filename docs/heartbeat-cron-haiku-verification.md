# Heartbeat & cron Haiku verification

**Conclusion: Config is correct. Heartbeat and cron are set to use Haiku, and Haiku is on the allowlist. If you restarted the gateway after adding Haiku, they should be using it. The low Haiku token count fits that heartbeat/cron are a small share of total traffic.**

---

## 1. Heartbeat

| Check | Status |
|-------|--------|
| `agents.defaults.heartbeat.model` | `"anthropic/claude-haiku-4-5"` ✓ |
| `anthropic/claude-haiku-4-5` in `agents.defaults.models` | Present ✓ |

So heartbeat is configured to use Haiku and the gateway is allowed to use that model. No fallback to Sonnet in config.

---

## 2. Cron jobs

| Job | Payload `model` | In allowlist? | Last run |
|-----|------------------|---------------|----------|
| Morning Big 3 Check-in | `anthropic/claude-haiku-4-5` | Yes | Error: "model not allowed" (before Haiku was added) |
| Evening Review | `anthropic/claude-haiku-4-5` | Yes | OK (3991 ms) |
| Nightly Notion Backup | `anthropic/claude-haiku-4-5` | Yes | Error: "model not allowed" (before Haiku was added) |
| Nightly Memory Write | `anthropic/claude-haiku-4-5` | Yes | Error: "cron announce delivery failed" (ran 44s then delivery failed) |

All four jobs request Haiku. Haiku is in `agents.defaults.models`, so the "model not allowed" errors on Morning Big 3 and Nightly Notion Backup should stop after a gateway restart (those errors were from before Haiku was added to the allowlist). Evening Review was already succeeding; with the allowlist fixed, it should be using Haiku.

---

## 3. Why only ~300k Haiku tokens?

- Heartbeat runs once per 55m **per session**. With a handful of sessions, that’s on the order of tens of heartbeat runs per day, each with a small prompt and short reply → tens or low hundreds of thousands of Haiku tokens per day is plausible.
- Cron: 4 jobs, each at most once per day, and some were failing. So cron adds at most a small amount of Haiku usage.
- So the vast majority of your 31M tokens is **chat** (Telegram) on the **primary model** (Sonnet). That matches “only 300k Haiku.”

---

## 4. How to confirm in practice

- **Restart gateway** (if you haven’t since adding Haiku):  
  `openclaw gateway restart`  
  Then let one cron run (e.g. Evening Review at 8pm) and optionally check after a heartbeat.
- **Usage by model:**  
  In Anthropic (or your provider) usage dashboard, filter by model. You should see:
  - Most tokens: `claude-sonnet-4-6` (chat).
  - A much smaller amount: `claude-haiku-4-5` (heartbeat + cron).
- **OpenClaw:**  
  `openclaw status --usage` (if it breaks down by model) or gateway logs for a specific heartbeat/cron run to see which model was actually called.

Config is consistent with heartbeat and cron using Haiku; the token split you see fits that they’re a small fraction of total usage.
