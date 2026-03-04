#!/usr/bin/env bash
# Deprecated: pods architect/qa/cybersec/dba (014). Use revisao-pos-dev.
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"
echo "==> ConfigMap agent-slot-scripts (deprecated)..."
kubectl create configmap agent-slot-scripts -n ai-agents \
  --from-file=gpu_lock.py=scripts/gpu_lock.py \
  --from-file=acefalo_redis.py=scripts/acefalo_redis.py \
  --dry-run=client -o yaml | kubectl apply -f -
