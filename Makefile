# ClawDevs — alvos principais: prepare (Docker + Minikube GPU), up (apply), down (destroy)
SHELL := /bin/bash
K8S_DIR := k8s
MINIKUBE_CPUS ?= 10
MINIKUBE_MEMORY ?= 20g

.PHONY: prepare up down openclaw-image verify

# 1. prepare: instala Docker e Minikube com suporte a GPU
prepare:
	@echo "==> Verificando Docker..."
	@command -v docker >/dev/null 2>&1 || { \
		echo "Docker não encontrado. Instalando (requer sudo)..."; \
		curl -fsSL https://get.docker.com | sh; \
		sudo usermod -aG docker $$USER 2>/dev/null || true; \
		echo "  Log out e log in (ou newgrp docker) para usar docker sem sudo."; \
	}
	@echo "==> Verificando kubectl..."
	@command -v kubectl >/dev/null 2>&1 || { \
		echo "kubectl não encontrado. Instalando..."; \
		curl -sLO "https://dl.k8s.io/release/$$(curl -L -s https://dl.k8s.io/release/stable.txt)/bin/linux/amd64/kubectl"; \
		chmod +x kubectl; sudo mv kubectl /usr/local/bin/; \
	}
	@echo "==> Verificando Minikube..."
	@command -v minikube >/dev/null 2>&1 || { \
		echo "Minikube não encontrado. Instalando..."; \
		curl -sLO https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64; \
		chmod +x minikube-linux-amd64; sudo mv minikube-linux-amd64 /usr/local/bin/minikube; \
	}
	@echo "==> Iniciando Minikube com Docker e GPU (driver=docker, nvidia-device-plugin)..."
	@if ! minikube status >/dev/null 2>&1; then \
		minikube start --driver=docker --addons=nvidia-device-plugin --cpus=$(MINIKUBE_CPUS) --memory=$(MINIKUBE_MEMORY); \
	else \
		echo "  Minikube já está rodando."; \
	fi
	@minikube addons enable nvidia-device-plugin 2>/dev/null || true
	@echo "==> prepare concluído. Use 'make up' para aplicar os recursos no cluster."

# 2. up: build da imagem OpenClaw, inicia Minikube (se necessário) e aplica todos os recursos
up: openclaw-image
	@echo "==> Verificando Minikube..."
	@if ! minikube status >/dev/null 2>&1; then \
		echo "==> Iniciando Minikube: minikube start --driver=docker --addons=nvidia-device-plugin --cpus=$(MINIKUBE_CPUS) --memory=$(MINIKUBE_MEMORY)"; \
		minikube start --driver=docker --addons=nvidia-device-plugin --cpus=$(MINIKUBE_CPUS) --memory=$(MINIKUBE_MEMORY); \
		minikube addons enable nvidia-device-plugin 2>/dev/null || true; \
	else \
		echo "  Minikube já está rodando."; \
	fi
	@echo "==> Aplicando namespace..."
	kubectl apply -f $(K8S_DIR)/namespace.yaml
	@echo "==> Aplicando Redis..."
	kubectl apply -f $(K8S_DIR)/redis/deployment.yaml
	@echo "==> Aplicando Ollama..."
	kubectl apply -f $(K8S_DIR)/ollama/deployment.yaml
	@if [ -f $(K8S_DIR)/ollama/secret.yaml ]; then \
		echo "==> Aplicando secret Ollama Cloud (k8s/ollama/secret.yaml)..."; \
		kubectl apply -f $(K8S_DIR)/ollama/secret.yaml; \
		kubectl rollout restart deployment/ollama-gpu -n ai-agents --timeout=60s 2>/dev/null || true; \
	fi
	@if [ -f $(K8S_DIR)/ollama/secret.yaml ]; then \
		echo "==> Ollama Cloud: exige confirmação de login (link no navegador) antes de continuar..."; \
		$(CURDIR)/scripts/ollama-ensure-cloud-auth.sh; \
	else \
		echo "==> Secret Ollama Cloud não encontrado (opcional). Para glm-5:cloud: cp k8s/ollama/secret.yaml.example k8s/ollama/secret.yaml e preencha OLLAMA_API_KEY"; \
	fi
	@echo "==> Aplicando OpenClaw (ConfigMap + Workspace CEO + Deployment)..."
	kubectl apply -f $(K8S_DIR)/openclaw/configmap.yaml
	kubectl apply -f $(K8S_DIR)/openclaw/workspace-ceo-configmap.yaml
	kubectl apply -f $(K8S_DIR)/openclaw/deployment.yaml
	@if [ -f $(K8S_DIR)/openclaw/secret.yaml ]; then \
		echo "==> Aplicando secret Telegram (k8s/openclaw/secret.yaml)..."; \
		kubectl apply -f $(K8S_DIR)/openclaw/secret.yaml; \
		kubectl rollout restart deployment/openclaw -n ai-agents --timeout=60s 2>/dev/null || true; \
	else \
		echo "==> Secret Telegram não encontrado (opcional). Crie k8s/openclaw/secret.yaml ou: kubectl create secret generic openclaw-telegram -n ai-agents --from-literal=TELEGRAM_BOT_TOKEN=... --from-literal=TELEGRAM_CHAT_ID=..."; \
	fi
	@echo "==> up concluído."
	@echo "  Envie mensagem ao ClawDev bot no Telegram; a resposta vem do Ollama no cluster."
	@echo "  Ollama: puxe o modelo do CEO se necessário: kubectl exec -n ai-agents deploy/ollama-gpu -- ollama pull stewyphoenix19/phi3-mini_v1:latest"

# Build da imagem OpenClaw para o Minikube (obrigatório antes do pod openclaw subir com o gateway real)
openclaw-image:
	@echo "==> Build da imagem openclaw-gateway:local no Docker do Minikube..."
	eval $$(minikube docker-env) && docker build -f $(K8S_DIR)/openclaw/Dockerfile -t openclaw-gateway:local $(K8S_DIR)/openclaw
	@echo "==> openclaw-image concluído."

# Verificação de hardware (máquina de referência + consumo GPU/CPU/RAM + Quest 65%) e cluster (Minikube + Ollama GPU)
verify:
	@docs/scripts/verify-machine.sh
	@docs/scripts/verify-gpu-cluster.sh

# 3. down: derruba tudo — deployments, PVCs, secrets, configmaps e namespace. Ambiente em estaca zero.
down:
	@echo "==> down: removendo todos os recursos do ambiente (estaca zero)..."
	@if ! kubectl get namespace ai-agents >/dev/null 2>&1; then \
		echo "  Namespace ai-agents não existe. Ambiente já está limpo."; \
		exit 0; \
	fi
	@echo "==> Deletando deployments (pods saem e liberam volumes)..."
	-kubectl delete deployment -n ai-agents --all --ignore-not-found --timeout=60s 2>/dev/null || true
	-kubectl delete statefulset -n ai-agents --all --ignore-not-found --timeout=60s 2>/dev/null || true
	@echo "==> Aguardando pods terminarem..."
	-kubectl wait --for=delete pod -l app=ollama -n ai-agents --timeout=90s 2>/dev/null || true
	-kubectl wait --for=delete pod -l app=openclaw -n ai-agents --timeout=90s 2>/dev/null || true
	-kubectl wait --for=delete pod -l app=redis -n ai-agents --timeout=90s 2>/dev/null || true
	@sleep 3
	@echo "==> Deletando PVCs (volumes persistentes)..."
	-kubectl delete pvc -n ai-agents --all --ignore-not-found --timeout=60s 2>/dev/null || true
	@echo "==> Deletando serviços, configmaps, secrets restantes e o namespace..."
	-kubectl delete namespace ai-agents --ignore-not-found --timeout=120s 2>/dev/null || true
	@echo "==> Verificando se o namespace sumiu..."
	@for i in 1 2 3 4 5 6 7 8 9 10; do \
		if ! kubectl get namespace ai-agents 2>/dev/null; then echo "  Namespace ai-agents removido."; break; fi; \
		echo "  Aguardando término do namespace ($$i/10)..."; sleep 6; \
	done
	@echo "==> down concluído. Ambiente limpo (estaca zero). Use 'make up' para subir de novo."
