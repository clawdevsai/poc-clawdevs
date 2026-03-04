#!/usr/bin/env bash
# Wrapper: delega para cluster/redis-streams-init.sh.
# Uso: ./scripts/redis-streams-init.sh  ou  REDIS_HOST=... REDIS_PORT=... ./scripts/redis-streams-init.sh
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/cluster/redis-streams-init.sh" "$@"
