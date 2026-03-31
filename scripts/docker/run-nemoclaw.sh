#!/usr/bin/env bash

set -euo pipefail

ENV_FILE="${1:-.env}"
STACK_NETWORK="${2:-clawdevs}"
NEMOCLAW_IMAGE="${3:-clawdevsai/openclaw-runtime:local}"
BOOTSTRAP_SCRIPTS_DIR="${4:-docker/base/bootstrap-scripts}"

HOST_PWD="$(pwd)"
DOCKER_BIN=(docker)
if [ "${OS:-}" = "Windows_NT" ] || [[ "${OSTYPE:-}" == msys* ]] || [[ "${OSTYPE:-}" == cygwin* ]]; then
  HOST_PWD="$(pwd -W 2>/dev/null || pwd)"
  HOST_PWD="${HOST_PWD//\\//}"
  DOCKER_BIN=(env MSYS_NO_PATHCONV=1 MSYS2_ARG_CONV_EXCL='*' docker)
fi

load_env_file() {
  local env_file="$1"
  while IFS= read -r raw_line || [ -n "$raw_line" ]; do
    line="${raw_line%$'\r'}"
    case "$line" in
      ''|\#*) continue ;;
    esac
    key="${line%%=*}"
    value="${line#*=}"
    key="$(printf '%s' "$key" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
    key="${key#export }"
    if ! printf '%s' "$key" | grep -Eq '^[A-Za-z_][A-Za-z0-9_]*$'; then
      echo "[nemoclaw-up] ERRO: chave invalida no .env: $key"
      return 1
    fi
    export "$key=$value"
  done < "$env_file"
}

wait_for_health() {
  local name="${1:-}"
  local timeout="${2:-360}"
  local elapsed=0
  local status=""
  while true; do
    status="$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$name" 2>/dev/null || true)"
    if [ "$status" = "healthy" ] || [ "$status" = "running" ]; then
      echo "[nemoclaw-up] $name pronto ($status)"
      return 0
    fi
    if [ "$status" = "exited" ] || [ "$status" = "dead" ] || [ "$status" = "unhealthy" ]; then
      echo "[nemoclaw-up] ERRO: $name em estado $status"
      docker logs "$name" || true
      return 1
    fi
    if [ "$elapsed" -ge "$timeout" ]; then
      echo "[nemoclaw-up] ERRO: timeout aguardando $name"
      docker logs "$name" || true
      return 1
    fi
    sleep 2
    elapsed=$((elapsed + 2))
  done
}

load_env_file "$ENV_FILE"
TELEGRAM_CHAT_ID_EFFECTIVE="${TELEGRAM_CHAT_ID_CEO:-${TELEGRAM_CHAT_ID:-}}"

if [ "${NEMOCLAW_EXTERNAL:-false}" = "true" ]; then
  echo "[nemoclaw-up] modo external habilitado; validando runtime no host."

  if [ -z "${NEMOCLAW_GATEWAY_URL:-}" ]; then
    echo "[nemoclaw-up][erro] NEMOCLAW_GATEWAY_URL nao configurado."
    echo "[nemoclaw-up] Sugestao: NEMOCLAW_GATEWAY_URL=http://host.docker.internal:18789"
    exit 1
  fi

  if command -v nemoclaw >/dev/null 2>&1; then
    # Best-effort: validate sandbox state when CLI is available.
    if ! nemoclaw clawdevs-ai status --json >/dev/null 2>&1; then
      echo "[nemoclaw-up][erro] sandbox 'clawdevs-ai' nao esta pronto no host."
      echo "[nemoclaw-up] Execute no host:"
      echo "  curl -fsSL https://www.nvidia.com/nemoclaw.sh | bash"
      echo "  nemoclaw onboard   # escolha o nome: clawdevs-ai"
      echo "  openshell term     # aprovar egress/policies quando solicitado"
      exit 1
    fi
  else
    echo "[nemoclaw-up][warn] comando 'nemoclaw' nao encontrado no PATH (modo external)."
    echo "[nemoclaw-up][warn] vou validar apenas o gateway via healthz. Para validar sandbox via CLI:"
    echo "  curl -fsSL https://www.nvidia.com/nemoclaw.sh | bash"
    echo "  nemoclaw onboard   # escolha o nome: clawdevs-ai"
  fi

  if command -v curl >/dev/null 2>&1; then
    if ! curl -sf "${NEMOCLAW_GATEWAY_URL%/}/healthz" >/dev/null 2>&1; then
      echo "[nemoclaw-up][erro] gateway nao respondeu em ${NEMOCLAW_GATEWAY_URL%/}/healthz"
      echo "[nemoclaw-up] Verifique o gateway/sandbox e aprove policy prompts em: openshell term"
      exit 1
    fi
  else
    echo "[nemoclaw-up][erro] comando 'curl' nao encontrado; nao foi possivel validar healthz."
    exit 1
  fi

  echo "[nemoclaw-up] ok: runtime external pronto (${NEMOCLAW_GATEWAY_URL%/})"
  exit 0
fi

echo "[up] iniciando clawdevs-nemoclaw"
docker rm -f clawdevs-nemoclaw >/dev/null 2>&1 || true
"${DOCKER_BIN[@]}" run -d --name clawdevs-nemoclaw --network "$STACK_NETWORK" --network-alias nemoclaw --network-alias openclaw \
  -p 18789:18789 \
  --env-file "$ENV_FILE" \
  -v openclaw-data:/data/openclaw \
  -v "$HOST_PWD/docker/base/openclaw-config:/bootstrap/openclaw-config:ro" \
  -v "$HOST_PWD/$BOOTSTRAP_SCRIPTS_DIR:/bootstrap/scripts:ro" \
  -v panel-token:/panel-token:ro \
  -e HOME=/data/openclaw \
  -e OPENCLAW_STATE_DIR=/data/openclaw \
  -e GH_CONFIG_DIR=/data/openclaw/.config/gh \
  -e MEMORY_BASE_PATH=/data/openclaw/memory \
  -e OLLAMA_BASE_URL=http://ollama:11434 \
  -e NEMOCLAW_RUNTIME_NAME="${NEMOCLAW_RUNTIME_NAME:-nemoclaw}" \
  -e NEMOCLAW_INFERENCE_PROFILE="${NEMOCLAW_INFERENCE_PROFILE:-local-first}" \
  -e NEMOCLAW_PROVIDER_ORDER="${NEMOCLAW_PROVIDER_ORDER:-ollama-local,ollama-cloud}" \
  -e NEMOCLAW_FALLBACK_ENABLED="${NEMOCLAW_FALLBACK_ENABLED:-true}" \
  -e NEMOCLAW_GATEWAY_TOKEN="${NEMOCLAW_GATEWAY_TOKEN:-${OPENCLAW_GATEWAY_TOKEN}}" \
  -e OPENCLAW_GATEWAY_TOKEN="${NEMOCLAW_GATEWAY_TOKEN:-${OPENCLAW_GATEWAY_TOKEN}}" \
  -e TELEGRAM_BOT_TOKEN_CEO="${TELEGRAM_BOT_TOKEN_CEO}" \
  -e TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID_EFFECTIVE}" \
  -e GH_TOKEN="${GH_TOKEN:-${GITHUB_TOKEN:-${GIT_TOKEN}}}" \
  -e GITHUB_TOKEN="${GITHUB_TOKEN:-${GH_TOKEN:-${GIT_TOKEN}}}" \
  -e GIT_TOKEN="${GIT_TOKEN}" \
  -e GIT_ORG="${GIT_ORG}" \
  -e OLLAMA_API_KEY="${OLLAMA_API_KEY:-}" \
  -e DIRECTORS_NAME="${DIRECTORS_NAME:-Director}" \
  -e LANGUAGE="${LANGUAGE:-pt-BR}" \
  -e PROVEDOR_LLM="${PROVEDOR_LLM:-ollama}" \
  -e OPENROUTER_API_KEY="${OPENROUTER_API_KEY:-}" \
  -e OPENROUTER_MODEL="${OPENROUTER_MODEL:-}" \
  -e OPENROUTER_BASE_URL="${OPENROUTER_BASE_URL:-https://openrouter.ai/api/v1}" \
  -e PANEL_API_URL=http://panel-backend:8000 \
  -e NODE_OPTIONS=--max-old-space-size=1024 \
  -e OPENCLAW_NO_RESPAWN=1 \
  -e OPENCLAW_SANDBOX_MODE="${OPENCLAW_SANDBOX_MODE:-off}" \
  -e NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache \
  -e OPENCLAW_LOG_LEVEL="${OPENCLAW_LOG_LEVEL:-error}" \
  -e DEBUG_LOG_ENABLED="${DEBUG_LOG_ENABLED:-false}" \
  -e OPENCLAW_CRON_LIST_TIMEOUT_SECONDS=8 \
  -e OPENCLAW_CRON_LIST_LOCK_WAIT_SECONDS=15 \
  -e OPENCLAW_SECURITY_AUDIT_DEEP_ON_START=true \
  -e OPENCLAW_SECURITY_AUDIT_TIMEOUT_SECONDS=45 \
  -e OPENCLAW_SECURITY_AUDIT_MAX_RETRIES=60 \
  -e OPENCLAW_SECURITY_AUDIT_RETRY_INTERVAL_SECONDS=5 \
  -e OPENCLAW_SECURITY_AUDIT_CRON_INTERVAL_SECONDS=3600 \
  -e AGENT_ERROR_ROUTER_ENABLED=true \
  -e AGENT_ERROR_ROUTER_INTERVAL_SECONDS=30 \
  -e DEV_BACKEND_CRON_ENABLED="${DEV_BACKEND_CRON_ENABLED:-true}" \
  -e DEV_BACKEND_CRON_NAME=dev_backend_hourly_queue_poll \
  -e DEV_BACKEND_CRON_EXPR="${DEV_BACKEND_CRON_EXPR:-0 * * * *}" \
  -e DEV_BACKEND_CRON_TZ=America/Sao_Paulo \
  -e DEV_FRONTEND_CRON_ENABLED="${DEV_FRONTEND_CRON_ENABLED:-true}" \
  -e DEV_FRONTEND_CRON_NAME=dev_frontend_hourly_queue_poll \
  -e DEV_FRONTEND_CRON_EXPR="${DEV_FRONTEND_CRON_EXPR:-15 * * * *}" \
  -e DEV_FRONTEND_CRON_TZ=America/Sao_Paulo \
  -e DEV_MOBILE_CRON_ENABLED="${DEV_MOBILE_CRON_ENABLED:-true}" \
  -e DEV_MOBILE_CRON_NAME=dev_mobile_hourly_queue_poll \
  -e DEV_MOBILE_CRON_EXPR="${DEV_MOBILE_CRON_EXPR:-30 * * * *}" \
  -e DEV_MOBILE_CRON_TZ=America/Sao_Paulo \
  -e QA_CRON_ENABLED="${QA_CRON_ENABLED:-true}" \
  -e QA_CRON_NAME=qa_engineer_hourly_queue_poll \
  -e QA_CRON_EXPR="${QA_CRON_EXPR:-45 * * * *}" \
  -e QA_CRON_TZ=America/Sao_Paulo \
  -e DEVOPS_SRE_CRON_ENABLED="${DEVOPS_SRE_CRON_ENABLED:-true}" \
  -e DEVOPS_SRE_CRON_NAME=devops_sre_queue_poll \
  -e DEVOPS_SRE_CRON_EXPR="${DEVOPS_SRE_CRON_EXPR:-*/30 * * * *}" \
  -e DEVOPS_SRE_CRON_TZ=America/Sao_Paulo \
  -e SECURITY_ENGINEER_CRON_ENABLED="${SECURITY_ENGINEER_CRON_ENABLED:-true}" \
  -e SECURITY_ENGINEER_CRON_NAME=security_engineer_scan \
  -e SECURITY_ENGINEER_CRON_EXPR="${SECURITY_ENGINEER_CRON_EXPR:-0 */6 * * *}" \
  -e SECURITY_ENGINEER_CRON_TZ=America/Sao_Paulo \
  -e UX_DESIGNER_CRON_ENABLED="${UX_DESIGNER_CRON_ENABLED:-true}" \
  -e UX_DESIGNER_CRON_NAME=ux_designer_queue_poll \
  -e UX_DESIGNER_CRON_EXPR="${UX_DESIGNER_CRON_EXPR:-0 */4 * * *}" \
  -e UX_DESIGNER_CRON_TZ=America/Sao_Paulo \
  -e DBA_DATA_ENGINEER_CRON_ENABLED="${DBA_DATA_ENGINEER_CRON_ENABLED:-true}" \
  -e DBA_DATA_ENGINEER_CRON_NAME=dba_data_engineer_queue_poll \
  -e DBA_DATA_ENGINEER_CRON_EXPR="${DBA_DATA_ENGINEER_CRON_EXPR:-30 */4 * * *}" \
  -e DBA_DATA_ENGINEER_CRON_TZ=America/Sao_Paulo \
  -e MEMORY_CURATOR_CRON_ENABLED="${MEMORY_CURATOR_CRON_ENABLED:-true}" \
  -e MEMORY_CURATOR_CRON_NAME=memory_curator_promote \
  -e MEMORY_CURATOR_CRON_EXPR="${MEMORY_CURATOR_CRON_EXPR:-0 2 * * *}" \
  -e MEMORY_CURATOR_CRON_TZ=America/Sao_Paulo \
  -e OPENCLAW_CONTROL_UI_ALLOWED_ORIGINS_JSON='["http://127.0.0.1:18789","http://localhost:18789","http://openclaw:18789","http://nemoclaw:18789"]' \
  --health-cmd="curl -sf http://localhost:18789/healthz" \
  --health-interval=10s --health-timeout=5s --health-retries=30 --health-start-period=120s \
  --restart unless-stopped \
  "$NEMOCLAW_IMAGE" >/dev/null

wait_for_health clawdevs-nemoclaw 360
