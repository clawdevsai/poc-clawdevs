#!/usr/bin/env bash
# Sobe o sistema completo: cluster/up + slot Revisão pós-Dev, Redis streams e orquestrador.
# Uso: ./scripts/cluster/up-all.sh
# Idempotente: pode rodar várias vezes.
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"
K8S_DIR="${K8S_DIR:-k8s}"
SCRIPTS_DIR="$REPO_ROOT/scripts"

echo "==> ClawDevs — subindo sistema completo (Minikube)"
echo ""

echo "==> [1/4] cluster/up (Minikube, Redis, Ollama, OpenClaw, Security, Orquestrador)..."
"$SCRIPTS_DIR/cluster/up.sh"
echo ""

echo "==> [2/4] Slot Revisão pós-Dev (configmap + deployment)..."
"$SCRIPTS_DIR/configmaps/revisao-slot.sh"
kubectl apply -f "$K8S_DIR/development-team/revisao-pos-dev/"
echo ""

echo "==> [3/4] Redis streams init (streams + consumer groups)..."
if kubectl get job redis-streams-init -n ai-agents &>/dev/null; then
  echo "    Job redis-streams-init já existe. Para recriar: kubectl delete job redis-streams-init -n ai-agents e rode este script de novo."
else
  kubectl apply -f "$K8S_DIR/redis/job-init-streams.yaml"
fi
echo ""

echo "==> [4/4] Reiniciando deployments (orquestrador + slot revisão)..."
kubectl rollout restart deployment/slack-events-consumer -n ai-agents --timeout=60s 2>/dev/null || true
kubectl rollout restart deployment/revisao-pos-dev -n ai-agents --timeout=60s 2>/dev/null || true
kubectl rollout status deployment/slack-events-consumer deployment/revisao-pos-dev -n ai-agents --timeout=90s 2>/dev/null || true
echo ""

echo "==> Sistema no ar."
echo "  OpenClaw (Slack/Telegram): deploy/openclaw"
echo "  Slot Revisão pós-Dev: deploy/revisao-pos-dev"
echo "  Orquestrador: deploy/slack-events-consumer + CronJobs (digest, cosmetic, consensus)"
echo "  Alertas Slack (opcional): ver docs/07-operations — kubectl create secret generic orchestrator-slack -n ai-agents --from-literal=SLACK_WEBHOOK_URL='...'"
echo "  Ollama: kubectl exec -n ai-agents deploy/ollama-gpu -- ollama pull <modelo>"
