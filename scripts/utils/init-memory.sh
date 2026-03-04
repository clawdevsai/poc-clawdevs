#!/usr/bin/env bash
# Inicializa estrutura de memória (decisions/projects/lessons/pending + .learnings/).
# Uso: ./scripts/utils/init-memory.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
K8S_DIR="${K8S_DIR:-$REPO_ROOT/k8s}"

echo "==> Aplicando ConfigMap de scripts de init-memory..."
kubectl apply -f "$K8S_DIR/management-team/openclaw/init-memory-configmap.yaml"
echo "==> Removendo Job anterior (se existir)..."
kubectl delete job init-memory-structure -n ai-agents --ignore-not-found=true
echo "==> Rodando Job init-memory-structure..."
kubectl apply -f "$K8S_DIR/management-team/openclaw/init-memory-job.yaml"
echo "  Aguardando conclusão (timeout 120s)..."
if kubectl wait --for=condition=complete job/init-memory-structure -n ai-agents --timeout=120s 2>/dev/null; then
  echo "==> init-memory concluído com sucesso."
else
  kubectl logs -n ai-agents -l component=init-memory --tail=30 2>/dev/null || true
  echo "ERRO: job falhou. Veja logs acima."
  exit 1
fi
