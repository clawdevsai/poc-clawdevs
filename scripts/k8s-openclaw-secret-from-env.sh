#!/usr/bin/env bash
# Cria ou atualiza o Secret openclaw-telegram no namespace ai-agents a partir do .env da raiz do repo.
# Lê OPENCLAW_SLACK_* (fallback SLACK_*) e grava no Secret como SLACK_* para o gateway.
# Uso: ./scripts/k8s-openclaw-secret-from-env.sh
# Pré-requisito: kubectl apontando para o cluster (ex.: minikube).
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"

if [[ ! -f "$REPO_ROOT/.env" ]]; then
  echo "Erro: .env não encontrado em $REPO_ROOT. Crie a partir de .env.example."
  exit 1
fi

set -a
source "$REPO_ROOT/.env"
set +a

# OpenClaw Slack: preferir OPENCLAW_SLACK_*, fallback para SLACK_* (transição)
SLACK_APP_TOKEN="${OPENCLAW_SLACK_APP_TOKEN:-$SLACK_APP_TOKEN}"
SLACK_BOT_TOKEN="${OPENCLAW_SLACK_BOT_TOKEN:-$SLACK_BOT_TOKEN}"
SLACK_DIRECTOR_USER_ID="${OPENCLAW_SLACK_DIRECTOR_USER_ID:-$SLACK_DIRECTOR_USER_ID}"
SLACK_ALLOWED_USER_IDS="${OPENCLAW_SLACK_ALLOWED_USER_IDS:-$SLACK_ALLOWED_USER_IDS}"
SLACK_ALL_CLAWDEVSAI_CHANNEL_ID="${OPENCLAW_SLACK_ALL_CLAWDEVSAI_CHANNEL_ID:-$SLACK_ALL_CLAWDEVSAI_CHANNEL_ID}"

ARGS=()
[[ -n "$TELEGRAM_BOT_TOKEN" ]]    && ARGS+=(--from-literal=TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN")
[[ -n "$TELEGRAM_CHAT_ID" ]]      && ARGS+=(--from-literal=TELEGRAM_CHAT_ID="$TELEGRAM_CHAT_ID")
[[ -n "$SLACK_APP_TOKEN" ]]       && ARGS+=(--from-literal=SLACK_APP_TOKEN="$SLACK_APP_TOKEN")
[[ -n "$SLACK_BOT_TOKEN" ]]       && ARGS+=(--from-literal=SLACK_BOT_TOKEN="$SLACK_BOT_TOKEN")
[[ -n "$SLACK_DIRECTOR_USER_ID" ]] && ARGS+=(--from-literal=SLACK_DIRECTOR_USER_ID="$SLACK_DIRECTOR_USER_ID")
[[ -n "$SLACK_ALLOWED_USER_IDS" ]] && ARGS+=(--from-literal=SLACK_ALLOWED_USER_IDS="$SLACK_ALLOWED_USER_IDS")
[[ -n "$SLACK_ALL_CLAWDEVSAI_CHANNEL_ID" ]] && ARGS+=(--from-literal=SLACK_ALL_CLAWDEVSAI_CHANNEL_ID="$SLACK_ALL_CLAWDEVSAI_CHANNEL_ID")
# Contas Slack por agente (um app por agente; gateway conecta cada app com accountId = ceo, po, devops, ...)
for key in CEO PO DEVOPS ARCHITECT DEVELOPER QA CYBERSEC UX DBA; do
  app_var="${key}_SLACK_APP_TOKEN"
  bot_var="${key}_SLACK_BOT_TOKEN"
  app_val="${!app_var}"
  bot_val="${!bot_var}"
  [[ -n "$app_val" ]] && ARGS+=(--from-literal="${key}_SLACK_APP_TOKEN=$app_val")
  [[ -n "$bot_val" ]] && ARGS+=(--from-literal="${key}_SLACK_BOT_TOKEN=$bot_val")
done

if [[ ${#ARGS[@]} -eq 0 ]]; then
  echo "Erro: nenhuma variável relevante definida no .env (TELEGRAM_*, OPENCLAW_SLACK_* ou SLACK_*)."
  exit 1
fi

if ! kubectl get namespace ai-agents &>/dev/null; then
  echo "Erro: namespace ai-agents não existe. Rode 'make up' antes."
  exit 1
fi

echo "==> Criando/atualizando Secret openclaw-telegram no namespace ai-agents a partir do .env..."
kubectl create secret generic openclaw-telegram -n ai-agents "${ARGS[@]}" --dry-run=client -o yaml | kubectl apply -f -
echo "==> Secret aplicado. Para o gateway no cluster usar: kubectl rollout restart deployment/openclaw -n ai-agents"
