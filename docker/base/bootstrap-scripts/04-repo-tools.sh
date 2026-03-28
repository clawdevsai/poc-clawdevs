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

mkdir -p "${OPENCLAW_STATE_DIR}/bin"
cat > "${OPENCLAW_STATE_DIR}/bin/repository-context-lib.sh" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
: "${OPENCLAW_STATE_DIR:=/data/openclaw}"
: "${GIT_ORG:=}"
CONTEXT_FILE="${OPENCLAW_STATE_DIR}/contexts/active_repository.env"
load_repo_context() {
  if [ -f "${CONTEXT_FILE}" ]; then
    . "${CONTEXT_FILE}"
  fi
}
normalize_repo_ref() {
  input="$1"
  case "${input}" in
    */*) printf '%s\n' "${input}" ;;
    *) printf '%s/%s\n' "${GIT_ORG}" "${input}" ;;
  esac
}
resolve_repo_id() {
  ref="$1"
  raw_repo_id="$(gh api "repos/${ref}" --jq '.id // empty' 2>/dev/null || true)"
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
write_repo_context_file() {
  ref="$1"
  branch="$2"
  repo_slug="${ref#*/}"
  repo_safe="$(printf '%s' "${repo_slug}" | tr '/' '_' | tr -cd '[:alnum:]_.-')"
  repo_id="$(resolve_repo_id "${ref}")"
  [ -n "${repo_id}" ] || repo_id="unknown"
  repo_context_dir="${OPENCLAW_STATE_DIR}/contexts/repos/${repo_safe}"
  mkdir -p "${repo_context_dir}/logs" "${repo_context_dir}/history"
  cat > "${CONTEXT_FILE}" <<CTX
GIT_ORG=${GIT_ORG}
ACTIVE_GIT_REPOSITORY=${ref}
ACTIVE_REPOSITORY_BRANCH=${branch}
ACTIVE_REPOSITORY_ID=${repo_id}
OPENCLAW_SESSION_ID=${OPENCLAW_SESSION_ID:-unknown}
REPOSITORY_CONTEXT_DIR=${repo_context_dir}
CTX
}
EOF
cat > "${OPENCLAW_STATE_DIR}/bin/claw-repo-discover" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
: "${OPENCLAW_STATE_DIR:=/data/openclaw}"
. "${OPENCLAW_STATE_DIR}/bin/repository-context-lib.sh"
filter="${1:-}"
if [ -n "${filter}" ]; then
  gh repo list "${GIT_ORG}" --limit 200 --json nameWithOwner,isPrivate,description --jq --arg f "${filter}" '.[] | select(.nameWithOwner | test($f;"i")) | [.nameWithOwner, (if .isPrivate then "private" else "public" end), (.description // "")] | @tsv'
else
  gh repo list "${GIT_ORG}" --limit 200 --json nameWithOwner,isPrivate,description --jq '.[] | [.nameWithOwner, (if .isPrivate then "private" else "public" end), (.description // "")] | @tsv'
fi
EOF
cat > "${OPENCLAW_STATE_DIR}/bin/claw-repo-ensure" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
: "${OPENCLAW_STATE_DIR:=/data/openclaw}"
. "${OPENCLAW_STATE_DIR}/bin/repository-context-lib.sh"
if [ "$#" -lt 1 ]; then
  echo "usage: claw-repo-ensure <repo|org/repo> [--create]"
  exit 1
fi
target_ref="$(normalize_repo_ref "$1")"
create_mode="false"
if [ "${2:-}" = "--create" ]; then
  create_mode="true"
fi
if gh api "repos/${target_ref}" --silent >/dev/null 2>&1; then
  echo "${target_ref}"
  exit 0
fi
if [ "${create_mode}" != "true" ]; then
  echo "NOT_FOUND:${target_ref}"
  exit 2
fi
repo_name="${target_ref#*/}"
gh repo create "${target_ref}" --private --add-readme >/tmp/claw-repo-create.log 2>&1
echo "${target_ref}"
EOF
cat > "${OPENCLAW_STATE_DIR}/bin/claw-repo-switch" <<'EOF'
#!/usr/bin/env bash
set -euo pipefail
: "${OPENCLAW_STATE_DIR:=/data/openclaw}"
. "${OPENCLAW_STATE_DIR}/bin/repository-context-lib.sh"
if [ "$#" -lt 1 ]; then
  echo "usage: claw-repo-switch <repo|org/repo> [branch]"
  exit 1
fi
target_ref="$(normalize_repo_ref "$1")"
branch="${2:-main}"
if ! gh api "repos/${target_ref}" --silent >/dev/null 2>&1; then
  echo "ERROR: repositorio '${target_ref}' nao encontrado ou sem acesso." >&2
  exit 1
fi
write_repo_context_file "${target_ref}" "${branch}"
for workspace in "${OPENCLAW_STATE_DIR}/workspace-ceo" "${OPENCLAW_STATE_DIR}/workspace-po" "${OPENCLAW_STATE_DIR}/workspace-arquiteto" "${OPENCLAW_STATE_DIR}/workspace-dev_backend" "${OPENCLAW_STATE_DIR}/workspace-dev_frontend" "${OPENCLAW_STATE_DIR}/workspace-dev_mobile" "${OPENCLAW_STATE_DIR}/workspace-qa_engineer" "${OPENCLAW_STATE_DIR}/workspace-devops_sre" "${OPENCLAW_STATE_DIR}/workspace-security_engineer" "${OPENCLAW_STATE_DIR}/workspace-ux_designer" "${OPENCLAW_STATE_DIR}/workspace-dba_data_engineer" "${OPENCLAW_STATE_DIR}/workspace-memory_curator"; do
  [ -f "${workspace}/REPOSITORY_CONTEXT.md" ] || true
  target_ref_escaped="$(printf '%s' "${target_ref}" | sed -e 's/[\\/&]/\\&/g')"
  branch_escaped="$(printf '%s' "${branch}" | sed -e 's/[\\/&]/\\&/g')"
  session_escaped="$(printf '%s' "${OPENCLAW_SESSION_ID:-unknown}" | sed -e 's/[\\/&]/\\&/g')"
  repo_id="$(resolve_repo_id "${target_ref}")"
  [ -n "${repo_id}" ] || repo_id="unknown"
  repo_id_escaped="$(printf '%s' "${repo_id}" | sed -e 's/[\\/&]/\\&/g')"
  if [ -f "${workspace}/AGENTS.md" ]; then
    sed -i -E "s|^(  active_repository: ).*$|\\1\"${target_ref_escaped}\"|" "${workspace}/AGENTS.md"
    sed -i -E "s|^(  active_branch: ).*$|\\1\"${branch_escaped}\"|" "${workspace}/AGENTS.md"
    sed -i -E "s|^(  active_repository_id: ).*$|\\1\"${repo_id_escaped}\"|" "${workspace}/AGENTS.md"
    sed -i -E "s|^(  session_id: ).*$|\\1\"${session_escaped}\"|" "${workspace}/AGENTS.md"
  fi
  cat > "${workspace}/REPOSITORY_CONTEXT.md" <<CTX
# REPOSITORY_CONTEXT
- organization: ${GIT_ORG}
- active_repository: ${target_ref}
- repository_id: ${repo_id}
- active_branch: ${branch}
- session_id: ${OPENCLAW_SESSION_ID:-unknown}
- repository_context_dir: ${OPENCLAW_STATE_DIR}/contexts/repos/$(printf '%s' "${target_ref#*/}" | tr '/' '_' | tr -cd '[:alnum:]_.-')
- policy: validar contexto ativo antes de qualquer acao e nunca misturar artefatos entre repositorios.
CTX
done
printf 'active_repository=%s\nbranch=%s\n' "${target_ref}" "${branch}"
EOF
chmod +x "${OPENCLAW_STATE_DIR}/bin/repository-context-lib.sh" "${OPENCLAW_STATE_DIR}/bin/claw-repo-discover" "${OPENCLAW_STATE_DIR}/bin/claw-repo-ensure" "${OPENCLAW_STATE_DIR}/bin/claw-repo-switch"
echo "[bootstrap] claw-repo tools installed in ${OPENCLAW_STATE_DIR}/bin"
