#!/usr/bin/env bash
# Wrapper: delega para utils/reset_agent_memory.sh.
# Uso: make reset-memory  ou  ./scripts/reset_agent_memory.sh [RESET_REDIS=0|RESET_REPO=0 ...]
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/utils/reset_agent_memory.sh" "$@"
