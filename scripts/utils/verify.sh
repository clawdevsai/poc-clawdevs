#!/usr/bin/env bash
# Verifica hardware (máquina e GPU no cluster).
# Uso: ./scripts/utils/verify.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
DOCS_SCRIPTS="$REPO_ROOT/docs/02-infra/scripts"

if [ -f "$DOCS_SCRIPTS/verify-machine.sh" ]; then
  "$DOCS_SCRIPTS/verify-machine.sh"
else
  echo "==> verify-machine.sh não encontrado em docs/02-infra/scripts/"
fi
if [ -f "$DOCS_SCRIPTS/verify-gpu-cluster.sh" ]; then
  "$DOCS_SCRIPTS/verify-gpu-cluster.sh"
else
  echo "==> verify-gpu-cluster.sh não encontrado em docs/02-infra/scripts/"
fi
