#!/usr/bin/env bash
# Wrapper: delega para ops/first-aid-gpu.sh.
# Uso: ./scripts/first-aid-gpu.sh [--phase 1|2|3]
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/ops/first-aid-gpu.sh" "$@"
