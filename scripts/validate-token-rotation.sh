#!/usr/bin/env bash
# Wrapper: delega para ops/validate-token-rotation.sh.
# Uso: ./scripts/validate-token-rotation.sh
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/ops/validate-token-rotation.sh" "$@"
