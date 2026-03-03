#!/usr/bin/env bash
# Cria/atualiza todos os Secrets no namespace ai-agents a partir do .env.
# Chamado por 'make up'. Nunca falha o make (exit 0); apenas avisa se .env ausente ou vazio.
# Secrets: openclaw-telegram, clawdevs-github-secret, orchestrator-slack, openclaw-telegram-rotation-source
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$REPO_ROOT"
NS="${NAMESPACE:-ai-agents}"

if [[ ! -f "$REPO_ROOT/.env" ]]; then
  echo "==> .env não encontrado; secrets não criados. Opcional: copie .env.example para .env e preencha."
  exit 0
fi

if ! kubectl get namespace "$NS" &>/dev/null; then
  echo "==> Namespace $NS não existe ainda; secrets serão criados após 'make up' aplicar o namespace."
  exit 0
fi

set -a
# shellcheck source=/dev/null
source "$REPO_ROOT/.env" 2>/dev/null || true
set +a

CREATED=0

# --- openclaw-telegram (Slack/Telegram para o gateway)
SLACK_APP_TOKEN="${OPENCLAW_SLACK_APP_TOKEN:-$SLACK_APP_TOKEN}"
SLACK_BOT_TOKEN="${OPENCLAW_SLACK_BOT_TOKEN:-$SLACK_BOT_TOKEN}"
SLACK_DIRECTOR_USER_ID="${OPENCLAW_SLACK_DIRECTOR_USER_ID:-$SLACK_DIRECTOR_USER_ID}"
SLACK_ALLOWED_USER_IDS="${OPENCLAW_SLACK_ALLOWED_USER_IDS:-$SLACK_ALLOWED_USER_IDS}"
SLACK_ALL_CLAWDEVSAI_CHANNEL_ID="${OPENCLAW_SLACK_ALL_CLAWDEVSAI_CHANNEL_ID:-$SLACK_ALL_CLAWDEVSAI_CHANNEL_ID}"
ARGS=()
[[ -n "$TELEGRAM_BOT_TOKEN" ]]    && ARGS+=(--from-literal=TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN")
[[ -n "$TELEGRAM_CHAT_ID" ]]     && ARGS+=(--from-literal=TELEGRAM_CHAT_ID="$TELEGRAM_CHAT_ID")
[[ -n "$SLACK_APP_TOKEN" ]]      && ARGS+=(--from-literal=SLACK_APP_TOKEN="$SLACK_APP_TOKEN")
[[ -n "$SLACK_BOT_TOKEN" ]]      && ARGS+=(--from-literal=SLACK_BOT_TOKEN="$SLACK_BOT_TOKEN")
[[ -n "$SLACK_DIRECTOR_USER_ID" ]] && ARGS+=(--from-literal=SLACK_DIRECTOR_USER_ID="$SLACK_DIRECTOR_USER_ID")
[[ -n "$SLACK_ALLOWED_USER_IDS" ]] && ARGS+=(--from-literal=SLACK_ALLOWED_USER_IDS="$SLACK_ALLOWED_USER_IDS")
[[ -n "$SLACK_ALL_CLAWDEVSAI_CHANNEL_ID" ]] && ARGS+=(--from-literal=SLACK_ALL_CLAWDEVSAI_CHANNEL_ID="$SLACK_ALL_CLAWDEVSAI_CHANNEL_ID")
for key in CEO PO DEVOPS ARCHITECT DEVELOPER QA CYBERSEC UX DBA; do
  app_var="${key}_SLACK_APP_TOKEN"
  bot_var="${key}_SLACK_BOT_TOKEN"
  app_val="${!app_var}"
  bot_val="${!bot_var}"
  [[ -n "$app_val" ]] && ARGS+=(--from-literal="${key}_SLACK_APP_TOKEN=$app_val")
  [[ -n "$bot_val" ]] && ARGS+=(--from-literal="${key}_SLACK_BOT_TOKEN=$bot_val")
done
if [[ ${#ARGS[@]} -gt 0 ]]; then
  echo "==> Secret openclaw-telegram (a partir do .env)..."
  kubectl create secret generic openclaw-telegram -n "$NS" "${ARGS[@]}" --dry-run=client -o yaml | kubectl apply -f -
  CREATED=1
fi

# --- clawdevs-github-secret (gh CLI / push-pull nos pods)
if [[ -n "$GITHUB_TOKEN" || -n "$GH_TOKEN" ]]; then
  echo "==> Secret clawdevs-github-secret (a partir do .env)..."
  kubectl create secret generic clawdevs-github-secret -n "$NS" \
    --from-literal=GITHUB_TOKEN="${GITHUB_TOKEN:-$GH_TOKEN}" \
    --from-literal=GH_TOKEN="${GH_TOKEN:-$GITHUB_TOKEN}" \
    --dry-run=client -o yaml | kubectl apply -f -
  CREATED=1
fi

# --- orchestrator-slack (alertas: digest, consensus, consumer)
WEBHOOK="${ORCHESTRATOR_SLACK_WEBHOOK_URL:-$SLACK_WEBHOOK_URL}"
BOT="${ORCHESTRATOR_SLACK_BOT_TOKEN:-$SLACK_BOT_TOKEN}"
CHAN="${ORCHESTRATOR_SLACK_ALERTS_CHANNEL_ID:-$SLACK_ALERTS_CHANNEL_ID}"
if [[ -n "$WEBHOOK" ]] || { [[ -n "$BOT" ]] && [[ -n "$CHAN" ]]; }; then
  echo "==> Secret orchestrator-slack (a partir do .env)..."
  ORGS=()
  [[ -n "$WEBHOOK" ]] && ORGS+=(--from-literal=SLACK_WEBHOOK_URL="$WEBHOOK")
  [[ -n "$BOT" ]]     && ORGS+=(--from-literal=SLACK_BOT_TOKEN="$BOT")
  [[ -n "$CHAN" ]]    && ORGS+=(--from-literal=SLACK_ALERTS_CHANNEL_ID="$CHAN")
  kubectl create secret generic orchestrator-slack -n "$NS" "${ORGS[@]}" --dry-run=client -o yaml | kubectl apply -f -
  CREATED=1
fi

# --- openclaw-telegram-rotation-source (fonte para CronJob de rotação de tokens)
if [[ -n "$TELEGRAM_BOT_TOKEN" && -n "$TELEGRAM_CHAT_ID" ]]; then
  echo "==> Secret openclaw-telegram-rotation-source (a partir do .env)..."
  kubectl create secret generic openclaw-telegram-rotation-source -n "$NS" \
    --from-literal=TELEGRAM_BOT_TOKEN="$TELEGRAM_BOT_TOKEN" \
    --from-literal=TELEGRAM_CHAT_ID="$TELEGRAM_CHAT_ID" \
    --dry-run=client -o yaml | kubectl apply -f -
  CREATED=1
fi

if [[ $CREATED -eq 1 ]]; then
  echo "==> Secrets aplicados a partir do .env."
else
  echo "==> Nenhuma variável de secret definida no .env; usando apenas secrets opcionais/arquivos."
fi
exit 0
