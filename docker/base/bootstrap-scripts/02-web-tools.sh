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

WEB_TOOLS_DIR="${OPENCLAW_BIN_DIR:-${OPENCLAW_STATE_DIR}/bin}"
mkdir -p "${WEB_TOOLS_DIR}"

# --- web-search: pesquisa via SearxNG (self-hosted, cluster-internal) ---
cat > "${WEB_TOOLS_DIR}/web-search" <<'SCRIPT'
#!/usr/bin/env bash
set -euo pipefail
query="${*}"
if [ -z "${query}" ]; then
  echo "Usage: web-search <query>" >&2
  exit 1
fi
encoded="$(python3 -c "import urllib.parse,sys; print(urllib.parse.quote(sys.argv[1]))" "${query}")"
result="$(curl -sf "http://searxng:8080/search?q=${encoded}&format=json&categories=general&language=pt-BR" 2>/dev/null || true)"
if [ -z "${result}" ]; then
  echo "[web-search] SearxNG indisponivel. Tente novamente." >&2
  exit 1
fi
echo "${result}" | python3 -c "
import json,sys
data = json.load(sys.stdin)
results = data.get('results', [])[:10]
for i, r in enumerate(results, 1):
    print(f'{i}. {r.get(\"title\",\"(sem titulo)\")}')
    print(f'   URL: {r.get(\"url\",\"\")}')
    print(f'   {r.get(\"content\",\"\")[:200]}')
    print()
if not results:
    print('Nenhum resultado encontrado.')
"
SCRIPT
chmod +x "${WEB_TOOLS_DIR}/web-search"
# --- web-read: leitura de paginas via Jina Reader (API publica gratuita) ---
cat > "${WEB_TOOLS_DIR}/web-read" <<'SCRIPT'
#!/usr/bin/env bash
set -euo pipefail
url="${1:-}"
if [ -z "${url}" ]; then
  echo "Usage: web-read <url>" >&2
  exit 1
fi
result="$(curl -sf -H "Accept: text/markdown" "https://r.jina.ai/${url}" 2>/dev/null || true)"
if [ -z "${result}" ]; then
  echo "[web-read] Nao foi possivel ler a URL: ${url}" >&2
  exit 1
fi
echo "${result}"
SCRIPT
chmod +x "${WEB_TOOLS_DIR}/web-read"
echo "[bootstrap] web-search e web-read instalados em ${WEB_TOOLS_DIR}/"
