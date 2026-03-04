#!/usr/bin/env bash
# Wrapper: delega para ops/validate_reverse_po_after_summary.sh.
# Uso: ./scripts/validate_reverse_po_after_summary.sh RESUMO.md CRITERIOS.md
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/ops/validate_reverse_po_after_summary.sh" "$@"
