#!/usr/bin/env bash
# Sobe o sistema principal: namespace, Redis, Ollama, OpenClaw, ConfigMaps, deployments, init-memory, pipeline.
# Uso: ./scripts/cluster/up.sh
# Variáveis: K8S_DIR, MINIKUBE_CPUS, MINIKUBE_MEMORY
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

K8S_DIR="${K8S_DIR:-k8s}"
OPENCLAW_BUILD_DIR="$K8S_DIR/management-team/openclaw"
OPENCLAW_CHECKSUM_FILE="/tmp/.openclaw-image-checksum"
SCRIPTS_DIR="$REPO_ROOT/scripts"

# Se Minikube não está rodando, executa prepare
if ! minikube status >/dev/null 2>&1; then
  echo "==> Minikube não está rodando. Executando prepare..."
  "$SCRIPTS_DIR/cluster/prepare.sh"
fi

# Build OpenClaw (condicional)
echo "==> Build OpenClaw (condicional)..."
NEW_SUM=$(cat "$OPENCLAW_BUILD_DIR/Dockerfile" "$OPENCLAW_BUILD_DIR/entrypoint.sh" 2>/dev/null | md5sum | cut -d' ' -f1)
OLD_SUM=$(cat "$OPENCLAW_CHECKSUM_FILE" 2>/dev/null || echo "none")
if [ "$NEW_SUM" != "$OLD_SUM" ]; then
  echo "  Dockerfile/entrypoint alterados — rebuild..."
  eval "$(minikube docker-env)" && docker build -q -f "$OPENCLAW_BUILD_DIR/Dockerfile" -t openclaw-gateway:local "$OPENCLAW_BUILD_DIR"
  echo "$NEW_SUM" > "$OPENCLAW_CHECKSUM_FILE"
  echo "  openclaw-image concluído."
else
  echo "  Imagem OpenClaw inalterada — skip build."
fi

echo "==> Namespace + limites..."
kubectl apply -f "$K8S_DIR/shared/infra/namespace.yaml" -f "$K8S_DIR/shared/infra/limits.yaml"

echo "==> Secrets (.env)..."
"$SCRIPTS_DIR/cluster/secrets-from-env.sh" || true

echo "==> Redis + Ollama..."
kubectl apply -f "$K8S_DIR/redis/deployment.yaml" -f "$K8S_DIR/redis/streams-configmap.yaml"
kubectl apply -f "$K8S_DIR/ollama/deployment.yaml"
if [ -f "$K8S_DIR/ollama/secret.yaml" ]; then
  echo "  Aplicando secret Ollama Cloud..."
  kubectl apply -f "$K8S_DIR/ollama/secret.yaml"
  kubectl rollout restart deployment/ollama-gpu -n ai-agents --timeout=60s 2>/dev/null || true
  "$SCRIPTS_DIR/openclaw/ollama-ensure-cloud-auth.sh" || true
fi

echo "==> ConfigMaps (LLM + OpenClaw + SOUL)..."
kubectl apply \
  -f "$K8S_DIR/shared/infra/llm-providers.yaml" \
  -f "$OPENCLAW_BUILD_DIR/configmap.yaml" \
  -f "$OPENCLAW_BUILD_DIR/workspace-ceo-configmap.yaml" \
  -f "$OPENCLAW_BUILD_DIR/workspace-po-configmap.yaml" \
  -f "$OPENCLAW_BUILD_DIR/workspace-architect-configmap.yaml" \
  -f "$OPENCLAW_BUILD_DIR/workspace-developer-configmap.yaml" \
  -f "$OPENCLAW_BUILD_DIR/workspace-devops-configmap.yaml" \
  -R -f "$K8S_DIR/management-team/ceo/soul/" \
  -R -f "$K8S_DIR/management-team/po/soul/" \
  -R -f "$K8S_DIR/development-team/"

if [ -d "$K8S_DIR/security" ]; then
  "$SCRIPTS_DIR/security/configmaps.sh"
  kubectl apply -f "$K8S_DIR/security/"
fi
if [ -d "$K8S_DIR/orchestrator" ]; then
  "$SCRIPTS_DIR/orchestrator/configmap.sh"
  "$SCRIPTS_DIR/configmaps/acefalo.sh" || true
  kubectl apply -f "$K8S_DIR/orchestrator/"
fi
if [ -f "$OPENCLAW_BUILD_DIR/serviceaccount.yaml" ]; then
  kubectl apply -f "$OPENCLAW_BUILD_DIR/serviceaccount.yaml"
fi

echo "==> Workspace compartilhado (PV + PVC + minikube mount)..."
"$SCRIPTS_DIR/utils/shared-ensure.sh"
kubectl apply -f "$OPENCLAW_BUILD_DIR/shared-workspace-pv.yaml" -f "$OPENCLAW_BUILD_DIR/shared-workspace-pvc.yaml"
# Se o PV ficou Released (ex.: PVC foi deletado em make down), libera o bind para o PVC atual
PV_STATUS=$(kubectl get pv openclaw-shared-workspace-pv -o jsonpath='{.status.phase}' 2>/dev/null || true)
PVC_STATUS=$(kubectl get pvc openclaw-shared-workspace-pvc -n ai-agents -o jsonpath='{.status.phase}' 2>/dev/null || true)
if [ "$PV_STATUS" = "Released" ] && [ "$PVC_STATUS" = "Pending" ]; then
  echo "  Corrigindo PV Released -> removendo claimRef antigo..."
  kubectl patch pv openclaw-shared-workspace-pv --type=json -p='[{"op": "remove", "path": "/spec/claimRef"}]' 2>/dev/null || true
fi

echo "==> Deployment OpenClaw..."
kubectl apply -f "$OPENCLAW_BUILD_DIR/deployment.yaml"
if [ -f "$OPENCLAW_BUILD_DIR/secret.yaml" ]; then
  kubectl apply -f "$OPENCLAW_BUILD_DIR/secret.yaml"
fi
kubectl rollout restart deployment/openclaw -n ai-agents --timeout=60s 2>/dev/null || true

echo "==> Init-memory (estrutura memory/ + shared/memory/ + .learnings/)..."
kubectl apply -f "$K8S_DIR/management-team/openclaw/init-memory-configmap.yaml"
kubectl delete job init-memory-structure -n ai-agents --ignore-not-found=true
kubectl apply -f "$K8S_DIR/management-team/openclaw/init-memory-job.yaml"
if kubectl wait --for=condition=complete job/init-memory-structure -n ai-agents --timeout=120s 2>/dev/null; then
  echo "  init-memory OK."
else
  kubectl logs -n ai-agents -l component=init-memory --tail=20 2>/dev/null || true
  echo "  AVISO: init-memory falhou; rode 'make init-memory' manualmente."
fi

echo "==> Pipeline (ConfigMaps + deployments)..."
"$SCRIPTS_DIR/configmaps/po.sh"
"$SCRIPTS_DIR/configmaps/architect-draft.sh"
"$SCRIPTS_DIR/configmaps/developer.sh"
"$SCRIPTS_DIR/configmaps/revisao-slot.sh"
"$SCRIPTS_DIR/configmaps/devops-worker.sh"
"$SCRIPTS_DIR/configmaps/audit-runner.sh"
"$SCRIPTS_DIR/configmaps/gateway-adapter.sh"
for dir in po architect-draft developer revisao-pos-dev devops-worker audit-runner gateway-redis-adapter; do
  kubectl apply -f "$K8S_DIR/development-team/$dir/" 2>/dev/null || true
done

if ! kubectl get job redis-streams-init -n ai-agents &>/dev/null; then
  echo "==> Redis streams init (job one-shot)..."
  kubectl apply -f "$K8S_DIR/redis/job-init-streams.yaml"
fi

echo "==> up concluído."
echo "  Ollama: kubectl exec -n ai-agents deploy/ollama-gpu -- ollama pull <modelo>"
IP=$(minikube ip)
echo ""
echo "  🚀 OpenClaw Control UI: http://$IP:30000"
echo ""
