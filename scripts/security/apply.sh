#!/usr/bin/env bash
# Aplica segurança: ConfigMaps + recursos em k8s/security/.
# Uso: ./scripts/security/apply.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
K8S_DIR="${K8S_DIR:-$REPO_ROOT/k8s}"

"$REPO_ROOT/scripts/security/configmaps.sh"
echo "==> Aplicando k8s/security/..."
kubectl apply -f "$K8S_DIR/security/"
echo "==> Segurança configurada."
