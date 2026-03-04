#!/usr/bin/env bash
# Teste: envia ordem para criar uma issue de teste no repo; a issue deve aparecer no GitHub.
# Uso: ./scripts/ops/test_github_create_issue.sh  ou  RUN_IN_CLUSTER=1 ...  ou  CLOSE_ISSUE=1 ...
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
REPO="${GITHUB_TEST_REPO:-clawdevsai/clawdevs}"
NAMESPACE="${K8S_NAMESPACE:-ai-agents}"
RUN_IN_CLUSTER="${RUN_IN_CLUSTER:-0}"
CLOSE_ISSUE="${CLOSE_ISSUE:-0}"

TS=$(date -u +"%Y-%m-%d %H:%M UTC")
TITLE="[Agente ClawDevs] Issue de teste — $TS"
BODY="Issue criada pelo **agente ClawDevs** (teste automatizado).

No GitHub, o **autor** desta issue é a conta associada ao token (identificação de quem criou).
Pode fechar quando quiser."

do_create() {
  local token="$1"
  if [ -z "$token" ]; then
    echo "Erro: GITHUB_TOKEN/GH_TOKEN não definido."
    return 1
  fi
  local json
  json=$(jq -n \
    --arg title "$TITLE" \
    --arg body "$BODY" \
    '{title: $title, body: $body}')
  curl -s -w "\n%{http_code}" \
    -X POST \
    -H "Authorization: Bearer $token" \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/$REPO/issues" \
    -d "$json"
}

do_close() {
  local token="$1"
  local num="$2"
  curl -s -o /dev/null -w "%{http_code}" \
    -X PATCH \
    -H "Authorization: Bearer $token" \
    -H "Accept: application/vnd.github.v3+json" \
    "https://api.github.com/repos/$REPO/issues/$num" \
    -d '{"state":"closed"}'
}

RESP=""
if [ "$RUN_IN_CLUSTER" = "1" ]; then
  echo "==> Criando issue a partir do agente (pod openclaw no cluster)..."
  if ! kubectl get deploy openclaw -n "$NAMESPACE" &>/dev/null; then
    echo "  Deploy openclaw não encontrado. Use RUN_IN_CLUSTER=0 para testar no host."
    exit 1
  fi
  POD=$(kubectl get pods -n "$NAMESPACE" -l app=openclaw -o jsonpath='{.items[0].metadata.name}' 2>/dev/null)
  if [ -z "$POD" ]; then
    echo "  Nenhum pod openclaw rodando."
    exit 1
  fi
  B64=$(jq -n --arg title "$TITLE" --arg body "$BODY" '{title: $title, body: $body}' | base64 -w0 2>/dev/null || base64 2>/dev/null | tr -d '\n')
  RESP=$(kubectl exec -n "$NAMESPACE" "$POD" -c gateway -- sh -c "echo '$B64' | base64 -d 2>/dev/null | curl -s -w '\n%{http_code}' -X POST -H 'Authorization: Bearer '\$GITHUB_TOKEN -H 'Accept: application/vnd.github.v3+json' --data-binary @- 'https://api.github.com/repos/$REPO/issues'" 2>/dev/null)
  if [ -z "$RESP" ] || ! echo "$RESP" | tail -n1 | grep -qE '^[0-9]{3}$'; then
    echo "  Pod sem curl/token; criando a partir do host com token do .env..."
    RUN_IN_CLUSTER=0
  fi
fi

if [ "$RUN_IN_CLUSTER" != "1" ]; then
  echo "==> Criando issue a partir do host (.env)..."
  if [ -f "$REPO_ROOT/.env" ]; then
    export $(grep -E '^GITHUB_TOKEN=|^GH_TOKEN=' "$REPO_ROOT/.env" 2>/dev/null | xargs) 2>/dev/null || true
  fi
  TOKEN="${GITHUB_TOKEN:-$GH_TOKEN}"
  RESP=$(do_create "$TOKEN")
fi

HTTP_BODY=$(echo "$RESP" | head -n -1)
HTTP_CODE=$(echo "$RESP" | tail -n 1)

if [ "$HTTP_CODE" != "201" ]; then
  echo "  Falhou: HTTP $HTTP_CODE"
  echo "$HTTP_BODY" | jq -r '.message // .' 2>/dev/null || echo "$HTTP_BODY"
  exit 1
fi

ISSUE_URL=$(echo "$HTTP_BODY" | jq -r '.html_url')
ISSUE_NUM=$(echo "$HTTP_BODY" | jq -r '.number')
USER=$(echo "$HTTP_BODY" | jq -r '.user.login // "?"')

echo "  Criada: $ISSUE_URL (#$ISSUE_NUM)"
echo "  Autor no GitHub: $USER (identificação de quem criou)"
echo ""
echo "  Veja na aba Issues do repositório: a issue deve aparecer em Open; o autor identifica o agente/conta."
echo ""

if [ "$CLOSE_ISSUE" = "1" ]; then
  TOKEN="${GITHUB_TOKEN:-$GH_TOKEN}"
  [ -z "$TOKEN" ] && [ -f "$REPO_ROOT/.env" ] && export $(grep -E '^GITHUB_TOKEN=|^GH_TOKEN=' "$REPO_ROOT/.env" 2>/dev/null | xargs) 2>/dev/null || true
  TOKEN="${GITHUB_TOKEN:-$GH_TOKEN}"
  do_close "$TOKEN" "$ISSUE_NUM" >/dev/null
  echo "  Issue #$ISSUE_NUM fechada (CLOSE_ISSUE=1)."
else
  echo "  Issue deixada aberta. Para fechar depois: CLOSE_ISSUE=1 ./scripts/ops/test_github_create_issue.sh (ou feche manualmente no GitHub)."
fi

echo "==> Teste OK: issue criada e identificável no GitHub."
