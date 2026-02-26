#!/usr/bin/env bash
# Start the approval bot. Run from anywhere (uses script dir to find workspace).
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WORKSPACE_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$WORKSPACE_ROOT"
exec node "$SCRIPT_DIR/approval-bot/server.js"
