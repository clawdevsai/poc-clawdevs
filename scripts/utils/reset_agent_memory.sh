#!/usr/bin/env bash
# Reset de memória dos agentes: Redis (project:v1:*) e workspace no K8s (restart do openclaw para reaplicar templates).
# Uso: make reset-memory  ou  RESET_REDIS=0 ./scripts/utils/reset_agent_memory.sh  ou  RESET_REPO=0 ...
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
REDIS_HOST="${REDIS_HOST:-}"
REDIS_PORT="${REDIS_PORT:-6379}"
RESET_REDIS="${RESET_REDIS:-1}"
RESET_REPO="${RESET_REPO:-1}"
NAMESPACE="${K8S_NAMESPACE:-ai-agents}"

LUA_DELETE_PROJECT_KEYS="local n=0; local cur='0'; repeat local r=redis.call('SCAN',cur,'MATCH','project:v1:*','COUNT',100); cur=r[1]; for _,k in ipairs(r[2]) do redis.call('UNLINK',k); n=n+1; end until cur=='0'; return n"

run_redis_evalsha() {
  if [ -n "$REDIS_HOST" ]; then
    redis-cli -h "$REDIS_HOST" -p "$REDIS_PORT" EVAL "$LUA_DELETE_PROJECT_KEYS" 0
  else
    kubectl exec -n "$NAMESPACE" deploy/redis -- redis-cli EVAL "$LUA_DELETE_PROJECT_KEYS" 0
  fi
}

if [ "$RESET_REPO" = "1" ]; then
  echo "==> Restartando deployment openclaw para reaplicar templates de workspace (MEMORY/working-buffer) no K8s..."
  if kubectl get deployment openclaw -n "$NAMESPACE" >/dev/null 2>&1; then
    kubectl rollout restart deployment/openclaw -n "$NAMESPACE"
    echo "    rollout restart iniciado; workspace do pod será repopulado pelos ConfigMaps no próximo start."
  else
    echo "    deployment openclaw não encontrado em $NAMESPACE; ignorando RESET_REPO."
  fi
fi

if [ "$RESET_REDIS" = "1" ]; then
  echo "==> Resetando estado dos agentes no Redis (project:v1:*)..."
  if [ -n "$REDIS_HOST" ]; then
    if ! command -v redis-cli >/dev/null 2>&1; then
      echo "    redis-cli não encontrado. Instale ou use sem REDIS_HOST para rodar via kubectl exec."
      exit 1
    fi
  else
    if ! kubectl get namespace "$NAMESPACE" >/dev/null 2>&1; then
      echo "    Namespace $NAMESPACE não existe. Use REDIS_HOST=127.0.0.1 REDIS_PORT=6379 com port-forward."
      exit 1
    fi
    if ! kubectl get deploy/redis -n "$NAMESPACE" >/dev/null 2>&1; then
      echo "    Deployment redis não encontrado em $NAMESPACE. Use REDIS_HOST com port-forward."
      exit 1
    fi
  fi
  N=$(run_redis_evalsha)
  echo "    $N chaves project:v1:* removidas."
fi

echo "==> reset-memory concluído."
