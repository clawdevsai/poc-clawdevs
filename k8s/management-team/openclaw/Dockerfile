# OpenClaw Gateway para rodar no Kubernetes (Telegram + Ollama no cluster).
# gh CLI: necessário para DevOps criar repositórios (gh repo create); usa GH_TOKEN/GITHUB_TOKEN do secret.
# Build no Minikube: eval $(minikube docker-env) && docker build -f k8s/management-team/openclaw/Dockerfile -t openclaw-gateway:local k8s/management-team/openclaw
FROM node:22-bookworm-slim
RUN apt-get update -qq && apt-get install -y -qq curl git wget \
  && mkdir -p -m 755 /etc/apt/keyrings \
  && wget -q -O- https://cli.github.com/packages/githubcli-archive-keyring.gpg | tee /etc/apt/keyrings/githubcli-archive-keyring.gpg > /dev/null \
  && chmod go+r /etc/apt/keyrings/githubcli-archive-keyring.gpg \
  && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" > /etc/apt/sources.list.d/github-cli.list \
  && apt-get update -qq && apt-get install -y -qq gh \
  && rm -rf /var/lib/apt/lists/*
RUN npm install -g openclaw@2026.3.2
EXPOSE 18789
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
