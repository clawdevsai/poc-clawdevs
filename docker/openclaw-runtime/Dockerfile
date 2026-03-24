FROM public.ecr.aws/docker/library/node:22-bookworm-slim

ARG OPENCLAW_VERSION=2026.3.23-2
ARG DEBIAN_FRONTEND=noninteractive

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN set -eux; \
    apt-get update; \
    apt-get upgrade -y; \
    apt-get install -y --no-install-recommends ca-certificates bash git; \
    npm install -g npm@11.12.0; \
    if [ -n "${OPENCLAW_VERSION}" ]; then OPENCLAW_NPM_SPEC="openclaw@${OPENCLAW_VERSION}"; else OPENCLAW_NPM_SPEC="openclaw@latest"; fi; \
    npm install -g --omit=dev "${OPENCLAW_NPM_SPEC}"; \
    npm install --omit=dev --prefix /usr/local/lib/node_modules/openclaw/dist/extensions/discord @hono/node-server@1.19.11; \
    npm install --omit=dev --prefix /usr/local/lib/node_modules/openclaw/dist/extensions/discord/node_modules/@buape/carbon @hono/node-server@1.19.11; \
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
