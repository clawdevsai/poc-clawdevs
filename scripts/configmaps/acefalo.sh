#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"
echo "==> ConfigMap acefalo-scripts..."
kubectl create configmap acefalo-scripts -n ai-agents \
  --from-file=acefalo_redis.py=app/contingency/acefalo_redis.py \
  --from-file=acefalo_contingency.py=app/contingency/acefalo_contingency.py \
  --from-file=acefalo_retomada.py=app/contingency/acefalo_retomada.py \
  --from-file=acefalo_heartbeat_writer.py=app/contingency/acefalo_heartbeat_writer.py \
  --from-file=acefalo_monitor.py=app/contingency/acefalo_monitor.py \
  --dry-run=client -o yaml | kubectl apply -f -
