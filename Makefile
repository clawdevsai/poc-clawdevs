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

ifeq ($(OS),Windows_NT)
SHELL := C:/Program Files/Git/bin/bash.exe
endif

NULL_DEV ?= /dev/null

ENV_FILE ?= .env
OPENCLAW_VERSION ?= 2026.3.24
IMAGE_TAG ?= local
REMOTE_IMAGE_TAG ?= latest
OLLAMA_GPU_FLAGS ?=

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
POSTGRES_IMAGE       := $(POSTGRES_IMAGE_REPO):$(IMAGE_TAG)
SEARXNG_IMAGE        := $(SEARXNG_IMAGE_REPO):$(IMAGE_TAG)
OLLAMA_IMAGE         := $(OLLAMA_IMAGE_REPO):$(IMAGE_TAG)
REDIS_IMAGE          := $(REDIS_IMAGE_REPO):$(IMAGE_TAG)
PANEL_BACKEND_IMAGE  := $(PANEL_BACKEND_IMAGE_REPO):$(IMAGE_TAG)
SEARXNG_PROXY_IMAGE  := $(SEARXNG_PROXY_IMAGE_REPO):$(IMAGE_TAG)
PANEL_WORKER_IMAGE   := $(PANEL_WORKER_IMAGE_REPO):$(IMAGE_TAG)
PANEL_FRONTEND_IMAGE := $(PANEL_FRONTEND_IMAGE_REPO):$(IMAGE_TAG)
OPENCLAW_IMAGE       := $(OPENCLAW_IMAGE_REPO):$(IMAGE_TAG)

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
.PHONY: up up-gpu down restart status logs
.PHONY: openclaw-logs backend-logs ollama-logs frontend-logs
.PHONY: logs-follow ps top
.PHONY: env-check panel-url panel-db-migrate panel-logs openclaw-shell push release clean prune
.PHONY: migrate openclaw-dashboard ollama-list ollama-sign
.PHONY: reset destroy
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
.PHONY: images-push images-release
.PHONY: spec-template vibe-playbook sdd-contract constitution-template speckit-flow sdd-checklist
.PHONY: brief-template clarify-template plan-template task-template validate-template
.PHONY: sdd-prompts sdd-example sdd-real-initiative

help:
	@echo "════════════════════════════════════════════════════════════════"
	@echo "  ClawDevs AI — Makefile (docker run)"
	@echo "════════════════════════════════════════════════════════════════"
	@echo ""
	@echo "make up            Build local + sobe todos os 10 containers"
	@echo "make up-gpu        Mesmo fluxo do up com --gpus all no Ollama"
	@echo "make down          Remove todos os containers da stack"
	@echo "make status        Lista status dos containers da stack"
	@echo "make logs          Logs agregados dos containers em execucao"
	@echo "make build         Build local das 10 imagens"
	@echo "make migrate       Executa migrations Alembic"

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
	@$(MAKE) sync-agent-config
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

up: preflight build network-create volumes-create containers-clean
	@set -euo pipefail; \
	load_env_file() { \
		local env_file="$$1"; \
		while IFS= read -r raw_line || [ -n "$$raw_line" ]; do \
			line="$${raw_line%$$'\r'}"; \
			case "$$line" in \
				''|\#*) continue ;; \
			esac; \
			key="$${line%%=*}"; \
			value="$${line#*=}"; \
			key="$$(printf '%s' "$$key" | sed 's/^[[:space:]]*//;s/[[:space:]]*$$//')"; \
			key="$${key#export }"; \
			if ! printf '%s' "$$key" | grep -Eq '^[A-Za-z_][A-Za-z0-9_]*$$'; then \
				echo "[up] ERRO: chave invalida no .env: $$key"; \
				return 1; \
			fi; \
			export "$$key=$$value"; \
		done < "$$env_file"; \
	}; \
	load_env_file "$(ENV_FILE)"; \
	wait_for_health() { \
		local name="$${1:-}"; local timeout="$${2:-120}"; local elapsed=0; local status=""; \
		while true; do \
			status="$$(docker inspect -f '{{if .State.Health}}{{.State.Health.Status}}{{else}}{{.State.Status}}{{end}}' "$$name" 2>/dev/null || true)"; \
			if [ "$$status" = "healthy" ] || [ "$$status" = "running" ]; then \
				echo "[up] $$name pronto ($$status)"; \
				return 0; \
			fi; \
			if [ "$$status" = "exited" ] || [ "$$status" = "dead" ] || [ "$$status" = "unhealthy" ]; then \
				echo "[up] ERRO: $$name em estado $$status"; \
				docker logs "$$name" || true; \
				return 1; \
			fi; \
			if [ "$$elapsed" -ge "$$timeout" ]; then \
				echo "[up] ERRO: timeout aguardando $$name"; \
				docker logs "$$name" || true; \
				return 1; \
			fi; \
			sleep 2; \
			elapsed=$$((elapsed + 2)); \
		done; \
	}; \
	wait_for_running() { \
		local name="$${1:-}"; local timeout="$${2:-120}"; local elapsed=0; local status=""; \
		while true; do \
			status="$$(docker inspect -f '{{.State.Status}}' "$$name" 2>/dev/null || true)"; \
			if [ "$$status" = "running" ]; then \
				echo "[up] $$name pronto ($$status)"; \
				return 0; \
			fi; \
			if [ "$$status" = "exited" ] || [ "$$status" = "dead" ]; then \
				echo "[up] ERRO: $$name em estado $$status"; \
				docker logs "$$name" || true; \
				return 1; \
			fi; \
			if [ "$$elapsed" -ge "$$timeout" ]; then \
				echo "[up] ERRO: timeout aguardando $$name"; \
				docker logs "$$name" || true; \
				return 1; \
			fi; \
			sleep 2; \
			elapsed=$$((elapsed + 2)); \
		done; \
	}; \
	wait_for_exit_success() { \
		local name="$${1:-}"; local timeout="$${2:-180}"; local elapsed=0; local status=""; local code=""; \
		while true; do \
			status="$$(docker inspect -f '{{.State.Status}}' "$$name" 2>/dev/null || true)"; \
			if [ "$$status" = "exited" ]; then \
				code="$$(docker inspect -f '{{.State.ExitCode}}' "$$name")"; \
				if [ "$$code" = "0" ]; then \
					echo "[up] $$name concluido com sucesso"; \
					return 0; \
				fi; \
				echo "[up] ERRO: $$name finalizou com exit code $$code"; \
				docker logs "$$name" || true; \
				return 1; \
			fi; \
			if [ "$$status" = "dead" ] || [ -z "$$status" ]; then \
				echo "[up] ERRO: $$name em estado $$status"; \
				docker logs "$$name" || true; \
				return 1; \
			fi; \
			if [ "$$elapsed" -ge "$$timeout" ]; then \
				echo "[up] ERRO: timeout aguardando $$name"; \
				docker logs "$$name" || true; \
				return 1; \
			fi; \
			sleep 2; \
			elapsed=$$((elapsed + 2)); \
		done; \
	}; \
	echo "[up] iniciando clawdevs-postgres"; \
	docker run -d --name clawdevs-postgres --network $(STACK_NETWORK) --network-alias postgres \
		-e POSTGRES_DB=clawdevs_panel \
		-e POSTGRES_USER=panel \
		-e POSTGRES_PASSWORD="$$PANEL_DB_PASSWORD" \
		-v postgres-data:/var/lib/postgresql/data \
		--health-cmd="pg_isready -U panel -d clawdevs_panel" \
		--health-interval=5s --health-timeout=3s --health-retries=10 --health-start-period=10s \
		--restart unless-stopped \
		$(POSTGRES_IMAGE) >$(NULL_DEV); \
	wait_for_health clawdevs-postgres 180; \
	echo "[up] iniciando clawdevs-redis"; \
	docker run -d --name clawdevs-redis --network $(STACK_NETWORK) --network-alias redis \
		-e PANEL_REDIS_PASSWORD="$$PANEL_REDIS_PASSWORD" \
		--health-cmd="sh -c 'redis-cli -a $$PANEL_REDIS_PASSWORD ping | grep PONG'" \
		--health-interval=5s --health-timeout=3s --health-retries=10 --health-start-period=5s \
		--restart unless-stopped \
		$(REDIS_IMAGE) \
		redis-server --requirepass "$$PANEL_REDIS_PASSWORD" >$(NULL_DEV); \
	wait_for_health clawdevs-redis 120; \
	echo "[up] iniciando clawdevs-ollama"; \
	docker run -d --name clawdevs-ollama --network $(STACK_NETWORK) --network-alias ollama \
		$(OLLAMA_GPU_FLAGS) \
		-p 11434:11434 \
		-v ollama-data:/root/.ollama \
		-e OLLAMA_HOST=0.0.0.0:11434 \
		-e OLLAMA_GPU_MEMORY=4096 \
		-e CUDA_MEM_POOL_MAX_SPLIT_SIZE_MB=512 \
		-e OLLAMA_API_KEY="$$OLLAMA_API_KEY" \
		-e OLLAMA_AUTO_PULL_MODELS="$${OLLAMA_AUTO_PULL_MODELS:-true}" \
		-e OLLAMA_BOOT_MODELS="$${OLLAMA_BOOT_MODELS:-nomic-embed-text}" \
		--health-cmd="ollama list" \
		--health-interval=15s --health-timeout=30s --health-retries=40 --health-start-period=180s \
		--restart unless-stopped \
		$(OLLAMA_IMAGE) >$(NULL_DEV); \
	wait_for_health clawdevs-ollama 600; \
	echo "[up] iniciando clawdevs-searxng"; \
	docker run -d --name clawdevs-searxng --network $(STACK_NETWORK) --network-alias searxng \
		-e SEARXNG_SETTINGS_PATH=//etc/searxng/settings.yml \
		-e SEARXNG_SECRET="$$SEARXNG_SECRET" \
		--health-cmd="wget -qO- http://localhost:8080/healthz" \
		--health-interval=10s --health-timeout=3s --health-retries=6 --health-start-period=15s \
		--restart unless-stopped \
		$(SEARXNG_IMAGE) >$(NULL_DEV); \
	wait_for_health clawdevs-searxng 180; \
	echo "[up] iniciando clawdevs-searxng-proxy"; \
	docker run -d --name clawdevs-searxng-proxy --network $(STACK_NETWORK) --network-alias searxng-proxy \
		-p 18080:18080 \
		-v "$$(pwd)/$(SEARXNG_PROXY_CONF):/etc/nginx/conf.d/default.conf:ro" \
		--health-cmd="wget -qO- http://127.0.0.1:18080/healthz" \
		--health-interval=10s --health-timeout=3s --health-retries=6 --health-start-period=10s \
		--restart unless-stopped \
		$(SEARXNG_PROXY_IMAGE) >$(NULL_DEV); \
	wait_for_health clawdevs-searxng-proxy 180; \
	echo "[up] iniciando clawdevs-panel-backend"; \
	docker run -d --name clawdevs-panel-backend --network $(STACK_NETWORK) --network-alias panel-backend \
		-p 8000:8000 \
		-v openclaw-data:/data/openclaw \
		-e PYTHONPATH=/app \
		-e PANEL_DB_PASSWORD="$$PANEL_DB_PASSWORD" \
		-e PANEL_REDIS_PASSWORD="$$PANEL_REDIS_PASSWORD" \
		-e PANEL_DATABASE_URL="postgresql+asyncpg://panel:$$PANEL_DB_PASSWORD@postgres:5432/clawdevs_panel" \
		-e PANEL_REDIS_URL="redis://:$$PANEL_REDIS_PASSWORD@redis:6379/0" \
		-e PANEL_OPENCLAW_GATEWAY_URL=http://openclaw:18789 \
		-e PANEL_SECRET_KEY="$$PANEL_SECRET_KEY" \
		-e PANEL_ADMIN_USERNAME="$$PANEL_ADMIN_USERNAME" \
		-e PANEL_ADMIN_PASSWORD="$$PANEL_ADMIN_PASSWORD" \
		-e GIT_TOKEN="$$GIT_TOKEN" \
		-e GIT_ORG="$$GIT_ORG" \
		--health-cmd="curl -sf http://localhost:8000/healthz" \
		--health-interval=10s --health-timeout=5s --health-retries=10 --health-start-period=20s \
		--restart unless-stopped \
		$(PANEL_BACKEND_IMAGE) \
		sh -c 'alembic upgrade head && exec uvicorn app.main:app --host 0.0.0.0 --port 8000' >$(NULL_DEV); \
	wait_for_health clawdevs-panel-backend 240; \
	echo "[up] iniciando clawdevs-panel-worker"; \
	docker run -d --name clawdevs-panel-worker --network $(STACK_NETWORK) --network-alias panel-worker \
		-v openclaw-data:/data/openclaw:ro \
		-e PYTHONPATH=/app \
		-e PANEL_DB_PASSWORD="$$PANEL_DB_PASSWORD" \
		-e PANEL_REDIS_PASSWORD="$$PANEL_REDIS_PASSWORD" \
		-e PANEL_DATABASE_URL="postgresql+asyncpg://panel:$$PANEL_DB_PASSWORD@postgres:5432/clawdevs_panel" \
		-e PANEL_REDIS_URL="redis://:$$PANEL_REDIS_PASSWORD@redis:6379/0" \
		-e GIT_TOKEN="$$GIT_TOKEN" \
		-e GIT_ORG="$$GIT_ORG" \
		--restart unless-stopped \
		$(PANEL_WORKER_IMAGE) >$(NULL_DEV); \
	wait_for_running clawdevs-panel-worker 60; \
	echo "[up] iniciando clawdevs-panel-frontend"; \
	docker run -d --name clawdevs-panel-frontend --network $(STACK_NETWORK) --network-alias panel-frontend \
		-p 3000:3000 \
		-e BACKEND_URL=http://panel-backend:8000 \
		-e NODE_ENV=production \
		--restart unless-stopped \
		$(PANEL_FRONTEND_IMAGE) >$(NULL_DEV); \
	wait_for_running clawdevs-panel-frontend 60; \
	echo "[up] iniciando clawdevs-token-init"; \
	docker run -d --name clawdevs-token-init --network $(STACK_NETWORK) --network-alias token-init \
		--user 0:0 \
		-e PANEL_ADMIN_USERNAME="$$PANEL_ADMIN_USERNAME" \
		-e PANEL_ADMIN_PASSWORD="$$PANEL_ADMIN_PASSWORD" \
		-v panel-token:/panel-token \
		--restart no \
		$(TOKEN_INIT_IMAGE) >$(NULL_DEV); \
	wait_for_exit_success clawdevs-token-init 180; \
	TELEGRAM_CHAT_ID_EFFECTIVE="$${TELEGRAM_CHAT_ID_CEO:-$${TELEGRAM_CHAT_ID:-}}"; \
	echo "[up] iniciando clawdevs-openclaw"; \
	docker run -d --name clawdevs-openclaw --network $(STACK_NETWORK) --network-alias openclaw \
		-p 18789:18789 \
		--env-file "$(ENV_FILE)" \
		-v openclaw-data:/data/openclaw \
		-v "$$(pwd)/$(AGENT_CONFIG_FLAT_DIR):/bootstrap/agent-config:ro" \
		-v "$$(pwd)/$(BOOTSTRAP_SCRIPTS_DIR):/bootstrap/scripts:ro" \
		-v panel-token:/panel-token:ro \
		-e HOME=/data/openclaw \
		-e OPENCLAW_STATE_DIR=/data/openclaw \
		-e GH_CONFIG_DIR=/data/openclaw/.config/gh \
		-e MEMORY_BASE_PATH=/data/openclaw/memory \
		-e OLLAMA_BASE_URL=http://ollama:11434 \
		-e OPENCLAW_GATEWAY_TOKEN="$$OPENCLAW_GATEWAY_TOKEN" \
		-e TELEGRAM_BOT_TOKEN_CEO="$$TELEGRAM_BOT_TOKEN_CEO" \
		-e TELEGRAM_CHAT_ID="$$TELEGRAM_CHAT_ID_EFFECTIVE" \
		-e GH_TOKEN="$$GIT_TOKEN" \
		-e GIT_TOKEN="$$GIT_TOKEN" \
		-e GIT_ORG="$$GIT_ORG" \
		-e GIT_DEFAULT_REPOSITORY="$${GIT_DEFAULT_REPOSITORY:-}" \
		-e OLLAMA_API_KEY="$$OLLAMA_API_KEY" \
		-e DIRECTORS_NAME="$${DIRECTORS_NAME:-Director}" \
		-e LANGUAGE="$${LANGUAGE:-pt-BR}" \
		-e PROVEDOR_LLM="$${PROVEDOR_LLM:-ollama}" \
		-e OPENROUTER_API_KEY="$${OPENROUTER_API_KEY:-}" \
		-e OPENROUTER_MODEL="$${OPENROUTER_MODEL:-}" \
		-e OPENROUTER_BASE_URL="$${OPENROUTER_BASE_URL:-https://openrouter.ai/api/v1}" \
		-e PANEL_API_URL=http://panel-backend:8000 \
		-e NODE_OPTIONS=--max-old-space-size=1024 \
		-e OPENCLAW_NO_RESPAWN=1 \
		-e OPENCLAW_SANDBOX_MODE="$${OPENCLAW_SANDBOX_MODE:-off}" \
		-e NODE_COMPILE_CACHE=/var/tmp/openclaw-compile-cache \
		-e OPENCLAW_LOG_LEVEL="$${OPENCLAW_LOG_LEVEL:-error}" \
		-e DEBUG_LOG_ENABLED="$${DEBUG_LOG_ENABLED:-false}" \
		-e OPENCLAW_CRON_LIST_TIMEOUT_SECONDS=8 \
		-e OPENCLAW_CRON_LIST_LOCK_WAIT_SECONDS=15 \
		-e OPENCLAW_SECURITY_AUDIT_DEEP_ON_START=true \
		-e OPENCLAW_SECURITY_AUDIT_TIMEOUT_SECONDS=45 \
		-e OPENCLAW_SECURITY_AUDIT_MAX_RETRIES=60 \
		-e OPENCLAW_SECURITY_AUDIT_RETRY_INTERVAL_SECONDS=5 \
		-e OPENCLAW_SECURITY_AUDIT_CRON_INTERVAL_SECONDS=3600 \
		-e AGENT_ERROR_ROUTER_ENABLED=true \
		-e AGENT_ERROR_ROUTER_INTERVAL_SECONDS=30 \
		-e DEV_BACKEND_CRON_ENABLED="$${DEV_BACKEND_CRON_ENABLED:-true}" \
		-e DEV_BACKEND_CRON_NAME=dev_backend_hourly_queue_poll \
		-e DEV_BACKEND_CRON_EXPR="$${DEV_BACKEND_CRON_EXPR:-0 * * * *}" \
		-e DEV_BACKEND_CRON_TZ=America/Sao_Paulo \
		-e DEV_FRONTEND_CRON_ENABLED="$${DEV_FRONTEND_CRON_ENABLED:-true}" \
		-e DEV_FRONTEND_CRON_NAME=dev_frontend_hourly_queue_poll \
		-e DEV_FRONTEND_CRON_EXPR="$${DEV_FRONTEND_CRON_EXPR:-15 * * * *}" \
		-e DEV_FRONTEND_CRON_TZ=America/Sao_Paulo \
		-e DEV_MOBILE_CRON_ENABLED="$${DEV_MOBILE_CRON_ENABLED:-true}" \
		-e DEV_MOBILE_CRON_NAME=dev_mobile_hourly_queue_poll \
		-e DEV_MOBILE_CRON_EXPR="$${DEV_MOBILE_CRON_EXPR:-30 * * * *}" \
		-e DEV_MOBILE_CRON_TZ=America/Sao_Paulo \
		-e QA_CRON_ENABLED="$${QA_CRON_ENABLED:-true}" \
		-e QA_CRON_NAME=qa_engineer_hourly_queue_poll \
		-e QA_CRON_EXPR="$${QA_CRON_EXPR:-45 * * * *}" \
		-e QA_CRON_TZ=America/Sao_Paulo \
		-e DEVOPS_SRE_CRON_ENABLED="$${DEVOPS_SRE_CRON_ENABLED:-true}" \
		-e DEVOPS_SRE_CRON_NAME=devops_sre_queue_poll \
		-e DEVOPS_SRE_CRON_EXPR="$${DEVOPS_SRE_CRON_EXPR:-*/30 * * * *}" \
		-e DEVOPS_SRE_CRON_TZ=America/Sao_Paulo \
		-e SECURITY_ENGINEER_CRON_ENABLED="$${SECURITY_ENGINEER_CRON_ENABLED:-true}" \
		-e SECURITY_ENGINEER_CRON_NAME=security_engineer_scan \
		-e SECURITY_ENGINEER_CRON_EXPR="$${SECURITY_ENGINEER_CRON_EXPR:-0 */6 * * *}" \
		-e SECURITY_ENGINEER_CRON_TZ=America/Sao_Paulo \
		-e UX_DESIGNER_CRON_ENABLED="$${UX_DESIGNER_CRON_ENABLED:-true}" \
		-e UX_DESIGNER_CRON_NAME=ux_designer_queue_poll \
		-e UX_DESIGNER_CRON_EXPR="$${UX_DESIGNER_CRON_EXPR:-0 */4 * * *}" \
		-e UX_DESIGNER_CRON_TZ=America/Sao_Paulo \
		-e DBA_DATA_ENGINEER_CRON_ENABLED="$${DBA_DATA_ENGINEER_CRON_ENABLED:-true}" \
		-e DBA_DATA_ENGINEER_CRON_NAME=dba_data_engineer_queue_poll \
		-e DBA_DATA_ENGINEER_CRON_EXPR="$${DBA_DATA_ENGINEER_CRON_EXPR:-30 */4 * * *}" \
		-e DBA_DATA_ENGINEER_CRON_TZ=America/Sao_Paulo \
		-e MEMORY_CURATOR_CRON_ENABLED="$${MEMORY_CURATOR_CRON_ENABLED:-true}" \
		-e MEMORY_CURATOR_CRON_NAME=memory_curator_promote \
		-e MEMORY_CURATOR_CRON_EXPR="$${MEMORY_CURATOR_CRON_EXPR:-0 2 * * *}" \
		-e MEMORY_CURATOR_CRON_TZ=America/Sao_Paulo \
		-e OPENCLAW_CONTROL_UI_ALLOWED_ORIGINS_JSON='["http://127.0.0.1:18789","http://localhost:18789","http://openclaw:18789"]' \
		--health-cmd="curl -sf http://localhost:18789/healthz" \
		--health-interval=10s --health-timeout=5s --health-retries=30 --health-start-period=120s \
		--restart unless-stopped \
		$(OPENCLAW_IMAGE) >$(NULL_DEV); \
	wait_for_health clawdevs-openclaw 360; \
	echo ""; \
	echo "Stack iniciada."; \
	echo "  http://localhost:3000        Painel de Controle"; \
	echo "  http://localhost:8000/docs   API Docs"; \
	echo "  http://localhost:18789       OpenClaw Gateway"; \
	echo "  http://localhost:11434       Ollama API"; \
	echo "  http://localhost:18080       SearXNG Proxy"

up-gpu:
	@$(MAKE) up OLLAMA_GPU_FLAGS="--gpus all"

down: containers-clean

restart:
	@$(MAKE) down
	@$(MAKE) up

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

ollama-list:
	@docker exec clawdevs-ollama ollama list

ollama-sign:
	@docker exec -it clawdevs-ollama ollama signin

reset:
	@echo "AVISO: isso vai apagar todos os volumes da stack."
	@read -p "Confirma? [y/N] " confirm && [ "$$confirm" = "y" ]
	@$(MAKE) down
	@set -eu; \
	for volume in $(STACK_VOLUMES); do \
		docker volume rm "$$volume" >$(NULL_DEV) 2>&1 || true; \
	done
	@echo "[reset] volumes removidos."

destroy:
	@echo "AVISO: isso vai remover containers, volumes e imagens locais da stack."
	@read -p "Confirma? [y/N] " confirm && [ "$$confirm" = "y" ]
	@$(MAKE) reset
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

token-init-image-build:
	docker build -t $(TOKEN_INIT_IMAGE) -f docker/clawdevs-token-init/Dockerfile .

token-init-image-push:
	docker push $(TOKEN_INIT_IMAGE_REPO):$(REMOTE_IMAGE_TAG)

postgres-image-build:
	docker build -t $(POSTGRES_IMAGE) -f docker/clawdevs-postgres/Dockerfile .

postgres-image-push:
	docker push $(POSTGRES_IMAGE_REPO):$(REMOTE_IMAGE_TAG)

searxng-image-build:
	docker build -t $(SEARXNG_IMAGE) -f docker/clawdevs-searxng/Dockerfile .

searxng-image-push:
	docker push $(SEARXNG_IMAGE_REPO):$(REMOTE_IMAGE_TAG)

ollama-image-build:
	docker build -t $(OLLAMA_IMAGE) -f docker/clawdevs-ollama/Dockerfile .

ollama-image-push:
	docker push $(OLLAMA_IMAGE_REPO):$(REMOTE_IMAGE_TAG)

redis-image-build:
	docker build -t $(REDIS_IMAGE) -f docker/clawdevs-redis/Dockerfile .

redis-image-push:
	docker push $(REDIS_IMAGE_REPO):$(REMOTE_IMAGE_TAG)

panel-backend-image-build:
	docker build -t $(PANEL_BACKEND_IMAGE) -f docker/clawdevs-panel-backend/Dockerfile control-panel/backend

panel-backend-image-push:
	docker push $(PANEL_BACKEND_IMAGE_REPO):$(REMOTE_IMAGE_TAG)

searxng-proxy-image-build:
	docker build -t $(SEARXNG_PROXY_IMAGE) -f docker/clawdevs-searxng-proxy/Dockerfile .

searxng-proxy-image-push:
	docker push $(SEARXNG_PROXY_IMAGE_REPO):$(REMOTE_IMAGE_TAG)

panel-worker-image-build:
	docker build -t $(PANEL_WORKER_IMAGE) -f docker/clawdevs-panel-worker/Dockerfile control-panel/backend

panel-worker-image-push:
	docker push $(PANEL_WORKER_IMAGE_REPO):$(REMOTE_IMAGE_TAG)

panel-frontend-image-build:
	docker build -t $(PANEL_FRONTEND_IMAGE) -f docker/clawdevs-panel-frontend/Dockerfile control-panel/frontend

panel-frontend-image-push:
	docker push $(PANEL_FRONTEND_IMAGE_REPO):$(REMOTE_IMAGE_TAG)

openclaw-image-build:
	docker build --build-arg OPENCLAW_VERSION=$(OPENCLAW_VERSION) -t $(OPENCLAW_IMAGE) -f docker/clawdevs-openclaw/Dockerfile .

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
	docker pull $(TOKEN_INIT_IMAGE_REPO):$(REMOTE_IMAGE_TAG); \
	docker pull $(POSTGRES_IMAGE_REPO):$(REMOTE_IMAGE_TAG); \
	docker pull $(SEARXNG_IMAGE_REPO):$(REMOTE_IMAGE_TAG); \
	docker pull $(OLLAMA_IMAGE_REPO):$(REMOTE_IMAGE_TAG); \
	docker pull $(REDIS_IMAGE_REPO):$(REMOTE_IMAGE_TAG); \
	docker pull $(PANEL_BACKEND_IMAGE_REPO):$(REMOTE_IMAGE_TAG); \
	docker pull $(SEARXNG_PROXY_IMAGE_REPO):$(REMOTE_IMAGE_TAG); \
	docker pull $(PANEL_WORKER_IMAGE_REPO):$(REMOTE_IMAGE_TAG); \
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
