#!/usr/bin/env bash
# Wrapper: delega para ops/ciso_local_scan.sh.
# Uso: ./scripts/ciso_local_scan.sh [--fix]
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/ops/ciso_local_scan.sh" "$@"
