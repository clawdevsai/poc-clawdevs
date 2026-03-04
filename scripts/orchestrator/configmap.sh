#!/usr/bin/env bash
# Cria ConfigMap orchestrator-scripts.
# Uso: ./scripts/orchestrator/configmap.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

echo "==> ConfigMap orchestrator-scripts..."
kubectl create configmap orchestrator-scripts -n ai-agents \
  --from-file=orchestration.py=app/core/orchestration.py \
  --from-file=orchestrator_autonomy.py=app/core/orchestrator_autonomy.py \
  --from-file=strikes.py=app/core/strikes.py \
  --from-file=slack_notify.py=app/shared/slack_notify.py \
  --from-file=consumer_orchestrator_events_slack.py=app/core/consumer_orchestrator_events_slack.py \
  --from-file=arbitrage_cloud.py=app/core/arbitrage_cloud.py \
  --from-file=digest_daily.py=app/features/digest_daily.py \
  --from-file=cosmetic_omission.py=app/features/cosmetic_omission.py \
  --from-file=set_consensus_pilot_result.py=app/features/set_consensus_pilot_result.py \
  --from-file=disjuntor_draft_rejected.py=app/features/disjuntor_draft_rejected.py \
  --from-file=rag_health_check.py=app/features/rag_health_check.py \
  --dry-run=client -o yaml | kubectl apply -f -
