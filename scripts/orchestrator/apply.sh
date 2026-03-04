#!/usr/bin/env bash
# Aplica orquestrador: ConfigMap + recursos em k8s/orchestrator/.
# Uso: ./scripts/orchestrator/apply.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
K8S_DIR="${K8S_DIR:-$REPO_ROOT/k8s}"

"$REPO_ROOT/scripts/orchestrator/configmap.sh"
echo "==> Aplicando k8s/orchestrator/..."
kubectl apply -f "$K8S_DIR/orchestrator/"
echo "==> Orquestrador aplicado."
