ifeq ($(OS),Windows_NT)
SHELL := C:/Program Files/Git/bin/bash.exe
endif

PROFILE ?= clawdevs-ai
KUBE_CONTEXT ?= clawdevs-ai
CPUS ?= 2
MEMORY ?= 7168
K8S_VERSION ?= v1.34.1
GPU ?= 1
PF_SERVICE ?= service/clawdevs-ai
PF_PORTS ?= 18789:18789
KUSTOMIZE_DIR ?= k8s
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
PUSH_IMAGE ?=
PUSH_IMAGE_ENV_RAW := $(shell [ -f k8s/.env ] && sed -n 's/^PUSH_IMAGE=//p' k8s/.env | head -n 1 | tr -d '\r' || true)
PUSH_IMAGE_MODE_RAW := $(if $(strip $(PUSH_IMAGE)),$(strip $(PUSH_IMAGE)),$(strip $(PUSH_IMAGE_ENV_RAW)))
PUSH_IMAGE_MODE := $(if $(strip $(PUSH_IMAGE_MODE_RAW)),$(strip $(PUSH_IMAGE_MODE_RAW)),remote)


.PHONY: help preflight manifests-validate minikube-up minikube-down minikube-status minikube-logs minikube-delete minikube-addons clawdevs-up clawdevs-down clawdevs-rebuild dashboard dashboard-url openclaw-apply openclaw-apply-gpu openclaw-restart openclaw-logs ollama-apply ollama-volume-apply ollama-logs stack-apply stack-status port-forward-start port-forward-stop port-forward-status net-allow-egress net-test-openclaw reset-all destroy-all storage-enable-expansion gpu-doctor docker-k8s-check docker-k8s-context gpu-plugin-apply gpu-node-check gpu-migrate-apply spec-template vibe-playbook sdd-contract constitution-template speckit-flow sdd-checklist brief-template clarify-template plan-template task-template validate-template sdd-prompts sdd-example sdd-real-initiative openclaw-image-build openclaw-image-push openclaw-image-release image-mode-prepare images-build-local

help:
	@echo "Targets disponiveis:"
	@echo ""
	@echo "Bootstrap / subida:"
	@echo "  make clawdevs-up            - sobe stack completo sem deletar recursos existentes"
	@echo "  make minikube-up            - sobe Minikube no Docker Desktop com GPU"
	@echo "  make minikube-context       - ajusta kubeconfig e seta contexto clawdevs-ai"
	@echo "  make minikube-addons        - habilita addons do Minikube"
	@echo "  make storage-enable-expansion - habilita expansao de volume no storageclass standard"
	@echo "  make preflight              - valida k8s/.env antes do deploy"
	@echo "  make manifests-validate     - valida renderizacao do kustomize"
	@echo ""
	@echo "Deploy / operacao:"
	@echo "  make stack-apply            - aplica ollama + openclaw + control-panel"
	@echo "  make panel-url              - URLs do control panel (NodePort + nota Windows)"
	@echo "  make panel-forward          - UI em http://localhost:3000 (driver docker no Windows)"
	@echo "  make stack-status           - status de pods e services do stack"
	@echo "  make ollama-volume-apply    - cria PVC ollama-data"
	@echo "  make ollama-apply           - aplica k8s/base/ollama-pod.yaml (Pod + Service)"
	@echo "  make openclaw-apply         - aplica k8s sem apagar deployment/sessoes"
	@echo "  make openclaw-restart       - reinicia o statefulset clawdevs-ai preservando PVC e sessoes"
	@echo "  make net-allow-egress       - aplica policy liberando egress"
	@echo "  make net-test-openclaw      - testa internet no pod openclaw"
	@echo "  make port-forward-start PF_SERVICE=service/openclaw PF_PORTS=18789:18789 PF_PID=.openclaw-forward.pid"
	@echo "  make port-forward-stop  PF_PID=.openclaw-forward.pid"
	@echo "  make port-forward-status PF_PORTS=18789:18789 PF_PID=.openclaw-forward.pid"
	@echo "  make dashboard              - abre dashboard do Minikube"
	@echo "  make dashboard-url          - mostra URL do dashboard"
	@echo ""
	@echo "Build de imagens:"
	@echo "  make openclaw-image-build OPENCLAW_IMAGE_TAG=latest OPENCLAW_VERSION=2026.3.22"
	@echo "  make openclaw-image-push OPENCLAW_IMAGE_TAG=latest"
	@echo "  make openclaw-image-release OPENCLAW_IMAGE_TAG=latest OPENCLAW_VERSION=2026.3.22"
	@echo ""
	@echo "Reset / destrutivo:"
	@echo "  make reset-all              - apaga pods e volumes do stack e recria tudo do zero"
	@echo "  make clawdevs-down          - destroi tudo (pods, volumes, imagens e perfil Minikube)"
	@echo "  make destroy-all            - limpeza destrutiva completa do ambiente"
	@echo "  make minikube-down          - para Minikube e remove o perfil"
	@echo ""
	@echo "Observabilidade (logs no final):"
	@echo "  make minikube-status"
	@echo "  make minikube-delete"
	@echo "  make minikube-logs"
	@echo "  make ollama-logs"
	@echo "  make openclaw-logs"
	@echo "  make spec-template  - mostra o template de SPEC e o backlog de specs"
	@echo "  make vibe-playbook   - mostra o playbook de vibe coding"
	@echo "  make sdd-contract    - mostra o contrato SDD do repositorio"
	@echo "  make constitution-template - mostra a constitution do repositorio"
	@echo "  make speckit-flow    - mostra o fluxo adaptado do Spec Kit"
	@echo "  make sdd-checklist   - mostra o checklist SDD"
	@echo "  make brief-template  - mostra o template de BRIEF"
	@echo "  make clarify-template - mostra o template de CLARIFY"
	@echo "  make plan-template   - mostra o template de PLAN"
	@echo "  make task-template   - mostra o template de TASK"
	@echo "  make validate-template - mostra o template de VALIDATE"
	@echo "  make sdd-prompts     - mostra o pack de prompts operacionais"
	@echo "  make sdd-example     - mostra o ciclo completo de exemplo"
	@echo "  make sdd-real-initiative - mostra a iniciativa real pronta para uso"
	@echo ""
	@echo "Fluxo GPU real (Docker Desktop Kubernetes):"
	@echo "  make gpu-doctor          - valida host NVIDIA + Docker Desktop + kube context"
	@echo "  make docker-k8s-check    - valida acesso ao contexto docker-desktop"
	@echo "  make gpu-plugin-apply    - aplica RuntimeClass + NVIDIA device plugin"
	@echo "  make gpu-node-check      - valida nvidia.com/gpu no node"
	@echo "  make gpu-migrate-apply   - aplica stack no contexto docker-desktop"

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

ifeq ($(OS),Windows_NT)
NULL_DEV ?= NUL
else
NULL_DEV ?= /dev/null
endif

manifests-validate:
	kubectl kustomize $(KUSTOMIZE_DIR)

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

clawdevs-up:
	@set -e; \
	steps="preflight minikube-up minikube-context minikube-addons storage-enable-expansion ollama-volume-apply stack-apply"; \
	total=7; \
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
	echo "ℹ para logs no final: make openclaw-logs"

clawdevs-down:
	@echo ""; echo "════════════════════════════════════════════"
	@echo " [clawdevs-down] Destruindo ambiente completo..."
	@echo "════════════════════════════════════════════"
	$(MAKE) destroy-all

minikube-status:
	minikube status --profile=$(PROFILE)

minikube-logs:
	minikube logs --profile=$(PROFILE)

dashboard:
	minikube dashboard -p $(PROFILE)

dashboard-url:
	minikube dashboard -p $(PROFILE) --url

ollama-apply: preflight image-mode-prepare ollama-volume-apply
	kubectl --context=$(KUBE_CONTEXT) apply -f k8s/base/ollama-pod.yaml --server-side --force-conflicts

ollama-volume-apply:
	kubectl --context=$(KUBE_CONTEXT) apply -f k8s/base/ollama-pvc.yaml --server-side --force-conflicts

ollama-logs:
	kubectl --context=$(KUBE_CONTEXT) logs -f pod/ollama

ollama-sign:
	kubectl --context=$(KUBE_CONTEXT) exec -it pod/ollama -- ollama signin

ollama-list:
	kubectl --context=$(KUBE_CONTEXT) exec -it pod/ollama -- ollama list

net-allow-egress:
	kubectl --context=$(KUBE_CONTEXT) apply -f k8s/base/networkpolicy-allow-egress.yaml

net-test-openclaw:
	kubectl --context=$(KUBE_CONTEXT) exec deployment/openclaw -- bash -lc "apt-get update >/dev/null 2>&1 || true; apt-get install -y --no-install-recommends curl ca-certificates dnsutils >/dev/null 2>&1 || true; echo 'DNS:'; nslookup google.com | head -n 5; echo 'HTTPS:'; curl -I -m 10 https://google.com | head -n 1"

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

DOCKER_VOLUMES_CLAWDEVS := $(shell docker volume ls -q --filter=name=clawdevs 2>$(NULL_DEV))
DOCKER_VOLUMES_OPENCLAW := $(shell docker volume ls -q --filter=name=openclaw 2>$(NULL_DEV))
DOCKER_VOLUMES_OLLAMA   := $(shell docker volume ls -q --filter=name=ollama 2>$(NULL_DEV))
DOCKER_IMAGES_PROJECT   := $(shell docker images --filter=reference=*clawdevs* --filter=reference=*openclaw* --filter=reference=*ollama* -q 2>$(NULL_DEV))

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

storage-enable-expansion:
	kubectl --context=$(KUBE_CONTEXT) patch storageclass standard -p "{\"allowVolumeExpansion\":true}"

clawdevs-rebuild: 
	$(MAKE) minikube-up
	$(MAKE) minikube-context
	$(MAKE) minikube-addons
	$(MAKE) storage-enable-expansion
	$(MAKE) stack-apply

stack-apply: ollama-apply openclaw-apply panel-apply

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

stack-status:
	kubectl --context=$(KUBE_CONTEXT) get pods -l app=ollama
	kubectl --context=$(KUBE_CONTEXT) get pods -l app=clawdevs-ai
	kubectl --context=$(KUBE_CONTEXT) get svc ollama clawdevs-ai

port-forward-start:
	kubectl --context=$(KUBE_CONTEXT) port-forward $(PF_SERVICE) $(PF_PORTS)

port-forward-stop:
	@echo "Sem PID/daemon. Use Ctrl+C na sessao onde o port-forward esta rodando."

port-forward-status:
	@echo "Sem PID/daemon. Rode o port-forward na sessao atual para acompanhar o status."

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

openclaw-image-build:
	docker build \
		--build-arg OPENCLAW_VERSION=$(OPENCLAW_VERSION) \
		-t $(OPENCLAW_IMAGE_REPO):$(OPENCLAW_IMAGE_TAG) \
		-f docker/openclaw-runtime/Dockerfile .

openclaw-image-push:
	docker push $(OPENCLAW_IMAGE_REPO):$(OPENCLAW_IMAGE_TAG)

openclaw-image-release: openclaw-image-build openclaw-image-push

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

# ─────────────────────────────────────────────────────────────
# Control Panel
# ─────────────────────────────────────────────────────────────

.PHONY: panel-build panel-apply panel-status panel-logs-backend panel-logs-frontend panel-db-migrate panel-restart panel-destroy panel-url panel-forward
.PHONY: images-build images-push images-release ollama-image-build ollama-image-push searxng-image-build searxng-image-push searxng-proxy-image-build searxng-proxy-image-push panel-backend-image-build panel-backend-image-push panel-frontend-image-build panel-frontend-image-push postgres-image-build postgres-image-push redis-image-build redis-image-push

images-build: openclaw-image-build ollama-image-build searxng-image-build searxng-proxy-image-build panel-backend-image-build panel-frontend-image-build postgres-image-build redis-image-build

images-push: openclaw-image-push ollama-image-push searxng-image-push searxng-proxy-image-push panel-backend-image-push panel-frontend-image-push postgres-image-push redis-image-push

images-release: images-build images-push

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

panel-build: ## Build control panel Docker images in minikube context
	minikube image build -t $(PANEL_BACKEND_IMAGE_REPO):$(STACK_IMAGE_TAG) control-panel/backend/
	minikube image build -t $(PANEL_FRONTEND_IMAGE_REPO):$(STACK_IMAGE_TAG) control-panel/frontend/

panel-apply: image-mode-prepare ## Deploy control panel to cluster
	kubectl apply -k k8s/base/control-panel/

panel-status: ## Show control panel pod status
	kubectl get pods -l app.kubernetes.io/part-of=clawdevs-panel 2>/dev/null || \
	kubectl get pods | grep clawdevs-panel

panel-logs-backend: ## Stream backend logs
	kubectl logs -l app=clawdevs-panel-backend -f --tail=100

panel-logs-frontend: ## Stream frontend logs
	kubectl logs -l app=clawdevs-panel-frontend -f --tail=100

panel-db-migrate: ## Run Alembic migrations
	kubectl exec -it $$(kubectl get pod -l app=clawdevs-panel-backend -o jsonpath='{.items[0].metadata.name}') \
	-- alembic upgrade head

panel-restart: ## Restart control panel pods
	kubectl rollout restart deployment/clawdevs-panel-backend deployment/clawdevs-panel-frontend deployment/clawdevs-panel-worker

panel-destroy: ## Remove all control panel resources
	kubectl delete -k k8s/base/control-panel/ || true

panel-url: ## Show access URLs for the control panel
	@echo "┌────────────────────────────────────────────────────────────┐"
	@echo "│     ClawDevs AI Control Panel URLs                         │"
	@echo "├────────────────────────────────────────────────────────────┤"
	@echo "│ NodePort (funciona de outro host na mesma rede que o VM):  │"
	@echo "│   Frontend: http://$$(minikube ip):31880                    │"
	@echo "│   Backend:  http://$$(minikube ip):31881                    │"
	@echo "│   API Docs: http://$$(minikube ip):31881/docs               │"
	@echo "├────────────────────────────────────────────────────────────┤"
	@echo "│ Windows + Minikube driver docker: o IP acima costuma NAO   │"
	@echo "│ abrir no navegador. Use uma destas opcoes:                 │"
	@echo "│   make panel-forward  -> http://localhost:3000             │"
	@echo "│   minikube service clawdevs-panel-frontend --url           │"
	@echo "│     (deixe o terminal aberto; abra a URL http://127.0.0.1)  │"
	@echo "└────────────────────────────────────────────────────────────┘"

panel-forward: ## Port-forward UI to http://localhost:3000 (Ctrl+C to stop)
	kubectl --context=$(KUBE_CONTEXT) port-forward svc/clawdevs-panel-frontend 3000:3000
