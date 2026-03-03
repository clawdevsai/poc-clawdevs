#!/usr/bin/env bash
# Compactação segura preservando blocos CRITERIOS_ACEITE e INVARIANTE_NEGOCIO (truncamento-finops).
# O DevOps deve usar este script (ou compact_preserve_protected.py) para higiene de buffer/memória.
# Uso: ./devops_compact_safe.sh < buffer.md > buffer.compact.md
#      ou: python app/compact_preserve_protected.py < buffer.md > buffer.compact.md
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec python3 "$SCRIPT_DIR/compact_preserve_protected.py" "$@"
