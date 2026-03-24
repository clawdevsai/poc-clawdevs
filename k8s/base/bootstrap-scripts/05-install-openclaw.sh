OPENCLAW_STAMP="${OPENCLAW_STATE_DIR}/backlog/status/.openclaw-installed"

openclaw_telegram_runtime_ok() {
  local pi_embedded
  shopt -s nullglob
  local pi_files=(/usr/local/lib/node_modules/openclaw/dist/pi-embedded-*.js)
  shopt -u nullglob
  if [ "${#pi_files[@]}" -eq 0 ]; then
    return 1
  fi
  pi_embedded="${pi_files[0]}"
  node -e "import(process.argv[1]).catch(() => process.exit(1))" "file://${pi_embedded}" >/dev/null 2>&1 || return 1
  return 0
}

openclaw_runtime_ok() {
  command -v openclaw >/dev/null 2>&1 || return 1
  openclaw --version >/dev/null 2>&1 || return 1
  # Validates command tree imports to avoid broken dist chunk installs.
  openclaw gateway run --help >/dev/null 2>&1 || return 1
  # Telegram failures in production can happen with missing dist chunks
  # even when gateway imports are healthy; verify embedded runtime import.
  openclaw_telegram_runtime_ok || return 1
  return 0
}

install_openclaw() {
  OPENCLAW_VERSION="${OPENCLAW_VERSION:-}"
  if [ -n "${OPENCLAW_VERSION}" ]; then
    curl -fsSL "https://openclaw.ai/install.sh" | bash -s -- --no-onboard --no-prompt --version "${OPENCLAW_VERSION}"
  else
    curl -fsSL "https://openclaw.ai/install.sh" | bash -s -- --no-onboard --no-prompt
  fi
}

if openclaw_runtime_ok; then
  echo "[bootstrap] openclaw ja instalado na imagem e runtime valido, pulando instalacao"
  touch "${OPENCLAW_STAMP}"
else
  if command -v openclaw >/dev/null 2>&1; then
    echo "[bootstrap] openclaw detectado mas runtime invalido; reinstalando"
  else
    echo "[bootstrap] openclaw ausente; instalando"
  fi
  install_openclaw
  touch "${OPENCLAW_STAMP}"
fi

if ! openclaw_runtime_ok; then
  echo "OpenClaw nao foi instalado corretamente" >&2
  exit 1
fi
openclaw --version | head -n 1
