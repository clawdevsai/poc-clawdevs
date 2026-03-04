# ClawDevs — Makefile (apenas delega para scripts .sh)
# Uso: make prepare && make up  |  make down  |  make help
SHELL := /bin/bash
SCRIPTS := $(CURDIR)/scripts
K8S_DIR ?= k8s
MINIKUBE_CPUS ?= 10
MINIKUBE_MEMORY ?= 20g

export K8S_DIR MINIKUBE_CPUS MINIKUBE_MEMORY

.PHONY: help
.PHONY: prepare up down up-all shared shared-ensure
.PHONY: openclaw-image up-management
.PHONY: configmaps-pipeline configmaps-phase2 configmaps-orchestrator
.PHONY: configmap-developer configmap-revisao-slot configmap-agent-slots configmap-gateway-adapter configmap-devops-worker configmap-audit-runner configmap-devops-compact configmap-acefalo
.PHONY: configmap-rotation configmap-url-sandbox configmap-url-sandbox-trigger configmap-quarantine
.PHONY: configmap-po configmap-architect-draft configmap-kanban-api
.PHONY: security-apply security-configmaps orchestrator-apply orchestrator-configmap
.PHONY: kanban-image kanban-apply kanban-url
.PHONY: verify reset-memory init-memory test-github-access validate-finops-po dashboard status status-pods ps
.PHONY: url-sandbox-run url-sandbox-trigger-apply

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
	@echo "    make configmaps-phase2        -> Carrega as instruções avançadas (segurança e rotinas extras)."
	@echo "    make configmaps-orchestrator  -> Carrega as rotinas que avisam no Slack e organizam as tarefas."
	@echo "    make configmap-<nome>          -> Carrega a instrução apenas de um agente específico."
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
	@echo "    make ps                 -> Valida consumo de hardware no K8s (ResourceQuota 65%, uso de nós e pods)."
	@echo "    make reset-memory       -> Apaga a memória das IAs (útil para recomeçar projetos do zero)."
	@echo "    make init-memory        -> Inicializa estrutura de memória (decisions/projects/lessons/pending + .learnings/)."
	@echo "    make test-github-access -> Testa se as IAs conseguem ler arquivos no Github."
	@echo "    make validate-finops-po -> Valida FinOps e validação reversa PO (test_config_finops + validate_reverse_po)."
	@echo "    make dashboard          -> Abre uma tela visual no seu navegador para ver o motor do sistema."
	@echo "    make shared             -> Cria uma pasta compartilhada para você ver os arquivos que a IA cria."

# ------------------------------------------------------------------------------
# Cluster lifecycle
# ------------------------------------------------------------------------------
# Prepara o ambiente: verifica/instala Docker, kubectl e Minikube; inicia o cluster com GPU (MINIKUBE_CPUS/MEMORY).
prepare:
	@$(SCRIPTS)/cluster/prepare.sh

# Sobe o sistema principal: namespace, Redis, Ollama, OpenClaw, ConfigMaps, deployments, init-memory e pipeline. Executa prepare se Minikube não estiver rodando.
up:
	@$(SCRIPTS)/cluster/up.sh

# Sobe tudo: faz make up e em seguida aplica slot Revisão pós-Dev, Redis streams e reinicia orquestrador e revisão.
up-all:
	@$(SCRIPTS)/cluster/up-all.sh

# Desliga e remove todos os recursos do ClawDevs no cluster (deployments, PVCs, namespace ai-agents).
down:
	@$(SCRIPTS)/cluster/down.sh

# ------------------------------------------------------------------------------
# OpenClaw
# ------------------------------------------------------------------------------
# Constrói a imagem Docker openclaw-gateway:local no Docker do Minikube (para rodar o gateway no cluster).
openclaw-image:
	@$(SCRIPTS)/openclaw/image.sh

# Aplica apenas o Management Team (CEO e PO): workspace ConfigMaps e deployment. Use se quiser scale openclaw a 0 e rodar outro gateway.
up-management:
	@$(SCRIPTS)/openclaw/up-management.sh

# ------------------------------------------------------------------------------
# ConfigMaps — Pipeline
# ------------------------------------------------------------------------------
# Cria/atualiza todos os ConfigMaps do pipeline (PO, architect-draft, developer, revisao-slot, devops-worker, audit-runner, gateway-adapter).
configmaps-pipeline:
	@$(SCRIPTS)/configmaps/pipeline.sh

# ConfigMap com scripts do agente PO (po_worker, gpu_lock, issue_state, openclaw_gateway_call).
configmap-po:
	@$(SCRIPTS)/configmaps/po.sh

# ConfigMap com scripts do consumidor Architect-draft (architect_draft_consumer e dependências).
configmap-architect-draft:
	@$(SCRIPTS)/configmaps/architect-draft.sh

# ConfigMap com scripts do Developer (developer_worker, gpu_lock, openclaw_gateway_call).
configmap-developer:
	@$(SCRIPTS)/configmaps/developer.sh

# ConfigMap com scripts do slot Revisão pós-Dev (slot_revisao_pos_dev, orchestration, architect_fallback, microadr, acefalo_redis).
configmap-revisao-slot:
	@$(SCRIPTS)/configmaps/revisao-slot.sh

# ConfigMap com scripts do worker DevOps (devops_worker e dependências).
configmap-devops-worker:
	@$(SCRIPTS)/configmaps/devops-worker.sh

# ConfigMap com scripts do audit runner (audit_runner e dependências).
configmap-audit-runner:
	@$(SCRIPTS)/configmaps/audit-runner.sh

# ConfigMap do gateway Redis adapter (gateway_redis_adapter, token_bucket, check_domain_reputation, truncate_payload, preflight_summarize).
configmap-gateway-adapter:
	@$(SCRIPTS)/configmaps/gateway-adapter.sh

# ConfigMap da API do Kanban (kanban_api, issue_state, kanban_db, kanban_event_publisher).
configmap-kanban-api:
	@$(SCRIPTS)/configmaps/kanban-api.sh

# ConfigMap do script de compactação segura (compact_preserve_protected) usado pelo DevOps.
configmap-devops-compact:
	@$(SCRIPTS)/configmaps/devops-compact.sh

# ConfigMap dos scripts de contingência Acefalo (acefalo_redis, contingency, retomada, heartbeat, monitor).
configmap-acefalo:
	@$(SCRIPTS)/configmaps/acefalo.sh

# ConfigMap legado dos agent-slots (deprecated; usar revisao-pos-dev).
configmap-agent-slots:
	@$(SCRIPTS)/configmaps/agent-slots.sh

# ------------------------------------------------------------------------------
# ConfigMaps — Phase2 (segurança)
# ------------------------------------------------------------------------------
# Cria/atualiza ConfigMaps de segurança: rotation, url-sandbox, url-sandbox-trigger, quarantine e gateway-adapter.
configmaps-phase2:
	@$(SCRIPTS)/configmaps/phase2.sh

# ConfigMap do script de rotação de tokens do gateway (rotate_gateway_token).
configmap-rotation:
	@$(SCRIPTS)/configmaps/rotation.sh

# ConfigMap do fetch em sandbox para URLs (url_sandbox_fetch).
configmap-url-sandbox:
	@$(SCRIPTS)/configmaps/url-sandbox.sh

# ConfigMap do trigger do url-sandbox (url_sandbox_trigger).
configmap-url-sandbox-trigger:
	@$(SCRIPTS)/configmaps/url-sandbox-trigger.sh

# ConfigMap do pipeline de quarentena (quarantine_pipeline, quarantine_entropy, trusted_package_verify).
configmap-quarantine:
	@$(SCRIPTS)/configmaps/quarantine.sh

# ------------------------------------------------------------------------------
# Security
# ------------------------------------------------------------------------------
# Prepara os ConfigMaps de segurança (phase2) sem aplicar os recursos em k8s/security/.
security-configmaps:
	@$(SCRIPTS)/security/configmaps.sh

# Prepara ConfigMaps de segurança e aplica todos os recursos em k8s/security/ (jobs, CronJobs, RBAC, etc.).
security-apply:
	@$(SCRIPTS)/security/apply.sh

# ------------------------------------------------------------------------------
# Orchestrator
# ------------------------------------------------------------------------------
# Cria/atualiza o ConfigMap orchestrator-scripts (orchestration, slack_notify, consumer Slack, digest, cosmetic, consensus, disjuntor, rag_health_check).
orchestrator-configmap:
	@$(SCRIPTS)/orchestrator/configmap.sh

# Alias: mesmo que orchestrator-configmap.
configmaps-orchestrator: orchestrator-configmap

# Prepara o ConfigMap do orquestrador e aplica os recursos em k8s/orchestrator/ (deployments, CronJobs).
orchestrator-apply:
	@$(SCRIPTS)/orchestrator/apply.sh

# ------------------------------------------------------------------------------
# Kanban
# ------------------------------------------------------------------------------
# Constrói a imagem Docker kanban-ui:v8 no Docker do Minikube.
kanban-image:
	@$(SCRIPTS)/kanban/image.sh

# Cria ConfigMap kanban-api, constrói a imagem e aplica os recursos em k8s/kanban/.
kanban-apply:
	@$(SCRIPTS)/kanban/apply.sh

# Mostra as URLs do Kanban UI e da API no navegador (baseado no IP do Minikube).
kanban-url:
	@$(SCRIPTS)/kanban/url.sh

# ------------------------------------------------------------------------------
# Utilitários
# ------------------------------------------------------------------------------
# Verifica se o hardware (máquina e GPU no cluster) atende ao sistema (scripts em docs/02-infra/scripts/).
verify:
	@$(SCRIPTS)/utils/verify.sh

# Mostra resumo do estado: Minikube, pods, deployments e services no namespace ai-agents.
status:
	@$(SCRIPTS)/utils/status.sh

# Mostra as últimas linhas de log (tail) dos pods principais: Redis, OpenClaw, Ollama, Revisão pós-Dev, Slack consumer.
status-pods:
	@$(SCRIPTS)/utils/status-pods.sh

# Valida consumo de hardware no K8s: ResourceQuota (limite 65%), uso real de nós e pods (requer metrics-server para top).
ps:
	@$(SCRIPTS)/utils/ps.sh

# Apaga a memória dos agentes: remove chaves project:v1:* no Redis e reinicia o deployment openclaw para reaplicar workspace.
reset-memory:
	@$(SCRIPTS)/utils/reset-memory.sh

# Roda o Job init-memory-structure: cria a estrutura de pastas de memória (decisions, projects, lessons, pending, .learnings) no workspace.
init-memory:
	@$(SCRIPTS)/utils/init-memory.sh

# Testa acesso ao GitHub: no host (.env) e/ou nos pods (secret clawdevs-github-secret). Use MODE=host|cluster|all (default: all).
test-github-access:
	@$(SCRIPTS)/utils/test-github-access.sh $(or $(MODE),all)

# Roda a validação FinOps (test_config_finops) e a validação reversa PO (validate_reverse_po com critérios de aceite).
validate-finops-po:
	@$(SCRIPTS)/utils/validate-finops-po.sh

# Habilita e abre o dashboard do Minikube no navegador (visão gráfica do cluster).
dashboard:
	@$(SCRIPTS)/utils/dashboard.sh

# Monta a pasta ~/clawdevs-shared no Minikube como /agent-shared (uid=0) para ver arquivos criados pelos agentes.
shared:
	@$(SCRIPTS)/utils/shared.sh

# Garante que o mount /agent-shared está ativo; se não estiver, executa make shared. Chamado internamente por make up.
shared-ensure:
	@$(SCRIPTS)/utils/shared-ensure.sh

# Dispara o job url-sandbox para analisar uma URL. Obrigatório: URL=https://exemplo.com make url-sandbox-run.
url-sandbox-run:
	@URL="$(URL)" $(SCRIPTS)/utils/url-sandbox-run.sh

# Aplica o ConfigMap url-sandbox-trigger e os recursos (RBAC + deployment) do trigger no namespace.
url-sandbox-trigger-apply:
	@$(SCRIPTS)/utils/url-sandbox-trigger-apply.sh

# ------------------------------------------------------------------------------
# Aliases (compatibilidade com nomes antigos)
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
