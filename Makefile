# ════════════════════════════════════════════════════════════════════════════
# ClawDevs AI - Makefile
# ════════════════════════════════════════════════════════════════════════════

ifeq ($(OS),Windows_NT)
SHELL := C:/Program Files/Git/bin/bash.exe
NULL_DEV ?= NUL
else
NULL_DEV ?= /dev/null
endif

# ────────────────────────────────────────────────────────────────────────────
# Variáveis de Configuração
# ────────────────────────────────────────────────────────────────────────────
PROFILE ?= clawdevs-ai
KUBE_CONTEXT ?= clawdevs-ai
CPUS ?= 2
MEMORY ?= 7168
K8S_VERSION ?= v1.34.1
GPU ?= 1
KUSTOMIZE_DIR ?= k8s

# Repositórios de Imagens
OPENCLAW_IMAGE_REPO ?= clawdevsai/openclaw-runtime
OPENCLAW_IMAGE_TAG ?= latest
OPENCLAW_VERSION ?= 2026.3.22
OLLAMA_IMAGE_REPO ?= clawdevsai/ollama-runtime
SEARXNG_IMAGE_REPO ?= clawdevsai/searxng-runtime
SEARXNG_PROXY_IMAGE_REPO ?= clawdevsai/searxng-proxy
PANEL_BACKEND_IMAGE_REPO ?= clawdevsai/clawdevs-panel-backend
PANEL_FRONTEND_IMAGE_REPO ?= clawdevsai/clawdevs-panel-frontend
POSTGRES_IMAGE_REPO ?= clawdevsai/postgres-runtime
REDIS_IMAGE_REPO ?= clawdevsai/redis-runtime
STACK_IMAGE_TAG ?= latest

# Modo de Push de Imagens
PUSH_IMAGE ?=
PUSH_IMAGE_ENV_RAW := $(shell [ -f k8s/.env ] && sed -n 's/^PUSH_IMAGE=//p' k8s/.env | head -n 1 | tr -d '\r' || true)
PUSH_IMAGE_MODE_RAW := $(if $(strip $(PUSH_IMAGE)),$(strip $(PUSH_IMAGE)),$(strip $(PUSH_IMAGE_ENV_RAW)))
PUSH_IMAGE_MODE := $(if $(strip $(PUSH_IMAGE_MODE_RAW)),$(strip $(PUSH_IMAGE_MODE_RAW)),remote)

# Volumes e Imagens Docker
DOCKER_VOLUMES_CLAWDEVS := $(shell docker volume ls -q --filter=name=clawdevs 2>$(NULL_DEV))
DOCKER_VOLUMES_OPENCLAW := $(shell docker volume ls -q --filter=name=openclaw 2>$(NULL_DEV))
DOCKER_VOLUMES_OLLAMA := $(shell docker volume ls -q --filter=name=ollama 2>$(NULL_DEV))
DOCKER_IMAGES_PROJECT := $(shell docker images --filter=reference=*clawdevs* --filter=reference=*openclaw* --filter=reference=*ollama* -q 2>$(NULL_DEV))

# ────────────────────────────────────────────────────────────────────────────
# .PHONY Targets
# ────────────────────────────────────────────────────────────────────────────
.PHONY: help
.PHONY: preflight manifests-validate secrets-apply
.PHONY: minikube-up minikube-down minikube-context minikube-addons minikube-status minikube-logs storage-enable-expansion
.PHONY: clawdevs-up clawdevs-down reset-all destroy-all
.PHONY: ollama-apply ollama-volume-apply ollama-logs ollama-sign ollama-list
.PHONY: openclaw-apply openclaw-apply-gpu openclaw-restart openclaw-logs openclaw-dashboard
.PHONY: panel-apply panel-status panel-logs-backend panel-logs-frontend panel-db-migrate panel-restart panel-destroy panel-url panel-forward services-expose services-stop
.PHONY: stack-apply stack-status
.PHONY: net-allow-egress net-test-openclaw
.PHONY: dashboard dashboard-url
.PHONY: image-mode-prepare images-build-local
.PHONY: openclaw-image-build openclaw-image-push openclaw-image-release
.PHONY: ollama-image-build ollama-image-push
.PHONY: searxng-image-build searxng-image-push
.PHONY: searxng-proxy-image-build searxng-proxy-image-push
.PHONY: panel-backend-image-build panel-backend-image-push
.PHONY: panel-frontend-image-build panel-frontend-image-push
.PHONY: postgres-image-build postgres-image-push
.PHONY: redis-image-build redis-image-push
.PHONY: images-build images-push images-release
.PHONY: gpu-doctor docker-k8s-check docker-k8s-context gpu-plugin-apply gpu-node-check gpu-migrate-apply
.PHONY: spec-template vibe-playbook sdd-contract constitution-template speckit-flow sdd-checklist
.PHONY: brief-template clarify-template plan-template task-template validate-template
.PHONY: sdd-prompts sdd-example sdd-real-initiative

# ════════════════════════════════════════════════════════════════════════════
# SEÇÃO 1: PREPARAÇÃO DE AMBIENTE
# ════════════════════════════════════════════════════════════════════════════

help:
	@echo "════════════════════════════════════════════════════════════════"
	@echo "  ClawDevs AI - Makefile Targets"
	@echo "════════════════════════════════════════════════════════════════"
	@echo ""
	@echo "┌─ SEÇÃO 1: PREPARAÇÃO DE AMBIENTE ─────────────────────────────┐"
	@echo "│ make clawdevs-up              - Setup completo (não destrutivo)│"
	@echo "│ make minikube-up              - Inicia Minikube com GPU        │"
	@echo "│ make minikube-context         - Configura contexto k8s         │"
	@echo "│ make minikube-addons          - Habilita addons necessários    │"
	@echo "│ make storage-enable-expansion - Habilita expansão de volumes   │"
	@echo "│ make preflight                - Valida k8s/.env                │"
	@echo "│ make manifests-validate       - Valida manifests kustomize     │"
	@echo "│                                                                │"
	@echo "│ GPU (Docker Desktop Kubernetes):                               │"
	@echo "│ make gpu-doctor               - Diagnóstico completo GPU       │"
	@echo "│ make docker-k8s-check         - Valida contexto docker-desktop │"
	@echo "│ make docker-k8s-context       - Muda para contexto docker-desk │"
	@echo "│ make gpu-plugin-apply         - Aplica NVIDIA device plugin    │"
	@echo "│ make gpu-node-check           - Verifica GPU no node           │"
	@echo "│ make gpu-migrate-apply        - Aplica stack com GPU           │"
	@echo "└────────────────────────────────────────────────────────────────┘"
	@echo ""
	@echo "┌─ SEÇÃO 2: DEPLOY E OPERAÇÃO ──────────────────────────────────┐"
	@echo "│ make stack-apply              - Deploy completo (ollama+openclaw+panel)│"
	@echo "│ make stack-status             - Status de todos os pods        │"
	@echo "│                                                                │"
	@echo "│ Ollama:                                                        │"
	@echo "│ make ollama-volume-apply      - Cria PVC ollama-data           │"
	@echo "│ make ollama-apply             - Deploy Ollama pod              │"
	@echo "│ make ollama-sign              - Login no Ollama                │"
	@echo "│ make ollama-list              - Lista modelos Ollama           │"
	@echo "│                                                                │"
	@echo "│ OpenClaw:                                                      │"
	@echo "│ make openclaw-apply           - Deploy OpenClaw                │"
	@echo "│ make openclaw-apply-gpu       - Deploy OpenClaw com GPU        │"
	@echo "│ make openclaw-restart         - Restart preservando PVC        │"
	@echo "│ make openclaw-dashboard       - Abre dashboard OpenClaw        │"
	@echo "│                                                                │"
	@echo "│ Control Panel:                                                 │"
	@echo "│ make panel-apply              - Deploy control panel           │"
	@echo "│ make panel-url                - Mostra URLs de acesso          │"
	@echo "│ make panel-forward            - Port-forward para localhost:3000│"
	@echo "│ make services-expose          - Expoe todos em portas fixas    │"
	@echo "│ make services-stop            - Para todos os port-forwards    │"
	@echo "│ make panel-status             - Status dos pods                │"
	@echo "│ make panel-db-migrate         - Executa migrations Alembic     │"
	@echo "│ make panel-restart            - Restart panel pods             │"
	@echo "│                                                                │"
	@echo "│ Rede:                                                          │"
	@echo "│ make net-allow-egress         - Aplica NetworkPolicy egress    │"
	@echo "│ make net-test-openclaw        - Testa conectividade internet   │"
	@echo "│                                                                │"
	@echo "│ Dashboard:                                                     │"
	@echo "│ make dashboard                - Abre Minikube dashboard        │"
	@echo "│ make dashboard-url            - Mostra URL do dashboard        │"
	@echo "│                                                                │"
	@echo "│ Build de Imagens:                                              │"
	@echo "│ make images-build             - Build todas as imagens         │"
	@echo "│ make images-push              - Push todas as imagens          │"
	@echo "│ make images-release           - Build + Push todas             │"
	@echo "│ make openclaw-image-release   - Build + Push OpenClaw          │"
	@echo "│                                                                │"
	@echo "│ Reset/Destrutivo:                                              │"
	@echo "│ make reset-all                - Recria stack do zero           │"
	@echo "│ make destroy-all              - Limpeza completa               │"
	@echo "│ make clawdevs-down            - Para e remove tudo             │"
	@echo "│ make minikube-down            - Para Minikube                  │"
	@echo "│ make panel-destroy            - Remove control panel           │"
	@echo "└────────────────────────────────────────────────────────────────┘"
	@echo ""
	@echo "┌─ SEÇÃO 3: LOGS E MONITORAMENTO ───────────────────────────────┐"
	@echo "│ make minikube-status          - Status do Minikube             │"
	@echo "│ make minikube-logs            - Logs do Minikube               │"
	@echo "│ make ollama-logs              - Logs do Ollama                 │"
	@echo "│ make openclaw-logs            - Logs do OpenClaw               │"
	@echo "│ make panel-logs-backend       - Logs do backend                │"
	@echo "│ make panel-logs-frontend      - Logs do frontend               │"
	@echo "│                                                                │"
	@echo "│ Templates SDD:                                                 │"
	@echo "│ make spec-template            - Template SPEC                  │"
	@echo "│ make vibe-playbook            - Playbook vibe coding           │"
	@echo "│ make sdd-contract             - Contrato SDD                   │"
	@echo "│ make constitution-template    - Constitution                   │"
	@echo "│ make speckit-flow             - Fluxo Spec Kit                 │"
	@echo "│ make sdd-checklist            - Checklist SDD                  │"
	@echo "│ make brief-template           - Template BRIEF                 │"
	@echo "│ make clarify-template         - Template CLARIFY               │"
	@echo "│ make plan-template            - Template PLAN                  │"
	@echo "│ make task-template            - Template TASK                  │"
	@echo "│ make validate-template        - Template VALIDATE              │"
	@echo "│ make sdd-prompts              - Prompts operacionais           │"
	@echo "│ make sdd-example              - Exemplo ciclo completo         │"
	@echo "│ make sdd-real-initiative      - Iniciativa real                │"
	@echo "└────────────────────────────────────────────────────────────────┘"
	@echo ""

# ────────────────────────────────────────────────────────────────────────────
# Validação e Preflight
# ────────────────────────────────────────────────────────────────────────────

preflight:
	@set -eu; \
	required_keys="OPENCLAW_GATEWAY_TOKEN TELEGRAM_BOT_TOKEN_CEO TELEGRAM_CHAT_ID_CEO GITHUB_TOKEN GITHUB_ORG OLLAMA_API_KEY"; \
	for key in $$required_keys; do \
		value="$$(sed -n "s/^$${key}=//p" k8s/.env | head -n 1 | tr -d '\r' || true)"; \
		if [ -z "$$value" ]; then \
			echo "Erro: $$key vazio em k8s/.env. Preencha os segredos antes de aplicar."; \
			exit 1; \
		fi; \
	done; \
	push_mode="$(PUSH_IMAGE_MODE)"; \
	if [ "$$push_mode" != "local" ] && [ "$$push_mode" != "remote" ]; then \
		echo "Erro: PUSH_IMAGE invalido ($$push_mode). Use PUSH_IMAGE=local ou PUSH_IMAGE=remote em k8s/.env."; \
		exit 1; \
	fi

manifests-validate:
	kubectl kustomize $(KUSTOMIZE_DIR)

secrets-apply:
	kubectl --context=$(KUBE_CONTEXT) apply -k $(KUSTOMIZE_DIR) --server-side --force-conflicts

# ────────────────────────────────────────────────────────────────────────────
# Minikube
# ────────────────────────────────────────────────────────────────────────────

minikube-up:
	@if minikube status --profile=$(PROFILE) >$(NULL_DEV) 2>&1; then \
		echo "[minikube-up] Perfil $(PROFILE) ja esta em execucao. Pulando start."; \
	else \
		minikube start \
			--profile=$(PROFILE) \
			--driver=docker \
			--container-runtime=docker \
			--gpus=all \
			--kubernetes-version=$(K8S_VERSION) \
			--cpus=$(CPUS) \
			--memory=$(MEMORY); \
	fi

minikube-down:
	minikube stop --profile=$(PROFILE)
	minikube delete --profile=$(PROFILE)

minikube-context:
	minikube profile $(PROFILE)
	minikube update-context -p $(PROFILE)
	kubectl config use-context $(PROFILE)

minikube-addons:
	minikube addons enable dashboard -p $(PROFILE) --force --refresh
	minikube addons enable metrics-server -p $(PROFILE) --force --refresh
	minikube addons enable default-storageclass -p $(PROFILE) --force --refresh
	minikube addons enable storage-provisioner -p $(PROFILE) --force --refresh
ifneq ($(GPU),0)
	minikube addons enable nvidia-device-plugin -p $(PROFILE) --force --refresh
endif

minikube-status:
	minikube status --profile=$(PROFILE)

minikube-logs:
	minikube logs --profile=$(PROFILE)

storage-enable-expansion:
	kubectl --context=$(KUBE_CONTEXT) patch storageclass standard -p "{\"allowVolumeExpansion\":true}"

dashboard:
	minikube dashboard -p $(PROFILE)

dashboard-url:
	minikube dashboard -p $(PROFILE) --url

# ────────────────────────────────────────────────────────────────────────────
# GPU (Docker Desktop Kubernetes)
# ────────────────────────────────────────────────────────────────────────────

gpu-doctor:
	@echo "[1/4] NVIDIA host..."
	powershell -NoProfile -Command "Get-CimInstance Win32_VideoController | Select-Object Name, DriverVersion | Format-Table -AutoSize"
	@echo "[2/4] Docker runtime..."
	docker info --format "{{json .Runtimes}}"
	@echo "[3/4] Docker Desktop Kubernetes (settings-store)..."
	powershell -NoProfile -Command "$$p=Join-Path $$env:APPDATA 'Docker\\settings-store.json'; if (!(Test-Path $$p)) { throw \"settings-store.json nao encontrado em $$p\" }; $$json=Get-Content $$p -Raw | ConvertFrom-Json; if (-not $$json.KubernetesEnabled) { throw 'KubernetesEnabled=false no Docker Desktop. Habilite Kubernetes em Settings > Kubernetes e aguarde ficar Running.' } else { Write-Host 'KubernetesEnabled=true' }"
	@echo "[4/4] kube contexts..."
	kubectl config get-contexts

docker-k8s-check:
	kubectl --context=docker-desktop cluster-info
	kubectl --context=docker-desktop get nodes -o wide

docker-k8s-context:
	kubectl config use-context docker-desktop

gpu-plugin-apply:
	kubectl --context=docker-desktop apply -k k8s/overlays/gpu
	kubectl --context=docker-desktop -n kube-system rollout status daemonset/nvidia-device-plugin-daemonset --timeout=240s

gpu-node-check:
	kubectl --context=docker-desktop get node -o custom-columns=NAME:.metadata.name,GPU_CAP:.status.capacity.\"nvidia.com/gpu\",GPU_ALLOC:.status.allocatable.\"nvidia.com/gpu\"
	powershell -NoProfile -Command "kubectl --context=docker-desktop get events -A --sort-by=.lastTimestamp | Select-Object -Last 40"

gpu-migrate-apply:
	$(MAKE) KUBE_CONTEXT=docker-desktop KUSTOMIZE_DIR=k8s/overlays/gpu stack-apply
	$(MAKE) KUBE_CONTEXT=docker-desktop stack-status

# ────────────────────────────────────────────────────────────────────────────
# Setup Completo
# ────────────────────────────────────────────────────────────────────────────

clawdevs-up:
	@set -e; \
	steps="preflight minikube-up minikube-context minikube-addons storage-enable-expansion ollama-volume-apply secrets-apply stack-apply panel-db-migrate"; \
	total=8; \
	i=1; \
	for step in $$steps; do \
		echo ""; \
		echo "════════════════════════════════════════════"; \
		echo " [$$i/$$total] Executando $$step..."; \
		echo "════════════════════════════════════════════"; \
		$(MAKE) $$step; \
		i=$$((i + 1)); \
	done; \
	echo ""; \
	echo "✔ clawdevs-up concluido (nao destrutivo)."; \
	echo "ℹ para logs: make openclaw-logs"

clawdevs-down:
	@echo "════════════════════════════════════════════"
	@echo " [clawdevs-down] Destruindo ambiente completo..."
	@echo "════════════════════════════════════════════"
	$(MAKE) destroy-all

# ════════════════════════════════════════════════════════════════════════════
# SEÇÃO 2: DEPLOY E OPERAÇÃO
# ════════════════════════════════════════════════════════════════════════════

# ────────────────────────────────────────────────────────────────────────────
# Ollama
# ────────────────────────────────────────────────────────────────────────────

ollama-volume-apply:
	kubectl --context=$(KUBE_CONTEXT) apply -f k8s/base/ollama-pvc.yaml --server-side --force-conflicts

ollama-apply: preflight image-mode-prepare ollama-volume-apply
	kubectl --context=$(KUBE_CONTEXT) apply -f k8s/base/ollama-pod.yaml --server-side --force-conflicts

ollama-logs:
	kubectl --context=$(KUBE_CONTEXT) logs -f pod/ollama

ollama-sign:
	kubectl --context=$(KUBE_CONTEXT) exec -it pod/ollama -- ollama signin

ollama-list:
	kubectl --context=$(KUBE_CONTEXT) exec -it pod/ollama -- ollama list

# ────────────────────────────────────────────────────────────────────────────
# OpenClaw
# ────────────────────────────────────────────────────────────────────────────

openclaw-apply: preflight image-mode-prepare manifests-validate net-allow-egress
	kubectl --context=$(KUBE_CONTEXT) apply -k $(KUSTOMIZE_DIR) --server-side --force-conflicts

openclaw-apply-gpu: preflight net-allow-egress
	$(MAKE) KUBE_CONTEXT=$(KUBE_CONTEXT) KUSTOMIZE_DIR=k8s/overlays/gpu manifests-validate
	kubectl --context=$(KUBE_CONTEXT) apply -k k8s/overlays/gpu --server-side --force-conflicts

openclaw-restart:
	kubectl --context=$(KUBE_CONTEXT) rollout restart statefulset/clawdevs-ai
	kubectl --context=$(KUBE_CONTEXT) rollout status statefulset/clawdevs-ai --timeout=240s

openclaw-logs:
	kubectl --context=$(KUBE_CONTEXT) logs -f statefulset/clawdevs-ai

openclaw-dashboard:
	kubectl --context=$(KUBE_CONTEXT) exec pod/clawdevs-ai-0 -- openclaw dashboard --no-open

# ────────────────────────────────────────────────────────────────────────────
# Control Panel
# ────────────────────────────────────────────────────────────────────────────

panel-apply: image-mode-prepare 
	kubectl apply -k k8s/base/control-panel/

panel-status:
	kubectl get pods -l app.kubernetes.io/part-of=clawdevs-panel 2>/dev/null || \
	kubectl get pods | grep clawdevs-panel

panel-logs-backend:
	kubectl logs -l app=clawdevs-panel-backend -f --tail=100

panel-logs-frontend:
	kubectl logs -l app=clawdevs-panel-frontend -f --tail=100

panel-db-migrate:
	kubectl exec -it $$(kubectl get pod -l app=clawdevs-panel-backend -o jsonpath='{.items[0].metadata.name}') \
	-- alembic upgrade head

panel-restart:
	kubectl rollout restart deployment/clawdevs-panel-backend deployment/clawdevs-panel-frontend deployment/clawdevs-panel-worker

panel-destroy:
	kubectl delete -k k8s/base/control-panel/ || true

panel-forward:
	minikube service clawdevs-panel-frontend --url -p clawdevs-ai

services-expose:
	@echo "════════════════════════════════════════════════════════════════"
	@echo "  Expondo servicos em portas fixas do localhost..."
	@echo "════════════════════════════════════════════════════════════════"
	@echo ""
	@echo "Iniciando port-forwards em background:"
	@echo "  - Painel (Frontend):  http://localhost:3000"
	@echo "  - Painel (Backend):   http://localhost:8000 (API docs: /docs)"
	@echo "  - OpenClaw (Gateway): http://localhost:18789"
	@echo ""
	@echo "Para parar: make services-stop"
	@echo ""
	@start /b powershell -NoProfile -WindowStyle Hidden -Command "kubectl --context=$(KUBE_CONTEXT) port-forward svc/clawdevs-panel-frontend 3000:3000 2>&1 | Out-Null" 2>/dev/null || \
	kubectl --context=$(KUBE_CONTEXT) port-forward svc/clawdevs-panel-frontend 3000:3000 > /dev/null 2>&1 &
	@sleep 2
	@start /b powershell -NoProfile -WindowStyle Hidden -Command "kubectl --context=$(KUBE_CONTEXT) port-forward svc/clawdevs-panel-backend 8000:8000 2>&1 | Out-Null" 2>/dev/null || \
	kubectl --context=$(KUBE_CONTEXT) port-forward svc/clawdevs-panel-backend 8000:8000 > /dev/null 2>&1 &
	@sleep 2
	@start /b powershell -NoProfile -WindowStyle Hidden -Command "kubectl --context=$(KUBE_CONTEXT) port-forward svc/clawdevs-ai 18789:18789 2>&1 | Out-Null" 2>/dev/null || \
	kubectl --context=$(KUBE_CONTEXT) port-forward svc/clawdevs-ai 18789:18789 > /dev/null 2>&1 &
	@sleep 2
	@echo "✔ Port-forwards iniciados!"
	@echo ""
	@echo "Acesse:"
	@echo "  http://localhost:3000  - Painel de Controle"
	@echo "  http://localhost:8000/docs - API Docs"
	@echo "  http://localhost:18789   - OpenClaw Gateway"

services-stop:
	@echo "Parando port-forwards..."
	-taskkill /F /IM kubectl.exe 2>/dev/null || pkill -f "port-forward" 2>/dev/null || true
	@echo "✔ Port-forwards parados."

# ────────────────────────────────────────────────────────────────────────────
# Stack Completo
# ────────────────────────────────────────────────────────────────────────────

stack-apply: ollama-apply openclaw-apply-gpu panel-apply

stack-status:
	kubectl --context=$(KUBE_CONTEXT) get pods -l app=ollama
	kubectl --context=$(KUBE_CONTEXT) get pods -l app=clawdevs-ai
	kubectl --context=$(KUBE_CONTEXT) get svc ollama clawdevs-ai

# ────────────────────────────────────────────────────────────────────────────
# Rede
# ────────────────────────────────────────────────────────────────────────────

net-allow-egress:
	kubectl --context=$(KUBE_CONTEXT) apply -f k8s/base/networkpolicy-allow-egress.yaml

net-test-openclaw:
	kubectl --context=$(KUBE_CONTEXT) exec deployment/openclaw -- bash -lc "apt-get update >/dev/null 2>&1 || true; apt-get install -y --no-install-recommends curl ca-certificates dnsutils >/dev/null 2>&1 || true; echo 'DNS:'; nslookup google.com | head -n 5; echo 'HTTPS:'; curl -I -m 10 https://google.com | head -n 1"

# ────────────────────────────────────────────────────────────────────────────
# Build e Push de Imagens
# ────────────────────────────────────────────────────────────────────────────

image-mode-prepare:
	@set -eu; \
	push_mode="$(PUSH_IMAGE_MODE)"; \
	if [ "$$push_mode" = "local" ]; then \
		echo "[image-mode-prepare] PUSH_IMAGE=local -> build local no Minikube."; \
		$(MAKE) images-build-local; \
	else \
		echo "[image-mode-prepare] PUSH_IMAGE=remote -> deploy por pull do Docker Hub."; \
	fi

images-build-local:
	minikube image build -t $(OPENCLAW_IMAGE_REPO):$(OPENCLAW_IMAGE_TAG) -f docker/openclaw-runtime/Dockerfile .
	minikube image build -t $(OLLAMA_IMAGE_REPO):$(STACK_IMAGE_TAG) -f docker/ollama-runtime/Dockerfile .
	minikube image build -t $(SEARXNG_IMAGE_REPO):$(STACK_IMAGE_TAG) -f docker/searxng-runtime/Dockerfile .
	minikube image build -t $(SEARXNG_PROXY_IMAGE_REPO):$(STACK_IMAGE_TAG) -f docker/searxng-proxy/Dockerfile .
	minikube image build -t $(PANEL_BACKEND_IMAGE_REPO):$(STACK_IMAGE_TAG) control-panel/backend/
	minikube image build -t $(PANEL_FRONTEND_IMAGE_REPO):$(STACK_IMAGE_TAG) control-panel/frontend/
	minikube image build -t $(POSTGRES_IMAGE_REPO):$(STACK_IMAGE_TAG) -f docker/postgres-runtime/Dockerfile .
	minikube image build -t $(REDIS_IMAGE_REPO):$(STACK_IMAGE_TAG) -f docker/redis-runtime/Dockerfile .

openclaw-image-build:
	docker build \
		--build-arg OPENCLAW_VERSION=$(OPENCLAW_VERSION) \
		-t $(OPENCLAW_IMAGE_REPO):$(OPENCLAW_IMAGE_TAG) \
		-f docker/openclaw-runtime/Dockerfile .

openclaw-image-push:
	docker push $(OPENCLAW_IMAGE_REPO):$(OPENCLAW_IMAGE_TAG)

openclaw-image-release: openclaw-image-build openclaw-image-push

ollama-image-build:
	docker build -t $(OLLAMA_IMAGE_REPO):$(STACK_IMAGE_TAG) -f docker/ollama-runtime/Dockerfile .

ollama-image-push:
	docker push $(OLLAMA_IMAGE_REPO):$(STACK_IMAGE_TAG)

searxng-image-build:
	docker build -t $(SEARXNG_IMAGE_REPO):$(STACK_IMAGE_TAG) -f docker/searxng-runtime/Dockerfile .

searxng-image-push:
	docker push $(SEARXNG_IMAGE_REPO):$(STACK_IMAGE_TAG)

searxng-proxy-image-build:
	docker build -t $(SEARXNG_PROXY_IMAGE_REPO):$(STACK_IMAGE_TAG) -f docker/searxng-proxy/Dockerfile .

searxng-proxy-image-push:
	docker push $(SEARXNG_PROXY_IMAGE_REPO):$(STACK_IMAGE_TAG)

panel-backend-image-build:
	docker build -t $(PANEL_BACKEND_IMAGE_REPO):$(STACK_IMAGE_TAG) control-panel/backend/

panel-backend-image-push:
	docker push $(PANEL_BACKEND_IMAGE_REPO):$(STACK_IMAGE_TAG)

panel-frontend-image-build:
	docker build -t $(PANEL_FRONTEND_IMAGE_REPO):$(STACK_IMAGE_TAG) control-panel/frontend/

panel-frontend-image-push:
	docker push $(PANEL_FRONTEND_IMAGE_REPO):$(STACK_IMAGE_TAG)

postgres-image-build:
	docker build -t $(POSTGRES_IMAGE_REPO):$(STACK_IMAGE_TAG) -f docker/postgres-runtime/Dockerfile .

postgres-image-push:
	docker push $(POSTGRES_IMAGE_REPO):$(STACK_IMAGE_TAG)

redis-image-build:
	docker build -t $(REDIS_IMAGE_REPO):$(STACK_IMAGE_TAG) -f docker/redis-runtime/Dockerfile .

redis-image-push:
	docker push $(REDIS_IMAGE_REPO):$(STACK_IMAGE_TAG)

images-build: openclaw-image-build ollama-image-build searxng-image-build searxng-proxy-image-build panel-backend-image-build panel-frontend-image-build postgres-image-build redis-image-build

images-push: openclaw-image-push ollama-image-push searxng-image-push searxng-proxy-image-push panel-backend-image-push panel-frontend-image-push postgres-image-push redis-image-push

images-release: images-build images-push

# ────────────────────────────────────────────────────────────────────────────
# Reset e Limpeza
# ────────────────────────────────────────────────────────────────────────────

reset-all:
	@echo "Reset completo: apaga todos os pods e volumes do stack e recria tudo do zero."
	kubectl --context=$(KUBE_CONTEXT) delete pod --all --ignore-not-found --wait=true --timeout=120s
	kubectl --context=$(KUBE_CONTEXT) delete pvc --all --ignore-not-found --wait=true --timeout=120s
	kubectl --context=$(KUBE_CONTEXT) delete statefulset clawdevs-ai --ignore-not-found --wait=true
	kubectl --context=$(KUBE_CONTEXT) delete configmap openclaw-agent-config --ignore-not-found
	kubectl --context=$(KUBE_CONTEXT) delete secret openclaw-auth ollama-auth --ignore-not-found
	kubectl --context=$(KUBE_CONTEXT) delete service ollama clawdevs-ai --ignore-not-found
	kubectl --context=$(KUBE_CONTEXT) delete networkpolicy allow-all-egress --ignore-not-found
	kubectl --context=$(KUBE_CONTEXT) delete runtimeclass nvidia --ignore-not-found
	kubectl --context=$(KUBE_CONTEXT) -n kube-system delete daemonset nvidia-device-plugin-daemonset --ignore-not-found
	$(MAKE) stack-apply
	kubectl --context=$(KUBE_CONTEXT) wait --for=condition=Ready pod/ollama --timeout=240s
	kubectl --context=$(KUBE_CONTEXT) wait --for=condition=Ready pod/clawdevs-ai-0 --timeout=240s
	$(MAKE) stack-status

destroy-all:
	@echo "[destroy-all] Removendo todos os recursos k8s do projeto clawdevs-ai..."
	-kubectl --context=$(KUBE_CONTEXT) delete statefulset clawdevs-ai --ignore-not-found --wait=true --timeout=120s
	-kubectl --context=$(KUBE_CONTEXT) delete pod --all --ignore-not-found --wait=true --timeout=120s
	-kubectl --context=$(KUBE_CONTEXT) delete pvc --all --ignore-not-found --wait=true --timeout=120s
	-kubectl --context=$(KUBE_CONTEXT) delete configmap openclaw-agent-config --ignore-not-found
	-kubectl --context=$(KUBE_CONTEXT) delete secret openclaw-auth ollama-auth --ignore-not-found
	-kubectl --context=$(KUBE_CONTEXT) delete service ollama clawdevs-ai --ignore-not-found
	-kubectl --context=$(KUBE_CONTEXT) delete networkpolicy allow-all-egress --ignore-not-found
	-kubectl --context=$(KUBE_CONTEXT) delete runtimeclass nvidia --ignore-not-found
	-kubectl --context=$(KUBE_CONTEXT) -n kube-system delete daemonset nvidia-device-plugin-daemonset --ignore-not-found
	@echo "[destroy-all] Destruindo perfil Minikube $(PROFILE)..."
	-minikube delete --profile=$(PROFILE)
ifeq ($(OS),Windows_NT)
	@echo "[destroy-all] Parando WSL para liberar memoria VmmemWSL..."
	-cmd /c "start /b wsl --shutdown"
endif
	@echo "[destroy-all] Removendo volumes Docker do projeto..."
	-docker volume rm clawdevs-ai-openclaw-data-clawdevs-ai-0 openclaw-data ollama-data
	$(if $(DOCKER_VOLUMES_CLAWDEVS),-docker volume rm $(DOCKER_VOLUMES_CLAWDEVS))
	$(if $(DOCKER_VOLUMES_OPENCLAW),-docker volume rm $(DOCKER_VOLUMES_OPENCLAW))
	$(if $(DOCKER_VOLUMES_OLLAMA),-docker volume rm $(DOCKER_VOLUMES_OLLAMA))
	@echo "[destroy-all] Removendo imagens Docker do projeto..."
	$(if $(DOCKER_IMAGES_PROJECT),-docker rmi --force $(DOCKER_IMAGES_PROJECT))
	@echo "[destroy-all] Removendo volumes Docker orfaos..."
	-docker volume prune --force
	@echo "[destroy-all] Concluido."

# ════════════════════════════════════════════════════════════════════════════
# SEÇÃO 3: LOGS E MONITORAMENTO
# ════════════════════════════════════════════════════════════════════════════

# (Logs já definidos nas seções anteriores: minikube-logs, ollama-logs, openclaw-logs, panel-logs-backend, panel-logs-frontend)

# ────────────────────────────────────────────────────────────────────────────
# Templates SDD
# ────────────────────────────────────────────────────────────────────────────

spec-template:
	@echo "Template: k8s/base/openclaw-config/shared/SPEC_TEMPLATE.md"
	@echo "Backlog de specs: /data/openclaw/backlog/specs/"

vibe-playbook:
	@echo "Playbook: k8s/base/openclaw-config/shared/VIBE_CODING_PLAYBOOK.md"

sdd-contract:
	@echo "Contrato SDD: k8s/base/openclaw-config/shared/SDD_OPERATING_MODEL.md"

constitution-template:
	@echo "Constitution: k8s/base/openclaw-config/shared/CONSTITUTION.md"

speckit-flow:
	@echo "Spec Kit adaptado: k8s/base/openclaw-config/shared/SPECKIT_ADAPTATION.md"

sdd-checklist:
	@echo "Checklist SDD: k8s/base/openclaw-config/shared/SDD_CHECKLIST.md"

brief-template:
	@echo "Brief template: k8s/base/openclaw-config/shared/BRIEF_TEMPLATE.md"

clarify-template:
	@echo "Clarify template: k8s/base/openclaw-config/shared/CLARIFY_TEMPLATE.md"

plan-template:
	@echo "Plan template: k8s/base/openclaw-config/shared/PLAN_TEMPLATE.md"

task-template:
	@echo "Task template: k8s/base/openclaw-config/shared/TASK_TEMPLATE.md"

validate-template:
	@echo "Validate template: k8s/base/openclaw-config/shared/VALIDATE_TEMPLATE.md"

sdd-prompts:
	@echo "Prompts operacionais: k8s/base/openclaw-config/shared/SDD_OPERATIONAL_PROMPTS.md"

sdd-example:
	@echo "Exemplo SDD completo: k8s/base/openclaw-config/shared/SDD_FULL_CYCLE_EXAMPLE.md"

sdd-real-initiative:
	@echo "Iniciativa real: k8s/base/openclaw-config/shared/initiatives/internal-sdd-operationalization/"
