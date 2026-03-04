#!/usr/bin/env bash
# Prepara ConfigMaps de segurança (phase2).
# Uso: ./scripts/security/configmaps.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
"$REPO_ROOT/scripts/configmaps/phase2.sh"
