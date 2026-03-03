# ClawDevs — alvos principais: prepare (Docker + Minikube GPU), up (apply), down (destroy)
SHELL := /bin/bash
K8S_DIR := k8s
MINIKUBE_CPUS ?= 10
MINIKUBE_MEMORY ?= 20g

.PHONY: prepare up down up-all openclaw-image verify revisao-slot-configmap agent-slots-configmap gateway-redis-adapter-configmap devops-compact-configmap acefalo-configmap up-management developer-configmap phase2-apply phase2-configmaps rotation-configmap url-sandbox-configmap quarantine-pipeline-configmap orchestrator-configmap orchestrator-apply dashboarding

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

# 2. up: inicia Minikube (prepare), build da imagem OpenClaw, aplica todos os recursos
up: prepare openclaw-image
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
	@echo "==> Aplicando ResourceQuota e LimitRange (65% hardware)..."
	kubectl apply -f $(K8S_DIR)/limits.yaml
	@echo "==> Aplicando Redis..."
	kubectl apply -f $(K8S_DIR)/redis/deployment.yaml
	kubectl apply -f $(K8S_DIR)/redis/streams-configmap.yaml
	@echo "==> Aplicando Ollama (GPU)..."
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
	@echo "==> Aplicando provedores de LLM por agente (ollama_local = Ollama GPU padrão)..."
	kubectl apply -f $(K8S_DIR)/llm-providers-configmap.yaml
	@echo "==> Aplicando OpenClaw (ConfigMap + Workspace CEO + SOUL antes do Deployment)..."
	kubectl apply -f $(K8S_DIR)/management-team/openclaw/configmap.yaml
	kubectl apply -f $(K8S_DIR)/management-team/openclaw/workspace-ceo-configmap.yaml
	@echo "==> Aplicando SOUL por escopo (management + development) — necessário para soul-merge initContainer..."
	kubectl apply -f $(K8S_DIR)/management-team/soul/configmap.yaml
	kubectl apply -f $(K8S_DIR)/development-team/soul/configmap.yaml
	@if [ -d $(K8S_DIR)/security ]; then \
		echo "==> ConfigMaps Fase 2 (rotação, URL sandbox, quarentena, gateway adapter)..."; \
		$(MAKE) phase2-configmaps; \
		echo "==> Aplicando Fase 2 (security + phase2-config + evoluções)..."; \
		kubectl apply -f $(K8S_DIR)/security/; \
	fi
	@if [ -d $(K8S_DIR)/orchestrator ]; then \
		echo "==> Orquestrador (Slack consumer, digest, cosmetic, consensus)..."; \
		$(MAKE) orchestrator-configmap; \
		kubectl apply -f $(K8S_DIR)/orchestrator/; \
	fi
	@if [ -f $(K8S_DIR)/management-team/openclaw/serviceaccount.yaml ]; then echo "==> Aplicando ServiceAccount openclaw-router (Fase 2 — 025)..."; kubectl apply -f $(K8S_DIR)/management-team/openclaw/serviceaccount.yaml; fi
	@echo "==> Aplicando Deployment OpenClaw..."
	kubectl apply -f $(K8S_DIR)/management-team/openclaw/deployment.yaml
	@if [ -f $(K8S_DIR)/management-team/openclaw/secret.yaml ]; then \
		echo "==> Aplicando secret openclaw-telegram (Telegram + Slack)..."; \
		kubectl apply -f $(K8S_DIR)/management-team/openclaw/secret.yaml; \
		kubectl rollout restart deployment/openclaw -n ai-agents --timeout=60s 2>/dev/null || true; \
	else \
		echo "==> Secret não encontrado. Padrão: Slack (OpenClaw) + Telegram (só CEO). Use: ./scripts/k8s-openclaw-secret-from-env.sh (OPENCLAW_SLACK_* e TELEGRAM_* no .env)"; \
	fi
	@echo "==> up concluído."
	@echo "  Padrão: Slack = todos os agentes (DM e canais, ex. #all-clawdevsai). Telegram = apenas CEO (Diretor ↔ CEO)."
	@echo "  Slack OpenClaw: defina OPENCLAW_SLACK_APP_TOKEN e OPENCLAW_SLACK_BOT_TOKEN no .env e rode ./scripts/k8s-openclaw-secret-from-env.sh; depois kubectl rollout restart deployment/openclaw -n ai-agents."
	@echo "  Telegram (só CEO): TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID no .env e no Secret."
	@echo "  Ollama: kubectl exec -n ai-agents deploy/ollama-gpu -- ollama pull stewyphoenix19/phi3-mini_v1:latest"
	@echo "  Orquestrador (app/canal próprios): Secret orchestrator-slack. Local: ORCHESTRATOR_SLACK_* no .env. Ver k8s/orchestrator/README.md."
	@echo "  Opcional: make up-management (CEO/PO apenas; scale openclaw a 0 para evitar dois gateways)."

# Sobe tudo em um script: up + slot revisão + Redis streams init + rollout restart.
up-all:
	@$(CURDIR)/scripts/up-all.sh

# Pods CEO e PO apenas (Fase 1 — 012). Usa mesma imagem openclaw-gateway:local e secret Telegram.
# Se usar este target, scale o gateway único a 0 para não ter dois listeners Telegram: kubectl scale deployment openclaw -n ai-agents --replicas=0
up-management:
	@echo "==> Aplicando Management Team (CEO, PO)..."
	kubectl apply -f $(K8S_DIR)/management-team/openclaw/workspace-ceo-configmap.yaml
	kubectl apply -f $(K8S_DIR)/management-team/configmap.yaml
	kubectl apply -f $(K8S_DIR)/management-team/deployment.yaml
	@if [ -f $(K8S_DIR)/management-team/openclaw/secret.yaml ]; then \
		echo "==> Secret Telegram já existe (openclaw)."; \
	else \
		echo "==> Crie o secret: kubectl create secret generic openclaw-telegram -n ai-agents --from-literal=TELEGRAM_BOT_TOKEN=... --from-literal=TELEGRAM_CHAT_ID=..."; \
	fi
	@echo "==> up-management concluído. Gateway CEO/PO: deploy/openclaw-management."

# ConfigMap dos scripts do pod Developer (013). Necessário para deployment developer.
developer-configmap:
	@echo "==> Criando ConfigMap developer-scripts..."
	@kubectl create configmap developer-scripts -n ai-agents \
	  --from-file=developer_worker.py=scripts/developer_worker.py \
	  --from-file=gpu_lock.py=scripts/gpu_lock.py \
	  --dry-run=client -o yaml | kubectl apply -f -
	@echo "==> developer-configmap concluído. Aplique k8s/development-team/developer/ (PVC + deployment)."

# Build da imagem OpenClaw para o Minikube (obrigatório antes do pod openclaw subir com o gateway real)
openclaw-image:
	@echo "==> Build da imagem openclaw-gateway:local no Docker do Minikube..."
	eval $$(minikube docker-env) && docker build -f $(K8S_DIR)/management-team/openclaw/Dockerfile -t openclaw-gateway:local $(K8S_DIR)/management-team/openclaw
	@echo "==> openclaw-image concluído."

# Verificação de hardware (máquina de referência + consumo GPU/CPU/RAM + Quest 65%) e cluster (Minikube + Ollama GPU)
verify:
	@docs/scripts/verify-machine.sh
	@docs/scripts/verify-gpu-cluster.sh

# ConfigMap dos scripts do slot Revisão pós-Dev (007/125). Necessário para o deployment revisao-pos-dev.
revisao-slot-configmap:
	@echo "==> Criando ConfigMap revisao-slot-scripts (slot + gpu_lock + orchestration_phase3 + microadr)..."
	@kubectl create configmap revisao-slot-scripts -n ai-agents \
	  --from-file=slot_revisao_pos_dev.py=scripts/slot_revisao_pos_dev.py \
	  --from-file=gpu_lock.py=scripts/gpu_lock.py \
	  --from-file=orchestration_phase3.py=scripts/orchestration_phase3.py \
	  --from-file=architect_fallback.py=scripts/architect_fallback.py \
	  --from-file=microadr_generate.py=scripts/microadr_generate.py \
	  --from-file=acefalo_redis.py=scripts/acefalo_redis.py \
	  --dry-run=client -o yaml | kubectl apply -f -
	@echo "==> revisao-slot-configmap concluído."

# ConfigMap dos scripts para pods separados por agente (Architect, QA, CyberSec, DBA — 014).
agent-slots-configmap:
	@echo "==> Criando ConfigMap agent-slot-scripts (slot_agent_single.py + gpu_lock.py)..."
	@kubectl create configmap agent-slot-scripts -n ai-agents \
	  --from-file=slot_agent_single.py=scripts/slot_agent_single.py \
	  --from-file=gpu_lock.py=scripts/gpu_lock.py \
	  --from-file=acefalo_redis.py=scripts/acefalo_redis.py \
	  --dry-run=client -o yaml | kubectl apply -f -
	@echo "==> agent-slots-configmap concluído. Aplique k8s/development-team/architect/ etc. (replicas: 0)."

# ConfigMap do adapter HTTP para publicação Redis (Fase 1 — 018) + scripts Fase 2 (token bucket, reputação).
gateway-redis-adapter-configmap:
	@echo "==> Criando ConfigMap gateway-redis-adapter-scripts..."
	@kubectl create configmap gateway-redis-adapter-scripts -n ai-agents \
	  --from-file=gateway_redis_adapter.py=scripts/gateway_redis_adapter.py \
	  --from-file=gateway_token_bucket.py=scripts/gateway_token_bucket.py \
	  --from-file=check_domain_reputation.py=scripts/check_domain_reputation.py \
	  --from-file=truncate_payload_border.py=scripts/truncate_payload_border.py \
	  --from-file=preflight_summarize.py=scripts/preflight_summarize.py \
	  --dry-run=client -o yaml | kubectl apply -f -
	@echo "==> gateway-redis-adapter-configmap concluído. Aplique k8s/development-team/gateway-redis-adapter/."

# ConfigMap do script de compactação segura de buffers (truncamento-finops). Para CronJob devops-compact.
devops-compact-configmap:
	@echo "==> Criando ConfigMap devops-compact-script..."
	@kubectl create configmap devops-compact-script -n ai-agents \
	  --from-file=compact_preserve_protected.py=scripts/compact_preserve_protected.py \
	  --dry-run=client -o yaml | kubectl apply -f -
	@echo "==> devops-compact-configmap concluído. Ver k8s/development-team/devops-compact-cronjob-example.yaml e docs/issues/devops-compactacao-buffer.md."

# ConfigMap dos scripts de contingência cluster acéfalo (124). Para rodar monitor/heartbeat em pods.
acefalo-configmap:
	@echo "==> Criando ConfigMap acefalo-scripts..."
	@kubectl create configmap acefalo-scripts -n ai-agents \
	  --from-file=acefalo_redis.py=scripts/acefalo_redis.py \
	  --from-file=acefalo_contingency.py=scripts/acefalo_contingency.py \
	  --from-file=acefalo_retomada.py=scripts/acefalo_retomada.py \
	  --from-file=acefalo_heartbeat_writer.py=scripts/acefalo_heartbeat_writer.py \
	  --from-file=acefalo_monitor.py=scripts/acefalo_monitor.py \
	  --dry-run=client -o yaml | kubectl apply -f -
	@echo "==> acefalo-configmap concluído. Ver docs/40-contingencia-cluster-acefalo.md"

# Fase 2 — Segurança: config central + ConfigMaps (rotação, URL sandbox, quarentena, adapter) + manifestos security/
phase2-apply: phase2-configmaps
	@echo "==> Aplicando Fase 2 (security: phase2-config, egress-whitelist, RBAC, CronJob, Jobs)..."
	@kubectl apply -f $(K8S_DIR)/security/
	@echo "==> Fase 2 configurada. Contrato: docs/44-fase2-seguranca-automacao.md"

# ConfigMaps Fase 2 (rotação, URL sandbox, quarantine pipeline, gateway adapter). Chamado por make up.
phase2-configmaps: rotation-configmap url-sandbox-configmap quarantine-pipeline-configmap gateway-redis-adapter-configmap
	@echo "==> ConfigMaps Fase 2 aplicados."

# Fase 2 evoluções: ConfigMaps para CronJob rotação, Job URL sandbox, Job quarantine pipeline
rotation-configmap:
	@echo "==> Criando ConfigMap rotation-scripts (rotate_gateway_token.py)..."
	@kubectl create configmap rotation-scripts -n ai-agents \
	  --from-file=rotate_gateway_token.py=scripts/rotate_gateway_token.py \
	  --dry-run=client -o yaml | kubectl apply -f -
	@echo "==> Aplique k8s/security/rotation-rbac.yaml e cronjob-token-rotation.yaml; crie Secret openclaw-telegram-rotation-source para fonte."

url-sandbox-configmap:
	@echo "==> Criando ConfigMap url-sandbox-scripts..."
	@kubectl create configmap url-sandbox-scripts -n ai-agents \
	  --from-file=url_sandbox_fetch.py=scripts/url_sandbox_fetch.py \
	  --dry-run=client -o yaml | kubectl apply -f -

quarantine-pipeline-configmap:
	@echo "==> Criando ConfigMap quarantine-pipeline-scripts..."
	@kubectl create configmap quarantine-pipeline-scripts -n ai-agents \
	  --from-file=quarantine_pipeline.py=scripts/quarantine_pipeline.py \
	  --from-file=quarantine_entropy.py=scripts/quarantine_entropy.py \
	  --from-file=trusted_package_verify.py=scripts/trusted_package_verify.py \
	  --dry-run=client -o yaml | kubectl apply -f -

# Fase 3 — Slack, digest, cosmetic timers, consensus loop (034–036)
orchestrator-configmap:
	@echo "==> Criando ConfigMap orchestrator-scripts (orchestration, slack, digest, cosmetic, consensus)..."
	@kubectl create configmap orchestrator-scripts -n ai-agents \
	  --from-file=orchestration_phase3.py=scripts/orchestration_phase3.py \
	  --from-file=slack_notify.py=scripts/slack_notify.py \
	  --from-file=consumer_orchestrator_events_slack.py=scripts/consumer_orchestrator_events_slack.py \
	  --from-file=arbitrage_cloud.py=scripts/arbitrage_cloud.py \
	  --from-file=digest_daily.py=scripts/digest_daily.py \
	  --from-file=cosmetic_omission.py=scripts/cosmetic_omission.py \
	  --from-file=set_consensus_pilot_result.py=scripts/set_consensus_pilot_result.py \
	  --from-file=consensus_loop_runner.py=scripts/consensus_loop_runner.py \
	  --dry-run=client -o yaml | kubectl apply -f -
	@echo "==> orchestrator-configmap concluído. Crie Secret orchestrator-slack e use make orchestrator-apply."

orchestrator-apply: orchestrator-configmap
	@echo "==> Aplicando orquestrador (configmap-env, CronJobs, consumer Slack)..."
	@kubectl apply -f $(K8S_DIR)/orchestrator/
	@echo "==> Orquestrador aplicado. Ref: docs/06-operacoes.md"

# Abre o dashboard do Minikube no navegador. Habilita o addon e inicia o proxy.
dashboard:
	@echo "==> Habilitando addon dashboard..."
	@minikube addons enable dashboard 2>/dev/null || true
	@echo "==> Abrindo dashboard..."
	@minikube dashboard

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
