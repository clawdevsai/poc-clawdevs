#!/usr/bin/env bash

set -euo pipefail

SANDBOX_NAME="${SANDBOX_NAME:-clawdevs-ai}"
PROVIDER_NAME="${PROVIDER_NAME:-ollama-local}"
MODEL="${MODEL:-mistral}"
TIMEOUT_SECONDS="${TIMEOUT_SECONDS:-120}"

require_cmd() {
  local name="$1"
  command -v "$name" >/dev/null 2>&1 || {
    echo "ERRO: comando nao encontrado no PATH: $name" >&2
    exit 1
  }
}

require_cmd nemoclaw
require_cmd openshell

echo "[nemoclaw] verificando CLI"
nemoclaw list >/dev/null

echo "[openshell] criando provider '${PROVIDER_NAME}' para Ollama local via host.openshell.internal"
# OpenShell routes from sandbox -> host via host.openshell.internal.
# Ollama container exposes host port 11434; OpenAI-compatible baseUrl uses /v1.
openshell provider create \
  --name "${PROVIDER_NAME}" \
  --type openai \
  --credential "OPENAI_API_KEY=unused" \
  --config "OPENAI_BASE_URL=http://host.openshell.internal:11434/v1" >/dev/null

echo "[openshell] setando inferencia ativa (provider=${PROVIDER_NAME}, model=${MODEL}, timeout=${TIMEOUT_SECONDS}s)"
openshell inference set \
  --provider "${PROVIDER_NAME}" \
  --model "${MODEL}" \
  --timeout "${TIMEOUT_SECONDS}" >/dev/null

echo "[nemoclaw] aplicando policy preset para local inference (pode ser interativo)"
nemoclaw "${SANDBOX_NAME}" policy-add

echo "[ok] provider local configurado. Se houver bloqueio de rede, rode: openshell term"
