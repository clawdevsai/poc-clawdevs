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

# Pipeline pods separados (014): um group por stream
PIPELINE_GROUPS="architect-slot:code:ready qa-slot:review_architect_done cybersec-slot:review_qa_done dba-slot:review_cybersec_done"
for entry in $PIPELINE_GROUPS; do
  g="${entry%%:*}"
  s="${entry##*:}"
  if $REDIS_CLI -h "$REDIS_HOST" -p "$REDIS_PORT" XGROUP CREATE "$s" "$g" "$" MKSTREAM 2>/dev/null; then
    echo "    $s: group $g (pipeline 014) criado"
  else
    echo "    $s: group $g já existe"
  fi
done

# Fase 3 (034): orchestrator:events — consumer Slack para alertas
ORCHESTRATOR_EVENTS="${ORCHESTRATOR_EVENTS:-orchestrator:events}"
SLACK_GROUP="${ORCHESTRATOR_EVENTS_SLACK_GROUP:-slack}"
if $REDIS_CLI -h "$REDIS_HOST" -p "$REDIS_PORT" XGROUP CREATE "$ORCHESTRATOR_EVENTS" "$SLACK_GROUP" "$" MKSTREAM 2>/dev/null; then
  echo "    $ORCHESTRATOR_EVENTS: stream e group $SLACK_GROUP (consumer Slack) criados"
else
  echo "    $ORCHESTRATOR_EVENTS: group $SLACK_GROUP já existe"
fi

# event:devops — DevOps worker (após merge; estado Deployed)
EVENT_DEVOPS="${EVENT_DEVOPS:-event:devops}"
if $REDIS_CLI -h "$REDIS_HOST" -p "$REDIS_PORT" XGROUP CREATE "$EVENT_DEVOPS" "$GROUP" "$" MKSTREAM 2>/dev/null; then
  echo "    $EVENT_DEVOPS: stream e group $GROUP (DevOps worker) criados"
else
  echo "    $EVENT_DEVOPS: group $GROUP já existe"
fi

# Disjuntor draft_rejected (127): consumer group para app/disjuntor_draft_rejected.py
DISJUNTOR_GROUP="${DISJUNTOR_GROUP:-disjuntor}"
if $REDIS_CLI -h "$REDIS_HOST" -p "$REDIS_PORT" XGROUP CREATE "draft_rejected" "$DISJUNTOR_GROUP" "$" MKSTREAM 2>/dev/null; then
  echo "    draft_rejected: group $DISJUNTOR_GROUP (disjuntor 127) criado"
else
  echo "    draft_rejected: group $DISJUNTOR_GROUP já existe"
fi

# audit:queue — auditorias sequenciais (QA, DBA, Security, UX)
AUDIT_QUEUE="${AUDIT_QUEUE:-audit:queue}"
if $REDIS_CLI -h "$REDIS_HOST" -p "$REDIS_PORT" XGROUP CREATE "$AUDIT_QUEUE" "$GROUP" "$" MKSTREAM 2>/dev/null; then
  echo "    $AUDIT_QUEUE: stream e group $GROUP (audit runner) criados"
else
  echo "    $AUDIT_QUEUE: group $GROUP já existe"
fi

echo "==> Concluído. Slot Revisão pós-Dev: XREADGROUP GROUP $REVISAO_GROUP ... no stream $CODE_READY."
echo "    Pipeline 014: architect-slot → qa-slot → cybersec-slot → dba-slot. Ref: docs/38-redis-streams-estado-global.md"
