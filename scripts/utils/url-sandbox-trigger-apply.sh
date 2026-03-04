#!/usr/bin/env bash
# Aplica url-sandbox-trigger (ConfigMap + RBAC + deployment).
# Uso: ./scripts/utils/url-sandbox-trigger-apply.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
K8S_DIR="${K8S_DIR:-$REPO_ROOT/k8s}"

"$REPO_ROOT/scripts/configmaps/url-sandbox-trigger.sh"
kubectl apply -f "$K8S_DIR/security/url-sandbox-trigger-rbac.yaml"
kubectl apply -f "$K8S_DIR/security/url-sandbox-trigger-deployment.yaml"
echo "Opcional: kubectl create secret generic url-sandbox-trigger-secret -n ai-agents --from-literal=TRIGGER_SECRET='...'"
