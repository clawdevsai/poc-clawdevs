#!/usr/bin/env bash
# Valida FinOps e validação reversa PO.
# Uso: ./scripts/utils/validate-finops-po.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
"$SCRIPT_DIR/run_validacao_finops_po.sh" "$@"
