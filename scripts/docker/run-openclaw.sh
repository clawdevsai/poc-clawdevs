#!/usr/bin/env bash

set -euo pipefail

ENV_FILE="${1:-.env}"
STACK_NETWORK="${2:-clawdevs}"
OPENCLAW_IMAGE="${3:-clawdevsai/openclaw-runtime:local}"
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
      echo "[openclaw-up] ERRO: chave invalida no .env: $key"
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
      echo "[openclaw-up] $name pronto ($status)"
      return 0
    fi
    if [ "$status" = "exited" ] || [ "$status" = "dead" ] || [ "$status" = "unhealthy" ]; then
      echo "[openclaw-up] ERRO: $name em estado $status"
      docker logs "$name" || true
      return 1
    fi
    if [ "$elapsed" -ge "$timeout" ]; then
      echo "[openclaw-up] ERRO: timeout aguardando $name"
      docker logs "$name" || true
      return 1
    fi
    sleep 2
    elapsed=$((elapsed + 2))
  done
}

load_env_file "$ENV_FILE"

echo "[up] iniciando clawdevs-openclaw"
docker rm -f clawdevs-openclaw >/dev/null 2>&1 || true
"${DOCKER_BIN[@]}" run -d --name clawdevs-openclaw --network "$STACK_NETWORK" --network-alias openclaw \
  -p 18789:18789 \
  --privileged \
  --cgroupns=host \
  --env-file "$ENV_FILE" \
  -v /var/run/docker.sock:/var/run/docker.sock \
  -v /sys/fs/cgroup:/sys/fs/cgroup:rw \
  -v openclaw-data:/data/openclaw \
  -v "${HOST_PWD}/${BOOTSTRAP_SCRIPTS_DIR}:/opt/bootstrap-scripts:ro" \
  -e OPENCLAW_STATE_DIR=/data/openclaw \
  -e OPENCLAW_GATEWAY_PORT=18789 \
  -e BOOTSTRAP_SCRIPTS_DIR=/opt/bootstrap-scripts \
  -e GH_TOKEN="${GH_TOKEN:-${GITHUB_TOKEN:-${GIT_TOKEN}}}" \
  -e GITHUB_TOKEN="${GITHUB_TOKEN:-${GH_TOKEN:-${GIT_TOKEN}}}" \
  -e GIT_TOKEN="${GIT_TOKEN}" \
  -e GIT_ORG="${GIT_ORG}" \
  -e OLLAMA_API_KEY="${OLLAMA_API_KEY:-}" \
  -e DIRECTORS_NAME="${DIRECTORS_NAME:-Director}" \
  -e LANGUAGE="${LANGUAGE:-pt-BR}" \
  -e OPENCLAW_GATEWAY_TOKEN="${OPENCLAW_GATEWAY_TOKEN:-}" \
  -e TELEGRAM_BOT_TOKEN_CEO="${TELEGRAM_BOT_TOKEN_CEO:-}" \
  -e TELEGRAM_CHAT_ID="${TELEGRAM_CHAT_ID_CEO:-${TELEGRAM_CHAT_ID:-}}" \
  --health-cmd="curl -sf http://localhost:18789/healthz" \
  --health-interval=10s --health-timeout=5s --health-retries=30 --health-start-period=120s \
  --restart unless-stopped \
  "$OPENCLAW_IMAGE" >/dev/null

wait_for_health clawdevs-openclaw 360
