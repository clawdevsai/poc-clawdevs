mkdir -p "${OPENCLAW_STATE_DIR}"
mkdir -p ~/.openclaw
mkdir -p "${OPENCLAW_STATE_DIR}/projects"

# Funcao para inicializar estrutura de backlog de um projeto.
# Chamada pelo DevOps apos validar/criar repositorio.
# Uso: init_project_backlog <nome-do-projeto>
init_project_backlog() {
  local project_name="$1"
  local project_dir="${OPENCLAW_STATE_DIR}/projects/${project_name}"
  local backlog_dir="${project_dir}/docs/backlogs"
  mkdir -p "${backlog_dir}/status"
  mkdir -p "${backlog_dir}/idea"
  mkdir -p "${backlog_dir}/specs"
  mkdir -p "${backlog_dir}/user_story"
  mkdir -p "${backlog_dir}/tasks"
  mkdir -p "${backlog_dir}/briefs"
  mkdir -p "${backlog_dir}/implementation"
  mkdir -p "${backlog_dir}/session_finished"
  mkdir -p "${backlog_dir}/ux"
  mkdir -p "${backlog_dir}/security/scans"
  mkdir -p "${backlog_dir}/database"
}

# Inicializar backlog para projetos ja existentes em /data/openclaw/projects/
for _existing_project in "${OPENCLAW_STATE_DIR}"/projects/*/; do
  [ -d "${_existing_project}" ] || continue
  _proj_name="$(basename "${_existing_project}")"
  [ -d "${_existing_project}/docs/backlogs" ] || init_project_backlog "${_proj_name}"
done
mkdir -p "${OPENCLAW_STATE_DIR}/scheduler"
mkdir -p "${OPENCLAW_STATE_DIR}/workspace-ceo"
mkdir -p "${OPENCLAW_STATE_DIR}/workspace-po"
mkdir -p "${OPENCLAW_STATE_DIR}/workspace-arquiteto"
mkdir -p "${OPENCLAW_STATE_DIR}/workspace-dev_backend"
mkdir -p "${OPENCLAW_STATE_DIR}/agents/ceo/agent" "${OPENCLAW_STATE_DIR}/agents/po/agent" "${OPENCLAW_STATE_DIR}/agents/arquiteto/agent" "${OPENCLAW_STATE_DIR}/agents/dev_backend/agent"
mkdir -p "${OPENCLAW_STATE_DIR}/workspace-dev_frontend" "${OPENCLAW_STATE_DIR}/workspace-dev_mobile" "${OPENCLAW_STATE_DIR}/workspace-qa_engineer"
mkdir -p "${OPENCLAW_STATE_DIR}/workspace-devops_sre" "${OPENCLAW_STATE_DIR}/workspace-security_engineer"
mkdir -p "${OPENCLAW_STATE_DIR}/workspace-ux_designer" "${OPENCLAW_STATE_DIR}/workspace-dba_data_engineer"
mkdir -p "${OPENCLAW_STATE_DIR}/workspace-memory_curator"
mkdir -p "${OPENCLAW_STATE_DIR}/agents/dev_frontend/agent" "${OPENCLAW_STATE_DIR}/agents/dev_mobile/agent" "${OPENCLAW_STATE_DIR}/agents/qa_engineer/agent"
mkdir -p "${OPENCLAW_STATE_DIR}/agents/devops_sre/agent" "${OPENCLAW_STATE_DIR}/agents/security_engineer/agent"
mkdir -p "${OPENCLAW_STATE_DIR}/agents/ux_designer/agent" "${OPENCLAW_STATE_DIR}/agents/dba_data_engineer/agent"
mkdir -p "${OPENCLAW_STATE_DIR}/agents/memory_curator/agent"

# Symlink projects/ em cada workspace — todos os agentes enxergam /data/openclaw/projects/ como ./projects/
for ws_agent in ceo po arquiteto dev_backend dev_frontend dev_mobile qa_engineer devops_sre security_engineer ux_designer dba_data_engineer memory_curator; do
  ws_dir="${OPENCLAW_STATE_DIR}/workspace-${ws_agent}"
  mkdir -p "${ws_dir}"
  ln -sfn "${OPENCLAW_STATE_DIR}/projects" "${ws_dir}/projects"
done
