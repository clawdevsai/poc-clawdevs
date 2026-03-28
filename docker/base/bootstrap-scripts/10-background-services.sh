# Copyright (c) 2026 Diego Silva Morais <lukewaresoftwarehouse@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

stream_agent_sessions() {
  declare -A agent_offsets=()
  while true; do
    for session_file in "${OPENCLAW_STATE_DIR}"/agents/*/sessions/*.jsonl; do
      [ -f "${session_file}" ] || continue
      agent_name="$(basename "$(dirname "$(dirname "${session_file}")")")"
      current_size="$(wc -c < "${session_file}" 2>/dev/null || echo 0)"
      previous_size="${agent_offsets["${session_file}"]:-0}"
      if [ "${current_size}" -gt "${previous_size}" ]; then
        tail -c +$((previous_size + 1)) "${session_file}" \
          | sed "s#^#[agent:${agent_name}] #" \
          | grep -Ev '\[tools\] read failed: (EISDIR: illegal operation on a directory, read|Offset [0-9]+ is beyond end of file \([0-9]+ lines total\))'
        agent_offsets["${session_file}"]="${current_size}"
      fi
    done
    sleep 2
  done
}

ensure_panel_read_permissions() {
  local dir_mode="${OPENCLAW_PANEL_DIR_MODE:-755}"
  local config_mode="${OPENCLAW_CONFIG_FILE_MODE:-644}"
  local sessions_mode="${OPENCLAW_SESSIONS_FILE_MODE:-644}"
  local transcripts_mode="${OPENCLAW_SESSION_TRANSCRIPT_FILE_MODE:-644}"
  local identity_mode="${OPENCLAW_IDENTITY_FILE_MODE:-644}"
  while true; do
    chmod "${dir_mode}" "${OPENCLAW_STATE_DIR}" 2>/dev/null || true
    chmod "${dir_mode}" "${OPENCLAW_STATE_DIR}/agents" 2>/dev/null || true
    chmod "${config_mode}" "${OPENCLAW_STATE_DIR}/openclaw.json" 2>/dev/null || true
    for _agent_dir in "${OPENCLAW_STATE_DIR}"/agents/*; do
      [ -d "${_agent_dir}" ] || continue
      chmod "${dir_mode}" "${_agent_dir}" 2>/dev/null || true
      chmod "${identity_mode}" "${_agent_dir}/IDENTITY.md" 2>/dev/null || true
      chmod "${dir_mode}" "${_agent_dir}/sessions" 2>/dev/null || true
      for _session_file in "${_agent_dir}"/sessions/sessions.json; do
        [ -f "${_session_file}" ] || continue
        chmod "${sessions_mode}" "${_session_file}" 2>/dev/null || true
      done
      for _transcript_file in "${_agent_dir}"/sessions/*.jsonl; do
        [ -f "${_transcript_file}" ] || continue
        chmod "${transcripts_mode}" "${_transcript_file}" 2>/dev/null || true
      done
    done
    sleep "${PANEL_PERMISSION_SYNC_INTERVAL_SECONDS:-5}"
  done
}

openclaw_gateway_is_ready() {
  curl -fsS --max-time "${OPENCLAW_HEALTHCHECK_TIMEOUT_SECONDS:-2}" \
    "http://127.0.0.1:${OPENCLAW_GATEWAY_PORT:-18789}/healthz" >/dev/null 2>&1
}

openclaw_cron_list_json() {
  local output_file="$1"
  local lock_file="/tmp/openclaw-cron-list.lock"
  local lock_wait_seconds="${OPENCLAW_CRON_LIST_LOCK_WAIT_SECONDS:-15}"
  local timeout_seconds="${OPENCLAW_CRON_LIST_TIMEOUT_SECONDS:-8}"

  openclaw_gateway_is_ready || return 1

  if command -v flock >/dev/null 2>&1; then
    (
      exec 9>"${lock_file}"
      flock -w "${lock_wait_seconds}" 9 || exit 1
      timeout "${timeout_seconds}"s openclaw cron list --json > "${output_file}" 2>/dev/null
    )
    return $?
  fi

  timeout "${timeout_seconds}"s openclaw cron list --json > "${output_file}" 2>/dev/null
}

run_security_audit_deep_once() {
  local audit_log="${OPENCLAW_STATE_DIR}/backlog/status/security-audit-deep.log"
  local retries="${OPENCLAW_SECURITY_AUDIT_MAX_RETRIES:-60}"
  local interval_seconds="${OPENCLAW_SECURITY_AUDIT_RETRY_INTERVAL_SECONDS:-5}"
  local timeout_seconds="${OPENCLAW_SECURITY_AUDIT_TIMEOUT_SECONDS:-45}"

  mkdir -p "$(dirname "${audit_log}")"
  for _ in $(seq 1 "${retries}"); do
    if openclaw_gateway_is_ready; then
      echo "[bootstrap] running openclaw security audit --deep"
      if timeout "${timeout_seconds}"s openclaw security audit --deep >> "${audit_log}" 2>&1; then
        echo "[bootstrap] openclaw security audit --deep concluido (log: ${audit_log})"
      else
        echo "[bootstrap] warning: openclaw security audit --deep falhou/timeout (log: ${audit_log})"
      fi
      return 0
    fi
    sleep "${interval_seconds}"
  done

  echo "[bootstrap] warning: gateway nao ficou pronto a tempo para rodar openclaw security audit --deep"
  return 0
}

run_security_audit_deep_recurring() {
  local audit_log="${OPENCLAW_STATE_DIR}/backlog/status/security-audit-deep.log"
  local interval_seconds="${OPENCLAW_SECURITY_AUDIT_CRON_INTERVAL_SECONDS:-3600}"
  local timeout_seconds="${OPENCLAW_SECURITY_AUDIT_TIMEOUT_SECONDS:-45}"

  mkdir -p "$(dirname "${audit_log}")"
  while true; do
    sleep "${interval_seconds}"
    if ! openclaw_gateway_is_ready; then
      echo "[bootstrap] warning: skipping recurring security audit -- gateway not ready" >> "${audit_log}"
      continue
    fi
    echo "[bootstrap] recurring openclaw security audit --deep" >> "${audit_log}"
    if timeout "${timeout_seconds}"s openclaw security audit --deep >> "${audit_log}" 2>&1; then
      echo "[bootstrap] recurring openclaw security audit --deep concluido" >> "${audit_log}"
    else
      echo "[bootstrap] warning: recurring openclaw security audit --deep falhou/timeout" >> "${audit_log}"
    fi
  done
}

track_breakglass_audit_events() {
  local approvals_file="${HOME}/.openclaw/exec-approvals.json"
  local audit_log="${OPENCLAW_STATE_DIR}/backlog/status/breakglass-audit.jsonl"
  local seen_log="${OPENCLAW_STATE_DIR}/backlog/status/.breakglass-seen.log"
  local poll_seconds="${OPENCLAW_BREAKGLASS_AUDIT_INTERVAL_SECONDS:-30}"
  local ttl_seconds="${OPENCLAW_BREAKGLASS_DEFAULT_TTL_SECONDS:-3600}"

  mkdir -p "$(dirname "${audit_log}")"
  touch "${audit_log}" "${seen_log}"

  while true; do
    if [ -f "${approvals_file}" ]; then
      jq -rc '
        (.agents // {})
        | to_entries[]
        | .key as $agent
        | (.value.allowlist // [])[]
        | select((.lastUsedAt // 0) > 0)
        | {
            key: ($agent + "|" + ((.lastUsedAt|tostring) // "0") + "|" + (.lastUsedCommand // "")),
            agent: $agent,
            lastUsedAt: .lastUsedAt,
            command: (.lastUsedCommand // "unknown")
          }
      ' "${approvals_file}" 2>/dev/null | while IFS= read -r evt; do
        [ -n "${evt}" ] || continue
        key="$(printf '%s' "${evt}" | jq -r '.key')"
        grep -Fxq "${key}" "${seen_log}" 2>/dev/null && continue
        printf '%s\n' "${key}" >> "${seen_log}"
        now_iso="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
        expires_iso="$(date -u -d "+${ttl_seconds} seconds" +"%Y-%m-%dT%H:%M:%SZ" 2>/dev/null || date -u +"%Y-%m-%dT%H:%M:%SZ")"
        agent="$(printf '%s' "${evt}" | jq -r '.agent')"
        command="$(printf '%s' "${evt}" | jq -r '.command' | sed 's/"/\\"/g')"
        last_used_at="$(printf '%s' "${evt}" | jq -r '.lastUsedAt')"
        printf '{"ts":"%s","reason":"panel_break_glass","agent":"%s","command":"%s","lastUsedAt":%s,"expiresAt":"%s"}\n' \
          "${now_iso}" "${agent}" "${command}" "${last_used_at}" "${expires_iso}" >> "${audit_log}"
      done
    fi
    sleep "${poll_seconds}"
  done
}

if [ "${PANEL_PERMISSION_SYNC_ENABLED:-true}" = "true" ]; then
  echo "[bootstrap] enabling panel permission sync for sessions.json"
  ( set +e; ensure_panel_read_permissions ) &
fi

if [ "${OPENCLAW_SECURITY_AUDIT_DEEP_ON_START:-true}" = "true" ]; then
  ( set +e; run_security_audit_deep_once ) &
fi

if [ "${OPENCLAW_SECURITY_AUDIT_DEEP_CRON_ENABLED:-true}" = "true" ]; then
  echo "[bootstrap] enabling recurring openclaw security audit --deep"
  ( set +e; run_security_audit_deep_recurring ) &
fi

if [ "${OPENCLAW_BREAKGLASS_AUDIT_ENABLED:-true}" = "true" ]; then
  echo "[bootstrap] enabling break-glass audit tracker (panel-only flow)"
  ( set +e; track_breakglass_audit_events ) &
fi

if [ "${DEBUG_LOG_ENABLED}" = "true" ]; then
  echo "[debug] streaming agent session files into bootstrap logs"
  ( set +e; stream_agent_sessions ) &
fi
if [ "${AGENT_ERROR_ROUTER_ENABLED:-false}" = "true" ]; then
  (
    set +e
    ERROR_CENTER="${OPENCLAW_STATE_DIR}/backlog/status/agent_error_center.jsonl"
    ERROR_SEEN="${OPENCLAW_STATE_DIR}/backlog/status/agent_error_seen.txt"
    mkdir -p "$(dirname "${ERROR_CENTER}")"
    touch "${ERROR_CENTER}" "${ERROR_SEEN}"
    while true; do
      for f in "${OPENCLAW_STATE_DIR}"/agents/*/sessions/*.jsonl; do
        [ -f "${f}" ] || continue
        agent="$(echo "${f}" | sed -E 's#^.*/agents/([^/]+)/sessions/.*$#\1#')"
        [ "${agent}" = "ceo" ] && continue
        tail_snippet="$(tail -n 80 "${f}" 2>/dev/null || true)"
        echo "${tail_snippet}" | grep -Eiq '\[tools\] read failed: (EISDIR: illegal operation on a directory, read|Offset [0-9]+ is beyond end of file \([0-9]+ lines total\))' && continue
        echo "${tail_snippet}" | grep -Eiq 'error|falha|exception|unauthorized|forbidden|timeout|critical|critico|traceback|panic' || continue
        event_hash="$(printf '%s' "${agent}:${tail_snippet}" | sha256sum | awk '{print $1}')"
        grep -q "${event_hash}" "${ERROR_SEEN}" 2>/dev/null && continue
        printf '%s\n' "${event_hash}" >> "${ERROR_SEEN}"
        now_iso="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
        snippet_safe="$(printf '%s' "${tail_snippet}" | tail -n 20 | tr '\n' ' ' | sed 's/"/\\"/g')"
        echo "{\"ts\":\"${now_iso}\",\"agent\":\"${agent}\",\"session_file\":\"${f}\",\"hash\":\"${event_hash}\",\"severity\":\"error\",\"snippet\":\"${snippet_safe}\"}" >> "${ERROR_CENTER}"
        alert_text="ALERTA-AUTOMATICO: erro detectado no agente ${agent}. Registro central: ${ERROR_CENTER}. Hash: ${event_hash}. Acao recomendada: verificar sessao e desbloquear."
        openclaw agent --agent ceo --message "${alert_text}" --no-deliver >/dev/null 2>&1 || true
      done
      sleep "${AGENT_ERROR_ROUTER_INTERVAL_SECONDS:-30}"
    done
  ) &
fi
(
  set +e
  CEO_CRON_NAME="ceo_daily_briefing"
  CEO_CRON_EXPR="0 8 * * *"
  CEO_CRON_TZ="${CEO_CRON_TZ:-America/Sao_Paulo}"
  CEO_CRON_MSG='Executar briefing diario: (1) verificar /data/openclaw/backlog/briefs/ por BRIEFs nao processados — para cada BRIEF sem SPEC correspondente, delegar ao PO via sessions_send para refinamento; (2) verificar /data/openclaw/backlog/status/agent_error_center.jsonl por erros nao resolvidos e tomar acao; (3) se nada pendente: registrar status OK no /data/openclaw/backlog/status/ceo-daily.log.'
  _cron_list_json="/tmp/openclaw-cron-${BASHPID}.json"
  for _ in $(seq 1 24); do
    sleep 5
    if openclaw_cron_list_json "${_cron_list_json}"; then
      CRON_ID="$(jq -r --arg n "${CEO_CRON_NAME}" '.jobs[]? | select(.name == $n) | .jobId' "${_cron_list_json}" | head -n1)"
      if [ -n "${CRON_ID}" ]; then
        echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") cron '${CEO_CRON_NAME}' ja existe (${CRON_ID})" >> "${OPENCLAW_STATE_DIR}/scheduler/ceo_daily.log"
        exit 0
      fi
      if openclaw cron add \
          --name "${CEO_CRON_NAME}" \
          --cron "${CEO_CRON_EXPR}" \
          --tz "${CEO_CRON_TZ}" \
          --session isolated \
          --message "${CEO_CRON_MSG}" \
          --agent ceo \
          --no-deliver >/tmp/openclaw-cron-add-ceo.log 2>&1; then
        echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") cron '${CEO_CRON_NAME}' criado com sucesso" >> "${OPENCLAW_STATE_DIR}/scheduler/ceo_daily.log"
        exit 0
      fi
    fi
  done
  echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") falha ao criar cron do ceo; gateway seguira sem cron automatico" >> "${OPENCLAW_STATE_DIR}/scheduler/ceo_daily.log"
  exit 0
) &
(
  set +e
  ARQ_CRON_NAME="arquiteto_spec_review"
  ARQ_CRON_EXPR="30 8 * * *"
  ARQ_CRON_TZ="${ARQ_CRON_TZ:-America/Sao_Paulo}"
  ARQ_CRON_MSG='Executar revisao proativa de artefatos: (1) verificar /data/openclaw/backlog/specs/ por SPECs aprovadas sem PLAN correspondente em /data/openclaw/backlog/tasks/ — para cada SPEC sem PLAN, criar PLAN e TASKs e delegar ao agente correto (dev_backend/dev_frontend/dev_mobile/dba) via sessions_spawn; (2) verificar issues GitHub com label "ready-for-dev" que nao possuem TASK criada e criar as TASKs; (3) se nada pendente: registrar status OK em /data/openclaw/backlog/status/arquiteto-daily.log.'
  _cron_list_json="/tmp/openclaw-cron-${BASHPID}.json"
  for _ in $(seq 1 24); do
    sleep 5
    if openclaw_cron_list_json "${_cron_list_json}"; then
      CRON_ID="$(jq -r --arg n "${ARQ_CRON_NAME}" '.jobs[]? | select(.name == $n) | .jobId' "${_cron_list_json}" | head -n1)"
      if [ -n "${CRON_ID}" ]; then
        echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") cron '${ARQ_CRON_NAME}' ja existe (${CRON_ID})" >> "${OPENCLAW_STATE_DIR}/scheduler/arquiteto_spec_review.log"
        exit 0
      fi
      if openclaw cron add \
          --name "${ARQ_CRON_NAME}" \
          --cron "${ARQ_CRON_EXPR}" \
          --tz "${ARQ_CRON_TZ}" \
          --session isolated \
          --message "${ARQ_CRON_MSG}" \
          --agent arquiteto \
          --no-deliver >/tmp/openclaw-cron-add-arquiteto.log 2>&1; then
        echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") cron '${ARQ_CRON_NAME}' criado com sucesso" >> "${OPENCLAW_STATE_DIR}/scheduler/arquiteto_spec_review.log"
        exit 0
      fi
    fi
  done
  echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") falha ao criar cron do arquiteto; gateway seguira sem cron automatico" >> "${OPENCLAW_STATE_DIR}/scheduler/arquiteto_spec_review.log"
  exit 0
) &
if [ "${DEV_BACKEND_CRON_ENABLED:-false}" = "true" ]; then
  (
    set +e
    CRON_NAME="${DEV_BACKEND_CRON_NAME:-dev_backend_hourly_queue_poll}"
    CRON_EXPR="${DEV_BACKEND_CRON_EXPR:-0 * * * *}"
    CRON_TZ="${DEV_BACKEND_CRON_TZ:-America/Sao_Paulo}"
    CRON_MSG='Poll GitHub issues com label "back_end"; se houver issue elegivel, implementar task com foco em baixissimo custo cloud e altissima performance; se nao houver, manter standby sem processamento desnecessario.'
    _cron_list_json="/tmp/openclaw-cron-${BASHPID}.json"
    for _ in $(seq 1 24); do
      sleep 5
      if openclaw_cron_list_json "${_cron_list_json}"; then
        CRON_ID="$(jq -r --arg n "${CRON_NAME}" '.jobs[]? | select(.name == $n) | .jobId' "${_cron_list_json}" | head -n1)"
        if [ -n "${CRON_ID}" ]; then
          echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") cron '${CRON_NAME}' ja existe (${CRON_ID})" >> "${OPENCLAW_STATE_DIR}/scheduler/dev_backend_hourly.log"
          exit 0
        fi
        if openclaw cron add \
            --name "${CRON_NAME}" \
            --cron "${CRON_EXPR}" \
            --tz "${CRON_TZ}" \
            --session isolated \
            --message "${CRON_MSG}" \
            --agent dev_backend \
            --no-deliver >/tmp/openclaw-cron-add-dev_backend.log 2>&1; then
          echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") cron '${CRON_NAME}' criado com sucesso" >> "${OPENCLAW_STATE_DIR}/scheduler/dev_backend_hourly.log"
          exit 0
        fi
      fi
    done
    echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") falha ao criar cron nativo do dev_backend; gateway seguira sem cron automatico" >> "${OPENCLAW_STATE_DIR}/scheduler/dev_backend_hourly.log"
    exit 0
  ) &
fi
if [ "${DEV_FRONTEND_CRON_ENABLED:-false}" = "true" ]; then
  (
    set +e
    CRON_NAME="${DEV_FRONTEND_CRON_NAME:-dev_frontend_hourly_queue_poll}"
    CRON_EXPR="${DEV_FRONTEND_CRON_EXPR:-15 * * * *}"
    CRON_TZ="${DEV_FRONTEND_CRON_TZ:-America/Sao_Paulo}"
    CRON_MSG='Poll GitHub issues com label "front_end"; se houver issue elegivel, implementar task frontend com React/Next.js/TypeScript respeitando Core Web Vitals e criterios de aceite da US; se nao houver, manter standby.'
    _cron_list_json="/tmp/openclaw-cron-${BASHPID}.json"
    for _ in $(seq 1 24); do
      sleep 5
      if openclaw_cron_list_json "${_cron_list_json}"; then
        CRON_ID="$(jq -r --arg n "${CRON_NAME}" '.jobs[]? | select(.name == $n) | .jobId' "${_cron_list_json}" | head -n1)"
        if [ -n "${CRON_ID}" ]; then
          echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") cron '${CRON_NAME}' ja existe (${CRON_ID})" >> "${OPENCLAW_STATE_DIR}/scheduler/dev_frontend_hourly.log"
          exit 0
        fi
        if openclaw cron add \
            --name "${CRON_NAME}" \
            --cron "${CRON_EXPR}" \
            --tz "${CRON_TZ}" \
            --session isolated \
            --message "${CRON_MSG}" \
            --agent dev_frontend \
            --no-deliver >/tmp/openclaw-cron-add-dev_frontend.log 2>&1; then
          echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") cron '${CRON_NAME}' criado com sucesso" >> "${OPENCLAW_STATE_DIR}/scheduler/dev_frontend_hourly.log"
          exit 0
        fi
      fi
    done
    echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") falha ao criar cron nativo do dev_frontend; gateway seguira sem cron automatico" >> "${OPENCLAW_STATE_DIR}/scheduler/dev_frontend_hourly.log"
    exit 0
  ) &
fi
if [ "${DEV_MOBILE_CRON_ENABLED:-false}" = "true" ]; then
  (
    set +e
    CRON_NAME="${DEV_MOBILE_CRON_NAME:-dev_mobile_hourly_queue_poll}"
    CRON_EXPR="${DEV_MOBILE_CRON_EXPR:-30 * * * *}"
    CRON_TZ="${DEV_MOBILE_CRON_TZ:-America/Sao_Paulo}"
    CRON_MSG='Poll GitHub issues com label "mobile"; se houver issue elegivel, implementar task mobile com React Native/Expo respeitando criterios de aceite da US; se nao houver, manter standby.'
    _cron_list_json="/tmp/openclaw-cron-${BASHPID}.json"
    for _ in $(seq 1 24); do
      sleep 5
      if openclaw_cron_list_json "${_cron_list_json}"; then
        CRON_ID="$(jq -r --arg n "${CRON_NAME}" '.jobs[]? | select(.name == $n) | .jobId' "${_cron_list_json}" | head -n1)"
        if [ -n "${CRON_ID}" ]; then
          echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") cron '${CRON_NAME}' ja existe (${CRON_ID})" >> "${OPENCLAW_STATE_DIR}/scheduler/dev_mobile_hourly.log"
          exit 0
        fi
        if openclaw cron add \
            --name "${CRON_NAME}" \
            --cron "${CRON_EXPR}" \
            --tz "${CRON_TZ}" \
            --session isolated \
            --message "${CRON_MSG}" \
            --agent dev_mobile \
            --no-deliver >/tmp/openclaw-cron-add-dev_mobile.log 2>&1; then
          echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") cron '${CRON_NAME}' criado com sucesso" >> "${OPENCLAW_STATE_DIR}/scheduler/dev_mobile_hourly.log"
          exit 0
        fi
      fi
    done
    echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") falha ao criar cron nativo do dev_mobile; gateway seguira sem cron automatico" >> "${OPENCLAW_STATE_DIR}/scheduler/dev_mobile_hourly.log"
    exit 0
  ) &
fi
if [ "${QA_CRON_ENABLED:-false}" = "true" ]; then
  (
    set +e
    CRON_NAME="${QA_CRON_NAME:-qa_engineer_hourly_queue_poll}"
    CRON_EXPR="${QA_CRON_EXPR:-45 * * * *}"
    CRON_TZ="${QA_CRON_TZ:-America/Sao_Paulo}"
    CRON_MSG='Poll GitHub issues com label "tests"; se houver issue elegivel, executar validacao BDD, testes e2e e relatorios de qualidade; se nao houver, manter standby.'
    _cron_list_json="/tmp/openclaw-cron-${BASHPID}.json"
    for _ in $(seq 1 24); do
      sleep 5
      if openclaw_cron_list_json "${_cron_list_json}"; then
        CRON_ID="$(jq -r --arg n "${CRON_NAME}" '.jobs[]? | select(.name == $n) | .jobId' "${_cron_list_json}" | head -n1)"
        if [ -n "${CRON_ID}" ]; then
          echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") cron '${CRON_NAME}' ja existe (${CRON_ID})" >> "${OPENCLAW_STATE_DIR}/scheduler/qa_engineer_hourly.log"
          exit 0
        fi
        if openclaw cron add \
            --name "${CRON_NAME}" \
            --cron "${CRON_EXPR}" \
            --tz "${CRON_TZ}" \
            --session isolated \
            --message "${CRON_MSG}" \
            --agent qa_engineer \
            --no-deliver >/tmp/openclaw-cron-add-qa_engineer.log 2>&1; then
          echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") cron '${CRON_NAME}' criado com sucesso" >> "${OPENCLAW_STATE_DIR}/scheduler/qa_engineer_hourly.log"
          exit 0
        fi
      fi
    done
    echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") falha ao criar cron nativo do qa_engineer; gateway seguira sem cron automatico" >> "${OPENCLAW_STATE_DIR}/scheduler/qa_engineer_hourly.log"
    exit 0
  ) &
fi
if [ "${SECURITY_ENGINEER_CRON_ENABLED:-false}" = "true" ]; then
  (
    set +e
    CRON_NAME="${SECURITY_ENGINEER_CRON_NAME:-security_engineer_scan}"
    CRON_EXPR="${SECURITY_ENGINEER_CRON_EXPR:-0 */6 * * *}"
    CRON_TZ="${SECURITY_ENGINEER_CRON_TZ:-America/Sao_Paulo}"
    CRON_MSG='Executar scan proativo de segurança: auditoria de dependências (CVEs), SAST, detecção de secrets e supply chain; aplicar patches autônomos para CVSS >= 7.0; escalar P0 (CVSS >= 9.0) ao CEO imediatamente.'
    _cron_list_json="/tmp/openclaw-cron-${BASHPID}.json"
    for _ in $(seq 1 24); do
      sleep 5
      if openclaw_cron_list_json "${_cron_list_json}"; then
        CRON_ID="$(jq -r --arg n "${CRON_NAME}" '.jobs[]? | select(.name == $n) | .jobId' "${_cron_list_json}" | head -n1)"
        if [ -n "${CRON_ID}" ]; then
          echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") cron '${CRON_NAME}' ja existe (${CRON_ID})" >> "${OPENCLAW_STATE_DIR}/scheduler/security_engineer.log"
          exit 0
        fi
        if openclaw cron add \
            --name "${CRON_NAME}" \
            --cron "${CRON_EXPR}" \
            --tz "${CRON_TZ}" \
            --session isolated \
            --message "${CRON_MSG}" \
            --agent security_engineer \
            --no-deliver >/tmp/openclaw-cron-add-security_engineer.log 2>&1; then
          echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") cron '${CRON_NAME}' criado com sucesso" >> "${OPENCLAW_STATE_DIR}/scheduler/security_engineer.log"
          exit 0
        fi
      fi
    done
    echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") falha ao criar cron nativo do security_engineer; gateway seguira sem cron automatico" >> "${OPENCLAW_STATE_DIR}/scheduler/security_engineer.log"
    exit 0
  ) &
fi
if [ "${DEVOPS_SRE_CRON_ENABLED:-false}" = "true" ]; then
  (
    set +e
    CRON_NAME="${DEVOPS_SRE_CRON_NAME:-devops_sre_queue_poll}"
    CRON_EXPR="${DEVOPS_SRE_CRON_EXPR:-*/30 * * * *}"
    CRON_TZ="${DEVOPS_SRE_CRON_TZ:-America/Sao_Paulo}"
    CRON_MSG='Poll GitHub issues com label "devops"; verificar SLOs, pipelines e alertas de producao; gerar PROD_METRICS semanal; se nao houver acao, manter standby.'
    _cron_list_json="/tmp/openclaw-cron-${BASHPID}.json"
    for _ in $(seq 1 24); do
      sleep 5
      if openclaw_cron_list_json "${_cron_list_json}"; then
        CRON_ID="$(jq -r --arg n "${CRON_NAME}" '.jobs[]? | select(.name == $n) | .jobId' "${_cron_list_json}" | head -n1)"
        if [ -n "${CRON_ID}" ]; then
          echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") cron '${CRON_NAME}' ja existe (${CRON_ID})" >> "${OPENCLAW_STATE_DIR}/scheduler/devops_sre.log"
          exit 0
        fi
        if openclaw cron add \
            --name "${CRON_NAME}" \
            --cron "${CRON_EXPR}" \
            --tz "${CRON_TZ}" \
            --session isolated \
            --message "${CRON_MSG}" \
            --agent devops_sre \
            --no-deliver >/tmp/openclaw-cron-add-devops_sre.log 2>&1; then
          echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") cron '${CRON_NAME}' criado com sucesso" >> "${OPENCLAW_STATE_DIR}/scheduler/devops_sre.log"
          exit 0
        fi
      fi
    done
    echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") falha ao criar cron nativo do devops_sre; gateway seguira sem cron automatico" >> "${OPENCLAW_STATE_DIR}/scheduler/devops_sre.log"
    exit 0
  ) &
fi
if [ "${UX_DESIGNER_CRON_ENABLED:-false}" = "true" ]; then
  (
    set +e
    CRON_NAME="${UX_DESIGNER_CRON_NAME:-ux_designer_queue_poll}"
    CRON_EXPR="${UX_DESIGNER_CRON_EXPR:-0 */4 * * *}"
    CRON_TZ="${UX_DESIGNER_CRON_TZ:-America/Sao_Paulo}"
    CRON_MSG='Poll GitHub issues com label "ux"; produzir wireframes, fluxos de usuario e design tokens; gerar artefatos UX-XXX.md em /data/openclaw/backlog/ux/; se nao houver acao, manter standby.'
    _cron_list_json="/tmp/openclaw-cron-${BASHPID}.json"
    for _ in $(seq 1 24); do
      sleep 5
      if openclaw_cron_list_json "${_cron_list_json}"; then
        CRON_ID="$(jq -r --arg n "${CRON_NAME}" '.jobs[]? | select(.name == $n) | .jobId' "${_cron_list_json}" | head -n1)"
        if [ -n "${CRON_ID}" ]; then
          echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") cron '${CRON_NAME}' ja existe (${CRON_ID})" >> "${OPENCLAW_STATE_DIR}/scheduler/ux_designer.log"
          exit 0
        fi
        if openclaw cron add \
            --name "${CRON_NAME}" \
            --cron "${CRON_EXPR}" \
            --tz "${CRON_TZ}" \
            --session isolated \
            --message "${CRON_MSG}" \
            --agent ux_designer \
            --no-deliver >/tmp/openclaw-cron-add-ux_designer.log 2>&1; then
          echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") cron '${CRON_NAME}' criado com sucesso" >> "${OPENCLAW_STATE_DIR}/scheduler/ux_designer.log"
          exit 0
        fi
      fi
    done
    echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") falha ao criar cron nativo do ux_designer; gateway seguira sem cron automatico" >> "${OPENCLAW_STATE_DIR}/scheduler/ux_designer.log"
    exit 0
  ) &
fi
if [ "${DBA_DATA_ENGINEER_CRON_ENABLED:-false}" = "true" ]; then
  (
    set +e
    CRON_NAME="${DBA_DATA_ENGINEER_CRON_NAME:-dba_data_engineer_queue_poll}"
    CRON_EXPR="${DBA_DATA_ENGINEER_CRON_EXPR:-30 */4 * * *}"
    CRON_TZ="${DBA_DATA_ENGINEER_CRON_TZ:-America/Sao_Paulo}"
    CRON_MSG='Poll GitHub issues com label "dba"; otimizar schemas, migrations, queries e politicas de retencao LGPD; gerar artefatos em /data/openclaw/backlog/tasks/; se nao houver acao, manter standby.'
    _cron_list_json="/tmp/openclaw-cron-${BASHPID}.json"
    for _ in $(seq 1 24); do
      sleep 5
      if openclaw_cron_list_json "${_cron_list_json}"; then
        CRON_ID="$(jq -r --arg n "${CRON_NAME}" '.jobs[]? | select(.name == $n) | .jobId' "${_cron_list_json}" | head -n1)"
        if [ -n "${CRON_ID}" ]; then
          echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") cron '${CRON_NAME}' ja existe (${CRON_ID})" >> "${OPENCLAW_STATE_DIR}/scheduler/dba_data_engineer.log"
          exit 0
        fi
        if openclaw cron add \
            --name "${CRON_NAME}" \
            --cron "${CRON_EXPR}" \
            --tz "${CRON_TZ}" \
            --session isolated \
            --message "${CRON_MSG}" \
            --agent dba_data_engineer \
            --no-deliver >/tmp/openclaw-cron-add-dba_data_engineer.log 2>&1; then
          echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") cron '${CRON_NAME}' criado com sucesso" >> "${OPENCLAW_STATE_DIR}/scheduler/dba_data_engineer.log"
          exit 0
        fi
      fi
    done
    echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") falha ao criar cron nativo do dba_data_engineer; gateway seguira sem cron automatico" >> "${OPENCLAW_STATE_DIR}/scheduler/dba_data_engineer.log"
    exit 0
  ) &
fi
if [ "${MEMORY_CURATOR_CRON_ENABLED:-false}" = "true" ]; then
  (
    set +e
    CRON_NAME="${MEMORY_CURATOR_CRON_NAME:-memory_curator_promote}"
    CRON_EXPR="${MEMORY_CURATOR_CRON_EXPR:-0 2 * * *}"
    CRON_TZ="${MEMORY_CURATOR_CRON_TZ:-America/Sao_Paulo}"
    CRON_MSG='Executar ciclo de curadoria de memoria: (1) ler todos os /data/openclaw/memory/<id>/MEMORY.md; (2) identificar padroes similares entre agentes; (3) promover padroes com >=3 agentes para SHARED_MEMORY.md; (4) arquivar padroes promovidos nos agentes de origem; (5) logar resultado em /data/openclaw/backlog/status/memory-curator.log.'
    _cron_list_json="/tmp/openclaw-cron-${BASHPID}.json"
    for _ in $(seq 1 24); do
      sleep 5
      if openclaw_cron_list_json "${_cron_list_json}"; then
        CRON_ID="$(jq -r --arg n "${CRON_NAME}" '.jobs[]? | select(.name == $n) | .jobId' "${_cron_list_json}" | head -n1)"
        if [ -n "${CRON_ID}" ]; then
          echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") cron '${CRON_NAME}' ja existe (${CRON_ID})" >> "${OPENCLAW_STATE_DIR}/scheduler/memory_curator.log"
          exit 0
        fi
        if openclaw cron add \
            --name "${CRON_NAME}" \
            --cron "${CRON_EXPR}" \
            --tz "${CRON_TZ}" \
            --session isolated \
            --message "${CRON_MSG}" \
            --agent memory_curator \
            --no-deliver >/tmp/openclaw-cron-add-memory_curator.log 2>&1; then
          echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") cron '${CRON_NAME}' criado com sucesso" >> "${OPENCLAW_STATE_DIR}/scheduler/memory_curator.log"
          exit 0
        fi
      fi
    done
    echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") falha ao criar cron nativo do memory_curator; gateway seguira sem cron automatico" >> "${OPENCLAW_STATE_DIR}/scheduler/memory_curator.log"
    exit 0
  ) &
fi
(
  set +e
  WATCHDOG_INTERVAL=3600
  declare -A CRON_CONFIGS
  CRON_CONFIGS[ceo]="ceo_daily_briefing|0 8 * * *|${CEO_CRON_TZ:-America/Sao_Paulo}|Executar briefing diario: verificar backlog/briefs/ por BRIEFs nao processados e delegar ao PO; verificar erros nao resolvidos; registrar status."
  CRON_CONFIGS[arquiteto]="arquiteto_spec_review|30 8 * * *|${ARQ_CRON_TZ:-America/Sao_Paulo}|Verificar SPECs aprovadas sem PLAN e criar TASKs; verificar issues ready-for-dev sem TASK; registrar status."
  CRON_CONFIGS[dev_backend]="${DEV_BACKEND_CRON_NAME:-dev_backend_hourly_queue_poll}|${DEV_BACKEND_CRON_EXPR:-0 * * * *}|${DEV_BACKEND_CRON_TZ:-America/Sao_Paulo}|Poll GitHub issues com label \"back_end\"; se houver issue elegivel, implementar task com foco em baixissimo custo cloud e altissima performance; se nao houver, manter standby."
  CRON_CONFIGS[dev_frontend]="${DEV_FRONTEND_CRON_NAME:-dev_frontend_hourly_queue_poll}|${DEV_FRONTEND_CRON_EXPR:-15 * * * *}|${DEV_FRONTEND_CRON_TZ:-America/Sao_Paulo}|Poll GitHub issues com label \"front_end\"; se houver issue elegivel, implementar task frontend; se nao houver, manter standby."
  CRON_CONFIGS[dev_mobile]="${DEV_MOBILE_CRON_NAME:-dev_mobile_hourly_queue_poll}|${DEV_MOBILE_CRON_EXPR:-30 * * * *}|${DEV_MOBILE_CRON_TZ:-America/Sao_Paulo}|Poll GitHub issues com label \"mobile\"; se houver issue elegivel, implementar task mobile; se nao houver, manter standby."
  CRON_CONFIGS[qa_engineer]="${QA_CRON_NAME:-qa_engineer_hourly_queue_poll}|${QA_CRON_EXPR:-45 * * * *}|${QA_CRON_TZ:-America/Sao_Paulo}|Poll GitHub issues com label \"tests\"; se houver issue elegivel, executar validacao BDD e testes e2e; se nao houver, manter standby."
  CRON_CONFIGS[security_engineer]="${SECURITY_ENGINEER_CRON_NAME:-security_engineer_scan}|${SECURITY_ENGINEER_CRON_EXPR:-0 */6 * * *}|${SECURITY_ENGINEER_CRON_TZ:-America/Sao_Paulo}|Executar scan proativo de seguranca: auditoria de dependencias (CVEs), SAST, deteccao de secrets e supply chain; aplicar patches autonomos para CVSS >= 7.0; escalar P0 ao CEO."
  CRON_CONFIGS[devops_sre]="${DEVOPS_SRE_CRON_NAME:-devops_sre_queue_poll}|${DEVOPS_SRE_CRON_EXPR:-*/30 * * * *}|${DEVOPS_SRE_CRON_TZ:-America/Sao_Paulo}|Poll GitHub issues com label \"devops\"; verificar SLOs, pipelines e alertas de producao; se nao houver acao, manter standby."
  CRON_CONFIGS[ux_designer]="${UX_DESIGNER_CRON_NAME:-ux_designer_queue_poll}|${UX_DESIGNER_CRON_EXPR:-0 */4 * * *}|${UX_DESIGNER_CRON_TZ:-America/Sao_Paulo}|Poll GitHub issues com label \"ux\"; produzir wireframes, fluxos de usuario e design tokens; se nao houver acao, manter standby."
  CRON_CONFIGS[dba_data_engineer]="${DBA_DATA_ENGINEER_CRON_NAME:-dba_data_engineer_queue_poll}|${DBA_DATA_ENGINEER_CRON_EXPR:-30 */4 * * *}|${DBA_DATA_ENGINEER_CRON_TZ:-America/Sao_Paulo}|Poll GitHub issues com label \"dba\"; otimizar schemas, migrations e queries; se nao houver acao, manter standby."
  CRON_CONFIGS[memory_curator]="${MEMORY_CURATOR_CRON_NAME:-memory_curator_promote}|${MEMORY_CURATOR_CRON_EXPR:-0 2 * * *}|${MEMORY_CURATOR_CRON_TZ:-America/Sao_Paulo}|Executar ciclo de curadoria de memoria: promover padroes cross-agent para SHARED_MEMORY; arquivar nos agentes de origem; logar resultado."
  while true; do
    sleep "${WATCHDOG_INTERVAL}"
    if openclaw_cron_list_json /tmp/openclaw-cron-watchdog.json; then
      for agent_name in ceo arquiteto dev_backend dev_frontend dev_mobile qa_engineer security_engineer devops_sre ux_designer dba_data_engineer memory_curator; do
        count="$(jq -r --arg n "${agent_name}" '[.jobs[]? | select(.name | startswith($n))] | length' /tmp/openclaw-cron-watchdog.json 2>/dev/null || echo 0)"
        if [ "${count}" = "0" ]; then
          echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") WATCHDOG: cron do agente ${agent_name} ausente — tentando recriar" >> "${OPENCLAW_STATE_DIR}/scheduler/watchdog.log"
          IFS='|' read -r cron_name cron_expr cron_tz cron_msg <<< "${CRON_CONFIGS[${agent_name}]}"
          if openclaw cron add \
              --name "${cron_name}" \
              --cron "${cron_expr}" \
              --tz "${cron_tz}" \
              --session isolated \
              --message "${cron_msg}" \
              --agent "${agent_name}" \
              --no-deliver >>/tmp/openclaw-cron-watchdog-recreate.log 2>&1; then
            echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") WATCHDOG: cron '${cron_name}' recriado com sucesso" >> "${OPENCLAW_STATE_DIR}/scheduler/watchdog.log"
          else
            echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") WATCHDOG: falha ao recriar cron do agente ${agent_name}" >> "${OPENCLAW_STATE_DIR}/scheduler/watchdog.log"
          fi
        fi
      done
    else
      echo "$(date -u +"%Y-%m-%dT%H:%M:%SZ") WATCHDOG: openclaw cron list falhou — gateway pode estar degradado" >> "${OPENCLAW_STATE_DIR}/scheduler/watchdog.log"
    fi
  done
) &
