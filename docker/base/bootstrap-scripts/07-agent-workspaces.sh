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

# Base configuration directory
OPENCLAW_CONFIG_DIR="/bootstrap/openclaw-config"

# List of all agents
AGENTS=(ceo po arquiteto dev_backend dev_frontend dev_mobile qa_engineer devops_sre security_engineer ux_designer dba_data_engineer memory_curator)

# Copy agent base files from structured directory
# Arguments: agent_name
setup_agent_workspace() {
  local agent="$1"
  local src_dir="${OPENCLAW_CONFIG_DIR}/${agent}"
  local ws_dir="${OPENCLAW_STATE_DIR}/workspace-${agent}"

  # Core agent files
  # Sempre sobrescreve AGENTS.md porque os workspaces ficam persistidos em volume.
  # Assim, alterações em __LANGUAGE__ e no conteúdo base entram em vigor na próxima inicialização.
  cp "${src_dir}/AGENTS.md" "${ws_dir}/AGENTS.md"
  cp "${src_dir}/BOOT.md" "${ws_dir}/BOOT.md"
  [ -f "${ws_dir}/BOOTSTRAP.md" ] || cp "${src_dir}/BOOTSTRAP.md" "${ws_dir}/BOOTSTRAP.md"
  cp "${src_dir}/HEARTBEAT.md" "${ws_dir}/HEARTBEAT.md"
  cp "${src_dir}/IDENTITY.md" "${ws_dir}/IDENTITY.md"
  cp "${src_dir}/INPUT_SCHEMA.json" "${ws_dir}/INPUT_SCHEMA.json"
  cp "${src_dir}/SOUL.md" "${ws_dir}/SOUL.md"
  cp "${src_dir}/SECURITY_TEST_CASES.md" "${ws_dir}/SECURITY_TEST_CASES.md"
  cp "${src_dir}/USER.md" "${ws_dir}/USER.md"
  cp "${src_dir}/TOOLS.md" "${ws_dir}/TOOLS.md"
}

# Copy shared files to agent workspace
# Arguments: agent_name
copy_shared_files() {
  local agent="$1"
  local shared_dir="${OPENCLAW_CONFIG_DIR}/shared"
  local ws_dir="${OPENCLAW_STATE_DIR}/workspace-${agent}"

  cp "${shared_dir}/CONSTITUTION.md" "${ws_dir}/CONSTITUTION.md"
  cp "${shared_dir}/CHANNEL_PRIVACY.md" "${ws_dir}/CHANNEL_PRIVACY.md"
  cp "${shared_dir}/BRIEF_TEMPLATE.md" "${ws_dir}/BRIEF_TEMPLATE.md"
  cp "${shared_dir}/CLARIFY_TEMPLATE.md" "${ws_dir}/CLARIFY_TEMPLATE.md"
  cp "${shared_dir}/SDD_CHECKLIST.md" "${ws_dir}/SDD_CHECKLIST.md"
  cp "${shared_dir}/SDD_FULL_CYCLE_EXAMPLE.md" "${ws_dir}/SDD_FULL_CYCLE_EXAMPLE.md"
  cp "${shared_dir}/SDD_OPERATIONAL_PROMPTS.md" "${ws_dir}/SDD_OPERATIONAL_PROMPTS.md"
  cp "${shared_dir}/SPEC_TEMPLATE.md" "${ws_dir}/SPEC_TEMPLATE.md"
  cp "${shared_dir}/PLAN_TEMPLATE.md" "${ws_dir}/PLAN_TEMPLATE.md"
  cp "${shared_dir}/TASK_TEMPLATE.md" "${ws_dir}/TASK_TEMPLATE.md"
  cp "${shared_dir}/VALIDATE_TEMPLATE.md" "${ws_dir}/VALIDATE_TEMPLATE.md"
  cp "${shared_dir}/VIBE_CODING_PLAYBOOK.md" "${ws_dir}/VIBE_CODING_PLAYBOOK.md"
  cp "${shared_dir}/SDD_OPERATING_MODEL.md" "${ws_dir}/SDD_OPERATING_MODEL.md"
  cp "${shared_dir}/SPECKIT_ADAPTATION.md" "${ws_dir}/SPECKIT_ADAPTATION.md"

  # Context Mode files
  cp "${shared_dir}/CONTEXT_MODE_README.md" "${ws_dir}/CONTEXT_MODE_README.md"
  cp "${shared_dir}/CONTEXT_MODE_AGENT_HELPERS.md" "${ws_dir}/CONTEXT_MODE_AGENT_HELPERS.md"
  cp "${shared_dir}/CONTEXT_MODE_HOOKS_CONFIG.yaml" "${ws_dir}/CONTEXT_MODE_HOOKS_CONFIG.yaml"
  cp "${shared_dir}/CONTEXT_ENGINE_CONFIG.md" "${ws_dir}/CONTEXT_ENGINE_CONFIG.md"
  cp "${shared_dir}/MEMORY_COMPACTION_CONFIG.md" "${ws_dir}/MEMORY_COMPACTION_CONFIG.md"
  cp "${shared_dir}/SESSION_MANAGEMENT_CONFIG.md" "${ws_dir}/SESSION_MANAGEMENT_CONFIG.md"
  cp "${shared_dir}/STANDING_ORDERS.md" "${ws_dir}/STANDING_ORDERS.md"
  cp "${shared_dir}/CRON_JOBS_REGISTRY.md" "${ws_dir}/CRON_JOBS_REGISTRY.md"
  cp "${shared_dir}/HOOKS_SPECIFICATION.md" "${ws_dir}/HOOKS_SPECIFICATION.md"
  cp "${shared_dir}/DYNAMIC_COST_ORCHESTRATION.md" "${ws_dir}/DYNAMIC_COST_ORCHESTRATION.md"
  cp "${shared_dir}/PROMPT_CHANGELOG.md" "${ws_dir}/PROMPT_CHANGELOG.md"

  # Schemas
  if [ -d "${shared_dir}/schemas" ]; then
    mkdir -p "${ws_dir}/schemas"
    cp -Rf "${shared_dir}/schemas/." "${ws_dir}/schemas/"
  fi

  # Utils
  if [ -d "${shared_dir}/utils" ]; then
    mkdir -p "${ws_dir}/utils"
    cp -Rf "${shared_dir}/utils/." "${ws_dir}/utils/"
  fi

  # Project README (renamed from PROJECT_README.md)
  cp "${shared_dir}/PROJECT_README.md" "${ws_dir}/README.md"

  # SDD Initiative files
  mkdir -p "${ws_dir}/initiatives/internal-sdd-operationalization"
  local sdd_dir="${shared_dir}/initiatives/internal-sdd-operationalization"
  cp "${sdd_dir}/README.md" "${ws_dir}/initiatives/internal-sdd-operationalization/README.md"
  cp "${sdd_dir}/BRIEF.md" "${ws_dir}/initiatives/internal-sdd-operationalization/BRIEF.md"
  cp "${sdd_dir}/SPEC.md" "${ws_dir}/initiatives/internal-sdd-operationalization/SPEC.md"
  cp "${sdd_dir}/CLARIFY.md" "${ws_dir}/initiatives/internal-sdd-operationalization/CLARIFY.md"
  cp "${sdd_dir}/PLAN.md" "${ws_dir}/initiatives/internal-sdd-operationalization/PLAN.md"
  cp "${sdd_dir}/TASK.md" "${ws_dir}/initiatives/internal-sdd-operationalization/TASK.md"
  cp "${sdd_dir}/VALIDATE.md" "${ws_dir}/initiatives/internal-sdd-operationalization/VALIDATE.md"
}

# Copy agent-specific skills from agents/<agent>/skills/ into <workspace>/skills/
# (OpenClaw: highest-precedence workspace skills live under <workspace>/skills/)
# Arguments: agent_name
copy_agent_skills() {
  local agent="$1"
  local skills_dir="${OPENCLAW_CONFIG_DIR}/agents/${agent}/skills"
  local ws_dir="${OPENCLAW_STATE_DIR}/workspace-${agent}"

  # Check if skills directory exists for this agent
  if [ -d "${skills_dir}" ]; then
    for skill_dir in "${skills_dir}"/*/; do
      [ -d "${skill_dir}" ] || continue
      local skill_name=$(basename "${skill_dir}")
      local target_dir="${ws_dir}/skills/${skill_name}"
      mkdir -p "${target_dir}"
      cp -Rf "${skill_dir}/." "${target_dir}/"
    done
  fi
}

# Setup all agent workspaces
for agent in "${AGENTS[@]}"; do
  setup_agent_workspace "${agent}"
  copy_shared_files "${agent}"
  copy_agent_skills "${agent}"
done

# Special handling for CEO DIRECTORS_NAME substitution
DIRECTORS_NAME_ESCAPED="$(printf '%s' "${DIRECTORS_NAME}" | sed -e 's/[\\/&]/\\&/g')"
sed -i "s|\${DIRECTORS_NAME}|${DIRECTORS_NAME_ESCAPED}|g" "${OPENCLAW_STATE_DIR}/workspace-ceo/USER.md"

# Create memory directories for all agents
for ws_agent in "${AGENTS[@]}"; do
  ws_dir="${OPENCLAW_STATE_DIR}/workspace-${ws_agent}"
  mkdir -p "${ws_dir}/memory"
done

# Create artifact tracking + shared projects link for all agents
for ws_agent in "${AGENTS[@]}"; do
  ws_dir="${OPENCLAW_STATE_DIR}/workspace-${ws_agent}"
  mkdir -p "${ws_dir}/artifacts"

  # Shared projects access
  ln -sfn "${OPENCLAW_STATE_DIR}/projects" "${ws_dir}/projects"

  # Artifact schema (v1)
  if [ ! -f "${ws_dir}/artifacts/artifacts.schema.json" ]; then
    cat > "${ws_dir}/artifacts/artifacts.schema.json" <<'EOF'
{
  "schema_version": "v1",
  "fields": {
    "command": "string",
    "args": "array",
    "cwd": "string",
    "started_at": "string",
    "finished_at": "string",
    "exit_code": "number",
    "stdout_hash": "string",
    "stderr_hash": "string",
    "files_changed": "array",
    "diffs_hash": "string",
    "tests_run": "array"
  }
}
EOF
  fi

  # Artifact log seed (v1)
  if [ ! -f "${ws_dir}/artifacts/artifacts.log.jsonl" ]; then
    printf '{"schema_version":"v1"}\n' > "${ws_dir}/artifacts/artifacts.log.jsonl"
  fi
done

# --- Sistema de Memória Cross-Agent (aiox-core pattern) ---
MEMORY_BASE="${OPENCLAW_STATE_DIR}/memory"
mkdir -p "${MEMORY_BASE}/shared"

# Memory agents (excluding memory_curator for special handling)
MEM_AGENTS=(ceo po arquiteto dev_backend dev_frontend dev_mobile qa_engineer security_engineer devops_sre ux_designer dba_data_engineer memory_curator)

for mem_agent in "${MEM_AGENTS[@]}"; do
  mkdir -p "${MEMORY_BASE}/${mem_agent}"
  if [ ! -f "${MEMORY_BASE}/${mem_agent}/MEMORY.md" ]; then
    src="${OPENCLAW_CONFIG_DIR}/memory/${mem_agent}/MEMORY.md"
    if [ -f "${src}" ]; then
      cp "${src}" "${MEMORY_BASE}/${mem_agent}/MEMORY.md"
    else
      printf '# MEMORY — %s\n\n## Active Patterns\n\n## Promotion Candidates\n\n## Archived\n' "${mem_agent}" > "${MEMORY_BASE}/${mem_agent}/MEMORY.md"
    fi
  fi
done

if [ ! -f "${MEMORY_BASE}/shared/SHARED_MEMORY.md" ]; then
  src_shared="${OPENCLAW_CONFIG_DIR}/shared/SHARED_MEMORY.md"
  if [ -f "${src_shared}" ]; then
    cp "${src_shared}" "${MEMORY_BASE}/shared/SHARED_MEMORY.md"
  else
    printf '# SHARED MEMORY — ClawDevs AI\n\n## Promoted Patterns\n' > "${MEMORY_BASE}/shared/SHARED_MEMORY.md"
  fi
fi

# Canonicaliza workspace-<agent>/MEMORY.md para o arquivo central:
for mem_agent in "${MEM_AGENTS[@]}"; do
  ws_memory="${OPENCLAW_STATE_DIR}/workspace-${mem_agent}/MEMORY.md"
  canonical_memory="${MEMORY_BASE}/${mem_agent}/MEMORY.md"
  migrated_snapshot="${MEMORY_BASE}/${mem_agent}/_migrated_workspace_MEMORY.md"

  if [ -f "${ws_memory}" ] && [ ! -L "${ws_memory}" ]; then
    if [ ! -f "${migrated_snapshot}" ]; then
      cp "${ws_memory}" "${migrated_snapshot}"
    fi
    if ! cmp -s "${ws_memory}" "${canonical_memory}"; then
      {
        printf '\n\n## Migrated From Workspace (%s)\n\n' "$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
        cat "${ws_memory}"
      } >> "${canonical_memory}"
    fi
    rm -f "${ws_memory}"
  fi

  ln -sfn "${canonical_memory}" "${ws_memory}"
done
# --- Fim: Sistema de Memória Cross-Agent ---

# --- Politica compartilhada de validacao de fontes (Zero Trust) ---
if [ -f "${OPENCLAW_CONFIG_DIR}/shared/SOURCE_VALIDATION.md" ]; then
  for src_agent in "${AGENTS[@]}"; do
    cp "${OPENCLAW_CONFIG_DIR}/shared/SOURCE_VALIDATION.md" "${OPENCLAW_STATE_DIR}/workspace-${src_agent}/SOURCE_VALIDATION.md"
  done
fi
# --- Fim: politica compartilhada de validacao de fontes ---

# --- Rollout dinamico de skills compartilhadas para todos os agentes ---
# OpenClaw: project-level agent skills under <workspace>/.agents/skills (precedence below <workspace>/skills).
# Source: agents/shared/skills/ -> every workspace-<agent>/.agents/skills/<skill_name>/
SHARED_SKILLS_DIR="${OPENCLAW_CONFIG_DIR}/agents/shared/skills"
if [ -d "${SHARED_SKILLS_DIR}" ]; then
  for shared_skill_dir in "${SHARED_SKILLS_DIR}"/*/; do
    [ -d "${shared_skill_dir}" ] || continue
    skill_name=$(basename "${shared_skill_dir}")

    # Copy to all agent workspaces
    for shared_agent in "${AGENTS[@]}"; do
      target_dir="${OPENCLAW_STATE_DIR}/workspace-${shared_agent}/.agents/skills/${skill_name}"
      mkdir -p "${target_dir}"
      cp -Rf "${shared_skill_dir}/." "${target_dir}/"
    done
  done
fi
# --- Fim: rollout dinamico de skills compartilhadas ---

# Skills partilhadas pertencem apenas a .agents/skills. Volumes antigos podem ter
# copias em workspace-*/skills/ (layout pre-OpenClaw); remove para evitar duplicacao
# e precedencia confusa com a doc.
if [ -d "${SHARED_SKILLS_DIR}" ]; then
  for shared_skill_dir in "${SHARED_SKILLS_DIR}"/*/; do
    [ -d "${shared_skill_dir}" ] || continue
    skill_name=$(basename "${shared_skill_dir}")
    for shared_agent in "${AGENTS[@]}"; do
      legacy_skills="${OPENCLAW_STATE_DIR}/workspace-${shared_agent}/skills/${skill_name}"
      if [ -d "${legacy_skills}" ]; then
        rm -rf "${legacy_skills}"
      fi
    done
  done
fi

# --- Render agent context for all workspaces ---
for agent in "${AGENTS[@]}"; do
  render_agent_context "${OPENCLAW_STATE_DIR}/workspace-${agent}"
done
# --- Fim: render agent context ---

# --- Skills no workspace compartilhado (backlog/implementation) ---
# Espelha no workspace compartilhado o mesmo layout da doc OpenClaw:
#   <workspace>/skills  e  <workspace>/.agents/skills
# (precedencia: skills/ > .agents/skills > ~/.openclaw/skills > bundled > extraDirs)
SHARED_WORKSPACE="${OPENCLAW_STATE_DIR}/backlog/implementation"
mkdir -p "${SHARED_WORKSPACE}/skills"
mkdir -p "${SHARED_WORKSPACE}/.agents/skills"

for skill_src_dir in "${OPENCLAW_STATE_DIR}"/workspace-*/skills/*/; do
  [ -d "${skill_src_dir}" ] || continue
  [ -f "${skill_src_dir}/SKILL.md" ] || continue
  skill_name="$(basename "${skill_src_dir}")"
  dest_dir="${SHARED_WORKSPACE}/skills/${skill_name}"
  mkdir -p "${dest_dir}"
  cp -Rf "${skill_src_dir}/." "${dest_dir}/"
done

for skill_src_dir in "${OPENCLAW_STATE_DIR}"/workspace-*/.agents/skills/*/; do
  [ -d "${skill_src_dir}" ] || continue
  [ -f "${skill_src_dir}/SKILL.md" ] || continue
  skill_name="$(basename "${skill_src_dir}")"
  dest_dir="${SHARED_WORKSPACE}/.agents/skills/${skill_name}"
  mkdir -p "${dest_dir}"
  cp -Rf "${skill_src_dir}/." "${dest_dir}/"
done
# --- Fim: Skills no workspace compartilhado ---

# --- Rollout global da skill self-improving (hardened) ---
# Fonte canonica da skill (path compartilhado).
SELF_IMPROVING_CANONICAL_SRC="${OPENCLAW_CONFIG_DIR}/agents/shared/skills/self-improving/SKILL.md"
SELF_IMPROVING_SECURITY_POLICY_SRC="${OPENCLAW_CONFIG_DIR}/agents/shared/skills/self-improving/references/skill-security-policy.md"

sanitize_skill_artifacts() {
  local skill_dir="$1"
  rm -rf "${skill_dir}/hooks" "${skill_dir}/scripts"
  rm -f "${skill_dir}/HOOK.md" "${skill_dir}/handler.js" "${skill_dir}/handler.ts"
}

if [ -f "${SELF_IMPROVING_CANONICAL_SRC}" ]; then
  for si_agent in "${AGENTS[@]}"; do
    si_ws="${OPENCLAW_STATE_DIR}/workspace-${si_agent}"
    si_skill_dir="${si_ws}/.agents/skills/self-improving"
    mkdir -p "${si_skill_dir}"
    cp -f "${SELF_IMPROVING_CANONICAL_SRC}" "${si_skill_dir}/SKILL.md"

    # Copy references if they exist
    if [ -f "${SELF_IMPROVING_SECURITY_POLICY_SRC}" ]; then
      mkdir -p "${si_skill_dir}/references"
      cp -f "${SELF_IMPROVING_SECURITY_POLICY_SRC}" "${si_skill_dir}/references/skill-security-policy.md"
    fi

    # Gate de seguranca: bloquear artefatos executaveis do pacote upstream 3.0.6.
    sanitize_skill_artifacts "${si_skill_dir}"

    # Estrutura minima de learnings por workspace (nao sobrescreve).
    si_learnings_dir="${si_ws}/.learnings"
    mkdir -p "${si_learnings_dir}"

    if [ ! -f "${si_learnings_dir}/LEARNINGS.md" ]; then
      printf '# LEARNINGS\n\n' > "${si_learnings_dir}/LEARNINGS.md"
    fi
    if [ ! -f "${si_learnings_dir}/ERRORS.md" ]; then
      printf '# ERRORS\n\n' > "${si_learnings_dir}/ERRORS.md"
    fi
    if [ ! -f "${si_learnings_dir}/FEATURE_REQUESTS.md" ]; then
      printf '# FEATURE REQUESTS\n\n' > "${si_learnings_dir}/FEATURE_REQUESTS.md"
    fi
    if [ "${si_agent}" = "security_engineer" ] && [ ! -f "${si_learnings_dir}/SKILL_SECURITY_DECISIONS.md" ]; then
      printf '# SKILL SECURITY DECISIONS\n\n' > "${si_learnings_dir}/SKILL_SECURITY_DECISIONS.md"
    fi
  done

  # Expor a mesma skill no workspace compartilhado utilizado pelos agentes.
  shared_self_improving_dir="${SHARED_WORKSPACE}/.agents/skills/self-improving"
  mkdir -p "${shared_self_improving_dir}"
  cp -f "${SELF_IMPROVING_CANONICAL_SRC}" "${shared_self_improving_dir}/SKILL.md"

  if [ -f "${SELF_IMPROVING_SECURITY_POLICY_SRC}" ]; then
    mkdir -p "${shared_self_improving_dir}/references"
    cp -f "${SELF_IMPROVING_SECURITY_POLICY_SRC}" "${shared_self_improving_dir}/references/skill-security-policy.md"
  fi

  sanitize_skill_artifacts "${shared_self_improving_dir}"
else
  echo "[bootstrap] warning: self-improving canonical files not found at ${SELF_IMPROVING_CANONICAL_SRC}"
fi
# --- Fim: rollout global da skill self-improving ---

# --- Contrato obrigatorio de persistencia em MEMORY.md ---
MEM_CONTRACT_AGENTS=(ceo po arquiteto dev_backend dev_frontend dev_mobile qa_engineer devops_sre security_engineer ux_designer dba_data_engineer)

for mem_contract_agent in "${MEM_CONTRACT_AGENTS[@]}"; do
  mem_contract_agents_file="${OPENCLAW_STATE_DIR}/workspace-${mem_contract_agent}/AGENTS.md"
  if [ -f "${mem_contract_agents_file}" ] && ! grep -q "memory_write_contract_v1" "${mem_contract_agents_file}"; then
    cat >> "${mem_contract_agents_file}" <<EOF

## Memory Persistence Contract (memory_write_contract_v1)
- At the end of every completed task/issue, append 1-3 lines to \`/data/openclaw/memory/${mem_contract_agent}/MEMORY.md\` under \`## Active Patterns\`.
- Use format: \`- [PATTERN] <concise learning> | Discovered: YYYY-MM-DD | Source: TASK-XXX\`.
- Before planning the next action, read \`/data/openclaw/memory/shared/SHARED_MEMORY.md\` and your agent memory file.
EOF
  fi
done
# --- Fim: contrato obrigatorio de persistencia em MEMORY.md ---
