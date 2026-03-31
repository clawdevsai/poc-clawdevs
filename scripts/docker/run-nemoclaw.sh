#!/usr/bin/env bash

set -euo pipefail

ENV_FILE="${1:-.env}"
STACK_NETWORK="${2:-clawdevs}"
NEMOCLAW_IMAGE="${3:-clawdevsai/nemoclaw-runtime:local}"
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
  --gpus all \
  -p 18789:18789 \
  --privileged \
  --cgroupns=host \
  --env-file "$ENV_FILE" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /sys/fs/cgroup:/sys/fs/cgroup:rw \
  -v nemoclaw-data:/data/nemoclaw \
  -e OLLAMA_BASE_URL=http://ollama:11434 \
  -e NEMOCLAW_RUNTIME_NAME="${NEMOCLAW_RUNTIME_NAME:-nemoclaw}" \
  -e NEMOCLAW_INFERENCE_PROFILE="${NEMOCLAW_INFERENCE_PROFILE:-local-first}" \
  -e NEMOCLAW_PROVIDER_ORDER="${NEMOCLAW_PROVIDER_ORDER:-ollama-local,ollama-cloud}" \
  -e NEMOCLAW_FALLBACK_ENABLED="${NEMOCLAW_FALLBACK_ENABLED:-true}" \
  -e NEMOCLAW_SANDBOX_NAME="${NEMOCLAW_SANDBOX_NAME:-clawdevs-ai}" \
  -e NEMOCLAW_PROVIDER="${NEMOCLAW_PROVIDER:-ollama}" \
  -e NEMOCLAW_MODEL="${NEMOCLAW_MODEL:-mistral}" \
  -e NEMOCLAW_POLICY_MODE="${NEMOCLAW_POLICY_MODE:-skip}" \
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
  --health-cmd="curl -sf http://localhost:18789/healthz" \
  --health-interval=10s --health-timeout=5s --health-retries=30 --health-start-period=120s \
  --restart unless-stopped \
  "$NEMOCLAW_IMAGE" >/dev/null

wait_for_health clawdevs-nemoclaw 360
