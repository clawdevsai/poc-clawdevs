#!/usr/bin/env bash
# Wrapper: delega para utils/run_validacao_finops_po.sh.
# Uso: ./scripts/run_validacao_finops_po.sh [--skip-tests]
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/utils/run_validacao_finops_po.sh" "$@"
