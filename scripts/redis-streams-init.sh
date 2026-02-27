#!/usr/bin/env bash
# Inicializa Redis Streams e consumer groups para o ClawDevs (Fase 0 — 005).
# Executar uma vez após o Redis estar no ar. Ex.: kubectl exec -n ai-agents deploy/redis -- redis-cli < scripts/redis-streams-init.sh
# Ou: REDIS_HOST=localhost REDIS_PORT=6379 ./scripts/redis-streams-init.sh (com port-forward)
set -e

REDIS_HOST="${REDIS_HOST:-redis-service.ai-agents.svc.cluster.local}"
REDIS_PORT="${REDIS_PORT:-6379}"
REDIS_CLI="${REDIS_CLI:-redis-cli}"
GROUP="${REDIS_CONSUMER_GROUP:-clawdevs}"

STREAMS=(
  "cmd:strategy"
  "task:backlog"
  "draft.2.issue"
  "draft_rejected"
  "code:ready"
)

echo "==> Inicializando Redis Streams (host=$REDIS_HOST port=$REDIS_PORT group=$GROUP)"

for stream in "${STREAMS[@]}"; do
  # Cria stream + consumer group em um comando (MKSTREAM cria o stream se não existir)
  if $REDIS_CLI -h "$REDIS_HOST" -p "$REDIS_PORT" XGROUP CREATE "$stream" "$GROUP" "$" MKSTREAM 2>/dev/null; then
    echo "    $stream: stream e group $GROUP criados"
  else
    # EEXIST = group já existe
    echo "    $stream: group já existe ou stream em uso"
  fi
done

# Slot único de revisão (007/125): group "revisao-pos-dev" apenas no stream code:ready
REVISAO_GROUP="${REVISAO_GROUP:-revisao-pos-dev}"
CODE_READY="code:ready"
if $REDIS_CLI -h "$REDIS_HOST" -p "$REDIS_PORT" XGROUP CREATE "$CODE_READY" "$REVISAO_GROUP" "$" MKSTREAM 2>/dev/null; then
  echo "    $CODE_READY: group $REVISAO_GROUP (slot Revisão pós-Dev) criado"
else
  echo "    $CODE_READY: group $REVISAO_GROUP já existe"
fi

echo "==> Concluído. Slot Revisão pós-Dev: XREADGROUP GROUP $REVISAO_GROUP ... no stream $CODE_READY."
echo "    Ref: docs/38-redis-streams-estado-global.md"
