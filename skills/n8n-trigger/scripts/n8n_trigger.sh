#!/usr/bin/env bash
# n8n-trigger — POST JSON payload to an n8n webhook. URLs from env or .env in skill dir.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SKILL_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
ENV_FILE="$SKILL_DIR/.env"

if [[ -f "$ENV_FILE" ]]; then
  set -a
  # shellcheck source=/dev/null
  source "$ENV_FILE"
  set +a
fi

if [[ $# -lt 2 ]]; then
  echo "Usage: $0 <workflow-name> '<json-payload>'"
  echo "Example: $0 send-email '{\"to\":\"x@y.com\",\"subject\":\"Hi\",\"body\":\"...\"}'"
  exit 1
fi

WORKFLOW_NAME="$1"
PAYLOAD="$2"

# Only the outbound-queue approval bot may trigger send-email (via queue.sh). Agent must not.
if [[ "$WORKFLOW_NAME" == "send-email" ]]; then
  echo "Error: send-email must not be triggered by the agent. Use the outbound-queue skill and the approval bot only." >&2
  exit 1
fi

# Map workflow name to env var (e.g. send-email -> N8N_WEBHOOK_SEND_EMAIL)
VAR_NAME="N8N_WEBHOOK_$(echo "$WORKFLOW_NAME" | tr 'a-z-' 'A-Z_' | tr -d ' ')"
WEBHOOK_URL="${!VAR_NAME}"

if [[ -z "$WEBHOOK_URL" ]]; then
  echo "Error: $VAR_NAME is not set. Add it to $ENV_FILE (or environment)."
  exit 1
fi

CURL_OPTS=(-s -S -X POST -H "Content-Type: application/json" -d "$PAYLOAD" "$WEBHOOK_URL")
if [[ -n "$N8N_WEBHOOK_SECRET" ]]; then
  CURL_OPTS=(-H "Authorization: Bearer $N8N_WEBHOOK_SECRET" "${CURL_OPTS[@]}")
fi

RESPONSE=$(curl "${CURL_OPTS[@]}" 2>&1)
EXIT=$?

if [[ $EXIT -ne 0 ]]; then
  echo "Error: curl failed (exit $EXIT). $RESPONSE"
  exit $EXIT
fi

echo "$RESPONSE"
