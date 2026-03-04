#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"
echo "==> ConfigMap devops-compact-script..."
kubectl create configmap devops-compact-script -n ai-agents \
  --from-file=compact_preserve_protected.py=app/features/compact_preserve_protected.py \
  --dry-run=client -o yaml | kubectl apply -f -
