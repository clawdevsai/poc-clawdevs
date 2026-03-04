#!/usr/bin/env bash
# Verificação de GPU no cluster (Minikube + pod Ollama) — somente leitura.
# Confere: (1) Minikube com addon nvidia-device-plugin; (2) Pod ollama-gpu em Running com nvidia.com/gpu alocado.
# Uso: ./verify-gpu-cluster.sh (ou via make verify)
# Ref: docs/37-deploy-fase0-telegram-ceo-ollama.md, k8s/ollama/deployment.yaml

set -e

echo ""
echo "=== Cluster (Minikube + GPU para Ollama) ==="

if ! command -v kubectl &>/dev/null; then
  echo "  kubectl não encontrado. Ignorando verificação do cluster (rode make prepare ou instale kubectl)."
  exit 0
fi

if ! command -v minikube &>/dev/null; then
  echo "  minikube não encontrado. Ignorando verificação do cluster."
  exit 0
fi

if ! minikube status &>/dev/null; then
  echo "  Minikube não está rodando. Inicie com: make up (ou minikube start --driver=docker --addons=nvidia-device-plugin ...)."
  exit 0
fi

# (1) Addon nvidia-device-plugin
if minikube addons list 2>/dev/null | grep -q 'nvidia-device-plugin.*enabled'; then
  echo "  Minikube addon nvidia-device-plugin: habilitado"
else
  echo "  AVISO: Addon nvidia-device-plugin não está habilitado. Ollama pode rodar em CPU."
  echo "    Habilitar: minikube addons enable nvidia-device-plugin"
fi

# (2) Pod ollama-gpu no namespace ai-agents
if ! kubectl get namespace ai-agents &>/dev/null; then
  echo "  Namespace ai-agents não existe. Aplique os recursos: make up"
  exit 0
fi

if ! kubectl get deployment ollama-gpu -n ai-agents &>/dev/null; then
  echo "  Deployment ollama-gpu não encontrado em ai-agents. Aplique: kubectl apply -f k8s/ollama/deployment.yaml"
  exit 0
fi

POD_STATUS=$(kubectl get pods -n ai-agents -l app=ollama -o jsonpath='{.items[0].status.phase}' 2>/dev/null || true)
if [[ -z "$POD_STATUS" ]]; then
  echo "  Pod Ollama ainda não está criado ou não encontrado (app=ollama). Aguarde o deployment."
  exit 0
fi

if [[ "$POD_STATUS" != "Running" ]]; then
  echo "  AVISO: Pod Ollama não está Running (status: ${POD_STATUS}). Verifique: kubectl get pods -n ai-agents -l app=ollama"
  kubectl describe pod -n ai-agents -l app=ollama 2>/dev/null | grep -E "Limits|Requests|Events:" -A 5 || true
  exit 0
fi

GPU_ALLOCATED=$(kubectl get pod -n ai-agents -l app=ollama -o jsonpath='{.items[0].spec.containers[0].resources.limits.nvidia\.com/gpu}' 2>/dev/null || true)
if [[ -n "$GPU_ALLOCATED" && "$GPU_ALLOCATED" != "0" ]]; then
  echo "  Pod Ollama: Running com nvidia.com/gpu: ${GPU_ALLOCATED} alocado"
else
  echo "  AVISO: Pod Ollama não tem nvidia.com/gpu nos limits. Pode estar rodando em CPU."
  echo "    Ver: kubectl describe pod -n ai-agents -l app=ollama"
fi

echo "  Verificação detalhada do pod: kubectl describe pod -n ai-agents -l app=ollama"
echo ""
