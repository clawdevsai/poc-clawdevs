#!/usr/bin/env bash
# Mostra resumo do que está rodando (Minikube, pods, deployments, services).
# Uso: ./scripts/utils/status.sh
set -e

echo "==> Minikube..."
minikube status 2>/dev/null || true
echo ""
echo "==> Pods (ai-agents)..."
kubectl get pods -n ai-agents -o wide 2>/dev/null || true
echo ""
echo "==> Deployments..."
kubectl get deployments -n ai-agents 2>/dev/null || true
echo ""
echo "==> Services..."
kubectl get svc -n ai-agents 2>/dev/null || true
