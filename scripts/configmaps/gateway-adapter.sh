#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"
echo "==> ConfigMap gateway-redis-adapter-scripts..."
kubectl create configmap gateway-redis-adapter-scripts -n ai-agents \
  --from-file=gateway_redis_adapter.py=app/shared/gateway_redis_adapter.py \
  --from-file=gateway_token_bucket.py=app/shared/gateway_token_bucket.py \
  --from-file=check_domain_reputation.py=app/safety/check_domain_reputation.py \
  --from-file=truncate_payload_border.py=app/features/truncate_payload_border.py \
  --from-file=preflight_summarize.py=app/features/preflight_summarize.py \
  --dry-run=client -o yaml | kubectl apply -f -
