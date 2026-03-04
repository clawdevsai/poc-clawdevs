#!/usr/bin/env bash
# Aplica Kanban: ConfigMap + image + k8s/kanban/.
# Uso: ./scripts/kanban/apply.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
K8S_DIR="${K8S_DIR:-$REPO_ROOT/k8s}"

"$REPO_ROOT/scripts/configmaps/kanban-api.sh"
"$REPO_ROOT/scripts/kanban/image.sh"
echo "==> Aplicando k8s/kanban/..."
kubectl apply -f "$K8S_DIR/kanban/"
echo "==> Kanban aplicado."
