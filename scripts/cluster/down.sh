#!/usr/bin/env bash
# Desliga e remove todos os recursos do ClawDevs no cluster (estaca zero).
# Uso: ./scripts/cluster/down.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
K8S_DIR="${K8S_DIR:-$REPO_ROOT/k8s}"

echo "==> down: removendo recursos (estaca zero)..."
if ! kubectl get namespace ai-agents >/dev/null 2>&1; then
  echo "  Namespace ai-agents não existe."
  exit 0
fi

kubectl delete deployment -n ai-agents --all --ignore-not-found --timeout=60s 2>/dev/null || true
kubectl delete statefulset -n ai-agents --all --ignore-not-found --timeout=60s 2>/dev/null || true
kubectl wait --for=delete pod -l app=ollama -n ai-agents --timeout=90s 2>/dev/null || true
kubectl wait --for=delete pod -l app=openclaw -n ai-agents --timeout=90s 2>/dev/null || true
kubectl wait --for=delete pod -l app=redis -n ai-agents --timeout=90s 2>/dev/null || true
sleep 3
kubectl delete pvc -n ai-agents --all --ignore-not-found --timeout=60s 2>/dev/null || true
kubectl delete namespace ai-agents --ignore-not-found --timeout=120s 2>/dev/null || true

echo "==> down concluído."
