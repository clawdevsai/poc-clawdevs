#!/usr/bin/env bash
# Gera o link para login no Ollama Cloud (modelos glm-5:cloud etc.).
# Uso: ./scripts/openclaw/ollama-signin.sh
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

if ! kubectl get deploy ollama-gpu -n ai-agents &>/dev/null; then
  echo "Erro: deployment ollama-gpu não encontrado no namespace ai-agents. Rode: make up"
  exit 1
fi

echo "==> Executando 'ollama signin' no pod (abre o link no navegador para concluir)..."
echo ""
OUTPUT=$(kubectl exec -n ai-agents deploy/ollama-gpu -- timeout 30 ollama signin 2>&1 || true)
echo "$OUTPUT"
echo ""
URL=$(echo "$OUTPUT" | grep -o 'https://ollama.com/connect[^[:space:]]*' | head -1)
if [[ -n "$URL" ]]; then
  echo "==> Abra este link no navegador (e faça login na Ollama se precisar):"
  echo "    $URL"
  echo ""
  echo "Depois de concluir, modelos cloud (ex.: glm-5:cloud) devem funcionar no pod."
fi
