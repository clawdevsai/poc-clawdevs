#!/usr/bin/env bash
# Baixa todos os modelos LLM usados pelos agentes no Ollama do cluster (deploy/ollama-gpu).
# Uso: ./scripts/ollama-pull-all-agent-models.sh
# Requer: kubectl, namespace ai-agents, deploy/ollama-gpu rodando.

set -e
NS="${KUBE_NS:-ai-agents}"
DEPLOY="ollama-gpu"

# Modelos usados pelos agentes (openclaw configmap + governance)
MODELS=(
  "qwen3-next:80b-cloud"        # CEO, PO, Cybersec, UX
  "devstral-2:123b-cloud"       # DevOps, Architect
  "qwen3-coder:480b-cloud"      # Developer
  "qwen3-coder-next:cloud"      # QA, DBA
  "nemotron-3-nano:30b-cloud"   # Governance
)

echo "Pulling ${#MODELS[@]} models in deploy/$DEPLOY (namespace $NS)..."
for m in "${MODELS[@]}"; do
  echo "--- ollama pull $m ---"
  kubectl exec -n "$NS" "deploy/$DEPLOY" -- ollama pull "$m" || true
done
echo "Done."
