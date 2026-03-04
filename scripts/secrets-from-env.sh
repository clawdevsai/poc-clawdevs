#!/usr/bin/env bash
# Wrapper: delega para cluster/secrets-from-env.sh.
# Uso: ./scripts/secrets-from-env.sh
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/cluster/secrets-from-env.sh"
