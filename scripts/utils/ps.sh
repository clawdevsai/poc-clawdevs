#!/usr/bin/env bash
# Valida o consumo de hardware no K8s: ResourceQuota (limite 65%), uso real de nós e pods.
# Uso: ./scripts/utils/ps.sh
# Requer: kubectl. Para uso real (kubectl top), ative: minikube addons enable metrics-server
set -e

NAMESPACE="${NAMESPACE:-ai-agents}"

echo "==> ResourceQuota (limite 65% — namespace $NAMESPACE)"
kubectl get resourcequota -n "$NAMESPACE" 2>/dev/null || true
echo ""
kubectl describe resourcequota -n "$NAMESPACE" 2>/dev/null || true
echo ""

echo "==> Uso real dos nós (CPU/memória)"
if kubectl top nodes 2>/dev/null; then
  :
else
  echo "  (metrics-server não disponível; para habilitar: minikube addons enable metrics-server)"
fi
echo ""

echo "==> Uso real dos pods ($NAMESPACE)"
if kubectl top pods -n "$NAMESPACE" 2>/dev/null; then
  :
else
  echo "  (metrics-server não disponível; para habilitar: minikube addons enable metrics-server)"
fi
