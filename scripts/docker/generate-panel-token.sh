#!/bin/sh
# Copyright (c) 2026 Diego Silva Morais <lukewaresoftwarehouse@gmail.com>
#
# Substitui o Kubernetes Job 'generate-agent-token-job'.
# Roda no container 'token-init' (imagem curlimages/curl).
# Aguarda o panel-backend, faz login, gera token de agente e salva em volume compartilhado.

set -e

# Rotas em app.main: /auth/* e /healthz na raiz (sem prefixo /api).
BACKEND="http://panel-backend:8000"
MAX_RETRIES=30
RETRY_DELAY=2

DEBUG_DIR="${DEBUG_DIR:-/panel-token}"
LAST_ERROR_FILE="${LAST_ERROR_FILE:-${DEBUG_DIR}/token-init-last-error.txt}"

write_last_error() {
  name="$1"
  status="$2"
  body="$3"
  now="$(date -u +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || echo "")"
  {
    echo "ts=${now}"
    echo "step=${name}"
    echo "status=${status}"
    echo "backend=${BACKEND}"
    echo "body_begin"
    printf '%s\n' "$body"
    echo "body_end"
  } > "${LAST_ERROR_FILE}" 2>/dev/null || true
}

log_http_failure() {
  name="$1"
  status="$2"
  body="$3"
  # Avoid dumping huge payloads; keep enough to debug.
  body_preview="$(printf '%s' "$body" | tr '\n' ' ' | cut -c1-500)"
  echo "[token-init] ERRO: ${name} falhou (HTTP ${status}). Body: ${body_preview}" >&2
  write_last_error "$name" "$status" "$body"
}

curl_json() {
  method="$1"
  url="$2"
  data="${3:-}"
  auth="${4:-}"

  tmp_body="$(mktemp)"
  tmp_status="$(mktemp)"

  if [ -n "${data}" ]; then
    if [ -n "${auth}" ]; then
      curl -sS --connect-timeout 2 --max-time 15 -X "${method}" "${url}" -H "Content-Type: application/json" -H "Authorization: Bearer ${auth}" -d "${data}" -o "${tmp_body}" -w "%{http_code}" > "${tmp_status}" || true
    else
      curl -sS --connect-timeout 2 --max-time 15 -X "${method}" "${url}" -H "Content-Type: application/json" -d "${data}" -o "${tmp_body}" -w "%{http_code}" > "${tmp_status}" || true
    fi
  else
    if [ -n "${auth}" ]; then
      curl -sS --connect-timeout 2 --max-time 15 -X "${method}" "${url}" -H "Content-Type: application/json" -H "Authorization: Bearer ${auth}" -o "${tmp_body}" -w "%{http_code}" > "${tmp_status}" || true
    else
      curl -sS --connect-timeout 2 --max-time 15 -X "${method}" "${url}" -H "Content-Type: application/json" -o "${tmp_body}" -w "%{http_code}" > "${tmp_status}" || true
    fi
  fi

  status="$(cat "${tmp_status}" 2>/dev/null || printf '')"
  body="$(cat "${tmp_body}" 2>/dev/null || printf '')"
  rm -f "${tmp_body}" "${tmp_status}"

  printf '%s\n' "${status}"
  printf '%s' "${body}"
}

extract_access_token() {
  # Minimal JSON extraction without jq (token-init image is curl-only).
  # Expected: {"access_token":"..."}
  printf '%s' "$1" | grep -o '"access_token":"[^"]*' | cut -d'"' -f4
}

echo "[token-init] Aguardando panel-backend em $BACKEND/healthz..."
i=0
# timeouts evitam travar o container quando DNS/conexão demoram
until curl -sf --connect-timeout 2 --max-time 4 "$BACKEND/healthz" > /dev/null 2>&1; do
  i=$((i + 1))
  if [ "$i" -ge "$MAX_RETRIES" ]; then
    echo "[token-init] ERRO: backend nao respondeu apos $MAX_RETRIES tentativas."
    exit 1
  fi
  echo "[token-init] Tentativa $i/$MAX_RETRIES..."
  sleep "$RETRY_DELAY"
done

echo "[token-init] Backend pronto. Fazendo login..."
login_payload="{\"username\":\"${PANEL_ADMIN_USERNAME}\",\"password\":\"${PANEL_ADMIN_PASSWORD}\"}"
ADMIN_TOKEN=""
i=0
while [ -z "${ADMIN_TOKEN}" ] && [ "$i" -lt "$MAX_RETRIES" ]; do
  i=$((i + 1))
  resp="$(curl_json POST "$BACKEND/auth/login" "${login_payload}")"
  status="$(printf '%s' "$resp" | sed -n '1p')"
  body="$(printf '%s' "$resp" | sed -n '2,$p')"

  if [ "$status" != "200" ] && [ "$status" != "201" ]; then
    log_http_failure "login" "$status" "$body"
    echo "[token-init] Tentativa login $i/$MAX_RETRIES..." >&2
    sleep "$RETRY_DELAY"
    continue
  fi

  ADMIN_TOKEN="$(extract_access_token "$body")"
  if [ -z "${ADMIN_TOKEN}" ]; then
    echo "[token-init] Tentativa login $i/$MAX_RETRIES... token ausente na resposta" >&2
    sleep "$RETRY_DELAY"
  fi
done

if [ -z "$ADMIN_TOKEN" ]; then
  echo "[token-init] ERRO: falha ao obter token admin apos $MAX_RETRIES tentativas."
  exit 1
fi

echo "[token-init] Login OK. Gerando token de agente..."
AGENT_TOKEN=""
i=0
while [ -z "${AGENT_TOKEN}" ] && [ "$i" -lt "$MAX_RETRIES" ]; do
  i=$((i + 1))
  resp="$(curl_json POST "$BACKEND/auth/agent-token" "" "$ADMIN_TOKEN")"
  status="$(printf '%s' "$resp" | sed -n '1p')"
  body="$(printf '%s' "$resp" | sed -n '2,$p')"

  if [ "$status" != "200" ] && [ "$status" != "201" ]; then
    log_http_failure "agent-token" "$status" "$body"
    echo "[token-init] Tentativa agent-token $i/$MAX_RETRIES..." >&2
    sleep "$RETRY_DELAY"
    continue
  fi

  AGENT_TOKEN="$(extract_access_token "$body")"
  if [ -z "${AGENT_TOKEN}" ]; then
    echo "[token-init] Tentativa agent-token $i/$MAX_RETRIES... token ausente na resposta" >&2
    sleep "$RETRY_DELAY"
  fi
done

if [ -z "$AGENT_TOKEN" ]; then
  echo "[token-init] ERRO: falha ao gerar token de agente apos $MAX_RETRIES tentativas."
  exit 1
fi

echo "$AGENT_TOKEN" > /panel-token/PANEL_TOKEN
echo "[token-init] Token salvo em /panel-token/PANEL_TOKEN"
rm -f "${LAST_ERROR_FILE}" >/dev/null 2>&1 || true
