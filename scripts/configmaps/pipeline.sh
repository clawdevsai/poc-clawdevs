#!/usr/bin/env bash
# Aplica todos os ConfigMaps do pipeline (PO, architect-draft, developer, revisao-slot, devops-worker, audit-runner, gateway-adapter).
# Uso: ./scripts/configmaps/pipeline.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SCRIPTS_DIR="$SCRIPT_DIR"
"$SCRIPTS_DIR/po.sh"
"$SCRIPTS_DIR/architect-draft.sh"
"$SCRIPTS_DIR/developer.sh"
"$SCRIPTS_DIR/revisao-slot.sh"
"$SCRIPTS_DIR/devops-worker.sh"
"$SCRIPTS_DIR/audit-runner.sh"
"$SCRIPTS_DIR/gateway-adapter.sh"
echo "==> ConfigMaps do pipeline aplicados."
