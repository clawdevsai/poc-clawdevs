#!/usr/bin/env bash
# Wrapper: delega para ops/devops_compact_safe.sh.
# Uso: ./scripts/devops_compact_safe.sh < buffer.md > buffer.compact.md
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/ops/devops_compact_safe.sh" "$@"
