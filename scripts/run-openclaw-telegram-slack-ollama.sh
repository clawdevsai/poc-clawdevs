#!/usr/bin/env bash
# Wrapper: delega para openclaw/run-openclaw-telegram-slack-ollama.sh.
# Uso: ./scripts/run-openclaw-telegram-slack-ollama.sh
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/openclaw/run-openclaw-telegram-slack-ollama.sh" "$@"
