#!/usr/bin/env bash
# Desbloqueio explícito da esteira após pausa por orçamento de degradação (Fase 3 — 017).
# Remove a chave orchestration:pause_degradation no Redis. A retomada só ocorre após este comando.
# Ref: docs/06-operacoes.md (Workflow de recuperação pós-degradação), docs/07-configuracao-e-prompts.md
set -e
REDIS_HOST="${REDIS_HOST:-127.0.0.1}"
REDIS_PORT="${REDIS_PORT:-6379}"
KEY_PAUSE_DEGRADATION="${KEY_PAUSE_DEGRADATION:-orchestration:pause_degradation}"
REDIS_CLI="${REDIS_CLI:-redis-cli}"
if command -v redis-cli &>/dev/null; then
  $REDIS_CLI -h "$REDIS_HOST" -p "$REDIS_PORT" DEL "$KEY_PAUSE_DEGRADATION"
  echo "Desbloqueio executado: $KEY_PAUSE_DEGRADATION removida. Esteira pode retomar."
else
  echo "redis-cli não encontrado. Execute no host com Redis acessível ou use kubectl exec."
  exit 2
fi
