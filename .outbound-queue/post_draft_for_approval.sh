#!/usr/bin/env bash
# Post a draft to the approval bot with [Approve] [Edit] [Delete] buttons.
# Zoé runs this script. This script does NOT run queue.sh send or queue.sh delete.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
QUEUE_SCRIPT="$SCRIPT_DIR/queue.sh"
CHAT_ID_FILE="$SCRIPT_DIR/approval_chat_id"
ENV_FILE="$WORKSPACE_ROOT/skills/n8n-trigger/.env"

if [[ $# -lt 1 ]]; then
  echo "Usage: $0 <draft-id>" >&2
  exit 1
fi
DRAFT_ID="$1"

if [[ ! -f "$CHAT_ID_FILE" ]]; then
  echo "Error: approval_chat_id not found. User must /start the approval bot first." >&2
  exit 1
fi
CHAT_ID=$(cat "$CHAT_ID_FILE")

if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck source=/dev/null
  source "$ENV_FILE"
  set +a
fi
if [[ -z "${TELEGRAM_APPROVAL_BOT_TOKEN:-}" ]]; then
  echo "Error: TELEGRAM_APPROVAL_BOT_TOKEN not set. Add to $ENV_FILE" >&2
  exit 1
fi

DRAFT_JSON=$("$QUEUE_SCRIPT" get "$DRAFT_ID")
if [[ -z "$DRAFT_JSON" ]]; then
  echo "Error: draft not found: $DRAFT_ID" >&2
  exit 1
fi

TYPE=$(echo "$DRAFT_JSON" | jq -r '.type')
TO=$(echo "$DRAFT_JSON" | jq -r '.payload.to')
SUBJECT=$(echo "$DRAFT_JSON" | jq -r '.payload.subject // ""')
BODY=$(echo "$DRAFT_JSON" | jq -r '.payload.body // ""')

if [[ "$TYPE" == "email" ]]; then
  TEXT="Draft $DRAFT_ID — To: $TO, Subject: $SUBJECT, Body: $BODY"
else
  TEXT="Draft $DRAFT_ID — To: $TO, Body: $BODY"
fi

# Build payload with jq so text is JSON-escaped. callback_data max 64 bytes.
PAYLOAD=$(jq -n \
  --arg chat_id "$CHAT_ID" \
  --arg text "$TEXT" \
  --arg id "$DRAFT_ID" \
  '{
    chat_id: $chat_id,
    text: $text,
    reply_markup: {
      inline_keyboard: [
        [
          { text: "Approve", callback_data: ("approve:" + $id) },
          { text: "Edit", callback_data: ("edit:" + $id) },
          { text: "Delete", callback_data: ("delete:" + $id) }
        ]
      ]
    }
  }')

curl -s -S -X POST "https://api.telegram.org/bot${TELEGRAM_APPROVAL_BOT_TOKEN}/sendMessage" \
  -H "Content-Type: application/json" \
  -d "$PAYLOAD" > /dev/null || { echo "Error: Telegram sendMessage failed" >&2; exit 1; }

echo "ok"
