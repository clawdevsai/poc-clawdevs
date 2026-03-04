#!/usr/bin/env bash
# Wrapper: delega para utils/test_github_access.sh.
# Uso: ./scripts/test_github_access.sh [host|cluster|all]
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/utils/test_github_access.sh" "$@"
