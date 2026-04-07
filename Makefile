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

# ------------------------------------------------------------------------------
# Shell multiplataforma (Linux, macOS, Windows)
#
# - Linux / macOS: /bin/bash
# - Windows: ordem de resolucao — variavel BASH, depois Git for Windows em
#   Progra~1/Progra~2 (atalhos 8.3 evitam espacos em "Program Files"), depois
#   bash no PATH. Se falhar: adicione Git\\bin ao PATH ou
#     make BASH="C:/Program Files/Git/bin/bash.exe"
#
# Redirecionamentos usam /dev/null (valido no bash do Git for Windows e MSYS2).
# ------------------------------------------------------------------------------
ifeq ($(OS),Windows_NT)
  WIN_GIT_BASH := $(or \
    $(wildcard C:/Progra~1/Git/bin/bash.exe), \
    $(wildcard C:/Progra~2/Git/bin/bash.exe))
  SHELL := $(or $(BASH),$(WIN_GIT_BASH),bash)
else
  SHELL := /bin/bash
endif

NULL_DEV ?= /dev/null

ENV_FILE ?= .env
-include $(ENV_FILE)

OPENCLAW_VERSION ?= 2026.3.24
IMAGE_TAG ?= local
REMOTE_IMAGE_TAG ?= latest
OLLAMA_GPU_FLAGS ?=
PUSH_IMAGE ?= local

ifeq ($(strip $(PUSH_IMAGE)),remote)
EFFECTIVE_IMAGE_TAG := $(REMOTE_IMAGE_TAG)
PANEL_WORKER_EFFECTIVE_IMAGE_REPO = $(PANEL_BACKEND_IMAGE_REPO)
else
EFFECTIVE_IMAGE_TAG := $(IMAGE_TAG)
PANEL_WORKER_EFFECTIVE_IMAGE_REPO = $(PANEL_WORKER_IMAGE_REPO)
endif

TOKEN_INIT_IMAGE_REPO    ?= clawdevsai/token-init-runtime
POSTGRES_IMAGE_REPO      ?= clawdevsai/postgres-runtime
SEARXNG_IMAGE_REPO       ?= clawdevsai/searxng-runtime
OLLAMA_IMAGE_REPO        ?= clawdevsai/ollama-runtime
REDIS_IMAGE_REPO         ?= clawdevsai/redis-runtime
PANEL_BACKEND_IMAGE_REPO ?= clawdevsai/clawdevs-panel-backend
SEARXNG_PROXY_IMAGE_REPO ?= clawdevsai/searxng-proxy
PANEL_WORKER_IMAGE_REPO  ?= clawdevsai/clawdevs-panel-worker
PANEL_FRONTEND_IMAGE_REPO ?= clawdevsai/clawdevs-panel-frontend
OPENCLAW_IMAGE_REPO      ?= clawdevsai/openclaw-runtime

TOKEN_INIT_IMAGE     := $(TOKEN_INIT_IMAGE_REPO):$(IMAGE_TAG)
POSTGRES_IMAGE       := $(POSTGRES_IMAGE_REPO):$(EFFECTIVE_IMAGE_TAG)
SEARXNG_IMAGE        := $(SEARXNG_IMAGE_REPO):$(EFFECTIVE_IMAGE_TAG)
OLLAMA_IMAGE         := $(OLLAMA_IMAGE_REPO):$(EFFECTIVE_IMAGE_TAG)
REDIS_IMAGE          := $(REDIS_IMAGE_REPO):$(EFFECTIVE_IMAGE_TAG)
PANEL_BACKEND_IMAGE  := $(PANEL_BACKEND_IMAGE_REPO):$(EFFECTIVE_IMAGE_TAG)
SEARXNG_PROXY_IMAGE  := $(SEARXNG_PROXY_IMAGE_REPO):$(EFFECTIVE_IMAGE_TAG)
PANEL_WORKER_IMAGE   := $(PANEL_WORKER_EFFECTIVE_IMAGE_REPO):$(EFFECTIVE_IMAGE_TAG)
PANEL_FRONTEND_IMAGE := $(PANEL_FRONTEND_IMAGE_REPO):$(EFFECTIVE_IMAGE_TAG)
OPENCLAW_IMAGE       := $(OPENCLAW_IMAGE_REPO):$(EFFECTIVE_IMAGE_TAG)

STACK_NETWORK ?= clawdevs
STACK_VOLUMES := openclaw-data ollama-data postgres-data panel-token
STACK_CONTAINERS := \
	clawdevs-token-init \
	clawdevs-postgres \
	clawdevs-searxng \
	clawdevs-ollama \
	clawdevs-redis \
	clawdevs-panel-backend \
	clawdevs-searxng-proxy \
	clawdevs-panel-worker \
	clawdevs-panel-frontend \
	clawdevs-openclaw

AGENT_CONFIG_FLAT_DIR := tmp/agent-config-flat
BOOTSTRAP_SCRIPTS_DIR := docker/base/bootstrap-scripts
SEARXNG_PROXY_CONF := docker/clawdevs-searxng-proxy/default.conf

.PHONY: help
.PHONY: preflight sync-agent-config
.PHONY: build images-build pull
.PHONY: build-with-cache images-build-with-cache
.PHONY: up up-all up-all-with-cache up-gpu down restart status logs
.PHONY: up-postgres up-redis up-ollama up-searxng up-searxng-proxy up-panel-backend up-panel-worker up-panel-frontend up-token-init up-openclaw up-openclaw-with-cache
.PHONY: openclaw-logs backend-logs ollama-logs frontend-logs
.PHONY: logs-follow ps top
.PHONY: env-check panel-url panel-db-migrate panel-logs openclaw-shell openclaw-restart push release clean prune
.PHONY: migrate openclaw-dashboard ollama-list ollama-sign
.PHONY: reset destroy destroy-complete
.PHONY: network-create volumes-create containers-clean
.PHONY: token-init-image-build token-init-image-push
.PHONY: postgres-image-build postgres-image-push
.PHONY: searxng-image-build searxng-image-push
.PHONY: ollama-image-build ollama-image-push
.PHONY: redis-image-build redis-image-push
.PHONY: panel-backend-image-build panel-backend-image-push
.PHONY: searxng-proxy-image-build searxng-proxy-image-push
.PHONY: panel-worker-image-build panel-worker-image-push
.PHONY: panel-frontend-image-build panel-frontend-image-push
.PHONY: openclaw-image-build openclaw-image-push
.PHONY: token-init-image-build-with-cache
.PHONY: postgres-image-build-with-cache
.PHONY: searxng-image-build-with-cache
.PHONY: ollama-image-build-with-cache
.PHONY: redis-image-build-with-cache
.PHONY: panel-backend-image-build-with-cache
.PHONY: searxng-proxy-image-build-with-cache
.PHONY: panel-worker-image-build-with-cache
.PHONY: panel-frontend-image-build-with-cache
.PHONY: openclaw-image-build-with-cache
.PHONY: images-push images-release
.PHONY: spec-template vibe-playbook sdd-contract constitution-template speckit-flow sdd-checklist
.PHONY: gen-secret
.PHONY: cypress cypress-ui

gen-secret:
	@python -c "import secrets; print(secrets.token_hex(32))"

# ─── Cypress E2E ──────────────────────────────────────────────────────────

CYPRESS_FRONTEND_URL ?= http://localhost:3000
CYPRESS_WAIT_TIMEOUT ?= 120

cypress:
	@echo "[cypress] Verificando se a aplicacao esta rodando em $(CYPRESS_FRONTEND_URL)..."
	@if curl -s -o /dev/null -w '' "$(CYPRESS_FRONTEND_URL)" 2>/dev/null; then \
		echo "[cypress] Aplicacao ja esta em execucao."; \
	else \
		echo "[cypress] Aplicacao nao encontrada. Iniciando stack..."; \
		$(MAKE) up-all-with-cache; \
		echo "[cypress] Aguardando aplicacao ficar disponivel..."; \
		timeout=$(CYPRESS_WAIT_TIMEOUT); \
		while [ $$timeout -gt 0 ]; do \
			if curl -s -o /dev/null -w '' "$(CYPRESS_FRONTEND_URL)" 2>/dev/null; then \
				echo "[cypress] Aplicacao pronta."; \
				break; \
			fi; \
			sleep 2; \
			timeout=$$((timeout - 2)); \
		done; \
		if [ $$timeout -le 0 ]; then \
			echo "ERRO: Timeout aguardando a aplicacao em $(CYPRESS_FRONTEND_URL)"; \
			exit 1; \
		fi; \
	fi
	@echo "[cypress] Executando testes E2E (headless)..."
	@cd control-panel/frontend && pnpm exec cypress run
	@echo "[cypress] Testes concluidos."

cypress-ui:
	@echo "[cypress] Verificando se a aplicacao esta rodando em $(CYPRESS_FRONTEND_URL)..."
	@if curl -s -o /dev/null -w '' "$(CYPRESS_FRONTEND_URL)" 2>/dev/null; then \
		echo "[cypress] Aplicacao ja esta em execucao."; \
	else \
		echo "[cypress] Aplicacao nao encontrada. Iniciando stack..."; \
		$(MAKE) up-all-with-cache; \
		echo "[cypress] Aguardando aplicacao ficar disponivel..."; \
		timeout=$(CYPRESS_WAIT_TIMEOUT); \
		while [ $$timeout -gt 0 ]; do \
			if curl -s -o /dev/null -w '' "$(CYPRESS_FRONTEND_URL)" 2>/dev/null; then \
				echo "[cypress] Aplicacao pronta."; \
				break; \
			fi; \
			sleep 2; \
			timeout=$$((timeout - 2)); \
		done; \
		if [ $$timeout -le 0 ]; then \
			echo "ERRO: Timeout aguardando a aplicacao em $(CYPRESS_FRONTEND_URL)"; \
			exit 1; \
		fi; \
	fi
	@echo "[cypress] Abrindo interface interativa..."
	@cd control-panel/frontend && pnpm exec cypress open

.PHONY: sdd-prompts sdd-example sdd-real-initiative

help:
	@echo "════════════════════════════════════════════════════════════════"
	@echo "  ClawDevs AI — Makefile (docker run)"
	@echo "  Linux / macOS / Windows (Git Bash + Docker Desktop)"
	@echo "════════════════════════════════════════════════════════════════"
	@echo ""
	@echo "make up-all        Build local + sobe todos os 10 containers"
	@echo "make up-all-with-cache  Build local (com cache) + sobe todos os 10 containers"
	@echo "PUSH_IMAGE=local   Build local (tag IMAGE_TAG, padrao: local)"
	@echo "PUSH_IMAGE=remote  Pull do Docker Hub (tag REMOTE_IMAGE_TAG, padrao: latest)"
	@echo "Exemplo remoto: PUSH_IMAGE=remote make up-all-with-cache"
	@echo "make up-gpu        Mesmo fluxo do up-all com --gpus all no Ollama"
	@echo "make up-<service>  Sobe container individual (ex.: up-postgres)"
	@echo "make up-openclaw / up-openclaw-with-cache  Rebuild imagem + recria so o OpenClaw (sem cache / com cache)"
	@echo "make openclaw-restart  Reinicia so o container (AGENTS.md em bind mount — sem rebuild)"
	@echo "make down          Remove todos os containers da stack"
	@echo "make status        Lista status dos containers da stack"
	@echo "make logs          Logs agregados dos containers em execucao"
	@echo "make build         Build local das 10 imagens"
	@echo "make build-with-cache   Build local das 10 imagens (com cache)"
	@echo "make migrate       Executa migrations Alembic"
	@echo "make gen-secret     Gera secret key aleatoria (32 bytes hex)"
	@echo "make cypress        Executa testes E2E Cypress (headless, inicia app se necessario)"
	@echo "make cypress-ui     Executa testes E2E Cypress (interface grafica, inicia app se necessario)"

preflight:
	@if [ ! -f "$(ENV_FILE)" ]; then \
		echo "ERRO: $(ENV_FILE) nao encontrado."; \
		echo "Execute: cp .env.example .env"; \
		exit 1; \
	fi
	@docker info >$(NULL_DEV) 2>&1 || { \
		echo "ERRO: Docker daemon indisponivel."; \
		exit 1; \
	}
	@set -eu; \
	for file in \
		docker/clawdevs-token-init/Dockerfile \
		docker/clawdevs-postgres/Dockerfile \
		docker/clawdevs-searxng/Dockerfile \
		docker/clawdevs-ollama/Dockerfile \
		docker/clawdevs-redis/Dockerfile \
		docker/clawdevs-panel-backend/Dockerfile \
		docker/clawdevs-searxng-proxy/Dockerfile \
		docker/clawdevs-panel-worker/Dockerfile \
		docker/clawdevs-panel-frontend/Dockerfile \
		docker/clawdevs-openclaw/Dockerfile \
		docker/clawdevs-openclaw/entrypoint.sh \
		$(SEARXNG_PROXY_CONF) \
		$(BOOTSTRAP_SCRIPTS_DIR)/11-start-gateway.sh \
		scripts/docker/run-openclaw.sh \
		scripts/docker/up-service.sh \
		scripts/docker/generate-panel-token.sh; do \
		if [ ! -f "$$file" ]; then \
			echo "ERRO: arquivo obrigatorio ausente: $$file"; \
			exit 1; \
		fi; \
	done
	@set -eu; \
	for key in OPENCLAW_GATEWAY_TOKEN TELEGRAM_BOT_TOKEN_CEO GIT_TOKEN GIT_ORG \
			   PANEL_DB_PASSWORD PANEL_REDIS_PASSWORD PANEL_SECRET_KEY \
			   PANEL_ADMIN_USERNAME PANEL_ADMIN_PASSWORD; do \
		value="$$(sed -n "s/^$${key}=//p" $(ENV_FILE) | head -n 1 | tr -d '\r' || true)"; \
		if [ -z "$$value" ]; then \
			echo "ERRO: $$key esta vazio em $(ENV_FILE)"; \
			exit 1; \
		fi; \
	done
	@echo "[preflight] ambiente validado."

env-check: preflight

sync-agent-config:
	@bash scripts/docker/sync-agent-config.sh

network-create:
	@docker network inspect $(STACK_NETWORK) >$(NULL_DEV) 2>&1 || docker network create $(STACK_NETWORK) >$(NULL_DEV)

volumes-create:
	@set -eu; \
	for volume in $(STACK_VOLUMES); do \
		docker volume inspect "$$volume" >$(NULL_DEV) 2>&1 || docker volume create "$$volume" >$(NULL_DEV); \
	done

containers-clean:
	@set -eu; \
	for c in $(STACK_CONTAINERS); do \
		docker rm -f "$$c" >$(NULL_DEV) 2>&1 || true; \
	done

build: images-build

build-with-cache: images-build-with-cache

images-build: \
	token-init-image-build \
	postgres-image-build \
	searxng-image-build \
	ollama-image-build \
	redis-image-build \
	panel-backend-image-build \
	searxng-proxy-image-build \
	panel-worker-image-build \
	panel-frontend-image-build \
	openclaw-image-build

images-build-with-cache: \
	token-init-image-build-with-cache \
	postgres-image-build-with-cache \
	searxng-image-build-with-cache \
	ollama-image-build-with-cache \
	redis-image-build-with-cache \
	panel-backend-image-build-with-cache \
	searxng-proxy-image-build-with-cache \
	panel-worker-image-build-with-cache \
	panel-frontend-image-build-with-cache \
	openclaw-image-build-with-cache

up:
	@echo "Use make up-all para subir a stack completa."
	@echo "Para subir um container: make up-postgres | up-redis | up-ollama | up-searxng | up-searxng-proxy | up-panel-backend | up-panel-worker | up-panel-frontend | up-token-init | up-openclaw | up-openclaw-with-cache"
	@exit 1

up-all: preflight build network-create volumes-create containers-clean
	@bash scripts/docker/up-all.sh "$(ENV_FILE)" "$(STACK_NETWORK)" \
		"$(POSTGRES_IMAGE)" "$(REDIS_IMAGE)" "$(OLLAMA_IMAGE)" \
		"$(SEARXNG_IMAGE)" "$(SEARXNG_PROXY_IMAGE)" "$(PANEL_BACKEND_IMAGE)" \
		"$(PANEL_WORKER_IMAGE)" "$(PANEL_FRONTEND_IMAGE)" "$(TOKEN_INIT_IMAGE)" \
		"$(SEARXNG_PROXY_CONF)"
	@bash scripts/docker/run-openclaw.sh "$(ENV_FILE)" "$(STACK_NETWORK)" "$(OPENCLAW_IMAGE)" "$(BOOTSTRAP_SCRIPTS_DIR)"
	@echo ""
	@echo "Stack iniciada."
	@echo "  http://localhost:3000        Painel de Controle"
	@echo "  http://localhost:8000/docs   API Docs"
	@echo "  http://localhost:18789       OpenClaw Gateway"
	@echo "  http://localhost:11434       Ollama API"
	@echo "  http://localhost:18080       SearXNG Proxy"

up-all-with-cache: preflight build-with-cache network-create volumes-create containers-clean
	@bash scripts/docker/up-all.sh "$(ENV_FILE)" "$(STACK_NETWORK)" \
		"$(POSTGRES_IMAGE)" "$(REDIS_IMAGE)" "$(OLLAMA_IMAGE)" \
		"$(SEARXNG_IMAGE)" "$(SEARXNG_PROXY_IMAGE)" "$(PANEL_BACKEND_IMAGE)" \
		"$(PANEL_WORKER_IMAGE)" "$(PANEL_FRONTEND_IMAGE)" "$(TOKEN_INIT_IMAGE)" \
		"$(SEARXNG_PROXY_CONF)"
	@bash scripts/docker/run-openclaw.sh "$(ENV_FILE)" "$(STACK_NETWORK)" "$(OPENCLAW_IMAGE)" "$(BOOTSTRAP_SCRIPTS_DIR)"
	@echo ""
	@echo "Stack iniciada."
	@echo "  http://localhost:3000        Painel de Controle"
	@echo "  http://localhost:8000/docs   API Docs"
	@echo "  http://localhost:18789       OpenClaw Gateway"
	@echo "  http://localhost:11434       Ollama API"
	@echo "  http://localhost:18080       SearXNG Proxy"

up-postgres: preflight network-create volumes-create postgres-image-build
	@ENV_FILE="$(ENV_FILE)" STACK_NETWORK="$(STACK_NETWORK)" POSTGRES_IMAGE="$(POSTGRES_IMAGE)" bash scripts/docker/up-service.sh postgres

up-redis: preflight network-create volumes-create redis-image-build
	@ENV_FILE="$(ENV_FILE)" STACK_NETWORK="$(STACK_NETWORK)" REDIS_IMAGE="$(REDIS_IMAGE)" bash scripts/docker/up-service.sh redis

up-ollama: preflight network-create volumes-create ollama-image-build
	@ENV_FILE="$(ENV_FILE)" STACK_NETWORK="$(STACK_NETWORK)" OLLAMA_IMAGE="$(OLLAMA_IMAGE)" bash scripts/docker/up-service.sh ollama

up-searxng: preflight network-create searxng-image-build
	@ENV_FILE="$(ENV_FILE)" STACK_NETWORK="$(STACK_NETWORK)" SEARXNG_IMAGE="$(SEARXNG_IMAGE)" bash scripts/docker/up-service.sh searxng

up-searxng-proxy: preflight network-create searxng-proxy-image-build
	@ENV_FILE="$(ENV_FILE)" STACK_NETWORK="$(STACK_NETWORK)" SEARXNG_PROXY_IMAGE="$(SEARXNG_PROXY_IMAGE)" SEARXNG_PROXY_CONF="$(SEARXNG_PROXY_CONF)" bash scripts/docker/up-service.sh searxng-proxy

up-panel-backend: preflight network-create volumes-create panel-backend-image-build
	@ENV_FILE="$(ENV_FILE)" STACK_NETWORK="$(STACK_NETWORK)" PANEL_BACKEND_IMAGE="$(PANEL_BACKEND_IMAGE)" bash scripts/docker/up-service.sh panel-backend

up-panel-worker: preflight network-create volumes-create panel-worker-image-build
	@ENV_FILE="$(ENV_FILE)" STACK_NETWORK="$(STACK_NETWORK)" PANEL_WORKER_IMAGE="$(PANEL_WORKER_IMAGE)" bash scripts/docker/up-service.sh panel-worker

up-panel-frontend: preflight network-create panel-frontend-image-build
	@ENV_FILE="$(ENV_FILE)" STACK_NETWORK="$(STACK_NETWORK)" PANEL_FRONTEND_IMAGE="$(PANEL_FRONTEND_IMAGE)" bash scripts/docker/up-service.sh panel-frontend

up-token-init: preflight network-create volumes-create token-init-image-build
	@ENV_FILE="$(ENV_FILE)" STACK_NETWORK="$(STACK_NETWORK)" TOKEN_INIT_IMAGE="$(TOKEN_INIT_IMAGE)" bash scripts/docker/up-service.sh token-init

up-openclaw: preflight network-create volumes-create openclaw-image-build
	@ENV_FILE="$(ENV_FILE)" STACK_NETWORK="$(STACK_NETWORK)" OPENCLAW_IMAGE="$(OPENCLAW_IMAGE)" BOOTSTRAP_SCRIPTS_DIR="$(BOOTSTRAP_SCRIPTS_DIR)" bash scripts/docker/up-service.sh openclaw

# Rebuild da imagem OpenClaw com cache Docker (mais rapido) e recria so o container clawdevs-openclaw.
up-openclaw-with-cache: preflight network-create volumes-create openclaw-image-build-with-cache
	@ENV_FILE="$(ENV_FILE)" STACK_NETWORK="$(STACK_NETWORK)" OPENCLAW_IMAGE="$(OPENCLAW_IMAGE)" BOOTSTRAP_SCRIPTS_DIR="$(BOOTSTRAP_SCRIPTS_DIR)" bash scripts/docker/up-service.sh openclaw

up-gpu:
	@$(MAKE) up-all OLLAMA_GPU_FLAGS="--gpus all"

down: containers-clean

restart:
	@$(MAKE) down
	@$(MAKE) up-all

status:
	@docker ps -a --filter "name=^/clawdevs-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

ps: status

logs:
	@set -euo pipefail; \
	running=0; \
	cleanup() { \
		for pid in $$(jobs -p); do kill $$pid >$(NULL_DEV) 2>&1 || true; done; \
	}; \
	trap cleanup EXIT INT TERM; \
	for c in $(STACK_CONTAINERS); do \
		if [ "$$(docker inspect -f '{{.State.Running}}' "$$c" 2>/dev/null || echo false)" = "true" ]; then \
			running=1; \
			docker logs -f --tail=100 "$$c" 2>&1 | sed "s/^/[$$c] /" & \
		fi; \
	done; \
	if [ "$$running" -eq 0 ]; then \
		echo "Nenhum container da stack esta em execucao."; \
		exit 1; \
	fi; \
	wait

logs-follow: logs

top:
	@docker stats --no-stream $(STACK_CONTAINERS) 2>$(NULL_DEV) || true

openclaw-logs:
	@docker logs clawdevs-openclaw -f --tail=200

backend-logs:
	@set -euo pipefail; \
	cleanup() { \
		for pid in $$(jobs -p); do kill $$pid >$(NULL_DEV) 2>&1 || true; done; \
	}; \
	trap cleanup EXIT INT TERM; \
	docker logs clawdevs-panel-backend -f --tail=100 2>&1 | sed 's/^/[clawdevs-panel-backend] /' & \
	docker logs clawdevs-panel-worker -f --tail=100 2>&1 | sed 's/^/[clawdevs-panel-worker] /' & \
	wait

panel-logs: backend-logs

panel-url:
	@echo "Control Panel Frontend: http://localhost:3000"
	@echo "Control Panel Backend : http://localhost:8000"
	@echo "Control Panel Docs    : http://localhost:8000/docs"

panel-db-migrate: migrate

ollama-logs:
	@docker logs clawdevs-ollama -f --tail=100

frontend-logs:
	@docker logs clawdevs-panel-frontend -f --tail=100

migrate:
	@docker exec clawdevs-panel-backend alembic upgrade head

openclaw-dashboard:
	@docker exec clawdevs-openclaw openclaw dashboard --no-open

openclaw-shell:
	@docker exec -it clawdevs-openclaw /bin/bash

# Reinicia o container OpenClaw sem rebuild (config em docker/base/openclaw-config ja reflete o disco).
openclaw-restart:
	@docker restart clawdevs-openclaw
	@echo "[openclaw-restart] clawdevs-openclaw reiniciado."

ollama-list:
	@docker exec clawdevs-ollama ollama list

ollama-sign:
	@docker exec -it clawdevs-ollama ollama signin

reset:
	@echo "AVISO: isso vai apagar todos os volumes da stack."
	@bash scripts/docker/confirm-yes.sh
	@$(MAKE) down
	@set -eu; \
	for volume in $(STACK_VOLUMES); do \
		docker volume rm "$$volume" >$(NULL_DEV) 2>&1 || true; \
	done
	@echo "[reset] volumes removidos."

destroy:
	@echo "AVISO: isso vai remover containers, volumes, network, build cache e imagens locais da stack."
	@if [ -t 0 ]; then bash scripts/docker/confirm-yes.sh; fi
	@$(MAKE) down
	@set -eu; \
	for volume in $(STACK_VOLUMES); do \
		docker volume rm "$$volume" >$(NULL_DEV) 2>&1 || true; \
	done
	@docker network rm $(STACK_NETWORK) >$(NULL_DEV) 2>&1 || true
	@docker builder prune -af >$(NULL_DEV) 2>&1 || true
	@set -eu; \
	for image in \
		$(TOKEN_INIT_IMAGE) \
		$(POSTGRES_IMAGE) \
		$(SEARXNG_IMAGE) \
		$(OLLAMA_IMAGE) \
		$(REDIS_IMAGE) \
		$(PANEL_BACKEND_IMAGE) \
		$(SEARXNG_PROXY_IMAGE) \
		$(PANEL_WORKER_IMAGE) \
		$(PANEL_FRONTEND_IMAGE) \
		$(OPENCLAW_IMAGE); do \
		docker rmi "$$image" >$(NULL_DEV) 2>&1 || true; \
	done
	@echo "[destroy] stack removida por completo."

destroy-complete:
	@echo "AVISO: isso vai remover TUDO do Docker (containers, volumes, networks, imagens, cache)."
	@if [ -t 0 ]; then bash scripts/docker/confirm-yes.sh; fi
	@docker stop $$(docker ps -aq) >$(NULL_DEV) 2>&1 || true
	@docker rm -f $$(docker ps -aq) >$(NULL_DEV) 2>&1 || true
	@docker rmi -f $$(docker images -aq) >$(NULL_DEV) 2>&1 || true
	@docker volume prune -af >$(NULL_DEV) 2>&1 || true
	@docker network prune -f >$(NULL_DEV) 2>&1 || true
	@docker builder prune -af >$(NULL_DEV) 2>&1 || true
	@docker system prune -af >$(NULL_DEV) 2>&1 || true
	@echo "[destroy-complete] Docker completamente limpo."

token-init-image-build:
	docker build --no-cache -t $(TOKEN_INIT_IMAGE) -f docker/clawdevs-token-init/Dockerfile .

token-init-image-build-with-cache:
	docker build -t $(TOKEN_INIT_IMAGE) -f docker/clawdevs-token-init/Dockerfile .

token-init-image-push:
	docker push $(TOKEN_INIT_IMAGE_REPO):$(REMOTE_IMAGE_TAG)

postgres-image-build:
	@if [ "$(PUSH_IMAGE)" = "remote" ]; then docker pull $(POSTGRES_IMAGE_REPO):$(REMOTE_IMAGE_TAG); else docker build --no-cache -t $(POSTGRES_IMAGE) -f docker/clawdevs-postgres/Dockerfile .; fi

postgres-image-build-with-cache:
	@if [ "$(PUSH_IMAGE)" = "remote" ]; then docker pull $(POSTGRES_IMAGE_REPO):$(REMOTE_IMAGE_TAG); else docker build -t $(POSTGRES_IMAGE) -f docker/clawdevs-postgres/Dockerfile .; fi

postgres-image-push:
	docker push $(POSTGRES_IMAGE_REPO):$(REMOTE_IMAGE_TAG)

searxng-image-build:
	@if [ "$(PUSH_IMAGE)" = "remote" ]; then docker pull $(SEARXNG_IMAGE_REPO):$(REMOTE_IMAGE_TAG); else docker build --no-cache -t $(SEARXNG_IMAGE) -f docker/clawdevs-searxng/Dockerfile .; fi

searxng-image-build-with-cache:
	@if [ "$(PUSH_IMAGE)" = "remote" ]; then docker pull $(SEARXNG_IMAGE_REPO):$(REMOTE_IMAGE_TAG); else docker build -t $(SEARXNG_IMAGE) -f docker/clawdevs-searxng/Dockerfile .; fi

searxng-image-push:
	docker push $(SEARXNG_IMAGE_REPO):$(REMOTE_IMAGE_TAG)

ollama-image-build:
	@if [ "$(PUSH_IMAGE)" = "remote" ]; then docker pull $(OLLAMA_IMAGE_REPO):$(REMOTE_IMAGE_TAG); else docker build --no-cache -t $(OLLAMA_IMAGE) -f docker/clawdevs-ollama/Dockerfile .; fi

ollama-image-build-with-cache:
	@if [ "$(PUSH_IMAGE)" = "remote" ]; then docker pull $(OLLAMA_IMAGE_REPO):$(REMOTE_IMAGE_TAG); else docker build -t $(OLLAMA_IMAGE) -f docker/clawdevs-ollama/Dockerfile .; fi

ollama-image-push:
	docker push $(OLLAMA_IMAGE_REPO):$(REMOTE_IMAGE_TAG)

redis-image-build:
	@if [ "$(PUSH_IMAGE)" = "remote" ]; then docker pull $(REDIS_IMAGE_REPO):$(REMOTE_IMAGE_TAG); else docker build --no-cache -t $(REDIS_IMAGE) -f docker/clawdevs-redis/Dockerfile .; fi

redis-image-build-with-cache:
	@if [ "$(PUSH_IMAGE)" = "remote" ]; then docker pull $(REDIS_IMAGE_REPO):$(REMOTE_IMAGE_TAG); else docker build -t $(REDIS_IMAGE) -f docker/clawdevs-redis/Dockerfile .; fi

redis-image-push:
	docker push $(REDIS_IMAGE_REPO):$(REMOTE_IMAGE_TAG)

panel-backend-image-build:
	@if [ "$(PUSH_IMAGE)" = "remote" ]; then docker pull $(PANEL_BACKEND_IMAGE_REPO):$(REMOTE_IMAGE_TAG); else docker build --no-cache -t $(PANEL_BACKEND_IMAGE) -f docker/clawdevs-panel-backend/Dockerfile control-panel/backend; fi

panel-backend-image-build-with-cache:
	@if [ "$(PUSH_IMAGE)" = "remote" ]; then docker pull $(PANEL_BACKEND_IMAGE_REPO):$(REMOTE_IMAGE_TAG); else docker build -t $(PANEL_BACKEND_IMAGE) -f docker/clawdevs-panel-backend/Dockerfile control-panel/backend; fi

panel-backend-image-push:
	docker push $(PANEL_BACKEND_IMAGE_REPO):$(REMOTE_IMAGE_TAG)

searxng-proxy-image-build:
	@if [ "$(PUSH_IMAGE)" = "remote" ]; then docker pull $(SEARXNG_PROXY_IMAGE_REPO):$(REMOTE_IMAGE_TAG); else docker build --no-cache -t $(SEARXNG_PROXY_IMAGE) -f docker/clawdevs-searxng-proxy/Dockerfile .; fi

searxng-proxy-image-build-with-cache:
	@if [ "$(PUSH_IMAGE)" = "remote" ]; then docker pull $(SEARXNG_PROXY_IMAGE_REPO):$(REMOTE_IMAGE_TAG); else docker build -t $(SEARXNG_PROXY_IMAGE) -f docker/clawdevs-searxng-proxy/Dockerfile .; fi

searxng-proxy-image-push:
	docker push $(SEARXNG_PROXY_IMAGE_REPO):$(REMOTE_IMAGE_TAG)

panel-worker-image-build:
	@if [ "$(PUSH_IMAGE)" = "remote" ]; then docker pull $(PANEL_WORKER_EFFECTIVE_IMAGE_REPO):$(REMOTE_IMAGE_TAG); else docker build --no-cache -t $(PANEL_WORKER_IMAGE) -f docker/clawdevs-panel-worker/Dockerfile control-panel/backend; fi

panel-worker-image-build-with-cache:
	@if [ "$(PUSH_IMAGE)" = "remote" ]; then docker pull $(PANEL_WORKER_EFFECTIVE_IMAGE_REPO):$(REMOTE_IMAGE_TAG); else docker build -t $(PANEL_WORKER_IMAGE) -f docker/clawdevs-panel-worker/Dockerfile control-panel/backend; fi

panel-worker-image-push:
	docker push $(PANEL_WORKER_IMAGE_REPO):$(REMOTE_IMAGE_TAG)

panel-frontend-image-build:
	@if [ "$(PUSH_IMAGE)" = "remote" ]; then docker pull $(PANEL_FRONTEND_IMAGE_REPO):$(REMOTE_IMAGE_TAG); else docker build --no-cache -t $(PANEL_FRONTEND_IMAGE) -f docker/clawdevs-panel-frontend/Dockerfile control-panel/frontend; fi

panel-frontend-image-build-with-cache:
	@if [ "$(PUSH_IMAGE)" = "remote" ]; then docker pull $(PANEL_FRONTEND_IMAGE_REPO):$(REMOTE_IMAGE_TAG); else docker build -t $(PANEL_FRONTEND_IMAGE) -f docker/clawdevs-panel-frontend/Dockerfile control-panel/frontend; fi

panel-frontend-image-push:
	docker push $(PANEL_FRONTEND_IMAGE_REPO):$(REMOTE_IMAGE_TAG)

openclaw-image-build:
	@if [ "$(PUSH_IMAGE)" = "remote" ]; then docker pull $(OPENCLAW_IMAGE_REPO):$(REMOTE_IMAGE_TAG); else docker build --no-cache --build-arg OPENCLAW_VERSION=$(OPENCLAW_VERSION) -t $(OPENCLAW_IMAGE) -f docker/clawdevs-openclaw/Dockerfile .; fi

openclaw-image-build-with-cache:
	@if [ "$(PUSH_IMAGE)" = "remote" ]; then docker pull $(OPENCLAW_IMAGE_REPO):$(REMOTE_IMAGE_TAG); else docker build --build-arg OPENCLAW_VERSION=$(OPENCLAW_VERSION) -t $(OPENCLAW_IMAGE) -f docker/clawdevs-openclaw/Dockerfile .; fi

openclaw-image-push:
	docker push $(OPENCLAW_IMAGE_REPO):$(REMOTE_IMAGE_TAG)

images-push: \
	token-init-image-push \
	postgres-image-push \
	searxng-image-push \
	ollama-image-push \
	redis-image-push \
	panel-backend-image-push \
	searxng-proxy-image-push \
	panel-worker-image-push \
	panel-frontend-image-push \
	openclaw-image-push

images-release: images-build images-push

push: images-push

release: images-release

pull:
	@set -eu; \
	echo "[pull] token-init permanece local (sem pull remoto)"; \
	docker pull $(POSTGRES_IMAGE_REPO):$(REMOTE_IMAGE_TAG); \
	docker pull $(SEARXNG_IMAGE_REPO):$(REMOTE_IMAGE_TAG); \
	docker pull $(OLLAMA_IMAGE_REPO):$(REMOTE_IMAGE_TAG); \
	docker pull $(REDIS_IMAGE_REPO):$(REMOTE_IMAGE_TAG); \
	docker pull $(PANEL_BACKEND_IMAGE_REPO):$(REMOTE_IMAGE_TAG); \
	docker pull $(SEARXNG_PROXY_IMAGE_REPO):$(REMOTE_IMAGE_TAG); \
	docker pull $(PANEL_WORKER_EFFECTIVE_IMAGE_REPO):$(REMOTE_IMAGE_TAG); \
	docker pull $(PANEL_FRONTEND_IMAGE_REPO):$(REMOTE_IMAGE_TAG); \
	docker pull $(OPENCLAW_IMAGE_REPO):$(REMOTE_IMAGE_TAG)

clean: reset

prune:
	docker system prune -af

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
