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
