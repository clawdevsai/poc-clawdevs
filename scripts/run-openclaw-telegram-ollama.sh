#!/usr/bin/env bash
# Conecta o OpenClaw ao seu bot do Telegram e usa o Ollama do cluster para responder.
# Pré-requisitos: kubectl (contexto apontando para o cluster com namespace ai-agents), Node.js/npx (openclaw roda via npx).
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

# Validar contexto e Minikube: namespace ai-agents e svc/ollama-service
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
# Porta 11434 no host: usada pelo port-forward para o Ollama no cluster
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

# Gerar config com allowFrom se TELEGRAM_CHAT_ID estiver definido (para dmPolicy allowlist)
if [[ -n "$TELEGRAM_CHAT_ID" ]]; then
  sed "s/\"allowFrom\": \[\]/\"allowFrom\": [\"$TELEGRAM_CHAT_ID\"]/" "$CONFIG_SRC" > "$CONFIG_RUN"
  CONFIG_TO_USE="$CONFIG_RUN"
else
  # Com allowFrom vazio, use dmPolicy "pairing" e aprove o primeiro DM com: openclaw pairing approve telegram <CODE>
  sed 's/"dmPolicy": "allowlist"/"dmPolicy": "pairing"/' "$CONFIG_SRC" > "$CONFIG_RUN"
  CONFIG_TO_USE="$CONFIG_RUN"
fi

# Habilitar Slack quando SLACK_APP_TOKEN e SLACK_BOT_TOKEN estiverem definidos (e SLACK_ENABLED != false)
if [[ -n "${SLACK_APP_TOKEN:-}" && -n "${SLACK_BOT_TOKEN:-}" && "${SLACK_ENABLED:-true}" != "false" ]]; then
  sed 's/enabled: false, \/\/ SLACK_TOGGLE/enabled: true, \/\/ SLACK_TOGGLE/' "$CONFIG_TO_USE" > "$CONFIG_RUN.tmp" && mv "$CONFIG_RUN.tmp" "$CONFIG_TO_USE"
  if [[ -n "${SLACK_DIRECTOR_USER_ID:-}" ]]; then
    sed "s/allowFrom: \[\], \/\/ SLACK_ALLOW_FROM/allowFrom: [\"$SLACK_DIRECTOR_USER_ID\"], \/\/ SLACK_ALLOW_FROM/" "$CONFIG_TO_USE" > "$CONFIG_RUN.tmp" && mv "$CONFIG_RUN.tmp" "$CONFIG_TO_USE"
  fi
  export SLACK_APP_TOKEN SLACK_BOT_TOKEN
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

echo "==> Iniciando OpenClaw gateway (Telegram: só CEO; Slack: todos os agentes; Ollama em 127.0.0.1:11434)..."
echo "    Config: $OPENCLAW_CONFIG_PATH"
echo "    Workspace único: config/openclaw/workspace-ceo (CWD=$REPO_ROOT)"
echo "    Telegram: só CEO. Slack: todos (discussões = Ollama local GPU)."
if [[ -n "${SLACK_APP_TOKEN:-}" && -n "${SLACK_BOT_TOKEN:-}" ]]; then
  echo "    Slack habilitado. Envie mensagem no Slack ou no Telegram para testar."
  echo "    Ex.: no Slack (DM ou canal): \"Pergunta ao Diretor: Qual a prioridade desta semana?\""
else
  echo "    Envie uma mensagem ao seu bot no Telegram para testar."
fi

# Garantir npx no PATH (ex.: nvm não carregado em script)
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

exec npx --yes openclaw@latest gateway
