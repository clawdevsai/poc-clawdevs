#!/usr/bin/env bash
# Desmonta o workspace compartilhado (mata o processo minikube mount que monta ~/clawdevs-shared em /agent-shared).
# Uso: ./scripts/utils/shared-unmount.sh
# Depois rode make shared para remontar e, se o OpenClaw já estiver no ar, kubectl rollout restart deployment/openclaw -n ai-agents
set -e

KILLED=0
for pid in $(pgrep -x minikube 2>/dev/null); do
  if grep -q 'mount.*agent-shared' /proc/"$pid"/cmdline 2>/dev/null; then
    kill "$pid" 2>/dev/null || true
    KILLED=1
  fi
done
if [[ "$KILLED" -eq 1 ]]; then
  echo "==> Processo minikube mount (agent-shared) encerrado. Para remontar: make shared"
else
  echo "==> Nenhum processo minikube mount (agent-shared) em execução."
fi
