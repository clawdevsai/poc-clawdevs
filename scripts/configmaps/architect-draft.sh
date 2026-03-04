#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"
echo "==> ConfigMap architect-draft-scripts..."
kubectl create configmap architect-draft-scripts -n ai-agents \
  --from-file=architect_draft_consumer.py=app/agents/architect_draft_consumer.py \
  --from-file=gpu_lock.py=app/features/gpu_lock.py \
  --from-file=issue_state.py=app/shared/issue_state.py \
  --from-file=openclaw_gateway_call.py=app/shared/openclaw_gateway_call.py \
  --dry-run=client -o yaml | kubectl apply -f -
