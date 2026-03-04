#!/usr/bin/env bash
# Aplica apenas o Management Team (CEO, PO).
# Uso: ./scripts/openclaw/up-management.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"
K8S_DIR="${K8S_DIR:-k8s}"

echo "==> Aplicando Management Team (CEO, PO)..."
kubectl apply -f "$K8S_DIR/management-team/openclaw/workspace-ceo-configmap.yaml"
kubectl apply -f "$K8S_DIR/management-team/configmap.yaml"
kubectl apply -f "$K8S_DIR/management-team/deployment.yaml"
echo "==> up-management concluído. Scale openclaw a 0 se usar dois gateways."
