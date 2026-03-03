# ClawDevs — Makefile (cluster K8s + OpenClaw + pipeline)
# Uso: make prepare && make up  |  make down  |  make help
SHELL := /bin/bash
K8S_DIR := k8s
MINIKUBE_CPUS ?= 10
MINIKUBE_MEMORY ?= 20g

.PHONY: help
.PHONY: prepare up down up-all
.PHONY: openclaw-image up-management
.PHONY: configmaps-pipeline configmaps-phase2 configmaps-orchestrator
.PHONY: configmap-developer configmap-revisao-slot configmap-agent-slots configmap-gateway-adapter configmap-devops-worker configmap-audit-runner configmap-devops-compact configmap-acefalo
.PHONY: configmap-rotation configmap-url-sandbox configmap-url-sandbox-trigger configmap-quarantine
.PHONY: phase2-apply phase2-configmaps orchestrator-apply orchestrator-configmap
.PHONY: verify reset-memory test-github-access dashboard

# ------------------------------------------------------------------------------
# Help
# ------------------------------------------------------------------------------
help:
	@echo "ClawDevs — alvos principais"
	@echo ""
	@echo "  Cluster"
	@echo "    make prepare      Minikube + Docker + GPU addon"
	@echo "    make up           prepare + openclaw-image + namespace, Redis, Ollama, OpenClaw, phase2, orchestrator"
	@echo "    make up-all      up + slot configmaps + Redis streams init + rollouts (scripts/up-all.sh)"
	@echo "    make down        Remove namespace e recursos (estaca zero)"
	@echo ""
	@echo "  OpenClaw"
	@echo "    make openclaw-image   Build openclaw-gateway:local no Minikube"
	@echo "    make up-management    Deploy CEO/PO (scale openclaw a 0 se usar dois gateways)"
	@echo ""
	@echo "  ConfigMaps (scripts para pods)"
	@echo "    make configmaps-pipeline     PO, Architect-draft, Developer, Revisão-slot, DevOps-worker, Gateway-adapter"
	@echo "    make configmaps-phase2       rotation, url-sandbox, quarantine, gateway-adapter"
	@echo "    make configmaps-orchestrator orchestrator-scripts (Slack, digest, cosmetic)"
	@echo "    make configmap-<nome>        Um só (ex: configmap-developer)"
	@echo ""
	@echo "  Fase 2 / Orchestrator"
	@echo "    make phase2-configmaps   Cria ConfigMaps da Fase 2"
	@echo "    make phase2-apply        phase2-configmaps + kubectl apply -f k8s/security/"
	@echo "    make orchestrator-configmap"
	@echo "    make orchestrator-apply  orchestrator-configmap + kubectl apply -f k8s/orchestrator/"
	@echo ""
	@echo "  Utilitários"
	@echo "    make verify             Verificação hardware + cluster"
	@echo "    make reset-memory       Reset Redis + workspace (MEMORY.md, etc.)"
	@echo "    make test-github-access  [MODE=host|cluster|all]"
	@echo "    make dashboard          Minikube dashboard no browser"

# ------------------------------------------------------------------------------
# Cluster lifecycle
# ------------------------------------------------------------------------------
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
	@echo "==> Iniciando Minikube com Docker e GPU..."
	@if ! minikube status >/dev/null 2>&1; then \
		minikube start --driver=docker --addons=nvidia-device-plugin --cpus=$(MINIKUBE_CPUS) --memory=$(MINIKUBE_MEMORY); \
	else \
		echo "  Minikube já está rodando."; \
	fi
	@minikube addons enable nvidia-device-plugin 2>/dev/null || true
	@echo "==> prepare concluído. Use 'make up' para aplicar os recursos."

up: prepare openclaw-image
	@echo "==> Verificando Minikube..."
	@if ! minikube status >/dev/null 2>&1; then \
		minikube start --driver=docker --addons=nvidia-device-plugin --cpus=$(MINIKUBE_CPUS) --memory=$(MINIKUBE_MEMORY); \
		minikube addons enable nvidia-device-plugin 2>/dev/null || true; \
	else \
		echo "  Minikube já está rodando."; \
	fi
	@echo "==> Aplicando namespace..."
	kubectl apply -f $(K8S_DIR)/namespace.yaml
	@echo "==> Aplicando ResourceQuota e LimitRange..."
	kubectl apply -f $(K8S_DIR)/limits.yaml
	@echo "==> Aplicando Redis..."
	kubectl apply -f $(K8S_DIR)/redis/deployment.yaml
	kubectl apply -f $(K8S_DIR)/redis/streams-configmap.yaml
	@echo "==> Aplicando Ollama (GPU)..."
	kubectl apply -f $(K8S_DIR)/ollama/deployment.yaml
	@if [ -f $(K8S_DIR)/ollama/secret.yaml ]; then \
		echo "==> Aplicando secret Ollama Cloud..."; \
		kubectl apply -f $(K8S_DIR)/ollama/secret.yaml; \
		kubectl rollout restart deployment/ollama-gpu -n ai-agents --timeout=60s 2>/dev/null || true; \
		$(CURDIR)/scripts/ollama-ensure-cloud-auth.sh; \
	else \
		echo "==> Secret Ollama Cloud não encontrado (opcional)."; \
	fi
	@echo "==> Aplicando provedores LLM..."
	kubectl apply -f $(K8S_DIR)/llm-providers-configmap.yaml
	@echo "==> Aplicando OpenClaw (ConfigMap + Workspace CEO + SOUL)..."
	kubectl apply -f $(K8S_DIR)/management-team/openclaw/configmap.yaml
	kubectl apply -f $(K8S_DIR)/management-team/openclaw/workspace-ceo-configmap.yaml
	kubectl apply -f $(K8S_DIR)/management-team/soul/configmap.yaml
	kubectl apply -f $(K8S_DIR)/development-team/soul/configmap.yaml
	@if [ -d $(K8S_DIR)/security ]; then \
		$(MAKE) phase2-configmaps; \
		kubectl apply -f $(K8S_DIR)/security/; \
	fi
	@if [ -d $(K8S_DIR)/orchestrator ]; then \
		$(MAKE) orchestrator-configmap; \
		kubectl apply -f $(K8S_DIR)/orchestrator/; \
	fi
	@if [ -f $(K8S_DIR)/management-team/openclaw/serviceaccount.yaml ]; then \
		kubectl apply -f $(K8S_DIR)/management-team/openclaw/serviceaccount.yaml; fi
	@echo "==> Aplicando Deployment OpenClaw..."
	kubectl apply -f $(K8S_DIR)/management-team/openclaw/deployment.yaml
	@if [ -f $(K8S_DIR)/management-team/openclaw/secret.yaml ]; then \
		kubectl apply -f $(K8S_DIR)/management-team/openclaw/secret.yaml; \
		kubectl rollout restart deployment/openclaw -n ai-agents --timeout=60s 2>/dev/null || true; \
	else \
		echo "==> Secret openclaw-telegram não encontrado. Use: ./scripts/k8s-openclaw-secret-from-env.sh"; \
	fi
	@echo "==> up concluído."
	@echo "  Slack/Telegram: OPENCLAW_SLACK_*, TELEGRAM_* no .env → k8s-openclaw-secret-from-env.sh"
	@echo "  Ollama: kubectl exec -n ai-agents deploy/ollama-gpu -- ollama pull <modelo>"
	@echo "  Pipeline (PO, Developer, Revisão, DevOps, etc.): make configmaps-pipeline && kubectl apply -f k8s/development-team/"

up-all:
	@$(CURDIR)/scripts/up-all.sh

down:
	@echo "==> down: removendo recursos (estaca zero)..."
	@if ! kubectl get namespace ai-agents >/dev/null 2>&1; then \
		echo "  Namespace ai-agents não existe."; exit 0; fi
	-kubectl delete deployment -n ai-agents --all --ignore-not-found --timeout=60s 2>/dev/null || true
	-kubectl delete statefulset -n ai-agents --all --ignore-not-found --timeout=60s 2>/dev/null || true
	-kubectl wait --for=delete pod -l app=ollama -n ai-agents --timeout=90s 2>/dev/null || true
	-kubectl wait --for=delete pod -l app=openclaw -n ai-agents --timeout=90s 2>/dev/null || true
	-kubectl wait --for=delete pod -l app=redis -n ai-agents --timeout=90s 2>/dev/null || true
	@sleep 3
	-kubectl delete pvc -n ai-agents --all --ignore-not-found --timeout=60s 2>/dev/null || true
	-kubectl delete namespace ai-agents --ignore-not-found --timeout=120s 2>/dev/null || true
	@echo "==> down concluído."

# ------------------------------------------------------------------------------
# OpenClaw
# ------------------------------------------------------------------------------
openclaw-image:
	@echo "==> Build openclaw-gateway:local (Minikube Docker)..."
	eval $$(minikube docker-env) && docker build -f $(K8S_DIR)/management-team/openclaw/Dockerfile -t openclaw-gateway:local $(K8S_DIR)/management-team/openclaw
	@echo "==> openclaw-image concluído."

up-management:
	@echo "==> Aplicando Management Team (CEO, PO)..."
	kubectl apply -f $(K8S_DIR)/management-team/openclaw/workspace-ceo-configmap.yaml
	kubectl apply -f $(K8S_DIR)/management-team/configmap.yaml
	kubectl apply -f $(K8S_DIR)/management-team/deployment.yaml
	@echo "==> up-management concluído. Scale openclaw a 0 se usar dois gateways."

# ------------------------------------------------------------------------------
# ConfigMaps — Pipeline (PO, Architect-draft, Developer, Revisão, DevOps, Gateway-adapter)
# ------------------------------------------------------------------------------
configmaps-pipeline: configmap-po configmap-architect-draft configmap-developer configmap-revisao-slot configmap-devops-worker configmap-gateway-adapter
	@echo "==> ConfigMaps do pipeline aplicados."

configmap-po:
	@echo "==> ConfigMap po-scripts..."
	@kubectl create configmap po-scripts -n ai-agents \
	  --from-file=po_worker.py=app/po_worker.py \
	  --from-file=gpu_lock.py=app/gpu_lock.py \
	  --from-file=issue_state.py=app/issue_state.py \
	  --from-file=openclaw_gateway_call.py=app/openclaw_gateway_call.py \
	  --dry-run=client -o yaml | kubectl apply -f -

configmap-architect-draft:
	@echo "==> ConfigMap architect-draft-scripts..."
	@kubectl create configmap architect-draft-scripts -n ai-agents \
	  --from-file=architect_draft_consumer.py=app/architect_draft_consumer.py \
	  --from-file=gpu_lock.py=app/gpu_lock.py \
	  --from-file=issue_state.py=app/issue_state.py \
	  --from-file=openclaw_gateway_call.py=app/openclaw_gateway_call.py \
	  --dry-run=client -o yaml | kubectl apply -f -

configmap-developer:
	@echo "==> ConfigMap developer-scripts..."
	@kubectl create configmap developer-scripts -n ai-agents \
	  --from-file=developer_worker.py=app/developer_worker.py \
	  --from-file=gpu_lock.py=app/gpu_lock.py \
	  --from-file=openclaw_gateway_call.py=app/openclaw_gateway_call.py \
	  --dry-run=client -o yaml | kubectl apply -f -

configmap-revisao-slot:
	@echo "==> ConfigMap revisao-slot-scripts..."
	@kubectl create configmap revisao-slot-scripts -n ai-agents \
	  --from-file=slot_revisao_pos_dev.py=app/slot_revisao_pos_dev.py \
	  --from-file=gpu_lock.py=app/gpu_lock.py \
	  --from-file=openclaw_gateway_call.py=app/openclaw_gateway_call.py \
	  --from-file=orchestration_phase3.py=app/orchestration_phase3.py \
	  --from-file=architect_fallback.py=app/architect_fallback.py \
	  --from-file=microadr_generate.py=app/microadr_generate.py \
	  --from-file=acefalo_redis.py=app/acefalo_redis.py \
	  --dry-run=client -o yaml | kubectl apply -f -

configmap-devops-worker:
	@echo "==> ConfigMap devops-worker-scripts..."
	@kubectl create configmap devops-worker-scripts -n ai-agents \
	  --from-file=devops_worker.py=app/devops_worker.py \
	  --from-file=gpu_lock.py=app/gpu_lock.py \
	  --from-file=issue_state.py=app/issue_state.py \
	  --from-file=openclaw_gateway_call.py=app/openclaw_gateway_call.py \
	  --dry-run=client -o yaml | kubectl apply -f -

configmap-audit-runner:
	@echo "==> ConfigMap audit-runner-scripts..."
	@kubectl create configmap audit-runner-scripts -n ai-agents \
	  --from-file=audit_runner.py=app/audit_runner.py \
	  --from-file=gpu_lock.py=app/gpu_lock.py \
	  --from-file=issue_state.py=app/issue_state.py \
	  --from-file=openclaw_gateway_call.py=app/openclaw_gateway_call.py \
	  --dry-run=client -o yaml | kubectl apply -f -

configmap-gateway-adapter:
	@echo "==> ConfigMap gateway-redis-adapter-scripts..."
	@kubectl create configmap gateway-redis-adapter-scripts -n ai-agents \
	  --from-file=gateway_redis_adapter.py=app/gateway_redis_adapter.py \
	  --from-file=gateway_token_bucket.py=app/gateway_token_bucket.py \
	  --from-file=check_domain_reputation.py=app/check_domain_reputation.py \
	  --from-file=truncate_payload_border.py=app/truncate_payload_border.py \
	  --from-file=preflight_summarize.py=app/preflight_summarize.py \
	  --dry-run=client -o yaml | kubectl apply -f -

configmap-devops-compact:
	@echo "==> ConfigMap devops-compact-script..."
	@kubectl create configmap devops-compact-script -n ai-agents \
	  --from-file=compact_preserve_protected.py=app/compact_preserve_protected.py \
	  --dry-run=client -o yaml | kubectl apply -f -

configmap-acefalo:
	@echo "==> ConfigMap acefalo-scripts..."
	@kubectl create configmap acefalo-scripts -n ai-agents \
	  --from-file=acefalo_redis.py=app/acefalo_redis.py \
	  --from-file=acefalo_contingency.py=app/acefalo_contingency.py \
	  --from-file=acefalo_retomada.py=app/acefalo_retomada.py \
	  --from-file=acefalo_heartbeat_writer.py=app/acefalo_heartbeat_writer.py \
	  --from-file=acefalo_monitor.py=app/acefalo_monitor.py \
	  --dry-run=client -o yaml | kubectl apply -f -

# Deprecated: pods architect/qa/cybersec/dba (014). Use revisao-pos-dev.
configmap-agent-slots:
	@echo "==> ConfigMap agent-slot-scripts (deprecated)..."
	@kubectl create configmap agent-slot-scripts -n ai-agents \
	  --from-file=gpu_lock.py=scripts/gpu_lock.py \
	  --from-file=acefalo_redis.py=scripts/acefalo_redis.py \
	  --dry-run=client -o yaml | kubectl apply -f -

# ------------------------------------------------------------------------------
# ConfigMaps — Phase2 (segurança: rotação, url-sandbox, quarentena)
# ------------------------------------------------------------------------------
configmaps-phase2: configmap-rotation configmap-url-sandbox configmap-quarantine configmap-gateway-adapter
	@echo "==> ConfigMaps Fase 2 aplicados."

configmap-rotation:
	@echo "==> ConfigMap rotation-scripts..."
	@kubectl create configmap rotation-scripts -n ai-agents \
	  --from-file=rotate_gateway_token.py=app/rotate_gateway_token.py \
	  --dry-run=client -o yaml | kubectl apply -f -

configmap-url-sandbox:
	@echo "==> ConfigMap url-sandbox-scripts..."
	@kubectl create configmap url-sandbox-scripts -n ai-agents \
	  --from-file=url_sandbox_fetch.py=app/url_sandbox_fetch.py \
	  --dry-run=client -o yaml | kubectl apply -f -

configmap-url-sandbox-trigger:
	@echo "==> ConfigMap url-sandbox-trigger-scripts..."
	@kubectl create configmap url-sandbox-trigger-scripts -n ai-agents \
	  --from-file=url_sandbox_trigger.py=app/url_sandbox_trigger.py \
	  --dry-run=client -o yaml | kubectl apply -f -

configmap-quarantine:
	@echo "==> ConfigMap quarantine-pipeline-scripts..."
	@kubectl create configmap quarantine-pipeline-scripts -n ai-agents \
	  --from-file=quarantine_pipeline.py=app/quarantine_pipeline.py \
	  --from-file=quarantine_entropy.py=app/quarantine_entropy.py \
	  --from-file=trusted_package_verify.py=app/trusted_package_verify.py \
	  --dry-run=client -o yaml | kubectl apply -f -

# ------------------------------------------------------------------------------
# Phase2 apply (security/)
# ------------------------------------------------------------------------------
phase2-configmaps: configmaps-phase2

phase2-apply: phase2-configmaps
	@echo "==> Aplicando k8s/security/..."
	@kubectl apply -f $(K8S_DIR)/security/
	@echo "==> Fase 2 configurada."

# ------------------------------------------------------------------------------
# ConfigMaps — Orchestrator (Slack consumer, digest, cosmetic)
# ------------------------------------------------------------------------------
configmaps-orchestrator: orchestrator-configmap

orchestrator-configmap:
	@echo "==> ConfigMap orchestrator-scripts..."
	@kubectl create configmap orchestrator-scripts -n ai-agents \
	  --from-file=orchestration_phase3.py=app/orchestration_phase3.py \
	  --from-file=slack_notify.py=app/slack_notify.py \
	  --from-file=consumer_orchestrator_events_slack.py=app/consumer_orchestrator_events_slack.py \
	  --from-file=arbitrage_cloud.py=app/arbitrage_cloud.py \
	  --from-file=digest_daily.py=app/digest_daily.py \
	  --from-file=cosmetic_omission.py=app/cosmetic_omission.py \
	  --from-file=set_consensus_pilot_result.py=app/set_consensus_pilot_result.py \
	  --dry-run=client -o yaml | kubectl apply -f -

orchestrator-apply: orchestrator-configmap
	@echo "==> Aplicando k8s/orchestrator/..."
	@kubectl apply -f $(K8S_DIR)/orchestrator/
	@echo "==> Orquestrador aplicado."

# ------------------------------------------------------------------------------
# Utilitários
# ------------------------------------------------------------------------------
verify:
	@docs/scripts/verify-machine.sh
	@docs/scripts/verify-gpu-cluster.sh

reset-memory:
	@$(CURDIR)/scripts/reset_agent_memory.sh

test-github-access:
	@$(CURDIR)/scripts/test_github_access.sh $(or $(MODE),all)

dashboard:
	@minikube addons enable dashboard 2>/dev/null || true
	@minikube dashboard

# ------------------------------------------------------------------------------
# Aliases (compatibilidade com comandos antigos)
# ------------------------------------------------------------------------------
developer-configmap: configmap-developer
revisao-slot-configmap: configmap-revisao-slot
agent-slots-configmap: configmap-agent-slots
gateway-redis-adapter-configmap: configmap-gateway-adapter
devops-compact-configmap: configmap-devops-compact
acefalo-configmap: configmap-acefalo
rotation-configmap: configmap-rotation
url-sandbox-configmap: configmap-url-sandbox
quarantine-pipeline-configmap: configmap-quarantine

url-sandbox-run: configmap-url-sandbox
	@test -n "$(URL)" || (echo "Uso: make url-sandbox-run URL=https://exemplo.com"; exit 1)
	@kubectl patch configmap phase2-config -n ai-agents -p '{"data":{"URL_SANDBOX_TARGET":"$(URL)"}}'
	@kubectl delete job url-sandbox -n ai-agents --ignore-not-found=true
	@kubectl apply -f $(K8S_DIR)/security/job-url-sandbox.yaml
	@echo "Acompanhe: kubectl logs -f job/url-sandbox -n ai-agents"

url-sandbox-trigger-apply: configmap-url-sandbox-trigger
	@kubectl apply -f $(K8S_DIR)/security/url-sandbox-trigger-rbac.yaml
	@kubectl apply -f $(K8S_DIR)/security/url-sandbox-trigger-deployment.yaml
	@echo "Opcional: kubectl create secret generic url-sandbox-trigger-secret -n ai-agents --from-literal=TRIGGER_SECRET='...'"
