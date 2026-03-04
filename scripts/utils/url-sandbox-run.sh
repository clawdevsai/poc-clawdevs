#!/usr/bin/env bash
# Dispara job url-sandbox com URL alvo. Uso: URL=https://exemplo.com ./scripts/utils/url-sandbox-run.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
K8S_DIR="${K8S_DIR:-$REPO_ROOT/k8s}"

if [ -z "${URL:-}" ]; then
  echo "Uso: make url-sandbox-run URL=https://exemplo.com"
  echo "  ou: URL=https://exemplo.com ./scripts/utils/url-sandbox-run.sh"
  exit 1
fi

"$REPO_ROOT/scripts/configmaps/url-sandbox.sh"
kubectl patch configmap security-config -n ai-agents -p '{"data":{"URL_SANDBOX_TARGET":"'"$URL"'"}}'
kubectl delete job url-sandbox -n ai-agents --ignore-not-found=true
kubectl apply -f "$K8S_DIR/security/job-url-sandbox.yaml"
echo "Acompanhe: kubectl logs -f job/url-sandbox -n ai-agents"
