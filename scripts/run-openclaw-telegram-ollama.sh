#!/usr/bin/env bash
# Conecta o OpenClaw ao seu bot do Telegram e usa o Ollama do cluster para responder.
# Pré-requisitos: kubectl (contexto apontando para o cluster com namespace ai-agents), openclaw CLI.
# Variáveis: TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID (ou arquivo .env na raiz do projeto).
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG_SRC="$REPO_ROOT/config/openclaw/openclaw.local.json5"
CONFIG_RUN="$REPO_ROOT/config/openclaw/openclaw.local.run.json5"
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

if [[ -z "$TELEGRAM_BOT_TOKEN" ]]; then
  echo "Erro: defina TELEGRAM_BOT_TOKEN (ou coloque em .env)."
  exit 1
fi
if [[ -z "$TELEGRAM_CHAT_ID" ]]; then
  echo "Aviso: TELEGRAM_CHAT_ID não definido. Use dmPolicy pairing e 'openclaw pairing approve telegram <CODE>' no primeiro DM."
fi

# Gerar config com allowFrom se TELEGRAM_CHAT_ID estiver definido (para dmPolicy allowlist)
if [[ -n "$TELEGRAM_CHAT_ID" ]]; then
  sed "s/\"allowFrom\": \[\]/\"allowFrom\": [\"$TELEGRAM_CHAT_ID\"]/" "$CONFIG_SRC" > "$CONFIG_RUN"
  CONFIG_TO_USE="$CONFIG_RUN"
else
  CONFIG_TO_USE="$CONFIG_SRC"
  # Com allowFrom vazio, use dmPolicy "pairing" e aprove o primeiro DM com: openclaw pairing approve telegram <CODE>
  sed 's/"dmPolicy": "allowlist"/"dmPolicy": "pairing"/' "$CONFIG_SRC" > "$CONFIG_RUN"
  CONFIG_TO_USE="$CONFIG_RUN"
fi

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

echo "==> Iniciando OpenClaw gateway (Telegram + Ollama em 127.0.0.1:11434)..."
echo "    Config: $OPENCLAW_CONFIG_PATH"
echo "    Envie uma mensagem ao seu bot no Telegram para testar."
exec openclaw gateway
