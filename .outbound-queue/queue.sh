#!/usr/bin/env bash
# Outbound queue CLI: list, add, update, get, send, delete, reject.
# Only the approval-bot callback handler may run send or delete. Zoé never runs them.
# Queue file: same dir as this script, queue.json.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
QUEUE_DIR="$SCRIPT_DIR"
QUEUE_FILE="$QUEUE_DIR/queue.json"
WORKSPACE_DIR="$(cd "$QUEUE_DIR/.." && pwd)"

# Ensure queue file exists
if [[ ! -f "$QUEUE_FILE" ]]; then
  echo '[]' > "$QUEUE_FILE"
fi

# Usage
usage() {
  echo "Usage: $0 list [--type email|imessage]"
  echo "       $0 add <type> '<payload-json>'"
  echo "       $0 update <id> '<payload-json>'"
  echo "       $0 get <id>"
  echo "       $0 send <id>"
  echo "       $0 delete <id>   (email: save to Gmail Trash via n8n if configured)"
  echo "       $0 reject <id>"
  exit 1
}

# Generate a short unique id
gen_id() {
  echo "q-$(date +%s)-$RANDOM"
}

# List items (optional filter by type). Output JSON.
cmd_list() {
  local type_filter=""
  if [[ "$1" == "--type" && -n "${2:-}" ]]; then
    type_filter="$2"
  fi
  if [[ -z "$type_filter" ]]; then
    jq -c '.' "$QUEUE_FILE"
  else
    jq -c --arg t "$type_filter" '[.[] | select(.type == $t)]' "$QUEUE_FILE"
  fi
}

# Add item. type=$1, payload=$2 (JSON string).
cmd_add() {
  local type="$1"
  local payload="$2"
  if [[ -z "$type" || -z "$payload" ]]; then
    usage
  fi
  local id
  id=$(gen_id)
  local created_at
  created_at=$(date -u +"%Y-%m-%dT%H:%M:%SZ")
  local item
  item=$(jq -n \
    --arg id "$id" \
    --arg type "$type" \
    --argjson pl "$payload" \
    --arg created "$created_at" \
    '{id: $id, type: $type, payload: $pl, status: "pending", created_at: $created}')
  jq --argjson new "$item" '. + [$new]' "$QUEUE_FILE" > "${QUEUE_FILE}.tmp" && mv "${QUEUE_FILE}.tmp" "$QUEUE_FILE"
  echo "$id"
}

# Update item by id. id=$1, payload=$2 (JSON string, merged with existing payload).
cmd_update() {
  local id="$1"
  local payload="$2"
  if [[ -z "$id" || -z "$payload" ]]; then
    usage
  fi
  local current
  current=$(jq -r --arg id "$id" '.[] | select(.id == $id) | .payload' "$QUEUE_FILE")
  if [[ -z "$current" || "$current" == "null" ]]; then
    echo "Error: draft not found: $id" >&2
    exit 1
  fi
  local merged
  merged=$(echo "$current" | jq -s --argjson upd "$payload" '.[0] * $upd')
  jq --arg id "$id" --argjson pl "$merged" 'map(if .id == $id then .payload = $pl else . end)' "$QUEUE_FILE" > "${QUEUE_FILE}.tmp" && mv "${QUEUE_FILE}.tmp" "$QUEUE_FILE"
  echo "ok"
}

# Get item by id. Output JSON.
cmd_get() {
  local id="$1"
  if [[ -z "$id" ]]; then
    usage
  fi
  jq -c --arg id "$id" '.[] | select(.id == $id)' "$QUEUE_FILE" || true
}

# Mark item sent or rejected
mark_status() {
  local id="$1"
  local status="$2"
  jq --arg id "$id" --arg s "$status" 'map(if .id == $id then .status = $s else . end)' "$QUEUE_FILE" > "${QUEUE_FILE}.tmp" && mv "${QUEUE_FILE}.tmp" "$QUEUE_FILE"
}

# Send item (approval bot only). Dispatches by type.
cmd_send() {
  if [[ "${OUTBOUND_QUEUE_APPROVAL_BOT:-}" != "1" ]]; then
    echo "Error: send may only be run by the approval bot. Add draft and use post_draft_for_approval.sh." >&2
    exit 1
  fi
  local id="$1"
  if [[ -z "$id" ]]; then
    usage
  fi
  local item
  item=$(cmd_get "$id")
  if [[ -z "$item" ]]; then
    echo "Error: draft not found: $id" >&2
    exit 1
  fi
  local type status
  type=$(echo "$item" | jq -r '.type')
  status=$(echo "$item" | jq -r '.status')
  if [[ "$status" != "pending" ]]; then
    echo "Error: draft not pending: $id (status=$status)" >&2
    exit 1
  fi

  if [[ "$type" == "email" ]]; then
    local to subject body
    to=$(echo "$item" | jq -r '.payload.to')
    subject=$(echo "$item" | jq -r '.payload.subject')
    body=$(echo "$item" | jq -r '.payload.body')
    local payload_json
    payload_json=$(jq -n --arg to "$to" --arg sub "$subject" --arg body "$body" '{to: $to, subject: $sub, body: $body}')
    ENV_FILE="$WORKSPACE_DIR/skills/n8n-trigger/.env"
    if [[ -f "$ENV_FILE" ]]; then
      set -a
      # shellcheck source=/dev/null
      source "$ENV_FILE"
      set +a
    fi
    if [[ -z "${N8N_WEBHOOK_SEND_EMAIL:-}" ]]; then
      echo "Error: N8N_WEBHOOK_SEND_EMAIL not set. Add to skills/n8n-trigger/.env" >&2
      exit 1
    fi
    local curl_out
    curl_out=$(curl -s -S -w "\n%{http_code}" -X POST -H "Content-Type: application/json" ${N8N_WEBHOOK_SECRET:+ -H "Authorization: Bearer $N8N_WEBHOOK_SECRET"} -d "$payload_json" "$N8N_WEBHOOK_SEND_EMAIL") || true
    local http_code
    http_code=$(echo "$curl_out" | tail -n1)
    if [[ "$http_code" =~ ^2[0-9][0-9]$ ]]; then
      mark_status "$id" "sent"
      echo "sent"
    else
      echo "Error: n8n webhook returned HTTP $http_code" >&2
      echo "$curl_out" | head -n -1 >&2
      exit 1
    fi
  elif [[ "$type" == "imessage" ]]; then
    local to body
    to=$(echo "$item" | jq -r '.payload.to')
    body=$(echo "$item" | jq -r '.payload.body')
    if openclaw message send --channel imessage --target "$to" --message "$body" 2>/dev/null; then
      mark_status "$id" "sent"
      echo "sent"
    else
      echo "Error: openclaw message send failed" >&2
      exit 1
    fi
  else
    echo "Error: unknown type: $type" >&2
    exit 1
  fi
}

# Delete item (approval bot only): for email, save to Gmail Trash via n8n if configured, then mark rejected.
cmd_delete() {
  if [[ "${OUTBOUND_QUEUE_APPROVAL_BOT:-}" != "1" ]]; then
    echo "Error: delete may only be run by the approval bot. Add draft and use post_draft_for_approval.sh." >&2
    exit 1
  fi
  local id="$1"
  if [[ -z "$id" ]]; then
    usage
  fi
  local item
  item=$(cmd_get "$id")
  if [[ -z "$item" ]]; then
    echo "Error: draft not found: $id" >&2
    exit 1
  fi
  local type status
  type=$(echo "$item" | jq -r '.type')
  status=$(echo "$item" | jq -r '.status')
  if [[ "$status" != "pending" ]]; then
    echo "Error: draft not pending: $id" >&2
    exit 1
  fi
  if [[ "$type" == "email" ]]; then
    ENV_FILE="$WORKSPACE_DIR/skills/n8n-trigger/.env"
    if [[ -f "$ENV_FILE" ]]; then
      set -a
      # shellcheck source=/dev/null
      source "$ENV_FILE"
      set +a
    fi
    if [[ -n "${N8N_WEBHOOK_EMAIL_TO_TRASH:-}" ]]; then
      local to subject body
      to=$(echo "$item" | jq -r '.payload.to')
      subject=$(echo "$item" | jq -r '.payload.subject')
      body=$(echo "$item" | jq -r '.payload.body')
      local payload_json
      payload_json=$(jq -n --arg to "$to" --arg sub "$subject" --arg body "$body" '{to: $to, subject: $sub, body: $body}')
      curl -s -S -X POST -H "Content-Type: application/json" ${N8N_WEBHOOK_SECRET:+ -H "Authorization: Bearer $N8N_WEBHOOK_SECRET"} -d "$payload_json" "$N8N_WEBHOOK_EMAIL_TO_TRASH" > /dev/null 2>&1 || true
    fi
  fi
  mark_status "$id" "rejected"
  echo "deleted"
}

# Reject item (mark rejected, no Gmail Trash)
cmd_reject() {
  local id="$1"
  if [[ -z "$id" ]]; then
    usage
  fi
  local item
  item=$(cmd_get "$id")
  if [[ -z "$item" ]]; then
    echo "Error: draft not found: $id" >&2
    exit 1
  fi
  mark_status "$id" "rejected"
  echo "rejected"
}

# Main
case "${1:-}" in
  list)   cmd_list "$2" "$3" ;;
  add)    cmd_add "$2" "$3" ;;
  update) cmd_update "$2" "$3" ;;
  get)    cmd_get "$2" ;;
  send)   cmd_send "$2" ;;
  delete) cmd_delete "$2" ;;
  reject) cmd_reject "$2" ;;
  *)     usage ;;
esac
