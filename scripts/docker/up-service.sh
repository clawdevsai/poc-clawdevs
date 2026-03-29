#!/usr/bin/env bash

set -euo pipefail

SERVICE="${1:-}"
if [ -z "${SERVICE}" ]; then
  echo "Usage: up-service.sh <service>"
  exit 1
fi

ENV_FILE="${ENV_FILE:-.env}"
STACK_NETWORK="${STACK_NETWORK:-clawdevs}"
POSTGRES_IMAGE="${POSTGRES_IMAGE:-clawdevsai/postgres-runtime:local}"
REDIS_IMAGE="${REDIS_IMAGE:-clawdevsai/redis-runtime:local}"
OLLAMA_IMAGE="${OLLAMA_IMAGE:-clawdevsai/ollama-runtime:local}"
SEARXNG_IMAGE="${SEARXNG_IMAGE:-clawdevsai/searxng-runtime:local}"
SEARXNG_PROXY_IMAGE="${SEARXNG_PROXY_IMAGE:-clawdevsai/searxng-proxy:local}"
PANEL_BACKEND_IMAGE="${PANEL_BACKEND_IMAGE:-clawdevsai/clawdevs-panel-backend:local}"
PANEL_WORKER_IMAGE="${PANEL_WORKER_IMAGE:-clawdevsai/clawdevs-panel-worker:local}"
PANEL_FRONTEND_IMAGE="${PANEL_FRONTEND_IMAGE:-clawdevsai/clawdevs-panel-frontend:local}"
TOKEN_INIT_IMAGE="${TOKEN_INIT_IMAGE:-clawdevsai/token-init-runtime:local}"
SEARXNG_PROXY_CONF="${SEARXNG_PROXY_CONF:-docker/clawdevs-searxng-proxy/default.conf}"

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
      echo "[up-${SERVICE}] ERRO: chave invalida no .env: $key"
      return 1
    fi
    export "$key=$value"
  done < "$env_file"
}

wait_for_health() {
  local name="${1:-}"
  local timeout="${2:-180}"
  local elapsed=0
  local status=""
  while true; do
    status="$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$name" 2>/dev/null || true)"
    if [ "$status" = "healthy" ] || [ "$status" = "running" ]; then
      echo "[up-${SERVICE}] $name pronto ($status)"
      return 0
    fi
    if [ "$status" = "exited" ] || [ "$status" = "dead" ] || [ "$status" = "unhealthy" ]; then
      echo "[up-${SERVICE}] ERRO: $name em estado $status"
      docker logs "$name" || true
      return 1
    fi
    if [ "$elapsed" -ge "$timeout" ]; then
      echo "[up-${SERVICE}] ERRO: timeout aguardando $name"
      docker logs "$name" || true
      return 1
    fi
    sleep 2
    elapsed=$((elapsed + 2))
  done
}

wait_for_running() {
  local name="${1:-}"
  local timeout="${2:-120}"
  local elapsed=0
  local status=""
  while true; do
    status="$(docker inspect -f '{{.State.Status}}' "$name" 2>/dev/null || true)"
    if [ "$status" = "running" ]; then
      echo "[up-${SERVICE}] $name pronto ($status)"
      return 0
    fi
    if [ "$status" = "exited" ] || [ "$status" = "dead" ]; then
      echo "[up-${SERVICE}] ERRO: $name em estado $status"
      docker logs "$name" || true
      return 1
    fi
    if [ "$elapsed" -ge "$timeout" ]; then
      echo "[up-${SERVICE}] ERRO: timeout aguardando $name"
      docker logs "$name" || true
      return 1
    fi
    sleep 2
    elapsed=$((elapsed + 2))
  done
}

wait_for_exit_success() {
  local name="${1:-}"
  local timeout="${2:-180}"
  local elapsed=0
  local status=""
  while true; do
    status="$(docker inspect -f '{{.State.Status}}' "$name" 2>/dev/null || true)"
    if [ "$status" = "exited" ]; then
      code="$(docker inspect -f '{{.State.ExitCode}}' "$name")"
      if [ "$code" = "0" ]; then
        echo "[up-${SERVICE}] $name concluido com sucesso"
        return 0
      fi
      echo "[up-${SERVICE}] ERRO: $name finalizou com exit code $code"
      docker logs "$name" || true
      return 1
    fi
    if [ "$status" = "dead" ] || [ -z "$status" ]; then
      echo "[up-${SERVICE}] ERRO: $name em estado $status"
      docker logs "$name" || true
      return 1
    fi
    if [ "$elapsed" -ge "$timeout" ]; then
      echo "[up-${SERVICE}] ERRO: timeout aguardando $name"
      docker logs "$name" || true
      return 1
    fi
    sleep 2
    elapsed=$((elapsed + 2))
  done
}

load_env_file "$ENV_FILE"
docker network inspect "$STACK_NETWORK" >/dev/null 2>&1 || docker network create "$STACK_NETWORK" >/dev/null

case "$SERVICE" in
  postgres)
    docker volume inspect postgres-data >/dev/null 2>&1 || docker volume create postgres-data >/dev/null
    docker rm -f clawdevs-postgres >/dev/null 2>&1 || true
    docker run -d --name clawdevs-postgres --network "$STACK_NETWORK" --network-alias postgres \
      -e POSTGRES_DB=clawdevs_panel \
      -e POSTGRES_USER=panel \
      -e POSTGRES_PASSWORD="${PANEL_DB_PASSWORD}" \
      -v postgres-data:/var/lib/postgresql/data \
      --health-cmd="pg_isready -U panel -d clawdevs_panel" \
      --health-interval=5s --health-timeout=3s --health-retries=10 --health-start-period=10s \
      --restart unless-stopped \
      "$POSTGRES_IMAGE" >/dev/null
    wait_for_health clawdevs-postgres 180
    ;;
  redis)
    docker rm -f clawdevs-redis >/dev/null 2>&1 || true
    docker run -d --name clawdevs-redis --network "$STACK_NETWORK" --network-alias redis \
      -e PANEL_REDIS_PASSWORD="${PANEL_REDIS_PASSWORD}" \
      --health-cmd="sh -c 'redis-cli -a \$PANEL_REDIS_PASSWORD ping | grep PONG'" \
      --health-interval=5s --health-timeout=3s --health-retries=10 --health-start-period=5s \
      --restart unless-stopped \
      "$REDIS_IMAGE" \
      redis-server --requirepass "${PANEL_REDIS_PASSWORD}" >/dev/null
    wait_for_health clawdevs-redis 120
    ;;
  ollama)
    docker volume inspect ollama-data >/dev/null 2>&1 || docker volume create ollama-data >/dev/null
    docker rm -f clawdevs-ollama >/dev/null 2>&1 || true
    docker run -d --name clawdevs-ollama --network "$STACK_NETWORK" --network-alias ollama \
      -p 11434:11434 \
      -v ollama-data:/root/.ollama \
      -e OLLAMA_HOST=0.0.0.0:11434 \
      -e OLLAMA_GPU_MEMORY=4096 \
      -e CUDA_MEM_POOL_MAX_SPLIT_SIZE_MB=512 \
      -e OLLAMA_API_KEY="${OLLAMA_API_KEY:-}" \
      -e OLLAMA_AUTO_PULL_MODELS="${OLLAMA_AUTO_PULL_MODELS:-true}" \
      -e OLLAMA_BOOT_MODELS="${OLLAMA_BOOT_MODELS:-nomic-embed-text}" \
      --health-cmd="ollama list" \
      --health-interval=15s --health-timeout=30s --health-retries=40 --health-start-period=180s \
      --restart unless-stopped \
      "$OLLAMA_IMAGE" >/dev/null
    wait_for_health clawdevs-ollama 600
    ;;
  searxng)
    docker rm -f clawdevs-searxng >/dev/null 2>&1 || true
    docker run -d --name clawdevs-searxng --network "$STACK_NETWORK" --network-alias searxng \
      -e SEARXNG_SETTINGS_PATH=//etc/searxng/settings.yml \
      -e SEARXNG_SECRET="${SEARXNG_SECRET}" \
      --health-cmd="wget -qO- http://localhost:8080/healthz" \
      --health-interval=10s --health-timeout=3s --health-retries=6 --health-start-period=15s \
      --restart unless-stopped \
      "$SEARXNG_IMAGE" >/dev/null
    wait_for_health clawdevs-searxng 180
    ;;
  searxng-proxy)
    docker rm -f clawdevs-searxng-proxy >/dev/null 2>&1 || true
    "${DOCKER_BIN[@]}" run -d --name clawdevs-searxng-proxy --network "$STACK_NETWORK" --network-alias searxng-proxy \
      -p 18080:18080 \
      -v "$HOST_PWD/$SEARXNG_PROXY_CONF:/etc/nginx/conf.d/default.conf:ro" \
      --health-cmd="wget -qO- http://127.0.0.1:18080/healthz" \
      --health-interval=10s --health-timeout=3s --health-retries=6 --health-start-period=10s \
      --restart unless-stopped \
      "$SEARXNG_PROXY_IMAGE" >/dev/null
    wait_for_health clawdevs-searxng-proxy 180
    ;;
  panel-backend)
    docker volume inspect openclaw-data >/dev/null 2>&1 || docker volume create openclaw-data >/dev/null
    docker rm -f clawdevs-panel-backend >/dev/null 2>&1 || true
    docker run -d --name clawdevs-panel-backend --network "$STACK_NETWORK" --network-alias panel-backend \
      -p 8000:8000 \
      -v openclaw-data:/data/openclaw \
      -e PYTHONPATH=/app \
      -e PANEL_DB_PASSWORD="${PANEL_DB_PASSWORD}" \
      -e PANEL_REDIS_PASSWORD="${PANEL_REDIS_PASSWORD}" \
      -e PANEL_DATABASE_URL="postgresql+asyncpg://panel:${PANEL_DB_PASSWORD}@postgres:5432/clawdevs_panel" \
      -e PANEL_REDIS_URL="redis://:${PANEL_REDIS_PASSWORD}@redis:6379/0" \
      -e PANEL_OPENCLAW_GATEWAY_URL=http://openclaw:18789 \
      -e PANEL_SECRET_KEY="${PANEL_SECRET_KEY}" \
      -e PANEL_ADMIN_USERNAME="${PANEL_ADMIN_USERNAME}" \
      -e PANEL_ADMIN_PASSWORD="${PANEL_ADMIN_PASSWORD}" \
      -e GIT_TOKEN="${GIT_TOKEN}" \
      -e GH_TOKEN="${GH_TOKEN:-${GITHUB_TOKEN:-${GIT_TOKEN}}}" \
      -e GITHUB_TOKEN="${GITHUB_TOKEN:-${GH_TOKEN:-${GIT_TOKEN}}}" \
      -e GIT_ORG="${GIT_ORG}" \
      --health-cmd="curl -sf http://localhost:8000/healthz" \
      --health-interval=10s --health-timeout=5s --health-retries=10 --health-start-period=20s \
      --restart unless-stopped \
      "$PANEL_BACKEND_IMAGE" \
      sh -c 'alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port 8000' >/dev/null
    wait_for_health clawdevs-panel-backend 240
    ;;
  panel-worker)
    docker volume inspect openclaw-data >/dev/null 2>&1 || docker volume create openclaw-data >/dev/null
    docker rm -f clawdevs-panel-worker >/dev/null 2>&1 || true
    docker run -d --name clawdevs-panel-worker --network "$STACK_NETWORK" --network-alias panel-worker \
      -v openclaw-data:/data/openclaw:ro \
      -e PYTHONPATH=/app \
      -e PANEL_DB_PASSWORD="${PANEL_DB_PASSWORD}" \
      -e PANEL_REDIS_PASSWORD="${PANEL_REDIS_PASSWORD}" \
      -e PANEL_DATABASE_URL="postgresql+asyncpg://panel:${PANEL_DB_PASSWORD}@postgres:5432/clawdevs_panel" \
      -e PANEL_REDIS_URL="redis://:${PANEL_REDIS_PASSWORD}@redis:6379/0" \
      -e GIT_TOKEN="${GIT_TOKEN}" \
      -e GH_TOKEN="${GH_TOKEN:-${GITHUB_TOKEN:-${GIT_TOKEN}}}" \
      -e GITHUB_TOKEN="${GITHUB_TOKEN:-${GH_TOKEN:-${GIT_TOKEN}}}" \
      -e GIT_ORG="${GIT_ORG}" \
      --restart unless-stopped \
      "$PANEL_WORKER_IMAGE" >/dev/null
    wait_for_running clawdevs-panel-worker 120
    ;;
  panel-frontend)
    docker rm -f clawdevs-panel-frontend >/dev/null 2>&1 || true
    docker run -d --name clawdevs-panel-frontend --network "$STACK_NETWORK" --network-alias panel-frontend \
      -p 3000:3000 \
      -e BACKEND_URL=http://panel-backend:8000 \
      -e OPENCLAW_GATEWAY_URL="${OPENCLAW_GATEWAY_URL:-http://openclaw:18789}" \
      -e PANEL_OPENCLAW_GATEWAY_URL="${PANEL_OPENCLAW_GATEWAY_URL:-http://openclaw:18789}" \
      -e OPENCLAW_GATEWAY_TOKEN="${OPENCLAW_GATEWAY_TOKEN}" \
      -e PANEL_OPENCLAW_GATEWAY_TOKEN="${PANEL_OPENCLAW_GATEWAY_TOKEN:-${OPENCLAW_GATEWAY_TOKEN}}" \
      -e NODE_ENV=production \
      --restart unless-stopped \
      "$PANEL_FRONTEND_IMAGE" >/dev/null
    wait_for_running clawdevs-panel-frontend 120
    ;;
  token-init)
    docker volume inspect panel-token >/dev/null 2>&1 || docker volume create panel-token >/dev/null
    docker rm -f clawdevs-token-init >/dev/null 2>&1 || true
    docker run -d --name clawdevs-token-init --network "$STACK_NETWORK" --network-alias token-init \
      --user 0:0 \
      -e PANEL_ADMIN_USERNAME="${PANEL_ADMIN_USERNAME}" \
      -e PANEL_ADMIN_PASSWORD="${PANEL_ADMIN_PASSWORD}" \
      -v panel-token:/panel-token \
      --restart no \
      "$TOKEN_INIT_IMAGE" >/dev/null
    wait_for_exit_success clawdevs-token-init 180
    ;;
  openclaw)
    bash scripts/docker/run-openclaw.sh "$ENV_FILE" "$STACK_NETWORK" "${OPENCLAW_IMAGE:-clawdevsai/openclaw-runtime:local}" \
      "${AGENT_CONFIG_FLAT_DIR:-tmp/agent-config-flat}" "${BOOTSTRAP_SCRIPTS_DIR:-docker/base/bootstrap-scripts}"
    ;;
  *)
    echo "Servico invalido: $SERVICE"
    echo "Servicos: postgres redis ollama searxng searxng-proxy panel-backend panel-worker panel-frontend token-init openclaw"
    exit 1
    ;;
esac
