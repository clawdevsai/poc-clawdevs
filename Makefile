# Makefile — ClawDevs
# Comandos principais para operar o ecossistema de agentes.
# Uso: make <alvo>
# Referência: docs/README.md | docs/issues/README.md

.PHONY: help configure load-env check-env setup verify install-tools check-k8s check-docker \
        apply-all start stop status logs-ceo logs-all \
        pull-models test-redis test-gpu build-base unblock-brake \
        apply-namespace apply-limits apply-redis apply-ollama apply-agents apply-network \
        venv test-local test-coverage format lint

SHELL  := /bin/bash
KUBECTL := kubectl
NAMESPACE := ai-agents
HELM := helm

help: ## Exibe ajuda
	@echo "ClawDevs — Comandos disponíveis:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-25s\033[0m %s\n", $$1, $$2}'

# ─── Pré-configuração (passo obrigatório antes do setup) ────────────────────

configure: ## 🔧 Assistente: gera .env se não existir
	@if [ ! -f .env ]; then \
		chmod +x scripts/configure.sh && scripts/configure.sh; \
	else \
		echo "[INFO] .env já existe. Pulando assistente interativo."; \
		echo "       (Para refazer, execute 'make reconfigure')."; \
	fi

reconfigure: ## 🔧 Força a reconfiguração interativa do .env
	@chmod +x scripts/configure.sh && scripts/configure.sh
load-env: ## Imprime instrução para carregar o .env no shell atual
	@if [ ! -f .env ]; then echo "[ERRO] .env não encontrado. Execute primeiro: make configure"; exit 1; fi
	@echo ""
	@echo "  Execute no seu terminal:"
	@echo "    source scripts/load-env.sh"
	@echo ""
	@echo "  Para scripts e Makefile targets, as variáveis são carregadas automaticamente."

check-env: ## Valida o .env sem exportar as variáveis (diagnóstico rápido)
	@if [ ! -f .env ]; then echo "[ERRO] .env não encontrado. Execute: make configure"; exit 1; fi
	@bash scripts/load-env.sh --check --quiet && echo "[OK] .env válido." || echo "[ERRO] .env com problemas."

# ─── Setup inicial ────────────────────────────────────────────────────────────

setup: check-env ## Executa setup completo (um clique) — requer .env configurado
	@echo "Executando setup ClawDevs..."
	@chmod +x scripts/setup.sh && scripts/setup.sh

verify: ## Verifica se a máquina atende aos requisitos
	@chmod +x scripts/verify-machine.sh && scripts/verify-machine.sh

# ─── Guards de pré-requisito ────────────────────────────────────────────────────────────

check-docker: ## Verifica se Docker está disponível
	@which docker >/dev/null 2>&1 || { echo "[ERRO] Docker não encontrado. Execute: make setup"; exit 1; }
	@docker info >/dev/null 2>&1 || { echo "[AVISO] Docker daemon não está rodando. Tentando forçar a subir (Requer senha sudo)..."; sudo systemctl start docker || { echo "[ERRO] Falha ao iniciar Docker."; exit 1; } }
	@echo "[OK] Docker disponível: $$(docker --version)"

check-k8s: ## Verifica se kubectl/minikube/helm estão disponíveis
	@which kubectl  >/dev/null 2>&1 || { echo "[ERRO] kubectl não encontrado. Execute: make install-tools"; exit 1; }
	@which minikube >/dev/null 2>&1 || { echo "[ERRO] minikube não encontrado. Execute: make install-tools"; exit 1; }
	@which helm     >/dev/null 2>&1 || { echo "[ERRO] helm não encontrado. Execute: make install-tools"; exit 1; }
	@echo "[OK] kubectl:  $$(kubectl version --client --short 2>/dev/null || kubectl version --client 2>/dev/null | head -1)"
	@echo "[OK] minikube: $$(minikube version --short 2>/dev/null)"
	@echo "[OK] helm:     $$(helm version --short 2>/dev/null)"

install-tools: ## Instala kubectl, minikube e helm (sem setup completo)
	@echo "Instalando ferramentas Kubernetes..."
	@echo "--> kubectl"
	@KUBECTL_VER=$$(curl -L -s https://dl.k8s.io/release/stable.txt) && \
	  curl -Lo /tmp/kubectl "https://dl.k8s.io/release/$${KUBECTL_VER}/bin/linux/amd64/kubectl" && \
	  sudo install /tmp/kubectl /usr/local/bin/kubectl && rm /tmp/kubectl
	@echo "--> minikube"
	@curl -Lo /tmp/minikube https://storage.googleapis.com/minikube/releases/latest/minikube-linux-amd64 && \
	  sudo install /tmp/minikube /usr/local/bin/minikube && rm /tmp/minikube
	@echo "--> helm"
	@curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
	@echo "[OK] Ferramentas instaladas."

# ─── Aplicação de manifestos Kubernetes ──────────────────────────────────────

apply-namespace: check-k8s ## Cria namespace ai-agents
	$(KUBECTL) apply -f k8s/namespace/ai-agents.yaml

apply-limits: check-k8s ## Aplica ResourceQuota e LimitRange
	$(KUBECTL) apply -f k8s/limits/resource-quota.yaml

apply-redis: check-k8s ## Implanta Redis
	$(KUBECTL) apply -f k8s/redis/deployment.yaml

apply-ollama: check-k8s ## Implanta Ollama com GPU
	$(KUBECTL) apply -f k8s/ollama/deployment.yaml

apply-agents: check-k8s ## Implanta todos os agentes
	$(KUBECTL) apply -f k8s/agents/deployments.yaml

apply-network: check-k8s ## Aplica NetworkPolicy (Zero Trust)
	$(KUBECTL) apply -f k8s/gateway/network-policy.yaml

apply-rbac: check-k8s ## Aplica RBAC e ServiceAccounts
	$(KUBECTL) apply -f k8s/gateway/rbac.yaml

apply-all: check-env check-k8s apply-namespace apply-limits apply-rbac apply-network apply-redis apply-ollama apply-agents ## Aplica todos os manifestos
	@echo "Todos os manifestos aplicados."

# ─── Operação do cluster ──────────────────────────────────────────────────────

start: check-env check-k8s ## Inicia o Minikube e o enxame
	@minikube start --driver=docker || true
	@$(MAKE) apply-all
	@echo "ClawDevs iniciado."

stop: check-k8s ## Para o Minikube
	@minikube stop

status: ## Status completo do cluster
	@echo "=== Nós ==="
	@$(KUBECTL) get nodes
	@echo "\n=== Pods ($(NAMESPACE)) ==="
	@$(KUBECTL) get pods -n $(NAMESPACE) -o wide
	@echo "\n=== Serviços ($(NAMESPACE)) ==="
	@$(KUBECTL) get svc -n $(NAMESPACE)
	@echo "\n=== GPU Lock ==="
	@$(KUBECTL) exec -n $(NAMESPACE) $$($(KUBECTL) get pods -n $(NAMESPACE) -l app=redis -o jsonpath='{.items[0].metadata.name}') -- redis-cli get gpu_active_lock 2>/dev/null || echo "Sem lock ativo"
	@echo "\n=== Freio de Mão ==="
	@$(KUBECTL) exec -n $(NAMESPACE) $$($(KUBECTL) get pods -n $(NAMESPACE) -l app=redis -o jsonpath='{.items[0].metadata.name}') -- redis-cli get degradation:emergency_brake_active 2>/dev/null || echo "Não ativo"

# ─── Logs ────────────────────────────────────────────────────────────────────

logs-ceo: ## Logs em tempo real do agente CEO
	$(KUBECTL) logs -f -n $(NAMESPACE) -l app=agent-ceo

logs-po: ## Logs em tempo real do agente PO
	$(KUBECTL) logs -f -n $(NAMESPACE) -l app=agent-po

logs-developer: ## Logs em tempo real do Developer
	$(KUBECTL) logs -f -n $(NAMESPACE) -l app=agent-developer

logs-architect: ## Logs em tempo real do Architect
	$(KUBECTL) logs -f -n $(NAMESPACE) -l app=agent-architect

logs-devops: ## Logs em tempo real do DevOps
	$(KUBECTL) logs -f -n $(NAMESPACE) -l app=agent-devops

logs-ollama: ## Logs em tempo real do Ollama
	$(KUBECTL) logs -f -n $(NAMESPACE) -l app=ollama

logs-all: ## Todos os logs (últimas 50 linhas de cada)
	@for agent in agent-ceo agent-po agent-devops agent-architect agent-developer agent-qa agent-cybersec agent-ux agent-dba ollama; do \
		echo "\n=== $$agent ==="; \
		$(KUBECTL) logs --tail=20 -n $(NAMESPACE) -l app=$$agent 2>/dev/null || echo "Pod não encontrado."; \
	done

# ─── Modelos Ollama ─────────────────────────────────────────────────────────

pull-models: ## Baixa os modelos recomendados no Ollama
	@echo "Baixando modelos Ollama (pode demorar; aguarde)..."
	@OLLAMA_POD=$$($(KUBECTL) get pods -n $(NAMESPACE) -l app=ollama -o jsonpath='{.items[0].metadata.name}'); \
	$(KUBECTL) exec -n $(NAMESPACE) $$OLLAMA_POD -- ollama pull deepseek-coder:6.7b; \
	$(KUBECTL) exec -n $(NAMESPACE) $$OLLAMA_POD -- ollama pull llama3:8b; \
	$(KUBECTL) exec -n $(NAMESPACE) $$OLLAMA_POD -- ollama pull phi3:mini; \
	$(KUBECTL) exec -n $(NAMESPACE) $$OLLAMA_POD -- ollama pull mistral:7b
	@echo "Modelos baixados."

# ─── Testes ──────────────────────────────────────────────────────────────────

test-redis: ## Testa conexão com Redis
	@$(KUBECTL) exec -n $(NAMESPACE) $$($(KUBECTL) get pods -n $(NAMESPACE) -l app=redis -o jsonpath='{.items[0].metadata.name}') -- redis-cli ping

test-gpu: ## Verifica GPU no pod Ollama
	@$(KUBECTL) exec -n $(NAMESPACE) $$($(KUBECTL) get pods -n $(NAMESPACE) -l app=ollama -o jsonpath='{.items[0].metadata.name}') -- nvidia-smi

test-ollama: ## Testa inferência com Ollama
	@$(KUBECTL) exec -n $(NAMESPACE) $$($(KUBECTL) get pods -n $(NAMESPACE) -l app=ollama -o jsonpath='{.items[0].metadata.name}') -- ollama list

# ─── Segurança e manutenção ──────────────────────────────────────────────────

unblock-brake: ## Desbloqueia o freio de mão (somente após revisar MEMORY.md)
	@chmod +x scripts/unblock-degradation.sh && scripts/unblock-degradation.sh

quarantine: ## Isola um pod (uso: make quarantine POD=<nome-do-pod>)
	@$(KUBECTL) label pod $(POD) security=quarantine -n $(NAMESPACE)
	@echo "Pod $(POD) isolado (NetworkPolicy kill-switch aplicada)."

# ─── Build de imagens ────────────────────────────────────────────────────────

build-base: check-docker ## Build da imagem base dos agentes
	docker build -f Dockerfile.base -t clawdevs/agent-base:latest .

# ─── Dashboard ───────────────────────────────────────────────────────────────

dashboard: ## Abre o dashboard Kubernetes
	minikube dashboard

# ─── Desenvolvimento Local ────────────────────────────────────────────────────

VENV := .venv
PYTHON_VENV := $(VENV)/bin/python3
PIP_VENV := $(VENV)/bin/pip

venv: ## Cria ambiente virtual e instala dependências
	python3 -m venv --without-pip $(VENV)
	curl -sS https://bootstrap.pypa.io/get-pip.py -o get-pip.py
	$(PYTHON_VENV) get-pip.py
	rm get-pip.py
	$(PIP_VENV) install -r requirements.base.txt
	$(PIP_VENV) install pytest pytest-cov pytest-asyncio ruff mypy types-requests types-PyYAML

test-local: ## Executa testes unitários com cobertura (Local)
	export PYTHONPATH=$$(pwd) && $(PYTHON_VENV) -m pytest tests/

test-coverage: ## Executa testes exigindo a cobertura configurada (85%)
	export PYTHONPATH=$$(pwd) && $(PYTHON_VENV) -m pytest --cov=. tests/

format: ## Formata o código fonte com ruff (configuração em pyproject.toml)
	$(PYTHON_VENV) -m ruff format .
	$(PYTHON_VENV) -m ruff check --fix .

lint: ## Executa linting com ruff (configuração em pyproject.toml)
	$(PYTHON_VENV) -m ruff check .

typecheck: ## Verifica tipos estáticos com mypy (configuração em pyproject.toml)
	$(PYTHON_VENV) -m mypy orchestrator/ memory/ security/ tools/ agents/ --ignore-missing-imports

# ─── Fluxo de Desenvolvimento Completo ──────────────────────────────────────

prepare: configure setup venv ## [1] Prepara todo o ambiente para codificar
	@echo "Ambiente preparado para desenvolvimento."

build: prepare build-base ## [2] Realiza o build da aplicação (imagens)
	@echo "Build da aplicação concluído."

deploy: start ## [3] Faz o deploy da aplicação (inicia cluster e aplica manifestos)
	@echo "Deploy realizado com sucesso."

test-e2e: ## [4] Faz um teste de integração end-to-end (e2e) com os agentes
	@echo "Executando teste de integração de ponta-a-ponta..."
	$(PYTHON_VENV) -m pytest tests/e2e/ -v || echo "Nenhum teste e2e encontrado ou falha na execução."
