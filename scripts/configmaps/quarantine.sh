#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"
echo "==> ConfigMap quarantine-pipeline-scripts..."
kubectl create configmap quarantine-pipeline-scripts -n ai-agents \
  --from-file=quarantine_pipeline.py=app/safety/quarantine_pipeline.py \
  --from-file=quarantine_entropy.py=app/safety/quarantine_entropy.py \
  --from-file=trusted_package_verify.py=app/safety/trusted_package_verify.py \
  --dry-run=client -o yaml | kubectl apply -f -
