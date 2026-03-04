#!/usr/bin/env bash
# Garante que o Ollama no cluster está autenticado no Ollama Cloud (modelos glm-5:cloud etc.).
# Uso: ./scripts/openclaw/ollama-ensure-cloud-auth.sh
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
cd "$REPO_ROOT"

NAMESPACE="${NAMESPACE:-ai-agents}"
CLOUD_MODEL="${CLOUD_MODEL:-glm-5:cloud}"

is_cloud_authenticated() {
  local out
  out=$(kubectl exec -n "$NAMESPACE" deploy/ollama-gpu -- sh -c "echo 'x' | timeout 20 ollama run $CLOUD_MODEL 2>&1" || true)
  if echo "$out" | grep -q "401 Unauthorized"; then
    return 1
  fi
  return 0
}

echo ""
echo "==> Ollama Cloud: verificando autenticação (modelo $CLOUD_MODEL)..."

if ! kubectl get deploy ollama-gpu -n "$NAMESPACE" &>/dev/null; then
  echo "    Deployment ollama-gpu não encontrado. Pulando verificação."
  exit 0
fi

echo "    Aguardando pod Ollama ficar Ready..."
if ! kubectl rollout status deployment/ollama-gpu -n "$NAMESPACE" --timeout=120s 2>/dev/null; then
  echo "    Pod não ficou Ready a tempo. Pulando verificação."
  exit 0
fi

if is_cloud_authenticated; then
  echo "    Já autenticado no Ollama Cloud. Nada a fazer."
  echo ""
  exit 0
fi

echo "    Ainda não autenticado. É necessário vincular este Ollama à sua conta em ollama.com."
echo ""
OUTPUT=$(kubectl exec -n "$NAMESPACE" deploy/ollama-gpu -- timeout 30 ollama signin 2>&1 || true)
echo "$OUTPUT"
echo ""
URL=$(echo "$OUTPUT" | grep -o 'https://ollama.com/connect[^[:space:]]*' | head -1)

if [[ -z "$URL" ]]; then
  echo "    Não foi possível obter o link de conexão. Execute manualmente: ./scripts/openclaw/ollama-signin.sh"
  exit 1
fi

echo "------------------------------------------------------------------------------"
echo "  AÇÃO OBRIGATÓRIA: Abra o link abaixo no navegador e conclua o login."
echo ""
echo "  $URL"
echo "------------------------------------------------------------------------------"
echo ""
printf "  Pressione ENTER após ter aberto o link e concluído o login no navegador... "
read -r
echo ""

echo "    Verificando autenticação novamente..."
for i in 1 2 3 4 5; do
  if is_cloud_authenticated; then
    echo "    Autenticação confirmada. Continuando."
    echo ""
    exit 0
  fi
  echo "    Ainda não autenticado. Se já concluiu o login, aguarde alguns segundos."
  sleep 3
done

echo "    ERRO: Autenticação não confirmada. Abra o link, conclua o login e execute: make up"
echo "    ou rode novamente: ./scripts/openclaw/ollama-ensure-cloud-auth.sh"
exit 1
