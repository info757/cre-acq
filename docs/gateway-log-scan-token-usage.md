# Gateway log scan: hook / cron / heartbeat activity

Summary of a scan of `~/.openclaw/logs/gateway.log` for `heartbeat`, `cron`, and `hook` to see what’s actually firing and how it could affect token use.

## Heartbeat

- **What shows up:** `[heartbeat] started` at gateway startup and after each restart.
- **Behavior:** Heartbeat runs on a **per-session** schedule (e.g. every 55m from your config). The log doesn’t list every heartbeat tick per session; it only shows “heartbeat started” when the gateway process starts. So the log confirms heartbeat is enabled and the scheduler is running, not the exact count of heartbeat runs per day.
- **Token impact:** With many Telegram sessions (e.g. 6+ topics + DM), each session gets a heartbeat every 55m. That’s on the order of tens of heartbeat runs per day across all sessions. Your config uses `anthropic/claude-haiku-4-5` for heartbeat, which keeps each run relatively cheap.

## Hooks

- **What shows up:** At each gateway start you see:
  - `[hooks:loader] Registered hook: boot-md -> gateway:startup`
  - `[hooks:loader] Registered hook: bootstrap-extra-files -> agent:bootstrap`
  - `[hooks:loader] Registered hook: command-logger -> command`
  - `[hooks:loader] Registered hook: session-memory -> command:new, command:reset`
  - `[hooks] loaded 4 internal hook handlers` (or 3 if session-memory is disabled in config).
- **Behavior:** These are one-time registrations at startup. They don’t indicate a loop. `boot-md` runs at gateway startup; `bootstrap-extra-files` runs at agent bootstrap; `command-logger` runs when a command is run; `session-memory` runs on `/new` and `/reset` (and in your current config session-memory is disabled, so it may not be loaded).
- **Token impact:** No evidence of hooks firing in a tight loop. Session-memory being off avoids extra LLM calls on every session update.

## Cron

- **What shows up:** Occasional `[ws] ⇄ res ✓ cron.run` lines with duration (e.g. `cron.run 23231ms`, `cron.run 2479ms`, `cron.run 237064ms`, `cron.run 3768ms`).
- **Behavior:** Cron runs are on schedule (once per job per day for your 4 jobs). The log shows successful cron runs; it doesn’t show the “model not allowed” errors (those appear in cron job state in `cron/jobs.json` or in the cron runner’s response).
- **Token impact:** Each successful cron run is one LLM call. If the job’s `model` was ignored and the default (Sonnet) was used, each run can be 20k+ tokens. Adding `anthropic/claude-haiku-4-5` to `agents.defaults.models` (so cron is allowed to use Haiku) should fix “model not allowed” and make cron jobs use Haiku, reducing tokens per run.

## Gmail watcher

- **What shows up:** `[gmail-watcher] gmail watcher stopped` when the gateway shuts down.
- **Behavior:** Indicates a Gmail-related component is tied to the gateway lifecycle. It doesn’t show how often the Gmail trigger fires; that’s in n8n, which POSTs to the gateway. So the “loop” risk is on the n8n side (see `docs/n8n-gmail-trigger-verification.md`).

## Summary

- **No sign of a tight loop** in the gateway log (no repeated hook/cron/heartbeat lines at sub-minute frequency).
- **Heartbeat:** Enabled, per-session, 55m; config uses Haiku for heartbeat.
- **Hooks:** Registered at startup; session-memory disabled; no evidence of repeated hook-driven runs.
- **Cron:** Runs on schedule; adding Haiku to the model allowlist should fix “model not allowed” and lower tokens per cron run.
- **Gmail:** Verify in n8n that the Gmail trigger fires only on new INBOX messages (see n8n Gmail trigger verification doc).
