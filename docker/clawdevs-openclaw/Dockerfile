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

FROM public.ecr.aws/docker/library/node:22-bookworm-slim

ARG OPENCLAW_VERSION=2026.3.24
ARG DEBIAN_FRONTEND=noninteractive

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN set -eux; \
    apt-get update; \
    apt-get upgrade -y; \
    apt-get install -y --no-install-recommends ca-certificates bash git curl jq python3 gh; \
    npm install -g npm@10.9.0; \
    if [ -n "${OPENCLAW_VERSION}" ]; then OPENCLAW_NPM_SPEC="openclaw@${OPENCLAW_VERSION}"; else OPENCLAW_NPM_SPEC="openclaw@latest"; fi; \
    npm install -g --omit=dev "${OPENCLAW_NPM_SPEC}"; \
    npm install --omit=dev --prefix /usr/local/lib/node_modules/openclaw/dist/extensions/discord @hono/node-server@1.19.11; \
    npm install --omit=dev --prefix /usr/local/lib/node_modules/openclaw/dist/extensions/discord/node_modules/@buape/carbon @hono/node-server@1.19.11; \
    shopt -s nullglob; \
    PI_FILES=(/usr/local/lib/node_modules/openclaw/dist/pi-embedded-*.js); \
    shopt -u nullglob; \
    test "${#PI_FILES[@]}" -gt 0; \
    node -e "import(process.argv[1]).catch(() => process.exit(1))" "file://${PI_FILES[0]}"; \
    npm cache clean --force; \
    openclaw --version | head -n 1; \
    apt-get autoremove -y --purge; \
    apt-get clean; \
    rm -rf /root/.npm /tmp/* /var/tmp/*; \
    rm -rf /var/lib/apt/lists/*

ENV OPENCLAW_NO_ONBOARD=1 \
    OPENCLAW_NO_PROMPT=1 \
    OPENCLAW_STATE_DIR=/data/openclaw \
    GH_CONFIG_DIR=/data/openclaw/.config/gh

WORKDIR /data/openclaw
