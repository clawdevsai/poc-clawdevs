# OpenClaw Gateway para rodar no Kubernetes (Telegram + Ollama no cluster).
# Build no Minikube: eval $(minikube docker-env) && docker build -f k8s/openclaw/Dockerfile -t openclaw-gateway:local .
FROM node:22-bookworm-slim
RUN apt-get update -qq && apt-get install -y -qq curl git && rm -rf /var/lib/apt/lists/*
RUN npm install -g openclaw@latest
EXPOSE 18789
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
