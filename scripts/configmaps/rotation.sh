#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"
echo "==> ConfigMap rotation-scripts..."
kubectl create configmap rotation-scripts -n ai-agents \
  --from-file=rotate_gateway_token.py=app/safety/rotate_gateway_token.py \
  --dry-run=client -o yaml | kubectl apply -f -
