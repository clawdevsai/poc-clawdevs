#!/usr/bin/env bash
# Wrapper: delega para openclaw/ollama-signin.sh.
# Uso: ./scripts/ollama-signin.sh
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/openclaw/ollama-signin.sh"
