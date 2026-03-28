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

APT_STAMP="${OPENCLAW_STATE_DIR}/backlog/status/.apt-installed"
required_tools="gh git jq python3 curl"
missing_tools=""
for tool in ${required_tools}; do
  if ! command -v "${tool}" >/dev/null 2>&1; then
    missing_tools="${missing_tools} ${tool}"
  fi
done

if [ -z "${missing_tools}" ]; then
  touch "${APT_STAMP}"
else
  if [ "$(id -u)" -eq 0 ] && [ ! -f "${APT_STAMP}" ]; then
    apt-get update
    apt-get install -y --no-install-recommends ca-certificates curl bash git jq python3 gh
    apt-get autoremove -y
    apt-get clean
    rm -rf /var/lib/apt/lists/*
    touch "${APT_STAMP}"
  else
    echo "[bootstrap][error] Missing required tools:${missing_tools}" >&2
    echo "[bootstrap][error] openclaw-runtime image must provide runtime dependencies." >&2
    exit 1
  fi
fi

gh --version | head -n 1
