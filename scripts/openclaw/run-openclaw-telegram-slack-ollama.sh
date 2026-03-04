#!/usr/bin/env bash
# DESCONTINUADO: o gateway deve rodar apenas no K8s. Use: make up, scripts/openclaw/k8s-openclaw-secret-from-env.sh, kubectl rollout restart deployment/openclaw -n ai-agents.
# Este script é só para emergência/debug local (ex.: port-forward do Ollama + gateway no host).
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
CONFIG_SRC="$REPO_ROOT/k8s/management-team/openclaw/openclaw.local.json5.example"
CONFIG_RUN="${TMPDIR:-/tmp}/openclaw.local.run.json5.$$"
PF_PID=""

cleanup() {
  if [[ -n "$PF_PID" ]] && kill -0 "$PF_PID" 2>/dev/null; then
    echo "Encerrando port-forward (PID $PF_PID)..."
    kill "$PF_PID" 2>/dev/null || true
  fi
  rm -f "$CONFIG_RUN"
}
trap cleanup EXIT

cd "$REPO_ROOT"
if [[ -f "$REPO_ROOT/.env" ]]; then
  set -a
  source "$REPO_ROOT/.env"
  set +a
fi

SLACK_APP_TOKEN="${OPENCLAW_SLACK_APP_TOKEN:-$SLACK_APP_TOKEN}"
SLACK_BOT_TOKEN="${OPENCLAW_SLACK_BOT_TOKEN:-$SLACK_BOT_TOKEN}"
SLACK_DIRECTOR_USER_ID="${OPENCLAW_SLACK_DIRECTOR_USER_ID:-$SLACK_DIRECTOR_USER_ID}"
SLACK_ALLOWED_USER_IDS="${OPENCLAW_SLACK_ALLOWED_USER_IDS:-$SLACK_ALLOWED_USER_IDS}"
SLACK_ALL_CLAWDEVSAI_CHANNEL_ID="${OPENCLAW_SLACK_ALL_CLAWDEVSAI_CHANNEL_ID:-$SLACK_ALL_CLAWDEVSAI_CHANNEL_ID}"
SLACK_ENABLED="${OPENCLAW_SLACK_ENABLED:-$SLACK_ENABLED}"

if [[ -z "$TELEGRAM_BOT_TOKEN" ]]; then
  echo "Erro: defina TELEGRAM_BOT_TOKEN (ou coloque em .env)."
  exit 1
fi
if [[ -z "$TELEGRAM_CHAT_ID" ]]; then
  echo "Aviso: TELEGRAM_CHAT_ID não definido. Use dmPolicy pairing e 'openclaw pairing approve telegram <CODE>' no primeiro DM."
fi

CTX="$(kubectl config current-context 2>/dev/null || true)"
if [[ -z "$CTX" ]]; then
  echo "Erro: kubectl sem contexto. Configure o cluster (ex.: minikube)."
  exit 1
fi
echo "==> Contexto kubectl: $CTX"
if ! kubectl get namespace ai-agents >/dev/null 2>&1; then
  echo "Erro: namespace ai-agents não existe. Rode 'make up' no repositório."
  exit 1
fi
if ! kubectl get svc ollama-service -n ai-agents >/dev/null 2>&1; then
  echo "Erro: svc/ollama-service não existe em ai-agents. Rode 'make up'."
  exit 1
fi
if command -v ss >/dev/null 2>&1; then
  if ss -tlnp 2>/dev/null | grep -q ':11434 '; then
    echo "Aviso: porta 11434 já está em uso no host. Libere ou use outro processo (ex.: mate o port-forward anterior)."
  fi
elif command -v lsof >/dev/null 2>&1; then
  if lsof -i :11434 >/dev/null 2>&1; then
    echo "Aviso: porta 11434 já está em uso no host. Libere ou use outro processo."
  fi
fi
echo "==> Ambiente validado: contexto=$CTX, namespace ai-agents, svc/ollama-service; porta 11434 (port-forward) livre no host."

if [[ -n "$TELEGRAM_CHAT_ID" ]]; then
  sed "s/\"allowFrom\": \[\]/\"allowFrom\": [\"$TELEGRAM_CHAT_ID\"]/" "$CONFIG_SRC" > "$CONFIG_RUN"
  CONFIG_TO_USE="$CONFIG_RUN"
else
  sed 's/"dmPolicy": "allowlist"/"dmPolicy": "pairing"/' "$CONFIG_SRC" > "$CONFIG_RUN"
  CONFIG_TO_USE="$CONFIG_RUN"
fi

if [[ -n "${SLACK_APP_TOKEN:-}" && -n "${SLACK_BOT_TOKEN:-}" && "${SLACK_ENABLED:-true}" != "false" ]]; then
  sed 's/enabled: false, \/\/ SLACK_TOGGLE/enabled: true, \/\/ SLACK_TOGGLE/' "$CONFIG_TO_USE" > "$CONFIG_RUN.tmp" && mv "$CONFIG_RUN.tmp" "$CONFIG_TO_USE"
  SLACK_ALLOW_FROM_IDS=()
  [[ -n "${SLACK_DIRECTOR_USER_ID:-}" ]] && SLACK_ALLOW_FROM_IDS+=("$SLACK_DIRECTOR_USER_ID")
  if [[ -n "${SLACK_ALLOWED_USER_IDS:-}" ]]; then
    while IFS=',' read -ra IDS; do
      for id in "${IDS[@]}"; do
        id="${id// /}"
        [[ -n "$id" ]] && SLACK_ALLOW_FROM_IDS+=("$id")
      done
    done <<< "$SLACK_ALLOWED_USER_IDS"
  fi
  if [[ ${#SLACK_ALLOW_FROM_IDS[@]} -gt 0 ]]; then
    ALLOW_JSON="[$(printf '"%s",' "${SLACK_ALLOW_FROM_IDS[@]}" | sed 's/,$//')]"
    sed "s/allowFrom: \[\], \/\/ SLACK_ALLOW_FROM/allowFrom: $ALLOW_JSON, \/\/ SLACK_ALLOW_FROM/" "$CONFIG_TO_USE" > "$CONFIG_RUN.tmp" && mv "$CONFIG_RUN.tmp" "$CONFIG_TO_USE"
  else
    sed '/mode: "socket",/,/SLACK_ALLOW_FROM/ s/dmPolicy: "allowlist"/dmPolicy: "pairing"/' "$CONFIG_TO_USE" > "$CONFIG_RUN.tmp" && mv "$CONFIG_RUN.tmp" "$CONFIG_TO_USE"
  fi
  export SLACK_APP_TOKEN SLACK_BOT_TOKEN
fi
CHAN_ID="${SLACK_ALL_CLAWDEVSAI_CHANNEL_ID:-CDAHISCLSQKC}"
sed "s/__SLACK_ALL_CLAWDEVSAI_CHANNEL_ID__/$CHAN_ID/g" "$CONFIG_TO_USE" > "$CONFIG_RUN.tmp" && mv "$CONFIG_RUN.tmp" "$CONFIG_TO_USE"

export TELEGRAM_BOT_TOKEN
export OPENCLAW_CONFIG_PATH="$CONFIG_TO_USE"

echo "==> Port-forward Ollama (svc/ollama-service :11434)..."
kubectl port-forward -n ai-agents svc/ollama-service 11434:11434 &
PF_PID=$!
sleep 2
if ! kill -0 "$PF_PID" 2>/dev/null; then
  echo "Erro: port-forward falhou. Confira se o namespace ai-agents e o svc/ollama-service existem (make up)."
  exit 1
fi

echo "==> Iniciando OpenClaw gateway (Telegram: só CEO; Slack: todos os agentes; Ollama em 127.0.0.1:11434)..."
echo "    Config: $OPENCLAW_CONFIG_PATH"
echo "    Config: k8s/management-team/openclaw (CWD=$REPO_ROOT)"
echo "    Telegram: só CEO. Slack: todos (discussões = Ollama local GPU)."
if [[ -n "${SLACK_APP_TOKEN:-}" && -n "${SLACK_BOT_TOKEN:-}" ]]; then
  echo "    Slack habilitado. Envie mensagem no Slack ou no Telegram para testar."
  echo "    Se alguém mandar DM e nada acontecer: adicione o Slack User ID em OPENCLAW_SLACK_ALLOWED_USER_IDS no .env (ou use pairing). Log: OPENCLAW_LOG=1 ./scripts/openclaw/run-openclaw-telegram-slack-ollama.sh"
else
  echo "    Envie uma mensagem ao seu bot no Telegram para testar."
fi

if ! command -v npx >/dev/null 2>&1; then
  if [[ -f "$HOME/.nvm/nvm.sh" ]]; then
    echo "==> Carregando nvm para usar npx..."
    source "$HOME/.nvm/nvm.sh"
  fi
fi
if ! command -v npx >/dev/null 2>&1; then
  echo "Erro: npx não encontrado. Instale Node.js (https://nodejs.org) ou rode com nvm ativo: source ~/.nvm/nvm.sh && $0"
  exit 1
fi

LOG_FILE=""
if [[ -n "${OPENCLAW_LOG:-}" ]]; then
  if [[ "$OPENCLAW_LOG" == "1" ]]; then
    mkdir -p "$REPO_ROOT/logs"
    LOG_FILE="$REPO_ROOT/logs/openclaw-gateway.log"
  else
    LOG_FILE="$OPENCLAW_LOG"
  fi
  echo "    Log gateway: $LOG_FILE (tail -f para acompanhar)"
  exec npx --yes openclaw@2026.3.2 gateway 2>&1 | tee -a "$LOG_FILE"
fi

exec npx --yes openclaw@2026.3.2 gateway
