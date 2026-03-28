#!/usr/bin/env bash

set -euo pipefail

if [ "$#" -gt 0 ]; then
  exec "$@"
fi

scripts_dir="${BOOTSTRAP_SCRIPTS_DIR:-/bootstrap/scripts}"
required_scripts=(
  00-env.sh
  01-deps.sh
  02-web-tools.sh
  03-gh-auth.sh
  04-repo-tools.sh
  05-install-openclaw.sh
  06-dirs.sh
  07-agent-workspaces.sh
  08-git-hooks.sh
  09-openclaw-config.sh
  10-background-services.sh
  11-start-gateway.sh
)

if [ ! -d "${scripts_dir}" ]; then
  echo "[entrypoint][error] bootstrap scripts dir not found: ${scripts_dir}" >&2
  exit 1
fi

export PANEL_TOKEN="$(cat /panel-token/PANEL_TOKEN 2>/dev/null || printf '')"

for script_name in "${required_scripts[@]}"; do
  script_path="${scripts_dir}/${script_name}"
  if [ ! -f "${script_path}" ]; then
    echo "[entrypoint][error] bootstrap script not found: ${script_path}" >&2
    exit 1
  fi
done

for script_name in "${required_scripts[@]}"; do
  script_path="${scripts_dir}/${script_name}"
  echo "[entrypoint] running ${script_path}"
  # shellcheck disable=SC1090
  . "${script_path}"
done

echo "[entrypoint] bootstrap sequence finished"
