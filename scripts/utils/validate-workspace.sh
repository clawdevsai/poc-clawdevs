#!/usr/bin/env bash
# Valida que /workspace está acessível e compartilhado para todos os agentes no pod do OpenClaw (evita I/O error).
# Uso: ./scripts/utils/validate-workspace.sh
set -e

echo "==> Validando acesso a /workspace (compartilhado com todos os agentes)..."
kubectl exec -n ai-agents deploy/openclaw -c gateway -- ls -la /workspace/
kubectl exec -n ai-agents deploy/openclaw -c gateway -- ls -la /workspace/workspace/ 2>/dev/null || true
echo "==> Workspace OK (acesso liberado)."
