#!/bin/bash
# Copyright (c) 2026 Diego Silva Morais <lukewaresoftwarehouse@gmail.com>
#
# Gera tmp/agent-config-flat/ com os artefatos de docker/base/openclaw-config
# usando o formato esperado pelos scripts em /bootstrap/agent-config.
#
# Uso: bash scripts/docker/sync-agent-config.sh

set -euo pipefail

SRC_ROOT="docker/base/openclaw-config"
BOOTSTRAP_DIR="docker/base/bootstrap-scripts"
DST="tmp/agent-config-flat"

if [ ! -d "${SRC_ROOT}" ]; then
  echo "[sync-agent-config] ERRO: ${SRC_ROOT} nao encontrado."
  exit 1
fi

if [ ! -d "${BOOTSTRAP_DIR}" ]; then
  echo "[sync-agent-config] ERRO: ${BOOTSTRAP_DIR} nao encontrado."
  exit 1
fi

rm -rf "${DST}"
mkdir -p "${DST}"

shopt -s nullglob

copied=0
had_missing_source=0

copy_key() {
  local key="$1"
  local src="$2"
  if [ ! -f "${src}" ]; then
    echo "[sync-agent-config] ERRO: arquivo fonte ausente para chave ${key}: ${src}"
    had_missing_source=1
    return
  fi
  cp "${src}" "${DST}/${key}"
  copied=$((copied + 1))
}

# 1) Arquivos base dos agentes (openclaw-config/<agente>/*)
for agent_dir in "${SRC_ROOT}"/*; do
  [ -d "${agent_dir}" ] || continue
  agent="$(basename "${agent_dir}")"
  case "${agent}" in
    agents|shared) continue ;;
  esac
  for file in "${agent_dir}"/*; do
    [ -f "${file}" ] || continue
    copy_key "${agent}-$(basename "${file}")" "${file}"
  done
done

# 2) Skills dos agentes (openclaw-config/agents/<agente>/skills/<skill>/SKILL.md)
for skill_file in "${SRC_ROOT}/agents"/*/skills/*/SKILL.md; do
  [ -f "${skill_file}" ] || continue
  skill_dir="$(dirname "${skill_file}")"
  skill_name="$(basename "${skill_dir}")"
  agent="$(basename "$(dirname "$(dirname "${skill_dir}")")")"
  copy_key "${agent}-skill-${skill_name}-SKILL.md" "${skill_file}"
done

# 3) Referencia obrigatoria da skill self-improving
copy_key \
  "shared-skill-self-improving-skill-security-policy.md" \
  "${SRC_ROOT}/agents/shared/skills/self-improving/references/skill-security-policy.md"

# 4) Artefatos compartilhados (openclaw-config/shared/*)
for file in "${SRC_ROOT}/shared"/*; do
  [ -f "${file}" ] || continue
  base="$(basename "${file}")"
  if [ "${base}" = "PROJECT_README.md" ]; then
    copy_key "project-README.md" "${file}"
  else
    copy_key "shared-${base}" "${file}"
  fi
done

# 5) Iniciativa SDD compartilhada
for file in "${SRC_ROOT}/shared/initiatives/internal-sdd-operationalization"/*.md; do
  [ -f "${file}" ] || continue
  copy_key "shared-sdd-initiative-$(basename "${file}")" "${file}"
done

if [ "${had_missing_source}" -ne 0 ]; then
  echo "[sync-agent-config] ERRO: faltam arquivos fonte para montar o agent-config-flat."
  exit 1
fi

# 6) Validacao: tudo que bootstrap referencia em /bootstrap/agent-config/ deve existir
mapfile -t referenced_keys < <(
  grep -RhoE '/bootstrap/agent-config/[A-Za-z0-9._${}-]+' "${BOOTSTRAP_DIR}" \
    | sed 's#.*/##' \
    | sort -u
)

mapfile -t mem_agents < <(
  find "${SRC_ROOT}" -mindepth 2 -maxdepth 2 -type f -name "MEMORY.md" \
    | sed -E 's#^'"${SRC_ROOT}"'/([^/]+)/MEMORY\.md$#\1#' \
    | sort -u
)

expected_keys=()
for key in "${referenced_keys[@]}"; do
  if [[ "${key}" == *'${mem_agent}'* ]]; then
    for mem_agent in "${mem_agents[@]}"; do
      expected_keys+=("${key//'${mem_agent}'/${mem_agent}}")
    done
  else
    expected_keys+=("${key}")
  fi
done

mapfile -t expected_keys < <(printf '%s\n' "${expected_keys[@]}" | sort -u)

missing_keys=()
for key in "${expected_keys[@]}"; do
  if [ ! -f "${DST}/${key}" ]; then
    missing_keys+=("${key}")
  fi
done

if [ "${#missing_keys[@]}" -gt 0 ]; then
  echo "[sync-agent-config] ERRO: chaves ausentes no ${DST}:"
  for key in "${missing_keys[@]}"; do
    echo "  - ${key}"
  done
  exit 1
fi

echo "[sync-agent-config] ${copied} arquivos sincronizados em ${DST}"
