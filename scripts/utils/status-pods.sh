#!/usr/bin/env bash
# Mostra logs (tail) dos principais pods.
# Uso: ./scripts/utils/status-pods.sh
set -e

echo "==> Redis (tail 5)..."
kubectl logs -n ai-agents deployment/redis --tail=5 2>/dev/null || true
echo ""
echo "==> OpenClaw (tail 5)..."
kubectl logs -n ai-agents deployment/openclaw --tail=5 2>/dev/null || true
echo ""
echo "==> Ollama (tail 5)..."
kubectl logs -n ai-agents deployment/ollama-gpu --tail=5 2>/dev/null || true
echo ""
echo "==> Revisão pós-Dev (tail 5)..."
kubectl logs -n ai-agents deployment/revisao-pos-dev --tail=5 2>/dev/null || true
echo ""
echo "==> Slack events consumer (tail 5)..."
kubectl logs -n ai-agents deployment/slack-events-consumer --tail=5 2>/dev/null || true
