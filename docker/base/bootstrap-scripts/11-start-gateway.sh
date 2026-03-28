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

echo "[bootstrap] starting openclaw gateway"
# Compat: schema atual exige models.providers.openrouter.baseUrl.
if [ -f "${OPENCLAW_STATE_DIR}/openclaw.json" ]; then
  _tmp_openclaw_json="$(mktemp)"
  _or_base_url="${OPENROUTER_BASE_URL:-https://openrouter.ai/api/v1}"
  if jq --arg baseUrl "${_or_base_url}" '
      if .models.providers.openrouter? then
        .models.providers.openrouter.baseUrl = (.models.providers.openrouter.baseUrl // $baseUrl)
      else
        .
      end
    ' "${OPENCLAW_STATE_DIR}/openclaw.json" > "${_tmp_openclaw_json}"; then
    mv "${_tmp_openclaw_json}" "${OPENCLAW_STATE_DIR}/openclaw.json"
    mkdir -p ~/.openclaw
    cp "${OPENCLAW_STATE_DIR}/openclaw.json" ~/.openclaw/openclaw.json
  else
    rm -f "${_tmp_openclaw_json}"
    echo "[bootstrap] warning: failed to enforce openrouter.baseUrl before doctor"
  fi
fi
echo "[bootstrap] running openclaw doctor --fix"
openclaw doctor --fix || echo "[bootstrap] warning: openclaw doctor --fix failed, proceeding with existing config"
# Doctor --fix pode reescrever config; reforca compat antes do gateway.
if [ -f "${OPENCLAW_STATE_DIR}/openclaw.json" ]; then
  _tmp_openclaw_json="$(mktemp)"
  _or_base_url="${OPENROUTER_BASE_URL:-https://openrouter.ai/api/v1}"
  if jq --arg baseUrl "${_or_base_url}" '
      if .models.providers.openrouter? then
        .models.providers.openrouter.baseUrl = (.models.providers.openrouter.baseUrl // $baseUrl)
      else
        .
      end
    ' "${OPENCLAW_STATE_DIR}/openclaw.json" > "${_tmp_openclaw_json}"; then
    mv "${_tmp_openclaw_json}" "${OPENCLAW_STATE_DIR}/openclaw.json"
    mkdir -p ~/.openclaw
    cp "${OPENCLAW_STATE_DIR}/openclaw.json" ~/.openclaw/openclaw.json
  else
    rm -f "${_tmp_openclaw_json}"
    echo "[bootstrap] warning: failed to enforce openrouter.baseUrl after doctor"
  fi
fi
set +e
openclaw gateway run --bind lan --port 18789
gateway_exit=$?
set -e
echo "[bootstrap] openclaw gateway exited with code ${gateway_exit}"
latest_gateway_log="$(ls -1t /tmp/openclaw/openclaw-*.log 2>/dev/null | head -n 1 || true)"
if [ -n "${latest_gateway_log}" ] && [ -f "${latest_gateway_log}" ]; then
  cp "${latest_gateway_log}" "${BOOTSTRAP_LOG_DIR}/openclaw-gateway-last.log" || true
  cat "${latest_gateway_log}" || true
fi
exit "${gateway_exit}"
