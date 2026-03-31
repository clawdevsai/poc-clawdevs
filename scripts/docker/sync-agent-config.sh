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
    agents|shared|memory) continue ;;
  esac
  for file in "${agent_dir}"/*; do
    [ -f "${file}" ] || continue
    copy_key "${agent}-$(basename "${file}")" "${file}"
  done
done

# 1.1) Garantir os MEMORY.md canonicos por agente.
required_memory_agents=(
  ceo
  po
  arquiteto
  dev_backend
  dev_frontend
  dev_mobile
  qa_engineer
  devops_sre
  security_engineer
  ux_designer
  dba_data_engineer
  memory_curator
)
for agent in "${required_memory_agents[@]}"; do
  copy_key "${agent}-MEMORY.md" "${SRC_ROOT}/memory/${agent}/MEMORY.md"
done

# 2) Skills dos agentes (openclaw-config/agents/<agente>/skills/<skill>/SKILL.md)
for skill_file in "${SRC_ROOT}/agents"/*/skills/*/SKILL.md; do
  [ -f "${skill_file}" ] || continue
  skill_dir="$(dirname "${skill_file}")"
  skill_name="$(basename "${skill_dir}")"
  agent="$(basename "$(dirname "$(dirname "${skill_dir}")")")"
  copy_key "${agent}-skill-${skill_name}-SKILL.md" "${skill_file}"
done

# 2.1) Arquivos auxiliares das skills (refs, docs, scripts etc.).
#      Chave: <agente>-skill-<skill>--asset--<caminho_relativo_com___SLASH__>
while IFS= read -r -d '' skill_asset; do
  rel_path="${skill_asset#${SRC_ROOT}/agents/}"
  case "${rel_path}" in
    */skills/*/*) ;;
    *) continue ;;
  esac

  agent="${rel_path%%/*}"
  post_agent="${rel_path#*/skills/}"
  skill_name="${post_agent%%/*}"
  asset_rel="${post_agent#*/}"

  # SKILL.md ja e exportado no passo 2.
  if [ "${asset_rel}" = "SKILL.md" ]; then
    continue
  fi

  asset_rel_encoded="${asset_rel//\//__SLASH__}"
  copy_key "${agent}-skill-${skill_name}--asset--${asset_rel_encoded}" "${skill_asset}"
done < <(find "${SRC_ROOT}/agents" -type f -print0)

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
# (sem mapfile: compativel com bash 3.2 / macOS)
referenced_keys=()
while IFS= read -r line || [ -n "${line}" ]; do
  [ -z "${line}" ] && continue
  referenced_keys+=("$line")
done < <(
  grep -RhoE '/bootstrap/agent-config/[A-Za-z0-9._${}*:-]+' "${BOOTSTRAP_DIR}" \
    | sed 's#.*/##' \
    | grep -v '\*' \
    | grep -v '\${' \
    | grep -vE '^[[:space:]]*$|.*-$' \
    | sort -u
)

mem_agents=()
while IFS= read -r line || [ -n "${line}" ]; do
  [ -z "${line}" ] && continue
  mem_agents+=("$line")
done < <(
  find "${SRC_ROOT}/memory" -mindepth 2 -maxdepth 2 -type f -name "MEMORY.md" \
    | sed -E 's#^'"${SRC_ROOT}"'/memory/([^/]+)/MEMORY\.md$#\1#' \
    | sort -u
)

# bash 3.2 + set -u: iterar por indice evita "${array[@]}" vazio como erro
expected_keys=()
rk_i=0
rk_n=${#referenced_keys[@]}
while [ "${rk_i}" -lt "${rk_n}" ]; do
  key="${referenced_keys[$rk_i]}"
  rk_i=$((rk_i + 1))
  if [[ "${key}" == *'${mem_agent}'* ]]; then
    ma_i=0
    ma_n=${#mem_agents[@]}
    while [ "${ma_i}" -lt "${ma_n}" ]; do
      mem_agent="${mem_agents[$ma_i]}"
      ma_i=$((ma_i + 1))
      expected_keys+=("${key//'${mem_agent}'/${mem_agent}}")
    done
  else
    expected_keys+=("${key}")
  fi
done

expected_keys_sorted=()
while IFS= read -r line || [ -n "${line}" ]; do
  [ -z "${line}" ] && continue
  expected_keys_sorted+=("$line")
done < <(
  if [ "${#expected_keys[@]}" -gt 0 ]; then
    printf '%s\n' "${expected_keys[@]}" | sort -u
  fi
)
expected_keys=()
eks_i=0
eks_n=${#expected_keys_sorted[@]}
while [ "${eks_i}" -lt "${eks_n}" ]; do
  expected_keys+=("${expected_keys_sorted[$eks_i]}")
  eks_i=$((eks_i + 1))
done

missing_keys=()
ek_i=0
ek_n=${#expected_keys[@]}
while [ "${ek_i}" -lt "${ek_n}" ]; do
  key="${expected_keys[$ek_i]}"
  ek_i=$((ek_i + 1))
  if [ ! -f "${DST}/${key}" ]; then
    missing_keys+=("${key}")
  fi
done

if [ "${#missing_keys[@]}" -gt 0 ]; then
  echo "[sync-agent-config] ERRO: chaves ausentes no ${DST}:"
  mk_i=0
  mk_n=${#missing_keys[@]}
  while [ "${mk_i}" -lt "${mk_n}" ]; do
    echo "  - ${missing_keys[$mk_i]}"
    mk_i=$((mk_i + 1))
  done
  exit 1
fi

echo "[sync-agent-config] ${copied} arquivos sincronizados em ${DST}"
