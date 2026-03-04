#!/usr/bin/env bash
# Wrapper para reset de memória dos agentes.
# Uso: ./scripts/utils/reset-memory.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
"$SCRIPT_DIR/reset_agent_memory.sh"
