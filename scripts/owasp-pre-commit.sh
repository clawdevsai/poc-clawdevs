#!/usr/bin/env bash
# Wrapper: delega para ops/owasp-pre-commit.sh.
# Uso: ln -sf ../../scripts/owasp-pre-commit.sh .git/hooks/pre-commit
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
exec "$SCRIPT_DIR/ops/owasp-pre-commit.sh" "$@"
