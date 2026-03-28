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

# ════════════════════════════════════════════════════════════════════════════
# ClawDevs AI — Makefile
# ════════════════════════════════════════════════════════════════════════════

ifeq ($(OS),Windows_NT)
SHELL := C:/Program Files/Git/bin/bash.exe
NULL_DEV ?= NUL
else
NULL_DEV ?= /dev/null
endif

# ────────────────────────────────────────────────────────────────────────────
# Variáveis
# ────────────────────────────────────────────────────────────────────────────

DC_ENV_FILE ?= .env
DC_FILE ?= docker/stack.compose.yaml
DC_CMD = docker compose --env-file $(DC_ENV_FILE) -f $(DC_FILE)
PUSH_IMAGE ?= remote

OPENCLAW_IMAGE_REPO  ?= clawdevsai/openclaw-runtime
OPENCLAW_IMAGE_TAG   ?= latest
OPENCLAW_VERSION     ?= 2026.3.24
OLLAMA_IMAGE_REPO    ?= clawdevsai/ollama-runtime
SEARXNG_IMAGE_REPO   ?= clawdevsai/searxng-runtime
SEARXNG_PROXY_REPO   ?= clawdevsai/searxng-proxy
PANEL_BACKEND_REPO   ?= clawdevsai/clawdevs-panel-backend
PANEL_FRONTEND_REPO  ?= clawdevsai/clawdevs-panel-frontend
POSTGRES_IMAGE_REPO  ?= clawdevsai/postgres-runtime
REDIS_IMAGE_REPO     ?= clawdevsai/redis-runtime
IMAGE_TAG            ?= latest

# ────────────────────────────────────────────────────────────────────────────
# .PHONY
# ────────────────────────────────────────────────────────────────────────────
.PHONY: help
.PHONY: up up-gpu down restart
.PHONY: preflight sync-agent-config
.PHONY: status logs openclaw-logs backend-logs ollama-logs frontend-logs
.PHONY: migrate openclaw-dashboard ollama-list ollama-sign
.PHONY: reset destroy
.PHONY: build pull
.PHONY: openclaw-image-build openclaw-image-push openclaw-image-release
.PHONY: ollama-image-build ollama-image-push
.PHONY: searxng-image-build searxng-image-push
.PHONY: searxng-proxy-image-build searxng-proxy-image-push
.PHONY: panel-backend-image-build panel-backend-image-push
.PHONY: panel-frontend-image-build panel-frontend-image-push
.PHONY: postgres-image-build postgres-image-push
.PHONY: redis-image-build redis-image-push
.PHONY: images-build images-push images-release
.PHONY: spec-template vibe-playbook sdd-contract constitution-template speckit-flow sdd-checklist
.PHONY: brief-template clarify-template plan-template task-template validate-template
.PHONY: sdd-prompts sdd-example sdd-real-initiative

# ════════════════════════════════════════════════════════════════════════════
# SEÇÃO 1: SETUP E CONTROLE DA STACK
# ════════════════════════════════════════════════════════════════════════════

help:
	@echo "════════════════════════════════════════════════════════════════"
	@echo "  ClawDevs AI — Makefile"
	@echo "════════════════════════════════════════════════════════════════"
	@echo ""
	@echo "┌─ SETUP ────────────────────────────────────────────────────────┐"
	@echo "│ make up              docker compose --env-file .env up -d      │"
	@echo "│ make up-gpu          Sobe com suporte a GPU NVIDIA             │"
	@echo "│ make down            Para e remove os containers               │"
	@echo "│ make restart         Reinicia todos os containers              │"
	@echo "│ make preflight       Valida o arquivo .env                     │"
	@echo "└────────────────────────────────────────────────────────────────┘"
	@echo ""
	@echo "┌─ OPERAÇÃO ─────────────────────────────────────────────────────┐"
	@echo "│ make status          Status de todos os containers             │"
	@echo "│ make migrate         Executa migrations Alembic (banco)        │"
	@echo "│ make openclaw-dashboard  Abre o dashboard do OpenClaw         │"
	@echo "│ make ollama-list     Lista modelos Ollama disponíveis          │"
	@echo "│ make ollama-sign     Login na conta Ollama                     │"
	@echo "└────────────────────────────────────────────────────────────────┘"
	@echo ""
	@echo "┌─ LOGS ─────────────────────────────────────────────────────────┐"
	@echo "│ make logs            Todos os serviços (tail -f)               │"
	@echo "│ make openclaw-logs   Logs do OpenClaw (agentes de IA)          │"
	@echo "│ make backend-logs    Logs do backend + worker                  │"
	@echo "│ make ollama-logs     Logs do Ollama                            │"
	@echo "│ make frontend-logs   Logs do frontend                          │"
	@echo "└────────────────────────────────────────────────────────────────┘"
	@echo ""
	@echo "┌─ IMAGENS ──────────────────────────────────────────────────────┐"
	@echo "│ make build           Build local de todas as imagens           │"
	@echo "│ make pull            Pull de todas as imagens do Docker Hub    │"
	@echo "│ make images-release  Build + Push de todas as imagens          │"
	@echo "│ make <svc>-image-build   Build de uma imagem específica        │"
	@echo "│ make <svc>-image-push    Push de uma imagem específica         │"
	@echo "└────────────────────────────────────────────────────────────────┘"
	@echo ""
	@echo "┌─ LIMPEZA ──────────────────────────────────────────────────────┐"
	@echo "│ make reset           Para + apaga volumes (banco, ollama, etc) │"
	@echo "│ make destroy         Para + apaga volumes + imagens locais     │"
	@echo "└────────────────────────────────────────────────────────────────┘"
	@echo ""
	@echo "┌─ TEMPLATES SDD ────────────────────────────────────────────────┐"
	@echo "│ make spec-template   make brief-template   make plan-template  │"
	@echo "│ make sdd-contract    make sdd-prompts      make sdd-example    │"
	@echo "└────────────────────────────────────────────────────────────────┘"

## up: Equivale a: docker compose --env-file .env up -d (apos preflight; sync opcional)
up: preflight
	@if [ -f docker/base/kustomization.yaml ]; then $(MAKE) sync-agent-config; else mkdir -p tmp/agent-config-flat; fi
	@if [ "$(PUSH_IMAGE)" = "local" ]; then \
		echo "[up] PUSH_IMAGE=local -> build local via Dockerfile"; \
		$(DC_CMD) up -d --build; \
	else \
		echo "[up] PUSH_IMAGE=$(PUSH_IMAGE) -> pull Docker Hub images"; \
		$(DC_CMD) pull; \
		$(DC_CMD) up -d; \
	fi
	@echo ""
	@echo "  Stack iniciada! Acesse:"
	@echo "    http://localhost:3000        Painel de Controle"
	@echo "    http://localhost:8000/docs   API Docs"
	@echo "    http://localhost:18789       OpenClaw Gateway"
	@echo "    http://localhost:11434       Ollama API"
	@echo ""
	@echo "  Logs em tempo real : make logs"
	@echo "  Status             : make status"

## up-gpu: Mesmo fluxo que up (GPU no compose quando houver override local)
up-gpu: preflight
	@if [ -f docker/base/kustomization.yaml ]; then $(MAKE) sync-agent-config; else mkdir -p tmp/agent-config-flat; fi
	@if [ "$(PUSH_IMAGE)" = "local" ]; then \
		echo "[up-gpu] PUSH_IMAGE=local -> build local via Dockerfile"; \
		$(DC_CMD) up -d --build; \
	else \
		echo "[up-gpu] PUSH_IMAGE=$(PUSH_IMAGE) -> pull Docker Hub images"; \
		$(DC_CMD) pull; \
		$(DC_CMD) up -d; \
	fi
	@echo "Stack GPU iniciada. Certifique-se de que Docker Desktop > Settings > Resources > GPU esta habilitado."

## down: Para e remove os containers (preserva volumes/dados)
down:
	$(DC_CMD) down

## restart: Reinicia todos os containers
restart:
	$(DC_CMD) restart

## preflight: Valida que o .env existe e tem as variáveis obrigatórias
preflight:
	@if [ ! -f "$(DC_ENV_FILE)" ]; then \
		echo "ERRO: $(DC_ENV_FILE) nao encontrado."; \
		echo "Execute: cp .env.example .env   e preencha os valores."; \
		exit 1; \
	fi
	@if [ ! -f "$(DC_FILE)" ]; then \
		echo "ERRO: $(DC_FILE) nao encontrado."; \
		exit 1; \
	fi
	@if [ "$(PUSH_IMAGE)" != "local" ] && [ "$(PUSH_IMAGE)" != "remote" ]; then \
		echo "ERRO: PUSH_IMAGE invalido: $(PUSH_IMAGE)"; \
		echo "Use PUSH_IMAGE=local ou PUSH_IMAGE=remote"; \
		exit 1; \
	fi
	@set -eu; \
	for key in OPENCLAW_GATEWAY_TOKEN TELEGRAM_BOT_TOKEN_CEO GIT_TOKEN GIT_ORG \
	           PANEL_DB_PASSWORD PANEL_REDIS_PASSWORD PANEL_SECRET_KEY \
	           PANEL_ADMIN_USERNAME PANEL_ADMIN_PASSWORD; do \
		value="$$(sed -n "s/^$${key}=//p" $(DC_ENV_FILE) | head -n 1 | tr -d '\r' || true)"; \
		if [ -z "$$value" ]; then \
			echo "ERRO: $$key esta vazio em $(DC_ENV_FILE)"; \
			exit 1; \
		fi; \
	done
	@echo "[preflight] .env validado."

## sync-agent-config: Gera tmp/agent-config-flat/ a partir do kustomization.yaml
sync-agent-config:
	@bash scripts/docker/sync-agent-config.sh

# ════════════════════════════════════════════════════════════════════════════
# SEÇÃO 2: OPERAÇÃO
# ════════════════════════════════════════════════════════════════════════════

## status: Exibe o status de todos os containers
status:
	$(DC_CMD) ps

## migrate: Executa migrations Alembic no container backend
migrate:
	$(DC_CMD) exec panel-backend alembic upgrade head

## openclaw-dashboard: Abre o dashboard do OpenClaw Gateway
openclaw-dashboard:
	$(DC_CMD) exec openclaw openclaw dashboard --no-open

## ollama-list: Lista os modelos disponíveis no Ollama
ollama-list:
	$(DC_CMD) exec ollama ollama list

## ollama-sign: Login na conta Ollama (para modelos pagos)
ollama-sign:
	$(DC_CMD) exec -it ollama ollama signin

# ════════════════════════════════════════════════════════════════════════════
# SEÇÃO 3: LOGS E MONITORAMENTO
# ════════════════════════════════════════════════════════════════════════════

## logs: Exibe logs de todos os serviços em tempo real
logs:
	$(DC_CMD) logs -f --tail=100

## openclaw-logs: Logs do container openclaw (agentes de IA)
openclaw-logs:
	$(DC_CMD) logs openclaw -f --tail=200

## backend-logs: Logs do panel-backend e worker
backend-logs:
	$(DC_CMD) logs panel-backend panel-worker -f --tail=100

## ollama-logs: Logs do Ollama
ollama-logs:
	$(DC_CMD) logs ollama -f --tail=100

## frontend-logs: Logs do panel-frontend
frontend-logs:
	$(DC_CMD) logs panel-frontend -f --tail=100

# ════════════════════════════════════════════════════════════════════════════
# SEÇÃO 4: LIMPEZA
# ════════════════════════════════════════════════════════════════════════════

## reset: DESTRUTIVO — remove containers e volumes (apaga banco, dados ollama, openclaw)
reset:
	@echo "AVISO: Isso vai apagar todos os volumes (banco, ollama, openclaw)!"
	@read -p "Confirma? [y/N] " confirm && [ "$$confirm" = "y" ]
	$(DC_CMD) down -v
	@echo "[reset] Volumes removidos. Execute 'make up' para recriar."

## destroy: DESTRUTIVO — remove containers, volumes e imagens locais
destroy:
	@echo "AVISO: Isso vai remover containers, volumes E imagens buildadas localmente!"
	@read -p "Confirma? [y/N] " confirm && [ "$$confirm" = "y" ]
	$(DC_CMD) down -v --rmi local
	@echo "[destroy] Stack destruida completamente."

# ════════════════════════════════════════════════════════════════════════════
# SEÇÃO 5: BUILD E PUSH DE IMAGENS
# ════════════════════════════════════════════════════════════════════════════

## build: Build local de todas as imagens via Docker Compose
build:
	@if [ "$(PUSH_IMAGE)" = "local" ]; then \
		echo "[build] PUSH_IMAGE=local -> build local via Dockerfile"; \
		$(DC_CMD) build; \
	else \
		echo "[build] PUSH_IMAGE=$(PUSH_IMAGE) -> pull Docker Hub images"; \
		$(DC_CMD) pull; \
	fi

## pull: Baixa todas as imagens pré-buildadas do Docker Hub
pull:
	$(DC_CMD) pull

openclaw-image-build:
	docker build \
		--build-arg OPENCLAW_VERSION=$(OPENCLAW_VERSION) \
		-t $(OPENCLAW_IMAGE_REPO):$(OPENCLAW_IMAGE_TAG) \
		-f docker/clawdevs-openclaw/Dockerfile .

openclaw-image-push:
	docker push $(OPENCLAW_IMAGE_REPO):$(OPENCLAW_IMAGE_TAG)

openclaw-image-release: openclaw-image-build openclaw-image-push

ollama-image-build:
	docker build -t $(OLLAMA_IMAGE_REPO):$(IMAGE_TAG) -f docker/clawdevs-ollama/Dockerfile .

ollama-image-push:
	docker push $(OLLAMA_IMAGE_REPO):$(IMAGE_TAG)

searxng-image-build:
	docker build -t $(SEARXNG_IMAGE_REPO):$(IMAGE_TAG) -f docker/clawdevs-searxng/Dockerfile .

searxng-image-push:
	docker push $(SEARXNG_IMAGE_REPO):$(IMAGE_TAG)

searxng-proxy-image-build:
	docker build -t $(SEARXNG_PROXY_REPO):$(IMAGE_TAG) -f docker/clawdevs-searxng-proxy/Dockerfile .

searxng-proxy-image-push:
	docker push $(SEARXNG_PROXY_REPO):$(IMAGE_TAG)

panel-backend-image-build:
	docker build -t $(PANEL_BACKEND_REPO):$(IMAGE_TAG) control-panel/backend/

panel-backend-image-push:
	docker push $(PANEL_BACKEND_REPO):$(IMAGE_TAG)

panel-frontend-image-build:
	docker build -t $(PANEL_FRONTEND_REPO):$(IMAGE_TAG) control-panel/frontend/

panel-frontend-image-push:
	docker push $(PANEL_FRONTEND_REPO):$(IMAGE_TAG)

postgres-image-build:
	docker build -t $(POSTGRES_IMAGE_REPO):$(IMAGE_TAG) -f docker/clawdevs-postgres/Dockerfile .

postgres-image-push:
	docker push $(POSTGRES_IMAGE_REPO):$(IMAGE_TAG)

redis-image-build:
	docker build -t $(REDIS_IMAGE_REPO):$(IMAGE_TAG) -f docker/clawdevs-redis/Dockerfile .

redis-image-push:
	docker push $(REDIS_IMAGE_REPO):$(IMAGE_TAG)

images-build: openclaw-image-build ollama-image-build searxng-image-build \
              searxng-proxy-image-build panel-backend-image-build \
              panel-frontend-image-build postgres-image-build redis-image-build

images-push: openclaw-image-push ollama-image-push searxng-image-push \
             searxng-proxy-image-push panel-backend-image-push \
             panel-frontend-image-push postgres-image-push redis-image-push

images-release: images-build images-push

# ════════════════════════════════════════════════════════════════════════════
# SEÇÃO 6: TEMPLATES SDD
# ════════════════════════════════════════════════════════════════════════════

spec-template:
	@echo "Template: docker/base/openclaw-config/shared/SPEC_TEMPLATE.md"

vibe-playbook:
	@echo "Playbook: docker/base/openclaw-config/shared/VIBE_CODING_PLAYBOOK.md"

sdd-contract:
	@echo "Contrato SDD: docker/base/openclaw-config/shared/SDD_OPERATING_MODEL.md"

constitution-template:
	@echo "Constitution: docker/base/openclaw-config/shared/CONSTITUTION.md"

speckit-flow:
	@echo "Spec Kit: docker/base/openclaw-config/shared/SPECKIT_ADAPTATION.md"

sdd-checklist:
	@echo "Checklist SDD: docker/base/openclaw-config/shared/SDD_CHECKLIST.md"

brief-template:
	@echo "Brief template: docker/base/openclaw-config/shared/BRIEF_TEMPLATE.md"

clarify-template:
	@echo "Clarify template: docker/base/openclaw-config/shared/CLARIFY_TEMPLATE.md"

plan-template:
	@echo "Plan template: docker/base/openclaw-config/shared/PLAN_TEMPLATE.md"

task-template:
	@echo "Task template: docker/base/openclaw-config/shared/TASK_TEMPLATE.md"

validate-template:
	@echo "Validate template: docker/base/openclaw-config/shared/VALIDATE_TEMPLATE.md"

sdd-prompts:
	@echo "Prompts operacionais: docker/base/openclaw-config/shared/SDD_OPERATIONAL_PROMPTS.md"

sdd-example:
	@echo "Exemplo SDD completo: docker/base/openclaw-config/shared/SDD_FULL_CYCLE_EXAMPLE.md"

sdd-real-initiative:
	@echo "Iniciativa real: docker/base/openclaw-config/shared/initiatives/internal-sdd-operationalization/"
