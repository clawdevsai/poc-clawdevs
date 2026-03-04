# ClawDevs — Makefile (cluster K8s + OpenClaw + pipeline)
# Uso: make prepare && make up  |  make down  |  make help
SHELL := /bin/bash
K8S_DIR := k8s
MINIKUBE_CPUS ?= 10
MINIKUBE_MEMORY ?= 20g

.PHONY: help
.PHONY: prepare up down up-all shared shared-ensure
.PHONY: openclaw-image up-management
.PHONY: configmaps-pipeline configmaps-phase2 configmaps-orchestrator
.PHONY: configmap-developer configmap-revisao-slot configmap-agent-slots configmap-gateway-adapter configmap-devops-worker configmap-audit-runner configmap-devops-compact configmap-acefalo
.PHONY: configmap-rotation configmap-url-sandbox configmap-url-sandbox-trigger configmap-quarantine
.PHONY: security-apply security-configmaps orchestrator-apply orchestrator-configmap
.PHONY: configmap-kanban-api kanban-image kanban-apply kanban-url
.PHONY: verify reset-memory init-memory test-github-access dashboard status status-pods

# ------------------------------------------------------------------------------
# Help
# ------------------------------------------------------------------------------
help:
	@echo "ClawDevs — Comandos Principais (Guia para Leigos)"
	@echo ""
	@echo "  🖥️  LIGAR E DESLIGAR O SISTEMA"
	@echo "    make prepare      -> Prepara seu computador: instala Docker, Minikube e liga o motor básico."
	@echo "    make up           -> Liga o sistema principal do ClawDevs (Banco de dados, IA local e Agentes)."
	@echo "    make up-all       -> Liga tudo (make up) + configurações extras para deixar 100% pronto para uso."
	@echo "    make down         -> Desliga e apaga todo o sistema ClawDevs (volta o PC ao estado normal)."
	@echo ""
	@echo "  🧠 INTELIGÊNCIA ARTIFICIAL E AGENTES"
	@echo "    make openclaw-image   -> Empacota o cerébro do sistema (OpenClaw) para rodar na sua máquina."
	@echo "    make up-management    -> Liga apenas os agentes chefes (CEO e o Dono do Produto/PO)."
	@echo ""
	@echo "  ⚙️  ARQUIVOS DE CONFIGURAÇÃO (Trabalhadores)"
	@echo "    make configmaps-pipeline     -> Carrega as instruções para os agentes (Desenvolvedor, Revisor, etc)."
	@echo "    make configmaps-phase2       -> Carrega as instruções avançadas (segurança e rotinas extras)."
	@echo "    make configmaps-orchestrator -> Carrega as rotinas que avisam no Slack e organizam as tarefas."
	@echo "    make configmap-<nome>        -> Carrega a instrução apenas de um agente específico."
	@echo ""
	@echo "  🛡️ SEGURANÇA E ORQUESTRAÇÃO"
	@echo "    make security-configmaps  -> Prepara as regras de segurança."
	@echo "    make security-apply       -> Ativa a segurança no sistema (avaliação de links perigosos, etc)."
	@echo "    make orchestrator-configmap -> Prepara o coordenador (Orquestrador)."
	@echo "    make orchestrator-apply   -> Ativa o coordenador (envio de alertas e organização do sistema)."
	@echo ""
	@echo "  🛠️  FERRAMENTAS ÚTEIS E DIAGNÓSTICO"
	@echo "    make verify             -> Verifica se o seu hardware (Placa de vídeo/CPU) aguenta o sistema."
	@echo "    make status             -> Mostra um resumo do que está rodando e se há travamentos."
	@echo "    make status-pods        -> Mostra o 'diário de bordo' (logs) das IAs rodando agora."
	@echo "    make reset-memory       -> Apaga a memória das IAs (útil para recomeçar projetos do zero)."
	@echo "    make init-memory        -> Inicializa estrutura de memória (decisions/projects/lessons/pending + .learnings/). Já rodado no 'make up'; use manualmente se o Job falhar."
	@echo "    make test-github-access -> Testa se as IAs conseguem ler arquivos no Github."
	@echo "    make dashboard          -> Abre uma tela visual no seu navegador para ver o motor do sistema."
	@echo "    make shared             -> Cria uma pasta compartilhada para você ver os arquivos que a IA cria."

# ------------------------------------------------------------------------------
# Cluster lifecycle
# ------------------------------------------------------------------------------
# LIGA O MOTOR: Instala o necessário (Docker, Minikube) e inicia o cluster básico.
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

# LIGA TUDO: Inicia o banco de dados, a Inteligência Artificial (Ollama) e os agentes principais.
# Otimizado: pula prepare se Minikube já roda; rebuild de imagem só se Dockerfile/entrypoint mudaram;
# agrupa kubectl apply para reduzir chamadas ao API server; configmaps em paralelo.
OPENCLAW_BUILD_DIR := $(K8S_DIR)/management-team/openclaw
OPENCLAW_CHECKSUM_FILE := /tmp/.openclaw-image-checksum

up:
	@if ! minikube status >/dev/null 2>&1; then \
		echo "==> Minikube não está rodando. Executando prepare..."; \
		$(MAKE) prepare; \
	fi
	@echo "==> Build OpenClaw (condicional)..."
	@NEW_SUM=$$(cat $(OPENCLAW_BUILD_DIR)/Dockerfile $(OPENCLAW_BUILD_DIR)/entrypoint.sh 2>/dev/null | md5sum | cut -d' ' -f1); \
	OLD_SUM=$$(cat $(OPENCLAW_CHECKSUM_FILE) 2>/dev/null || echo "none"); \
	if [ "$$NEW_SUM" != "$$OLD_SUM" ]; then \
		echo "  Dockerfile/entrypoint alterados — rebuild..."; \
		eval $$(minikube docker-env) && docker build -q -f $(OPENCLAW_BUILD_DIR)/Dockerfile -t openclaw-gateway:local $(OPENCLAW_BUILD_DIR); \
		echo "$$NEW_SUM" > $(OPENCLAW_CHECKSUM_FILE); \
		echo "  openclaw-image concluído."; \
	else \
		echo "  Imagem OpenClaw inalterada — skip build."; \
	fi
	@echo "==> Namespace + limites..."
	@kubectl apply -f $(K8S_DIR)/shared/infra/namespace.yaml -f $(K8S_DIR)/shared/infra/limits.yaml
	@echo "==> Secrets (.env)..."
	@$(CURDIR)/scripts/secrets-from-env.sh || true
	@echo "==> Redis + Ollama..."
	@kubectl apply -f $(K8S_DIR)/redis/deployment.yaml -f $(K8S_DIR)/redis/streams-configmap.yaml
	@kubectl apply -f $(K8S_DIR)/ollama/deployment.yaml
	@if [ -f $(K8S_DIR)/ollama/secret.yaml ]; then \
		echo "  Aplicando secret Ollama Cloud..."; \
		kubectl apply -f $(K8S_DIR)/ollama/secret.yaml; \
		kubectl rollout restart deployment/ollama-gpu -n ai-agents --timeout=60s 2>/dev/null || true; \
		$(CURDIR)/scripts/ollama-ensure-cloud-auth.sh; \
	fi
	@echo "==> ConfigMaps (LLM + OpenClaw + SOUL)..."
	@kubectl apply \
		-f $(K8S_DIR)/shared/infra/llm-providers.yaml \
		-f $(OPENCLAW_BUILD_DIR)/configmap.yaml \
		-f $(OPENCLAW_BUILD_DIR)/workspace-ceo-configmap.yaml \
		-f $(OPENCLAW_BUILD_DIR)/workspace-po-configmap.yaml \
		-f $(OPENCLAW_BUILD_DIR)/workspace-architect-configmap.yaml \
		-f $(OPENCLAW_BUILD_DIR)/workspace-developer-configmap.yaml \
		-R -f $(K8S_DIR)/management-team/ceo/soul/ \
		-R -f $(K8S_DIR)/management-team/po/soul/ \
		-R -f $(K8S_DIR)/development-team/
	@if [ -d $(K8S_DIR)/security ]; then \
		$(MAKE) security-configmaps; \
		kubectl apply -f $(K8S_DIR)/security/; \
	fi
	@if [ -d $(K8S_DIR)/orchestrator ]; then \
		$(MAKE) orchestrator-configmap; \
		kubectl apply -f $(K8S_DIR)/orchestrator/; \
	fi
	@if [ -f $(OPENCLAW_BUILD_DIR)/serviceaccount.yaml ]; then \
		kubectl apply -f $(OPENCLAW_BUILD_DIR)/serviceaccount.yaml; fi
	@echo "==> Workspace compartilhado (PV + PVC + minikube mount)..."
	@$(MAKE) shared-ensure
	@kubectl apply -f $(OPENCLAW_BUILD_DIR)/shared-workspace-pv.yaml -f $(OPENCLAW_BUILD_DIR)/shared-workspace-pvc.yaml
	@echo "==> Deployment OpenClaw..."
	@kubectl apply -f $(OPENCLAW_BUILD_DIR)/deployment.yaml
	@if [ -f $(OPENCLAW_BUILD_DIR)/secret.yaml ]; then \
		kubectl apply -f $(OPENCLAW_BUILD_DIR)/secret.yaml; \
	fi
	@kubectl rollout restart deployment/openclaw -n ai-agents --timeout=60s 2>/dev/null || true
	@echo "==> Init-memory (estrutura memory/ + shared/memory/ + .learnings/)..."
	@kubectl apply -f $(K8S_DIR)/management-team/openclaw/init-memory-configmap.yaml
	@kubectl delete job init-memory-structure -n ai-agents --ignore-not-found=true
	@kubectl apply -f $(K8S_DIR)/management-team/openclaw/init-memory-job.yaml
	@kubectl wait --for=condition=complete job/init-memory-structure -n ai-agents --timeout=120s \
		&& echo "  init-memory OK." \
		|| (kubectl logs -n ai-agents -l component=init-memory --tail=20 2>/dev/null; echo "  AVISO: init-memory falhou; rode 'make init-memory' manualmente.")
	@echo "==> Pipeline (ConfigMaps em paralelo + deployments)..."
	@$(MAKE) -j4 configmap-po configmap-architect-draft configmap-developer configmap-revisao-slot configmap-devops-worker configmap-audit-runner configmap-gateway-adapter
	@for dir in po architect-draft developer revisao-pos-dev devops-worker audit-runner gateway-redis-adapter; do \
		kubectl apply -f $(K8S_DIR)/development-team/$$dir/ 2>/dev/null || true; \
	done
	@if ! kubectl get job redis-streams-init -n ai-agents &>/dev/null; then \
		echo "==> Redis streams init (job one-shot)..."; \
		kubectl apply -f $(K8S_DIR)/redis/job-init-streams.yaml; \
	fi
	@echo "==> up concluído."
	@echo "  Ollama: kubectl exec -n ai-agents deploy/ollama-gpu -- ollama pull <modelo>"
	@IP=$$(minikube ip); \
	echo ""; \
	echo "  🚀 OpenClaw Control UI: http://$$IP:30000"; \
	echo ""

# LIGA TUDO + EXTRAS: Faz o 'make up' e logo depois já aplica funções extras prontas para uso.
up-all:
	@$(CURDIR)/scripts/up-all.sh

# DESLIGA TUDO: Apaga todo o ambiente do ClawDevs do seu computador, limpando a memória e desligando os processos.
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
# EMPACOTA O CÉREBRO: Pega o código do OpenClaw e gera o pacote (imagem Docker) para rodar localmente.
openclaw-image:
	@echo "==> Build openclaw-gateway:local (Minikube Docker)..."
	eval $$(minikube docker-env) && docker build -f $(K8S_DIR)/management-team/openclaw/Dockerfile -t openclaw-gateway:local $(K8S_DIR)/management-team/openclaw
	@echo "==> openclaw-image concluído."

# LIGA A GERÊNCIA: Sobe apenas os agentes de controle (CEO e PO).
up-management:
	@echo "==> Aplicando Management Team (CEO, PO)..."
	kubectl apply -f $(K8S_DIR)/management-team/openclaw/workspace-ceo-configmap.yaml
	kubectl apply -f $(K8S_DIR)/management-team/configmap.yaml
	kubectl apply -f $(K8S_DIR)/management-team/deployment.yaml
	@echo "==> up-management concluído. Scale openclaw a 0 se usar dois gateways."

# ------------------------------------------------------------------------------
# ConfigMaps — Pipeline (PO, Architect-draft, Developer, Revisão, DevOps, Gateway-adapter)
# ------------------------------------------------------------------------------
# CARREGA A EQUIPE: Envia as instruções de trabalho para toda a equipe de desenvolvimento (Dev, PO, Arquiteto, etc).
configmaps-pipeline: configmap-po configmap-architect-draft configmap-developer configmap-revisao-slot configmap-devops-worker configmap-audit-runner configmap-gateway-adapter
	@echo "==> ConfigMaps do pipeline aplicados."

configmap-po:
	@echo "==> ConfigMap po-scripts..."
	@kubectl create configmap po-scripts -n ai-agents \
	  --from-file=po_worker.py=app/agents/po_worker.py \
	  --from-file=gpu_lock.py=app/features/gpu_lock.py \
	  --from-file=issue_state.py=app/shared/issue_state.py \
	  --from-file=openclaw_gateway_call.py=app/shared/openclaw_gateway_call.py \
	  --dry-run=client -o yaml | kubectl apply -f -

configmap-architect-draft:
	@echo "==> ConfigMap architect-draft-scripts..."
	@kubectl create configmap architect-draft-scripts -n ai-agents \
	  --from-file=architect_draft_consumer.py=app/agents/architect_draft_consumer.py \
	  --from-file=gpu_lock.py=app/features/gpu_lock.py \
	  --from-file=issue_state.py=app/shared/issue_state.py \
	  --from-file=openclaw_gateway_call.py=app/shared/openclaw_gateway_call.py \
	  --dry-run=client -o yaml | kubectl apply -f -

configmap-developer:
	@echo "==> ConfigMap developer-scripts..."
	@kubectl create configmap developer-scripts -n ai-agents \
	  --from-file=developer_worker.py=app/agents/developer_worker.py \
	  --from-file=gpu_lock.py=app/features/gpu_lock.py \
	  --from-file=openclaw_gateway_call.py=app/shared/openclaw_gateway_call.py \
	  --dry-run=client -o yaml | kubectl apply -f -

configmap-revisao-slot:
	@echo "==> ConfigMap revisao-slot-scripts..."
	@kubectl create configmap revisao-slot-scripts -n ai-agents \
	  --from-file=slot_revisao_pos_dev.py=app/agents/slot_revisao_pos_dev.py \
	  --from-file=gpu_lock.py=app/features/gpu_lock.py \
	  --from-file=openclaw_gateway_call.py=app/shared/openclaw_gateway_call.py \
	  --from-file=orchestration.py=app/core/orchestration.py \
	  --from-file=architect_fallback.py=app/core/architect_fallback.py \
	  --from-file=microadr_generate.py=app/features/microadr_generate.py \
	  --from-file=acefalo_redis.py=app/contingency/acefalo_redis.py \
	  --dry-run=client -o yaml | kubectl apply -f -

configmap-devops-worker:
	@echo "==> ConfigMap devops-worker-scripts..."
	@kubectl create configmap devops-worker-scripts -n ai-agents \
	  --from-file=devops_worker.py=app/agents/devops_worker.py \
	  --from-file=gpu_lock.py=app/features/gpu_lock.py \
	  --from-file=issue_state.py=app/shared/issue_state.py \
	  --from-file=openclaw_gateway_call.py=app/shared/openclaw_gateway_call.py \
	  --dry-run=client -o yaml | kubectl apply -f -

configmap-audit-runner:
	@echo "==> ConfigMap audit-runner-scripts..."
	@kubectl create configmap audit-runner-scripts -n ai-agents \
	  --from-file=audit_runner.py=app/agents/audit_runner.py \
	  --from-file=gpu_lock.py=app/features/gpu_lock.py \
	  --from-file=issue_state.py=app/shared/issue_state.py \
	  --from-file=openclaw_gateway_call.py=app/shared/openclaw_gateway_call.py \
	  --dry-run=client -o yaml | kubectl apply -f -

configmap-gateway-adapter:
	@echo "==> ConfigMap gateway-redis-adapter-scripts..."
	@kubectl create configmap gateway-redis-adapter-scripts -n ai-agents \
	  --from-file=gateway_redis_adapter.py=app/shared/gateway_redis_adapter.py \
	  --from-file=gateway_token_bucket.py=app/shared/gateway_token_bucket.py \
	  --from-file=check_domain_reputation.py=app/safety/check_domain_reputation.py \
	  --from-file=truncate_payload_border.py=app/features/truncate_payload_border.py \
	  --from-file=preflight_summarize.py=app/features/preflight_summarize.py \
	  --dry-run=client -o yaml | kubectl apply -f -

configmap-kanban-api:
	@echo "==> ConfigMap kanban-api-scripts..."
	@kubectl create configmap kanban-api-scripts -n ai-agents \
	  --from-file=kanban_api.py=app/core/kanban_api.py \
	  --from-file=issue_state.py=app/shared/issue_state.py \
	  --from-file=kanban_db.py=app/core/kanban_db.py \
	  --from-file=kanban_event_publisher.py=app/core/kanban_event_publisher.py \
	  --dry-run=client -o yaml | kubectl apply -f -

kanban-image:
	@echo "==> Build kanban-ui:local (Minikube Docker)..."
	eval $$(minikube docker-env) && docker build -t kanban-ui:v8 kanban-ui
	@echo "==> kanban-ui:local concluído."

kanban-apply: configmap-kanban-api kanban-image
	@echo "==> Aplicando k8s/kanban/..."
	kubectl apply -f $(K8S_DIR)/kanban/
	@echo "==> Kanban aplicado."

kanban-url:
	@IP=$$(minikube ip); \
	echo "==> Kanban UI:  http://$$IP:32000"; \
	echo "==> Kanban API: http://$$IP:32001"

configmap-devops-compact:
	@echo "==> ConfigMap devops-compact-script..."
	@kubectl create configmap devops-compact-script -n ai-agents \
	  --from-file=compact_preserve_protected.py=app/features/compact_preserve_protected.py \
	  --dry-run=client -o yaml | kubectl apply -f -

configmap-acefalo:
	@echo "==> ConfigMap acefalo-scripts..."
	@kubectl create configmap acefalo-scripts -n ai-agents \
	  --from-file=acefalo_redis.py=app/contingency/acefalo_redis.py \
	  --from-file=acefalo_contingency.py=app/contingency/acefalo_contingency.py \
	  --from-file=acefalo_retomada.py=app/contingency/acefalo_retomada.py \
	  --from-file=acefalo_heartbeat_writer.py=app/contingency/acefalo_heartbeat_writer.py \
	  --from-file=acefalo_monitor.py=app/contingency/acefalo_monitor.py \
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
configmaps-phase2: configmap-rotation configmap-url-sandbox configmap-url-sandbox-trigger configmap-quarantine configmap-gateway-adapter
	@echo "==> ConfigMaps de segurança aplicados."

configmap-rotation:
	@echo "==> ConfigMap rotation-scripts..."
	@kubectl create configmap rotation-scripts -n ai-agents \
	  --from-file=rotate_gateway_token.py=app/safety/rotate_gateway_token.py \
	  --dry-run=client -o yaml | kubectl apply -f -

configmap-url-sandbox:
	@echo "==> ConfigMap url-sandbox-scripts..."
	@kubectl create configmap url-sandbox-scripts -n ai-agents \
	  --from-file=url_sandbox_fetch.py=app/safety/url_sandbox_fetch.py \
	  --dry-run=client -o yaml | kubectl apply -f -

configmap-url-sandbox-trigger:
	@echo "==> ConfigMap url-sandbox-trigger-scripts..."
	@kubectl create configmap url-sandbox-trigger-scripts -n ai-agents \
	  --from-file=url_sandbox_trigger.py=app/safety/url_sandbox_trigger.py \
	  --dry-run=client -o yaml | kubectl apply -f -

configmap-quarantine:
	@echo "==> ConfigMap quarantine-pipeline-scripts..."
	@kubectl create configmap quarantine-pipeline-scripts -n ai-agents \
	  --from-file=quarantine_pipeline.py=app/safety/quarantine_pipeline.py \
	  --from-file=quarantine_entropy.py=app/safety/quarantine_entropy.py \
	  --from-file=trusted_package_verify.py=app/safety/trusted_package_verify.py \
	  --dry-run=client -o yaml | kubectl apply -f -

# ------------------------------------------------------------------------------
# Security apply (security/)
# ------------------------------------------------------------------------------
security-configmaps: configmaps-phase2

# APLICA SEGURANÇA: Coloca em prática as politicas de proteção e quarentena do sistema.
security-apply: security-configmaps
	@echo "==> Aplicando k8s/security/..."
	@kubectl apply -f $(K8S_DIR)/security/
	@echo "==> Segurança configurada."

# ------------------------------------------------------------------------------
# ConfigMaps — Orchestrator (Slack consumer, digest, cosmetic)
# ------------------------------------------------------------------------------
configmaps-orchestrator: orchestrator-configmap

orchestrator-configmap:
	@echo "==> ConfigMap orchestrator-scripts..."
	@kubectl create configmap orchestrator-scripts -n ai-agents \
	  --from-file=orchestration.py=app/core/orchestration.py \
	  --from-file=slack_notify.py=app/shared/slack_notify.py \
	  --from-file=consumer_orchestrator_events_slack.py=app/core/consumer_orchestrator_events_slack.py \
	  --from-file=arbitrage_cloud.py=app/core/arbitrage_cloud.py \
	  --from-file=digest_daily.py=app/features/digest_daily.py \
	  --from-file=cosmetic_omission.py=app/features/cosmetic_omission.py \
	  --from-file=set_consensus_pilot_result.py=app/features/set_consensus_pilot_result.py \
	  --dry-run=client -o yaml | kubectl apply -f -

# APLICA ORQUESTRADOR: Coloca em prática o coordenador que notifica e organiza as rotinas.
orchestrator-apply: orchestrator-configmap
	@echo "==> Aplicando k8s/orchestrator/..."
	@kubectl apply -f $(K8S_DIR)/orchestrator/
	@echo "==> Orquestrador aplicado."

# ------------------------------------------------------------------------------
# Utilitários
# ------------------------------------------------------------------------------
# TESTA HARDWARE: Roda scripts para checar se seu computador e placa de vídeo dão conta do recado.
verify:
	@docs/scripts/verify-machine.sh
	@docs/scripts/verify-gpu-cluster.sh

# COMO ESTÃO AS COISAS?: Mostra a situação atual dos serviços rodando.
status:
	@echo "==> Minikube..."
	@minikube status 2>/dev/null || true
	@echo ""
	@echo "==> Pods (ai-agents)..."
	@kubectl get pods -n ai-agents -o wide 2>/dev/null || true
	@echo ""
	@echo "==> Deployments..."
	@kubectl get deployments -n ai-agents 2>/dev/null || true
	@echo ""
	@echo "==> Services..."
	@kubectl get svc -n ai-agents 2>/dev/null || true

# LÊ OS DIÁRIOS: Mostra as saídas de texto mais recentes dos agentes rodando no momento.
status-pods:
	@echo "==> Redis (tail 5)..."
	@kubectl logs -n ai-agents deployment/redis --tail=5 2>/dev/null || true
	@echo ""
	@echo "==> OpenClaw (tail 5)..."
	@kubectl logs -n ai-agents deployment/openclaw --tail=5 2>/dev/null || true
	@echo ""
	@echo "==> Ollama (tail 5)..."
	@kubectl logs -n ai-agents deployment/ollama-gpu --tail=5 2>/dev/null || true
	@echo ""
	@echo "==> Revisão pós-Dev (tail 5)..."
	@kubectl logs -n ai-agents deployment/revisao-pos-dev --tail=5 2>/dev/null || true
	@echo ""
	@echo "==> Slack events consumer (tail 5)..."
	@kubectl logs -n ai-agents deployment/slack-events-consumer --tail=5 2>/dev/null || true

# AMNÉSIA: Apaga a memória dos agentes do sistema.
reset-memory:
	@$(CURDIR)/scripts/reset_agent_memory.sh

# INICIALIZA MEMÓRIA: Cria estrutura de memória por domínio (decisions/projects/lessons/pending)
# para todos os agentes e shared/memory/ cross-agent. Roda uma vez após 'make up'.
init-memory:
	@echo "==> Aplicando ConfigMap de scripts de init-memory..."
	@kubectl apply -f $(K8S_DIR)/management-team/openclaw/init-memory-configmap.yaml
	@echo "==> Removendo Job anterior (se existir)..."
	@kubectl delete job init-memory-structure -n ai-agents --ignore-not-found=true
	@echo "==> Rodando Job init-memory-structure..."
	@kubectl apply -f $(K8S_DIR)/management-team/openclaw/init-memory-job.yaml
	@echo "  Aguardando conclusão (timeout 120s)..."
	@kubectl wait --for=condition=complete job/init-memory-structure -n ai-agents --timeout=120s \
		&& echo "==> init-memory concluído com sucesso." \
		|| (kubectl logs -n ai-agents -l component=init-memory --tail=30 2>/dev/null; echo "ERRO: job falhou. Veja logs acima."; exit 1)

# CONEXÃO COM GITHUB: Confirma se o sistema consegue acessar repósitórios sem problemas.
test-github-access:
	@$(CURDIR)/scripts/test_github_access.sh $(or $(MODE),all)

# TELA DE CONTROLE: Abre uma página web para visualizar graficamente todos os componentes do sistema.
dashboard:
	@minikube addons enable dashboard 2>/dev/null || true
	@minikube dashboard

# PASTA COMPARTILHADA: Cria um acesso direto no seu PC para a pasta onde os agentes guardam arquivos.
# Usa --uid=0 --gid=0 porque o container do OpenClaw roda como root; sem isso dá I/O error.
shared:
	@echo "==> Montando workspace compartilhado no Minikube (uid=0, gid=0)..."
	@mkdir -p ~/clawdevs-shared
	@for pid in $$(pgrep -x minikube 2>/dev/null); do \
		if grep -q 'mount.*agent-shared' /proc/$$pid/cmdline 2>/dev/null; then \
			kill $$pid 2>/dev/null || true; \
		fi; \
	done
	@sleep 1
	@nohup minikube mount ~/clawdevs-shared:/agent-shared --uid=0 --gid=0 > ~/minikube-mount.log 2>&1 &
	@sleep 3
	@if pgrep -x minikube > /dev/null 2>&1 && grep -q "Successfully mounted" ~/minikube-mount.log 2>/dev/null; then \
		echo "==> Mount ativo (uid=0, gid=0). Logs em ~/minikube-mount.log"; \
	else \
		echo "ERRO: minikube mount não iniciou. Verifique ~/minikube-mount.log"; exit 1; \
	fi

# VERIFICA MOUNT: Garante que o minikube mount está rodando; se não, inicia automaticamente.
# Chamado por 'make up' para evitar I/O errors no workspace.
shared-ensure:
	@if pgrep -x minikube > /dev/null 2>&1 && grep -q "Successfully mounted" ~/minikube-mount.log 2>/dev/null; then \
		echo "  Mount /agent-shared já está ativo."; \
	else \
		echo "  Mount /agent-shared não encontrado. Iniciando..."; \
		$(MAKE) shared; \
	fi

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
	@kubectl patch configmap security-config -n ai-agents -p '{"data":{"URL_SANDBOX_TARGET":"$(URL)"}}'
	@kubectl delete job url-sandbox -n ai-agents --ignore-not-found=true
	@kubectl apply -f $(K8S_DIR)/security/job-url-sandbox.yaml
	@echo "Acompanhe: kubectl logs -f job/url-sandbox -n ai-agents"

url-sandbox-trigger-apply: configmap-url-sandbox-trigger
	@kubectl apply -f $(K8S_DIR)/security/url-sandbox-trigger-rbac.yaml
	@kubectl apply -f $(K8S_DIR)/security/url-sandbox-trigger-deployment.yaml
	@echo "Opcional: kubectl create secret generic url-sandbox-trigger-secret -n ai-agents --from-literal=TRIGGER_SECRET='...'"
