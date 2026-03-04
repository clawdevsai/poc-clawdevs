#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"
echo "==> ConfigMap devops-worker-scripts..."
kubectl create configmap devops-worker-scripts -n ai-agents \
  --from-file=devops_worker.py=app/agents/devops_worker.py \
  --from-file=gpu_lock.py=app/features/gpu_lock.py \
  --from-file=issue_state.py=app/shared/issue_state.py \
  --from-file=openclaw_gateway_call.py=app/shared/openclaw_gateway_call.py \
  --dry-run=client -o yaml | kubectl apply -f -
