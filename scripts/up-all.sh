#!/usr/bin/env bash
# Wrapper: delega para cluster/up-all.sh.
# Uso: ./scripts/up-all.sh
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/cluster/up-all.sh"
