#!/usr/bin/env bash
# Wrapper: delega para ops/test_github_create_issue.sh.
# Uso: ./scripts/test_github_create_issue.sh  ou  RUN_IN_CLUSTER=1 ...  ou  CLOSE_ISSUE=1 ...
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/ops/test_github_create_issue.sh" "$@"
