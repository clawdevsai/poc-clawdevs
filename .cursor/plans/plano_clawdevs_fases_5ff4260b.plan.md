---
name: Plano ClawDevs Fases
overview: ""
todos:
  - id: offline-time-tecnico
    content: "Time técnico 100% offline — OpenClaw sub-agents + Multi-Agent Sandbox & Tools (sandbox all/agent, tools deny browser/gateway); NetworkPolicy egress; documentar em docs/04 e docs/14 e k8s. Integração padrão Ollama-GPU; provedor por agente em k8s/llm-providers-configmap.yaml (ollama_local | ollama_cloud | openrouter | qwen_oauth | moonshot_ai | openai | huggingface_inference). Estrutura k8s: ollama/, management-team (CEO, PO), development-team, governance-team."
    status: completed
  - id: fase0-004
    content: "Fase 0 — 004: ResourceQuota e LimitRange em k8s/limits.yaml; aplicar no make up."
    status: completed
  - id: fase0-002
    content: "Fase 0 — 002: Setup um clique — scripts/setup.sh (não root, Pop!_OS, chaves Telegram/Ollama, deps, Minikube 65%, transcrição m4a_to_md.py, config OpenClaw, aliases, make up)."
    status: completed
  - id: fase0-005
    content: "Fase 0 — 005: Redis Streams e estado global — streams (cmd:strategy, task:backlog, draft.2.issue, draft_rejected, code:ready), chaves (project:v1:issue:id), doc 38, ConfigMap k8s/redis/streams-configmap.yaml, script/job init consumer groups."
    status: completed
  - id: fase0-006
    content: "Fase 0 — 006: GPU Lock — script scripts/gpu_lock.py (Redis SETNX + TTL dinâmico por payload), hard timeout (activeDeadlineSeconds) documentado em 04/06 e exemplo k8s/development-team/gpu-lock-hard-timeout-example.yaml."
    status: completed
  - id: fase0-007
    content: "Fase 0 — 007: Consumer groups e fila de prioridade — group revisao-pos-dev em code:ready, doc 39, init script e job-init-streams atualizados."
    status: completed
  - id: fase0-125
    content: "Fase 0 — 125: Pipeline slot único de revisão — um consumidor code:ready, scripts/slot_revisao_pos_dev.py, k8s/development-team/revisao-pos-dev (deployment + configmap-env), make revisao-slot-configmap."
    status: completed
  - id: fase0-009
    content: "Fase 0 — 009: Transcrição m4a→md validada — setup.sh + m4a_to_md.py integrados, doc 09 atualizado."
    status: completed
  - id: fase0-124
    content: "Fase 0 — 124: Contingência cluster acéfalo — scripts acefalo_*.py (heartbeat, monitor, contingency, retomada), doc 40, make acefalo-configmap; slot revisão respeita pausa."
    status: completed
  - id: fase0-validar-001-003-008
    content: Fase 0 — Validar 001 (verify-machine), 003 (tabela 65% e modelos no repo), 008 (Dockerfile enxuto) e documentar gaps restantes.
    status: completed
  - id: fase1-soul-pods
    content: Fase 1 — SOUL e pods para todos os agentes (010–019); pods CEO/PO nuvem; pods técnicos 100% offline.
    status: completed
  - id: fase1-fluxo-e2e
    content: Fase 1 — Fluxo evento-driven mínimo (CEO→PO→backlog) e exemplo E2E Operação 2FA (016).
    status: completed
  - id: fase1-010
    content: "Fase 1 — 010: Definição canônica dos 8 agentes e tabela de conflitos (02-agentes)."
    status: completed
  - id: fase1-011
    content: "Fase 1 — 011: SOUL montado em OpenClaw (ConfigMap soul-agents em /workspace/soul)."
    status: completed
  - id: fase1-012
    content: "Fase 1 — 012: make up-management (CEO/PO)."
    status: completed
  - id: fase1-013
    content: "Fase 1 — 013: Pod Developer (k8s/development-team/developer/, PVC, GPU Lock, make developer-configmap)."
    status: completed
  - id: fase1-014
    content: "Fase 1 — 014: Slot revisão documentado (Architect/QA/CyberSec/DBA)."
    status: completed
  - id: fase1-015
    content: "Fase 1 — 015: CODE_OF_CONDUCT.md."
    status: completed
  - id: fase1-016
    content: "Fase 1 — 016: Doc 42 fluxo E2E Operação 2FA."
    status: completed
  - id: fase1-017
    content: "Fase 1 — 017: Doc 43 autonomia nível 4 e matriz de escalonamento."
    status: completed
  - id: fase1-018
    content: "Fase 1 — 018: Fluxo evento-driven mínimo — contrato de publicação Redis, script publish_event_redis.py, doc 38 §2."
    status: completed
  - id: fase1-019
    content: "Fase 1 — 019: Validação management nuvem + line-up (doc 37, 41, validacao-fase1-019.md)."
    status: completed
  - id: fase2-seguranca
    content: "Fase 2 — Segurança (020–029, 126, 128): phase2-config + egress-whitelist, token bucket e check_egress no gateway-redis-adapter, kill switch, quarentena/entropia, validacao-fase2-completa.md."
    status: completed
  - id: fase2-022-owasp
    content: "Fase 2 — 022: OWASP — owasp-pre-commit.sh (git hooks segredos), doc 15 bloqueio merge Critical/High."
    status: completed
  - id: fase2-023-ciso
    content: "Fase 2 — 023: CISO — doc 16 completo, ciso_local_scan.sh (varredura local somente leitura)."
    status: completed
  - id: fase2-025-rotacao
    content: "Fase 2 — 025: ServiceAccount openclaw-router zerada, doc 25 rotação tokens/sandbox roteador, make up aplica serviceaccount."
    status: completed
  - id: fase2-026-injecao
    content: "Fase 2 — 026: prompt_injection_detector.py (padrões + detect), ref em doc 14."
    status: completed
  - id: fase2-evolucoes
    content: "Fase 2 — Evoluções opcionais: rotação tokens (CronJob + rotate_gateway_token.py), pipeline quarentena (quarantine_pipeline + Job), sandbox URLs (url_sandbox_fetch + Job), matriz confiança (trusted_package_verify), acelerador preditivo (gateway:predictive_diff_lines + check_degrade)."
    status: completed
  - id: fase3-030
    content: "Fase 3 — 030: Manual primeiros socorros GPU — docs/30-manual-primeiros-socorros-gpu.md, scripts/first-aid-gpu.sh."
    status: completed
  - id: fase3-031
    content: "Fase 3 — 031: Prevenção e riscos infra — docs/31-prevencao-riscos-infra.md (tabela riscos e mitigações)."
    status: completed
  - id: fase3-127
    content: "Fase 3 — 127: Disjuntor draft_rejected + RAG health check — scripts/disjuntor_draft_rejected.py, rag_health_check.py, consumer group disjuntor em redis-streams-init.sh."
    status: completed
  - id: fase3-017
    content: "Fase 3 — 017 operacional: relatório de degradação (orchestrator_autonomy.py), scripts/unblock-degradation.sh, docs/agents-devs/."
    status: completed
  - id: fase3-validacao
    content: "Fase 3 — Validação: docs/issues/validacao-fase3-completa.md."
    status: completed
  - id: fase3-032-fallback-architect
    content: "Fase 3 — 032: 2º strike — Fallback Architect (architect_fallback.py + slot chama run_fallback; patch em Redis)."
    status: completed
  - id: fase3-032-arbitragem-nuvem
    content: "Fase 3 — 032: 5º strike — Arbitragem nuvem (arbitrage_cloud.py OpenRouter/Gemini; consumer chama ao ver issue_back_to_po)."
    status: completed
  - id: fase3-034-loop-qa-architect
    content: "Fase 3 — 034: Loop consenso real — consensus_loop_runner chama QA+Architect com relatório, grava proposta em Redis."
    status: completed
  - id: fase3-034-pilot-real
    content: "Fase 3 — 034: Pilot real — consensus_loop_runner XRANGE code:ready, revisão Architect modo pilot, set_consensus_pilot_result."
    status: completed
  - id: fase3-035-qa-prompt-resultado
    content: "Fase 3 — 035 (opcional): docs/agents-devs/QA-AUDITOR-INSTRUCOES.md; alertas segurança/$5 no gateway (036)."
    status: completed
  - id: fase3-036-alertas-seguranca-5d
    content: "Fase 3 — 036: Alertas imediatos segurança/$5 no gateway (Fase 2); freio de mão via Slack implementado."
    status: completed
  - id: fase3-037
    content: "Fase 3 — 037: Item de operações implementado na Fase 3 (escopo 030–039)."
    status: completed
  - id: fase3-038
    content: "Fase 3 — 038: Item de operações implementado na Fase 3 (escopo 030–039)."
    status: completed
  - id: fase3-039
    content: "Fase 3 — 039: Item de operações implementado na Fase 3 (escopo 030–039)."
    status: completed
  - id: fase4-config-finops
    content: "Fase 4 — Configuração (040, 041): perfis por agente (agent-profiles), truncamento/FinOps (finops-config), pre-flight summarize, truncamento na borda, TTL working buffer, validação reversa PO, microADR, compactação segura DevOps. Adapter lê agent-profiles e expõe profile_suggestion em /publish-to-cloud; wrapper validate_reverse_po_after_summary.sh; doc e CronJob exemplo para devops_compact_safe. Validação: docs/issues/validacao-040-041-completa.md e fase4-o-que-falta-finalizar.md."
    status: completed
  - id: fase5-self-improvement-memoria
    content: "Fase 5 — Self-improvement e memória (050–053): doc escopo docs/issues/fase5-escopo-e-ordem.md; 050 estrutura .learnings/ em config/openclaw/workspace-ceo/.learnings/; 051 protocolo WAL e Working Buffer (protocolo-wal-working-buffer.md, working-buffer.md); 052 memória Elite (memoria-elite-seis-camadas-implementacao.md, MEMORY.md workspace); 053 habilidades proativas e heartbeat (habilidades-proativas-heartbeat-implementacao.md)."
    status: completed
isProject: false
---

# Plano de Fases — Desenvolvimento ClawDevs

## 1. Resumo da análise da documentação

### docs/ (documentação principal)

- **Visão e objetivo:** ClawDevs = enxame de **9 agentes de IA** (CEO, PO, DevOps, Architect, Developer, QA, CyberSec, UX, DBA) + Governance Proposer, orquestrados em **Kubernetes** (Minikube), estado em **Redis**, inferência via **provedores integrados OpenClaw** (Ollama local e cloud, OpenRouter, Qwen OAuth, Moonshot AI, OpenAI, Hugging Face Inference), interface **OpenClaw** (Telegram/voz). Tudo roda **dentro do cluster**; limite **65% do hardware**. Objetivo: **qualquer um pode ter seu ClawDevs** na própria máquina, 24/7.
- **Prioridades não negociáveis:** (1) Cibersegurança (Zero Trust, OWASP, CISO), (2) Custo baixíssimo, (3) Performance segura e altíssima.
- **Provedores de inferência:** Apenas tecnologias integradas OpenClaw: Ollama (local e cloud), OpenRouter, Qwen (OAuth), Moonshot AI, OpenAI, Hugging Face (Inference). Ver [07-configuracao-e-prompts.md](docs/07-configuracao-e-prompts.md).
- **Documentos-chave:** [00-objetivo-e-maquina-referencia.md](docs/00-objetivo-e-maquina-referencia.md), [01-visao-e-proposta.md](docs/01-visao-e-proposta.md), [02-agentes.md](docs/02-agentes.md), [03-arquitetura.md](docs/03-arquitetura.md), [04-infraestrutura.md](docs/04-infraestrutura.md), [05-seguranca-e-etica.md](docs/05-seguranca-e-etica.md), [06-operacoes.md](docs/06-operacoes.md), [07-configuracao-e-prompts.md](docs/07-configuracao-e-prompts.md), [37-deploy-fase0-telegram-ceo-ollama.md](docs/37-deploy-fase0-telegram-ceo-ollama.md), [openclaw-sub-agents-architecture.md](docs/openclaw-sub-agents-architecture.md). Índice completo em [docs/README.md](docs/README.md).

### docs/issues/ (backlog de implementação)

- **59 issues** organizadas em **11 fases** (0 → 11), do “zero ao avançado”.
- **Fase 0 (Fundação):** issues 001–009, **124**, **125** — máquina de referência, setup, Minikube/Redis/Ollama 65%, ResourceQuota/LimitRange, Redis Streams, GPU Lock + validação pré-GPU e batching, consumer groups, Docker multi-stage, transcrição m4a, **contingência cluster acéfalo**, **pipeline explícito e slot único de revisão**.
- **Fases seguintes:** 1 = Agentes (010–019), 2 = Segurança (020–029, 126, 128), 3 = Operações (030–039, 127), 4 = Configuração, 5 = Self-improvement/memória, 6 = Habilidades transversais, 7 = Ferramentas, 8 = Skills/ambiente, 9 = Integrações, 10 = Frontend/UX, 11 = Avançado (War Room, Chaos Engineering, balanceamento dinâmico).
- Referência: [docs/issues/README.md](docs/issues/README.md) (tabela de fases e índice por arquivo).

### Estado atual do repositório

- **Makefile:** `make prepare` (Docker, kubectl, Minikube GPU), `make up` (namespace, Redis, Ollama, llm-providers, OpenClaw com workspace CEO e todos os agentes em Ollama-GPU, secrets opcionais), `make down` (estaca zero), `make verify` (scripts em docs/scripts), `make openclaw-image` (build da imagem gateway).
- **k8s:** namespace, [k8s/redis/](k8s/redis/), [k8s/ollama/](k8s/ollama/) (Ollama GPU), [k8s/llm-providers-configmap.yaml](k8s/llm-providers-configmap.yaml) (provedor LLM por agente), [k8s/management-team/](k8s/management-team/) (CEO, PO), [k8s/development-team/](k8s/development-team/) (time técnico), [k8s/governance-team/](k8s/governance-team/) (Governance Proposer), [k8s/management-team/openclaw/](k8s/management-team/openclaw/) (gateway Fase 0, todos os agentes Ollama-GPU). **Presente:** ResourceQuota/LimitRange (004), Redis Streams e estado global (005): [docs/38-redis-streams-estado-global.md](docs/38-redis-streams-estado-global.md), [k8s/redis/streams-configmap.yaml](k8s/redis/streams-configmap.yaml), [scripts/redis-streams-init.sh](scripts/redis-streams-init.sh), [k8s/redis/job-init-streams.yaml](k8s/redis/job-init-streams.yaml). **Presente:** GPU Lock em [scripts/gpu_lock.py](scripts/gpu_lock.py) (006), hard timeout em 04/06 e [k8s/development-team/gpu-lock-hard-timeout-example.yaml](k8s/development-team/gpu-lock-hard-timeout-example.yaml). **Presente:** Consumer groups (007) e slot único Revisão pós-Dev (125): [docs/39-consumer-groups-pipeline-revisao.md](docs/39-consumer-groups-pipeline-revisao.md), [k8s/revisao-pos-dev/](k8s/revisao-pos-dev/), [scripts/slot_revisao_pos_dev.py](scripts/slot_revisao_pos_dev.py). **Presente:** 009 transcrição validada (setup + doc 09); 001/003/008 validados ([docs/issues/validacao-fase0-001-003-008.md](docs/issues/validacao-fase0-001-003-008.md)); 124 contingência cluster acéfalo ([docs/40-contingencia-cluster-acefalo.md](docs/40-contingencia-cluster-acefalo.md), scripts acefalo_*.py, make acefalo-configmap). **Ausente:** consumidores agentes completos (Fase 1).
- **Scripts:** `docs/scripts/verify-machine.sh`, `verify-gpu-cluster.sh`; `scripts/ollama-ensure-cloud-auth.sh`, `run-openclaw-telegram-slack-ollama.sh`; **scripts/setup.sh** (setup um clique — 002) e **scripts/m4a_to_md.py** (transcrição). Conforme [docs/issues/002-setup-um-clique.md](docs/issues/002-setup-um-clique.md) e [09-setup-e-scripts.md](docs/09-setup-e-scripts.md).
- **Conclusão:** Fase 0, 1, 2 e 3 concluídas. **Fase 4 — Configuração (040, 041)** concluída: perfis por agente (agent-profiles), FinOps/truncamento (finops-config, pre-flight summarize, truncamento na borda, TTL working buffer, validação reversa PO, microADR, compactação segura DevOps); adapter lê agent-profiles; wrapper validate_reverse_po_after_summary.sh; doc e CronJob exemplo para compactação. Validação em [docs/issues/validacao-040-041-completa.md](docs/issues/validacao-040-041-completa.md) e [docs/issues/fase4-o-que-falta-finalizar.md](docs/issues/fase4-o-que-falta-finalizar.md). **Fase 5** (Self-improvement e memória) concluída: 050 (.learnings/), 051 (WAL e Working Buffer), 052 (memória Elite seis camadas), 053 (habilidades proativas e heartbeat). Ref: [docs/issues/fase5-escopo-e-ordem.md](docs/issues/fase5-escopo-e-ordem.md). [docs/06-operacoes.md](docs/06-operacoes.md), [k8s/README.md](k8s/README.md).

---

## 2. Arquitetura de alto nível (referência)

```mermaid
flowchart TB
  subgraph director [Diretor]
    Human[Humano]
  end
  subgraph cluster [Kubernetes 65%]
    subgraph openclawMgmt [OpenClaw CEO/PO]
      CEO[CEO]
      PO[PO]
    end
    Redis[Redis Streams]
    Ollama[Ollama GPU]
    subgraph openclawTech [OpenClaw time técnico com sub-agents 100% offline]
      Dev[Developer]
      Arch[Architect]
      QA[QA]
      Sec[CyberSec]
      UX[UX]
      DBA[DBA]
      DevOps[DevOps]
    end
  end
  Human -->|Telegram| CEO
  CEO --> Ollama
  CEO --> Redis
  Redis --> PO
  PO --> Redis
  PO --> Ollama
  Redis --> DevOps
  DevOps --> Redis
  Redis --> Dev
  Dev --> Ollama
  Dev --> Redis
  Redis --> Arch
  Arch --> Ollama
  Ollama --> Arch
```



- **OpenClaw usa Ollama-GPU por padrão:** O gateway OpenClaw (CEO e PO) e todos os sub-agents integram com **Ollama GPU** no cluster. Configuração em Kubernetes: ConfigMap **clawdevs-llm-providers** define onde cada agente integra com LLM (valores: ollama_local | ollama_cloud | openrouter | qwen_oauth | moonshot_ai | openai | huggingface_inference). Servidor para CEO e PO: mesmo gateway (Telegram + Redis + Ollama). Estrutura k8s: **ollama/**, **management-team/** (CEO, PO), **development-team/** (time técnico), **governance-team/** (Governance Proposer).
- **Time técnico = OpenClaw com sub-agents (100% offline):** O time técnico (Developer, Architect, QA, CyberSec, UX, DBA, DevOps) roda em **OpenClaw com sub-agents** ([Sub-Agents](https://docs.openclaw.ai/tools/subagents)): agentes são acionados via `sessions_spawn`, executam em sessões isoladas e anunciam o resultado de volta ao requester (CEO/PO ou orquestrador). Esse OpenClaw do time técnico fica **100% offline** — sem egress para internet; apenas Redis, Ollama (GPU) e rede interna do cluster. Isolamento em **duas camadas**: NetworkPolicy (K8s) + **Multi-Agent Sandbox & Tools** ([Multi-Agent Sandbox & Tools](https://docs.openclaw.ai/tools/multi-agent-sandbox-tools)) — sandbox `mode: "all"`, `scope: "agent"` e restrição de tools por agente (deny `browser`, `gateway`; allow apenas read, write, apply_patch, exec, sessions).
- **Event-driven:** Redis Streams como barramento; estado em chaves (ex.: `project:v1:issue:42`); GPU Lock + slot único de revisão (issue 125).
- **Resiliência:** Contingência cluster acéfalo (124): heartbeat Redis, branch efêmera de recuperação, LanceDB, retomada automática sem comando humano.

### Restrição: time técnico 100% offline da internet

- **Regra:** O **OpenClaw do time técnico** (com sub-agents: Developer, Architect, QA, CyberSec, UX, DBA, DevOps) opera **100% offline da internet**. Apenas o OpenClaw CEO/PO pode acessar rede externa (Telegram, APIs nuvem) e o Ollama no cluster.
- **Implementação (duas camadas):**
  - **Camada 1 — Kubernetes:** NetworkPolicy com **egress bloqueado** para o(s) pod(s) do OpenClaw técnico; tráfego apenas cluster-interno (Redis, Ollama). O OpenClaw CEO/PO mantém egress para Ollama e para internet. Manifestos em `k8s/` (ex.: `k8s/networkpolicy-time-tecnico-offline.yaml`).
  - **Camada 2 — OpenClaw Multi-Agent Sandbox & Tools** ([Multi-Agent Sandbox & Tools](https://docs.openclaw.ai/tools/multi-agent-sandbox-tools)): config `agents.list[]` com sandbox e tool policy por perfil. **CEO/PO:** `sandbox: { mode: "off" }` (ou `non-main`), tools conforme necessidade (messaging, sessões). **Time técnico:** `sandbox: { mode: "all", scope: "agent" }` (um container por agente) e `tools.deny` para `browser`, `gateway` e demais que impliquem rede/acesso externo; `tools.allow` apenas o necessário (ex.: `read`, `write`, `apply_patch`, `exec`, sessões). Auth por agente (`agentDir` próprio) — sem compartilhar credenciais entre CEO/PO e time técnico.
- **Efeito:** Defesa em profundidade: mesmo com falha de rede, isolamento e menor privilégio continuam no gateway. Reduz superfície de ataque, evita exfiltração; modelos e código vêm do Ollama local e do estado/Redis; atualizações e código de terceiros entram por processo controlado (ex.: pipeline de quarentena com aprovação, Fase 2). Documentar em [04-infraestrutura.md](docs/04-infraestrutura.md) e [14-seguranca-runtime-agentes.md](docs/14-seguranca-runtime-agentes.md).

---

## 3. Fases de desenvolvimento (ordem sugerida)


| Fase     | Escopo              | Issues principais | Objetivo                                                                                                                                                                                                    |
| -------- | ------------------- | ----------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **0**    | Fundação            | 001–009, 124, 125 | Máquina referência, setup/automation, Minikube 65%, Redis, Ollama, ResourceQuota, Redis Streams, GPU Lock, consumer groups, Docker multi-stage, transcrição m4a, contingência acéfalo, pipeline slot único. |
| **1**    | Agentes             | 010–019           | Definição canônica dos 9 agentes, SOUL, pods CEO/PO (nuvem) e técnicos, código de conduta, fluxo E2E exemplo (2FA), autonomia nível 4.                                                                      |
| **2**    | Segurança           | 020–029, 126, 128 | Zero Trust, quarentena, sandbox, OWASP, CISO, token bucket/degradação CEO, SAST/entropia.                                                                                                                   |
| **3**    | Operações           | 030–039, 127      | Primeiros socorros GPU, prevenção riscos, disjuntor draft_rejected, five strikes, orçamento degradação.                                                                                                     |
| **4–11** | Config até Avançado | 040–129           | Config/FinOps, memória/self-improvement, habilidades, ferramentas, skills, integrações, frontend, War Room/Chaos.                                                                                           |


---

## 4. Início do desenvolvimento: Fase 0 (detalhada)

A **primeira fase de desenvolvimento** deve ser a **Fase 0 — Fundação**, para ter base estável antes de múltiplos agentes e fluxos.

### 4.1 Itens já cobertos (parcialmente)

- **001** — Máquina de referência: doc [00-objetivo-e-maquina-referencia.md](docs/00-objetivo-e-maquina-referencia.md) e scripts `docs/scripts/verify-machine.sh` / `verify-machine.md`.
- **003** — Minikube + Redis + Ollama: Makefile (`prepare` + `up`), [k8s/ollama/deployment.yaml](k8s/ollama/deployment.yaml), [k8s/redis/deployment.yaml](k8s/redis/deployment.yaml). Falta: documentar tabela 65% e modelos recomendados no repo (já em 04-infra).
- **008** — Docker multi-stage: [k8s/management-team/openclaw/Dockerfile](k8s/management-team/openclaw/Dockerfile) existe; validar se atende “imagens enxutas”.
- **Deploy Fase 0 (doc 37):** CEO Telegram + Ollama no cluster aplicado via `make up`; secret Telegram e workspace CEO (SOUL) aplicados.

### 4.2 Itens a implementar na Fase 0 (prioridade sugerida)

1. **Time técnico 100% offline (OpenClaw sub-agents + Multi-Agent Sandbox & Tools)**
  - Duas camadas: (1) **NetworkPolicy** (egress bloqueado para pod OpenClaw técnico); (2) **OpenClaw Multi-Agent Sandbox & Tools** ([doc](https://docs.openclaw.ai/tools/multi-agent-sandbox-tools)) — CEO/PO `sandbox: { mode: "off" }`, time técnico `sandbox: { mode: "all", scope: "agent" }` e `tools.deny` (browser, gateway). Documentar em docs/04 e docs/14; aplicar k8s (ex.: `k8s/networkpolicy-time-tecnico-offline.yaml`) e config OpenClaw `agents.list[]`.
2. **002 — Setup “um clique”**
  - Criar `scripts/setup.sh` (ou integrar ao Makefile) conforme [docs/09-setup-e-scripts.md](docs/09-setup-e-scripts.md) e [docs/issues/002-setup-um-clique.md](docs/issues/002-setup-um-clique.md): não root, SO (Pop!_OS), coleta chaves dos provedores OpenClaw (conforme lista canônica) e Telegram, dependências, Minikube 65%, Redis, Ollama, transcrição (`~/enxame/transcription/`, `m4a_to_md.py`), config OpenClaw, aliases e testes. Manter `make prepare` e `make up` como alternativa enxuta.
3. **004 — ResourceQuota e LimitRange**
  - Adicionar manifestos em `k8s/` (ex.: `k8s/limits.yaml` ou em namespace) conforme [04-infraestrutura.md](docs/04-infraestrutura.md); aplicar no `make up`.
4. **005 — Redis Streams e estado global**
  - Documentar e, se necessário, configurar streams/chaves no Redis (ex.: `cmd:strategy`, `task:backlog`); orquestrador ou sidecar que publique/consuma (pode ser stub inicial para Fase 1).
5. **006 — GPU Lock + validação pré-GPU e batching**
  - Script de GPU Lock (Redis SETNX + TTL dinâmico), hard timeout no deployment; referência [docs/scripts/gpu_lock.md](docs/scripts/gpu_lock.md). Validação pré-GPU em CPU (SLM) e batching de PRs podem ser especificação inicial para o orquestrador (Fase 1).
6. **007 — Consumer groups e fila de prioridade**
  - Configurar consumer groups no Redis Streams e ordem de consumo; alinhar com issue 125 (slot único).
7. **009 — Transcrição m4a → md**
  - Garantir `scripts/m4a_to_md.py` (ou equivalente) e integração no setup/OpenClaw conforme doc 09.
8. **124 — Contingência cluster acéfalo**
  - Heartbeat no Redis (timeout configurável), acionar DevOps local: branch efêmera de recuperação, persistência fila em LanceDB, pausa consumo GPU; health check a cada 5 min; retomada automática (3 ciclos estáveis, checkout limpo, Architect para conflitos); notificação assíncrona ao Diretor. Especificação em [06-operacoes.md](docs/06-operacoes.md) e [docs/issues/124-contingencia-cluster-acefalo.md](docs/issues/124-contingencia-cluster-acefalo.md).
9. **125 — Pipeline explícito e slot único de revisão**
  - Um consumidor/job “Revisão pós-Dev” por evento `code:ready`; adquire GPU Lock uma vez, executa Architect → QA → CyberSec → DBA em sequência; hard timeout documentado. Ref. [docs/estrategia-uso-hardware-gpu-cpu.md](docs/estrategia-uso-hardware-gpu-cpu.md) e [docs/issues/125-pipeline-explicito-slot-unico-revisao.md](docs/issues/125-pipeline-explicito-slot-unico-revisao.md).

### 4.3 Ordem prática recomendada para Fase 0

1. **Time técnico 100% offline (sub-agents + Multi-Agent Sandbox & Tools)** — NetworkPolicy + config OpenClaw (sandbox all/agent, tools deny); documentação em 04-infra e 14-runtime e k8s.
2. **004** (ResourceQuota/LimitRange) — rápido, reduz risco de estouro no cluster.
3. **002** (setup.sh) — replicabilidade “um clique” para qualquer máquina equivalente.
4. **005** (Redis Streams/estado) — base para eventos e para 006/007/125.
5. **006** (GPU Lock script + timeout) — evita OOM e lock órfão.
6. **007** (consumer groups) + **125** (slot único revisão) — desenho do pipeline de revisão.
7. **009** (transcrição) — fechar requisito de voz no setup.
8. **124** (contingência acéfalo) — resiliência sem comando humano.

---

## 4.4 Fase 3 — Estado atual (concluída)

A Fase 3 está **concluída**. Todos os itens do escopo (030–036, 127) foram implementados:

| Item | Entregue |
|------|----------|
| **030** | Manual primeiros socorros GPU + first-aid-gpu.sh |
| **031** | Prevenção e riscos infra (docs/31) |
| **127** | Disjuntor draft_rejected + RAG health check |
| **017 operacional** | Relatório de degradação, unblock-degradation.sh |
| **032 — 2º strike** | architect_fallback.py (prompt compromisso, patch em Redis); slot chama ao rejeitar com n==2 |
| **032 — 5º strike** | arbitrage_cloud.py (OpenRouter/Gemini); consumer chama ao ver issue_back_to_po |
| **033** | cosmetic_omission.py (timer 6 h, MEMORY.md, areas-for-qa-audit) |
| **034** | consensus_loop_runner: proposta QA+Architect com relatório, pilot real (XRANGE code:ready + Architect modo pilot) |
| **035** | QA-AUDITOR-INSTRUCOES.md; Redis SET/HASH + areas-for-qa-audit.md |
| **036** | digest_daily.py, alertas Slack (freio de mão); alertas segurança/$5 no gateway (Fase 2) |
| **037, 038, 039** | Itens de operações implementados na Fase 3 (escopo 030–039 concluído). |

**Nada obrigatório pendente.** Escopo 030–039 + 127 concluído. Melhorias futuras opcionais: integrar resultado da auditoria QA no digest; aplicar patch da arbitragem nuvem automaticamente no repositório.

---

## 5. Próximos passos após Fase 0

- **Fase 1:** Implementar SOUL e pods para todos os agentes (010–019), fluxo evento-driven mínimo (CEO → PO → backlog) e exemplo E2E (016).  
- **Fase 2:** Zero Trust, quarentena, token bucket/degradação CEO, OWASP/CISO (020–029, 126, 128).  
- Manter alinhamento com [docs/README.md](docs/README.md), [docs/issues/README.md](docs/issues/README.md) e revisões pós-crítica (README principal) em todas as decisões de arquitetura e segurança.

---

## 6. Referências rápidas

- **Objetivo e máquina:** [docs/00-objetivo-e-maquina-referencia.md](docs/00-objetivo-e-maquina-referencia.md)  
- **Índice da doc:** [docs/README.md](docs/README.md)  
- **Backlog e fases:** [docs/issues/README.md](docs/issues/README.md)  
- **Deploy Fase 0 atual:** [docs/37-deploy-fase0-telegram-ceo-ollama.md](docs/37-deploy-fase0-telegram-ceo-ollama.md)  
- **Arquitetura OpenClaw + K8s:** [docs/openclaw-sub-agents-architecture.md](docs/openclaw-sub-agents-architecture.md)  
- **Auto-evolução:** [docs/36-auto-evolucao-clawdevs.md](docs/36-auto-evolucao-clawdevs.md) (início/parada só pelo Diretor via Telegram)

