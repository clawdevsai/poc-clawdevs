# OpenClaw Gateway para rodar no Kubernetes (Telegram + Ollama no cluster).
# Build no Minikube: eval $(minikube docker-env) && docker build -f k8s/management-team/openclaw/Dockerfile -t openclaw-gateway:local k8s/management-team/openclaw
FROM node:22-bookworm-slim
RUN apt-get update -qq && apt-get install -y -qq curl git && rm -rf /var/lib/apt/lists/*
RUN npm install -g openclaw@2026.3.2
EXPOSE 18789
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
