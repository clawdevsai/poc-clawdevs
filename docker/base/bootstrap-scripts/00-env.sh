set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
export OPENCLAW_NO_ONBOARD=1
export OPENCLAW_NO_PROMPT=1
export OPENCLAW_STATE_DIR=/data/openclaw
export OPENCLAW_BIN_DIR="${OPENCLAW_STATE_DIR}/bin"
export GH_CONFIG_DIR="${GH_CONFIG_DIR:-${OPENCLAW_STATE_DIR}/.config/gh}"
export OPENCLAW_LOG_LEVEL="${OPENCLAW_LOG_LEVEL:-info}"
BOOTSTRAP_LOG_DIR="${OPENCLAW_STATE_DIR}/backlog/status"
BOOTSTRAP_LOG_FILE="${BOOTSTRAP_LOG_DIR}/openclaw-bootstrap.log"
mkdir -p "${BOOTSTRAP_LOG_DIR}"
touch "${BOOTSTRAP_LOG_FILE}"
mkdir -p "${GH_CONFIG_DIR}"
mkdir -p "${OPENCLAW_BIN_DIR}"
export PATH="${OPENCLAW_BIN_DIR}:${PATH}"
DEBUG_LOG_ENABLED="${DEBUG_LOG_ENABLED:-false}"
if [ "${DEBUG_LOG_ENABLED}" = "true" ]; then
  export LOG_LEVEL=debug
  export DEBUG=1
  DEBUG_LOG_FILE="${BOOTSTRAP_LOG_DIR}/openclaw-debug.log"
  touch "${DEBUG_LOG_FILE}"
  exec > >(tee -a "${BOOTSTRAP_LOG_FILE}" "${DEBUG_LOG_FILE}") 2>&1
  export PS4='+ [${BASH_SOURCE:-script}:${LINENO}] '
  set -x
  echo "[debug] debug logging enabled"
else
  export LOG_LEVEL="${LOG_LEVEL:-info}"
  exec > >(tee -a "${BOOTSTRAP_LOG_FILE}") 2>&1
fi
trap 'status=$?; echo "[bootstrap][error] line=${LINENO} cmd=${BASH_COMMAND} exit=${status}" >&2' ERR
echo "[bootstrap] log file: ${BOOTSTRAP_LOG_FILE}"
echo "[bootstrap] debug mode: ${DEBUG_LOG_ENABLED}"
for var_name in OPENCLAW_GATEWAY_TOKEN NEMOCLAW_EXTERNAL NEMOCLAW_GATEWAY_URL NEMOCLAW_GATEWAY_TOKEN TELEGRAM_BOT_TOKEN_CEO TELEGRAM_CHAT_ID GIT_TOKEN GIT_ORG OLLAMA_API_KEY; do
  if [ -n "${!var_name:-}" ]; then
    echo "[bootstrap] ${var_name}=set"
  else
    echo "[bootstrap] ${var_name}=empty"
  fi
done
# Organizacao GitHub; repositorio ativo e definido em 03-gh-auth (primeiro repo listavel da org) ou claw-repo-switch.
export GIT_ORG="${GIT_ORG:-lukeware-ai}"
export ACTIVE_GIT_REPOSITORY="${ACTIVE_GIT_REPOSITORY:-}"
export GIT_REPOSITORY="${GIT_REPOSITORY:-}"
export GH_REPO="${GH_REPO:-}"
export ACTIVE_REPOSITORY_BRANCH="${ACTIVE_REPOSITORY_BRANCH:-main}"
export ACTIVE_REPOSITORY_ID="${ACTIVE_REPOSITORY_ID:-unknown}"
export REPOSITORY_CONTEXT_DIR="${REPOSITORY_CONTEXT_DIR:-${OPENCLAW_STATE_DIR}/contexts/repos/_pending}"
export OPENCLAW_SESSION_ID="${OPENCLAW_SESSION_ID:-$(date -u +%Y%m%dT%H%M%SZ)-$(cat /proc/sys/kernel/random/uuid | cut -d- -f1)}"
# Fallback para quando DIRECTORS_NAME nao estiver definido no Secret
export DIRECTORS_NAME="${DIRECTORS_NAME:-Director}"
# Idioma padrao dos agentes (sobrescrito via LANGUAGE no .env)
export LANGUAGE="${LANGUAGE:-pt-BR}"
# Alinhar aliases de token para evitar divergencia entre ferramentas
export GITHUB_TOKEN="${GITHUB_TOKEN:-${GH_TOKEN:-${GIT_TOKEN:-}}}"
export GH_TOKEN="${GH_TOKEN:-${GITHUB_TOKEN:-${GIT_TOKEN:-}}}"
export GIT_TOKEN="${GIT_TOKEN:-${GH_TOKEN:-${GITHUB_TOKEN:-}}}"
mkdir -p "${OPENCLAW_STATE_DIR}/contexts/repos"
resolve_repo_id_safe() {
  repo_ref="$1"
  # gh pode devolver payload JSON de erro no stdout (ex.: 401). Aceitamos apenas ID numerico.
  raw_repo_id="$(gh api "repos/${repo_ref}" --jq '.id // empty' 2>/dev/null || true)"
  raw_repo_id="$(printf '%s' "${raw_repo_id}" | awk 'NR==1{print; exit}')"
  case "${raw_repo_id}" in
    ''|*[!0-9]*)
      printf '%s\n' ""
      ;;
    *)
      printf '%s\n' "${raw_repo_id}"
      ;;
  esac
}
write_repository_context() {
  repo_ref="$1"
  repo_branch="$2"
  repo_slug="${repo_ref#*/}"
  repo_safe="$(printf '%s' "${repo_slug}" | tr '/' '_' | tr -cd '[:alnum:]_.-')"
  repo_id="$(resolve_repo_id_safe "${repo_ref}")"
  if [ -z "${repo_id}" ]; then
    repo_id="unknown"
  fi
  repo_context_dir="${OPENCLAW_STATE_DIR}/contexts/repos/${repo_safe}"
  mkdir -p "${repo_context_dir}/logs" "${repo_context_dir}/history"
  cat > "${OPENCLAW_STATE_DIR}/contexts/active_repository.env" <<EOF
GIT_ORG=${GIT_ORG}
ACTIVE_GIT_REPOSITORY=${repo_ref}
ACTIVE_REPOSITORY_BRANCH=${repo_branch}
ACTIVE_REPOSITORY_ID=${repo_id}
OPENCLAW_SESSION_ID=${OPENCLAW_SESSION_ID}
REPOSITORY_CONTEXT_DIR=${repo_context_dir}
EOF
  export ACTIVE_GIT_REPOSITORY="${repo_ref}"
  export GIT_REPOSITORY="${repo_ref}"
  export GH_REPO="${repo_ref}"
  export ACTIVE_REPOSITORY_BRANCH="${repo_branch}"
  export ACTIVE_REPOSITORY_ID="${repo_id}"
  export REPOSITORY_CONTEXT_DIR="${repo_context_dir}"
  echo "[bootstrap] repository context active=${ACTIVE_GIT_REPOSITORY} id=${ACTIVE_REPOSITORY_ID} branch=${ACTIVE_REPOSITORY_BRANCH} session=${OPENCLAW_SESSION_ID}"
}
render_agent_context() {
  agent_workspace="$1"
  [ -f "${OPENCLAW_STATE_DIR}/contexts/active_repository.env" ] && . "${OPENCLAW_STATE_DIR}/contexts/active_repository.env"
  ACTIVE_GIT_REPOSITORY="${ACTIVE_GIT_REPOSITORY:-pending}"
  ACTIVE_REPOSITORY_BRANCH="${ACTIVE_REPOSITORY_BRANCH:-main}"
  OPENCLAW_SESSION_ID="${OPENCLAW_SESSION_ID:-unknown}"
  ACTIVE_REPOSITORY_ID="${ACTIVE_REPOSITORY_ID:-unknown}"
  REPOSITORY_CONTEXT_DIR="${REPOSITORY_CONTEXT_DIR:-${OPENCLAW_STATE_DIR}/contexts/repos/_pending}"
  GIT_ORG_ESCAPED="$(printf '%s' "${GIT_ORG}" | sed -e 's/[\\/&]/\\&/g')"
  ACTIVE_GIT_REPOSITORY_ESCAPED="$(printf '%s' "${ACTIVE_GIT_REPOSITORY}" | sed -e 's/[\\/&]/\\&/g')"
  ACTIVE_REPOSITORY_BRANCH_ESCAPED="$(printf '%s' "${ACTIVE_REPOSITORY_BRANCH}" | sed -e 's/[\\/&]/\\&/g')"
  OPENCLAW_SESSION_ID_ESCAPED="$(printf '%s' "${OPENCLAW_SESSION_ID}" | sed -e 's/[\\/&]/\\&/g')"
  ACTIVE_REPOSITORY_ID_ESCAPED="$(printf '%s' "${ACTIVE_REPOSITORY_ID}" | sed -e 's/[\\/&]/\\&/g')"
  LANGUAGE_ESCAPED="$(printf '%s' "${LANGUAGE}" | sed -e 's/[\\/&]/\\&/g')"
  if [ -f "${agent_workspace}/AGENTS.md" ]; then
    sed -i "s|__GIT_ORG__|${GIT_ORG_ESCAPED}|g" "${agent_workspace}/AGENTS.md"
    sed -i "s|__ACTIVE_GIT_REPOSITORY__|${ACTIVE_GIT_REPOSITORY_ESCAPED}|g" "${agent_workspace}/AGENTS.md"
    sed -i "s|__ACTIVE_REPOSITORY_BRANCH__|${ACTIVE_REPOSITORY_BRANCH_ESCAPED}|g" "${agent_workspace}/AGENTS.md"
    sed -i "s|__OPENCLAW_SESSION_ID__|${OPENCLAW_SESSION_ID_ESCAPED}|g" "${agent_workspace}/AGENTS.md"
    sed -i "s|__ACTIVE_REPOSITORY_ID__|${ACTIVE_REPOSITORY_ID_ESCAPED}|g" "${agent_workspace}/AGENTS.md"
    sed -i "s|__GIT_REPOSITORY__|${ACTIVE_GIT_REPOSITORY_ESCAPED}|g" "${agent_workspace}/AGENTS.md"
    sed -i "s|__LANGUAGE__|${LANGUAGE_ESCAPED}|g" "${agent_workspace}/AGENTS.md"
  fi
  cat > "${agent_workspace}/REPOSITORY_CONTEXT.md" <<EOF
# REPOSITORY_CONTEXT
- organization: ${GIT_ORG}
- active_repository: ${ACTIVE_GIT_REPOSITORY}
- repository_id: ${ACTIVE_REPOSITORY_ID}
- active_branch: ${ACTIVE_REPOSITORY_BRANCH}
- session_id: ${OPENCLAW_SESSION_ID}
- repository_context_dir: ${REPOSITORY_CONTEXT_DIR}
- policy: validar contexto ativo antes de qualquer acao e nunca misturar artefatos entre repositorios.
EOF
}
