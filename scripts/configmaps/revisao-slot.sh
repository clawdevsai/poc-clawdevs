#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"
echo "==> ConfigMap revisao-slot-scripts..."
kubectl create configmap revisao-slot-scripts -n ai-agents \
  --from-file=slot_revisao_pos_dev.py=app/agents/slot_revisao_pos_dev.py \
  --from-file=gpu_lock.py=app/features/gpu_lock.py \
  --from-file=openclaw_gateway_call.py=app/shared/openclaw_gateway_call.py \
  --from-file=orchestration.py=app/core/orchestration.py \
  --from-file=architect_fallback.py=app/core/architect_fallback.py \
  --from-file=microadr_generate.py=app/features/microadr_generate.py \
  --from-file=acefalo_redis.py=app/contingency/acefalo_redis.py \
  --dry-run=client -o yaml | kubectl apply -f -
