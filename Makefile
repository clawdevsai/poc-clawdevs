# Makefile — ClawDevs
# Comandos principais para operar o ecossistema de agentes.
# Uso: make <alvo>
# Referência: docs/README.md | docs/issues/README.md

.PHONY: help setup verify apply-all start stop status logs-ceo logs-all \
        pull-models test-redis test-gpu build-base unblock-brake \
        apply-namespace apply-limits apply-redis apply-ollama apply-agents apply-network \
        venv test-local test-coverage format lint

KUBECTL := kubectl
NAMESPACE := ai-agents
HELM := helm

help: ## Exibe ajuda
	@echo "ClawDevs — Comandos disponíveis:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-25s\033[0m %s\n", $$1, $$2}'

# ─── Setup inicial ────────────────────────────────────────────────────────────

setup: ## Executa setup completo (um clique)
	@echo "Executando setup ClawDevs..."
	@chmod +x scripts/setup.sh && scripts/setup.sh

verify: ## Verifica se a máquina atende aos requisitos
	@chmod +x scripts/verify-machine.sh && scripts/verify-machine.sh

# ─── Aplicação de manifestos Kubernetes ──────────────────────────────────────

apply-namespace: ## Cria namespace ai-agents
	$(KUBECTL) apply -f k8s/namespace/ai-agents.yaml

apply-limits: ## Aplica ResourceQuota e LimitRange
	$(KUBECTL) apply -f k8s/limits/resource-quota.yaml

apply-redis: ## Implanta Redis
	$(KUBECTL) apply -f k8s/redis/deployment.yaml

apply-ollama: ## Implanta Ollama com GPU
	$(KUBECTL) apply -f k8s/ollama/deployment.yaml

apply-agents: ## Implanta todos os agentes
	$(KUBECTL) apply -f k8s/agents/deployments.yaml

apply-network: ## Aplica NetworkPolicy (Zero Trust)
	$(KUBECTL) apply -f k8s/gateway/network-policy.yaml

apply-rbac: ## Aplica RBAC e ServiceAccounts
	$(KUBECTL) apply -f k8s/gateway/rbac.yaml

apply-all: apply-namespace apply-limits apply-rbac apply-network apply-redis apply-ollama apply-agents ## Aplica todos os manifestos
	@echo "Todos os manifestos aplicados."

# ─── Operação do cluster ──────────────────────────────────────────────────────

start: ## Inicia o Minikube e o enxame
	@minikube start --driver=docker || true
	@$(MAKE) apply-all
	@echo "ClawDevs iniciado."

stop: ## Para o Minikube
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

build-base: ## Build da imagem base dos agentes
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
	$(PIP_VENV) install pytest pytest-cov ruff

test-local: ## Executa testes unitários com cobertura (Local)
	export PYTHONPATH=$$(pwd) && $(PYTHON_VENV) -m pytest --cov=. --cov-report=term-missing tests/

test-coverage: ## Executa testes e valida 90% de cobertura
	export PYTHONPATH=$$(pwd) && $(PYTHON_VENV) -m pytest --cov=. --cov-fail-under=90 tests/

format: ## Formata o código fonte (Local)
	$(PYTHON_VENV) -m ruff format .

lint: ## Executa linting e checagem de tipos (Local)
	$(PYTHON_VENV) -m ruff check .
