# OpenClaw workspace

OpenClaw workspace: skills, outbound queue, approval bot, and design docs (SOUL, AGENTS, TOOLS).

## After clone / on a new machine

1. **Secrets:** Copy `skills/n8n-trigger/.env.example` to `skills/n8n-trigger/.env` and fill in your n8n webhook URLs and `TELEGRAM_APPROVAL_BOT_TOKEN`.
2. **Approval bot:** Run `.outbound-queue/run-approval-bot.sh`, then send `/start` to the approval bot in Telegram so `approval_chat_id` is created.

See AGENTS.md, SOUL.md, and TOOLS.md for how the workspace is used.
# life_automation
# life_automation
