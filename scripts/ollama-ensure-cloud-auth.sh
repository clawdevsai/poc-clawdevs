#!/usr/bin/env bash
# Wrapper: delega para openclaw/ollama-ensure-cloud-auth.sh.
# Uso: ./scripts/ollama-ensure-cloud-auth.sh
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/openclaw/ollama-ensure-cloud-auth.sh"
