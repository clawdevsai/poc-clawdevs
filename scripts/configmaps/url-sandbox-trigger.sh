#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"
echo "==> ConfigMap url-sandbox-trigger-scripts..."
kubectl create configmap url-sandbox-trigger-scripts -n ai-agents \
  --from-file=url_sandbox_trigger.py=app/safety/url_sandbox_trigger.py \
  --dry-run=client -o yaml | kubectl apply -f -
