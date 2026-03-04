#!/usr/bin/env bash
# Testa acesso ao GitHub (host e/ou cluster).
# Uso: ./scripts/utils/test-github-access.sh [host|cluster|all]
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
MODE="${1:-all}"
"$SCRIPT_DIR/test_github_access.sh" "$MODE"
