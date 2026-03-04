#!/usr/bin/env bash
# Compactação segura preservando blocos CRITERIOS_ACEITE e INVARIANTE_NEGOCIO (truncamento-finops).
# Uso: ./scripts/ops/devops_compact_safe.sh < buffer.md > buffer.compact.md
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
exec python3 "$REPO_ROOT/app/features/compact_preserve_protected.py" "$@"
