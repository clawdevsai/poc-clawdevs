#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"
echo "==> ConfigMap audit-runner-scripts..."
kubectl create configmap audit-runner-scripts -n ai-agents \
  --from-file=audit_runner.py=app/agents/audit_runner.py \
  --from-file=gpu_lock.py=app/features/gpu_lock.py \
  --from-file=issue_state.py=app/shared/issue_state.py \
  --from-file=openclaw_gateway_call.py=app/shared/openclaw_gateway_call.py \
  --dry-run=client -o yaml | kubectl apply -f -
