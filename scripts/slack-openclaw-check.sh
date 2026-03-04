#!/usr/bin/env bash
# Wrapper: delega para ops/slack-openclaw-check.sh.
# Uso: ./scripts/slack-openclaw-check.sh
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/ops/slack-openclaw-check.sh"
