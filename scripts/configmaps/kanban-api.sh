#!/usr/bin/env bash
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"
echo "==> ConfigMap kanban-api-scripts..."
kubectl create configmap kanban-api-scripts -n ai-agents \
  --from-file=kanban_api.py=app/core/kanban_api.py \
  --from-file=issue_state.py=app/shared/issue_state.py \
  --from-file=kanban_db.py=app/core/kanban_db.py \
  --from-file=kanban_event_publisher.py=app/core/kanban_event_publisher.py \
  --dry-run=client -o yaml | kubectl apply -f -
