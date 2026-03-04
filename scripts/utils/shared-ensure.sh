#!/usr/bin/env bash
# Garante que o mount /agent-shared está ativo; se não, inicia.
# Uso: ./scripts/utils/shared-ensure.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

if pgrep -x minikube >/dev/null 2>&1 && grep -q "Successfully mounted" ~/minikube-mount.log 2>/dev/null; then
  echo "  Mount /agent-shared já está ativo."
else
  echo "  Mount /agent-shared não encontrado. Iniciando..."
  "$REPO_ROOT/scripts/utils/shared.sh"
fi
