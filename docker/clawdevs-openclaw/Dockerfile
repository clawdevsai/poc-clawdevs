FROM public.ecr.aws/docker/library/node:22-bookworm-slim

ARG DEBIAN_FRONTEND=noninteractive
ARG OPENCLAW_VERSION=2026.3.24
ARG DOCKER_CLI_VERSION=29.2.1
ENV TZ=America/Sao_Paulo

SHELL ["/bin/bash", "-o", "pipefail", "-c"]

RUN set -eux; \
    apt-get update; \
    apt-get upgrade -y; \
    apt-get install -y --no-install-recommends \
      ca-certificates bash git curl jq python3 python3-venv python3-pip \
      tzdata openssh-client procps; \
    ln -snf /usr/share/zoneinfo/$TZ /etc/localtime; \
    echo $TZ > /etc/timezone; \
    curl -fsSL "https://github.com/cli/cli/releases/download/v2.67.0/gh_2.67.0_linux_amd64.tar.gz" -o /tmp/gh.tar.gz; \
    tar -xzf /tmp/gh.tar.gz -C /tmp; \
    install -m 0755 /tmp/gh_2.67.0_linux_amd64/bin/gh /usr/local/bin/gh; \
    rm -rf /tmp/gh*; \
    curl -fsSL "https://download.docker.com/linux/static/stable/x86_64/docker-${DOCKER_CLI_VERSION}.tgz" -o /tmp/docker.tgz; \
    tar -xzf /tmp/docker.tgz -C /tmp; \
    install -m 0755 /tmp/docker/docker /usr/local/bin/docker; \
    rm -rf /tmp/docker.tgz /tmp/docker; \
    npm install -g npm@10.9.0; \
    apt-get autoremove -y --purge; \
    apt-get clean; \
    rm -rf /root/.npm /tmp/* /var/tmp/* /var/lib/apt/lists/*

ENV HOME=/data/nemoclaw \
    NEMOCLAW_STATE_DIR=/data/nemoclaw \
    OPENCLAW_STATE_DIR=/data/nemoclaw \
    NEMOCLAW_NON_INTERACTIVE=1 \
    OPENCLAW_NO_ONBOARD=1 \
    OPENCLAW_NO_PROMPT=1

WORKDIR /data/nemoclaw

COPY docker/clawdevs-openclaw/entrypoint.sh /usr/local/bin/nemoclaw-entrypoint.sh
RUN chmod +x /usr/local/bin/nemoclaw-entrypoint.sh

EXPOSE 18789

ENTRYPOINT ["/usr/local/bin/nemoclaw-entrypoint.sh"]
