# 02 — Backlog e Escopo do MVP
> **Objetivo:** Definir os épicos, a especificação das regras de negócio do MVP e o foco de entregas.
> **Público-alvo:** PO, Todos
> **Ação Esperada:** PO deve usar este documento para guiar a criação das User Stories no Workspace; Devs devem usá-lo para entender o escopo delimitado da v1.0.

**v2.0 | Atualizado em: 06 de março de 2026**

---

## 1. O Escopo do MVP v1.0

- **O que será entregue na v1.0?**
  - Um time de 5 agentes core: `CEO`, `PO`, `Architect`, `Developer`, `QA`.
  - Orquestração rodando em um Cluster Kubernetes Local (Minikube).
  - Inferência puramente local usando *Ollama*.

- **Multi‑agente como padrão de 2026 em diante**  
  - 2026 marcado pela transição de agentes individuais para **sistemas multi‑agentes** em produção.  
  - ClawDevs AI se posiciona como **time de agentes open source, self‑hosted, replicável**, em contraste com SDKs proprietários de cloud.  
  (`11-futuro-agentes-ia.md`)

### Propósito e objetivo

- **Propósito do ClawDevs AI**
  - Permitir que um Diretor (humano) comande um **time de agentes especializados** para:
    - Criar novos produtos de software do zero.
    - Manter e evoluir sistemas em produção.
    - Operar 24/7 com **custo de núcleo próximo de zero**.
  - Objetivo prático: em até 3 meses, qualquer pessoa com hardware de referência consegue subir o time completo e **obter PRs reais gerados pelos agentes**.  
  (README, `09-plano-de-acao.md`, `19-fluxos-desenvolvimento.md`)

- **Objetivos de sucesso v1.0**
  - Time de 5 agentes desenvolve **projeto real end‑to‑end**, sem intervenção humana no código.
  - Custo comprovadamente baixo (núcleo de software a R$0, apenas energia + eventual fallback OpenRouter).
  - Terceiro externo consegue subir o ambiente em **< 4 horas** apenas seguindo a documentação.
  - Self_evolution gera **≥ 3 melhorias reais via PR** aprovado pelo Diretor.
  - Zero incidentes de segurança na auditoria do mês 3; repositório público com primeiras contribuições.  
  (README, `09-plano-de-acao.md`)

---

## Product Context

### Problema que o produto resolve

- **Dependência de clouds proprietárias e custos elevados**
  - Alternativas atuais de agentes (SDKs OpenAI, Anthropic, Google) implicam:
    - Custos mensais elevados (US$ 500–5.000/mês).
    - Lock‑in de vendor e dependência de nuvem.
    - Dados sensíveis saindo da infraestrutura da empresa.  
  (`01-stack-tecnica.md`, `11-futuro-agentes-ia.md`)

- **Ausência de um “time” de agentes replicável e soberano**
  - Mercado focado em:
    - Chatbots,
    - “Assistentes” isolados,
    - Frameworks de orquestração de propósito geral.  
  - Falta uma solução que entregue um **time de engenharia completo**, opinionado, com:
    - Papéis claros,
    - Políticas de segurança fortes,
    - Fluxos de desenvolvimento completos.  
  (`11-futuro-agentes-ia.md`, `10-decisoes-estrategicas.md`)

- **Riscos ignorados em sistemas multi‑agentes**
  - Riscos críticos mapeados: segurança multi‑agente, complexidade A2A, self_evolution incontrolável, custo cloud explosivo, hardware insuficiente, degradação de contexto, orquestrador como single point of failure.  
  (`08-riscos-mitigacoes.md`, `17-resolucao-riscos.md`)

### Contexto do projeto

- **Arquitetura e implantação**
  - Cluster `Kubernetes (Minikube)` local com namespaces:
    - `clawdevs-gateway`: OpenClaw + Orquestrador.
    - `clawdevs-agents`: 5 agentes (CEO, PO, Architect, Dev, QA).
    - `clawdevs-infra`: `Ollama` e `OpenRouter`.
  (`00-visao-geral.md`, `02-arquitetura-kubernetes.md`, `18-dashboard-diretor.md`)

- **Stack técnica em camadas**
  - L0 Interface (Telegram, Slack, WhatsApp, Discord).
  - L1 Gateway de mensagens (OpenClaw).
  - L2 Orquestração (Kubernetes + LangGraph).
  - L3 Agentes de IA (5 papéis).
  - L4 Inferência (Ollama primário, OpenRouter fallback).
  (`01-stack-tecnica.md`, `02-arquitetura-kubernetes.md`, `14-comunicacao-agentes.md`)

- **Princípios inegociáveis**
  - Ordem imutável:
    1. **Cibersegurança** (Zero Trust, OWASP).
    2. **Custo zero no núcleo** (software MIT/Apache self‑hosted; cloud opcional com teto).
    3. **Performance sustentável** (whitelist de CPU, kill switches, análise estática).  
  (`00-visao-geral.md`, `06-politicas-primícias.md`, README)

- **Escopo do MVP v1.0**
  - Cluster local, 5 agentes, comunicação A2A interna, memória em PVCs K8s, OpenClaw + Telegram, modo self_evolution com aprovação humana.  
  (`README.md`, `09-plano-de-acao.md`, `12-a2a-contexto-compartilhado.md`)

---

## Core Concepts

### Time de agentes (papéis e responsabilidades)

- **Papéis**
  - `CEO (Claw)`: status, coordenação, bloqueios, daily reports para o Diretor.
  - `PO (Priya)`: backlog, épicos, user stories, critérios de aceite.
  - `Architect (Axel)`: ADRs, decisões de stack, revisão arquitetural, segurança.
  - `Developer (Dev)`: implementação, testes, PRs.
  - `QA (Quinn)`: estratégia de testes, validação, bugs, aprovação de PR.  
  (`00-visao-geral.md`, `05-soul-agentes.md`, `13-simulacao-time-real.md`, `19-fluxos-desenvolvimento.md`)

- **Relações e escalonamento**
  - CEO coordena PO e Architect; PO e Architect direcionam Dev e QA.
  - Conflitos técnicos: Architect arbitra; de produto: PO arbitra; sem resolução → CEO escala ao Diretor.
  - Comportamento anômalo ou violação de segurança: isolamento do agente, alerta ao Diretor.  
  (`05-soul-agentes.md`, `06-politicas-primícias.md`, `13-simulacao-time-real.md`, `17-resolucao-riscos.md`)

### SOUL dos agentes

- **SOUL (arquivo de identidade)**
  - Define: `identity`, `capabilities`, `collaboration`, `inference`, `constraints`.
  - Especificado em YAML por agente (`soul/<papel>.yaml`).
  - Cada SOUL inclui: personalidade, expertise, blind spots, working style, outputs, nível de segurança.  
  (`05-soul-agentes.md`)

- **Exemplos**
  - CEO: direto, orientado a decisões, nunca escreve código, sempre entrega STATUS/BLOQUEIOS/PRÓXIMOS PASSOS.
  - PO: obcecado por critério de aceite, recusa ambiguidade, prioriza impacto.
  - Architect: pragmático, documenta decisões como ADRs, prioriza segurança e simplicidade.
  - Developer: focado em código e testes; não decide requisitos nem arquitetura.
  - QA: guardião de qualidade e regressão; aprova PRs somente com critérios cobertos.  
  (`05-soul-agentes.md`)

### Primícias e políticas

- **Ordem de prioridade absoluta**
  - `Segurança` → `Custo zero no núcleo` → `Performance sustentável` (nunca inverter).
  - Zero Trust entre namespaces e agentes; nenhum agente acessa internet diretamente.
  - Commits e PRs com políticas específicas (tipos, bloqueios, reviews obrigatórios).  
  (`06-politicas-primícias.md`, README)

- **Zero Trust multi‑agente**
  - Níveis de confiança do Diretor até serviços de infra.
  - Proibições: elevação de privilégios por agentes, acesso direto à internet, secrets em código ou contexto.  
  (`06-politicas-primícias.md`)

### Arquitetura A2A e contexto compartilhado

- **A2A (agent‑to‑agent)**
  - Padrão `A2A Protocol (Linux Foundation)` adotado como base.
  - Cada agente publica um `Agent Card` com capabilities, endpoint, modelo, nível de segurança.
  - Mensagens A2A roteadas internamente com schema padrão (source, destination, payload, routing, auth).  
  (`10-decisoes-estrategicas.md`, `12-a2a-contexto-compartilhado.md`, `14-comunicacao-agentes.md`)

- **Contexto compartilhado e memória**
  - Estado atual e histórico gerenciados em arquivos locais do K8s (PVCs).
  (`12-a2a-contexto-compartilhado.md`, `08-riscos-mitigacoes.md`)

### Modos de operação

- **Estados do sistema**
  - `Standby`: cluster iniciado.
  - `Executing`: tarefa em execução.
  - `SelfEvolution`: agentes propondo melhorias.
  - `AwaitingApproval`: PRs aguardando decisão do Diretor.
  - `CircuitBreaker`: kill switches ativados por hardware ou budget.  
  (`00-visao-geral.md`, `04-inferencia-ollama-openrouter.md`, `06-politicas-primícias.md`)

### Fluxos de desenvolvimento

- **Três fluxos macros**
  - **Novo Produto**: ideia → research → visão → PRD → arquitetura → backlog → design → dev → QA → CI/CD → staging → produção → monitoramento → feedback → iteração.
  - **Manutenção**: alerta → triagem → root cause → fix → QA → deploy → RCA.
  - **Evolução**: feedback → feature → sprint → dev → QA → feature flags/A‑B → release.  
  (`19-fluxos-desenvolvimento.md`)

- **Responsabilidade por agente em cada fluxo**
  - Tabelas e gráficos atribuindo responsabilidades por fase para CEO, PO, Architect, Dev, QA.  
  (`19-fluxos-desenvolvimento.md`)

### Segurança, observabilidade e riscos

- **Segurança**
  - Secrets via K8s Secrets.
  - Policies para reviews, PRs, dependências, secrets, self_evolution.
  - Runbooks para incidentes: GPU OOM, loops de agentes, custo cloud, contexto corrompido, credenciais vazadas, etc.  
  (`06-politicas-primícias.md`, `08-riscos-mitigacoes.md`, `17-resolucao-riscos.md`)

- **Monitoramento e dashboard**
  - Dashboard nativo exibindo agentes ativos, tarefas, painéis por tipo de trabalho, fluxo A2A, alertas e métricas.  
  (`18-dashboard-diretor.md`, `16-performance-paralelismo.md`)

---

## Features mencionadas

### Interface e gateway

- **OpenClaw como única porta de entrada**
  - Recebe mensagens de Telegram, Slack, WhatsApp, Discord.
  - Roteia por hashtag (`#ceo`, `#po`, `#arch`, `#dev`, `#qa`, `#time`, `#evolui`).
  - Webhooks seguros para o Orquestrador (`/hooks/agent`, `/hooks/wake`, `/hooks/status`).  
  (`03-integracao-openclaw.md`, `07-config-openclaw.md`, `14-comunicacao-agentes.md`, `15-integracao-sistemas.md`)

- **Configuração completa via `openclaw.json`**
  - Seções: `gateway`, `hooks`, `channels`, `agents`, `inference`, `security`.
  - Allowlist de `chat_id` do Diretor, rate limits, limites de payload, políticas de sessão.  
  (`07-config-openclaw.md`)

### Time de agentes e SOULs

- **Cinco agentes especializados com SOULs completos**
  - Arquivos `soul/ceo.yaml`, `soul/po.yaml`, `soul/architect.yaml`, `soul/developer.yaml`, `soul/qa.yaml`.
  - Cada um com: identidade, expertise, blind spots, capabilities, ferramentas, outputs, constraints, modelos primário/fallback.  
  (`05-soul-agentes.md`, `04-inferencia-ollama-openrouter.md`)

### A2A, contexto compartilhado e memória

- **Protocolo A2A**
  - Formato de mensagem padronizado (Linux Foundation draft v0.2).
  - Tipos: `TASK_DELEGATE`, `TASK_ACCEPT`, `TASK_RESULT`, `TASK_REJECT`, `CONTEXT_REQUEST`, `CONTEXT_UPDATE`, `BROADCAST_ALERT`, `SELF_EVOLUTION_PROPOSAL`, `HEARTBEAT`, `CAPABILITY_QUERY`.  
  (`14-comunicacao-agentes.md`)

- **Memória compartilhada**
  - Armazenamento em arquivos locais persistidos no Kubernetes (PVC).
  (`12-a2a-contexto-compartilhado.md`, `08-riscos-mitigacoes.md`)

### Orquestração e performance

- **LangGraph como orquestrador core**
  - Grafo de estados para features (aprovação do CEO → spec PO/Arch → dev → QA → merge → notificação).
  - Suporte a reexecução de tarefas após falhas.  
  (`10-decisoes-estrategicas.md`, `16-performance-paralelismo.md`)

- **Worker pool de agentes com slots**
  - `CEO` serial (1 slot), `PO`/`Arch` 2 slots, `Dev`/`QA` 3 slots.
  - Slot manager controla concorrência via workers.  
  (`16-performance-paralelismo.md`)

- **Circuit breakers multi‑agente**
  - Circuit breaker por agente: `CLOSED` → `OPEN` → `HALF_OPEN` com thresholds e cooldown.
  - Notificações ao Diretor quando circuit breaker abre ou fecha.  
  (`16-performance-paralelismo.md`, `04-inferencia-ollama-openrouter.md`)

### Inferência (Ollama + OpenRouter)

- **Roteamento de inferência**
  - Verificação de hardware (GPU/CPU), budget OpenRouter, viabilidade de Ollama (modelo, VRAM, contexto) e kill switches.
  - Ollama como primário, OpenRouter como fallback com teto de gasto.  
  (`04-inferencia-ollama-openrouter.md`, `01-stack-tecnica.md`, `08-riscos-mitigacoes.md`)

- **Modelos por agente**
  - Tabelas de modelos para cada papel: Qwen 2.5 coder, Qwen 2.5, Llama, DeepSeek‑R1, etc., com parâmetros (temp, tokens, thinking).  
  (`01-stack-tecnica.md`, `04-inferencia-ollama-openrouter.md`)

### Dashboard do Diretor

- **Torre de controle de engenharia**
  - Visão de agentes (status, carga, tasks ativas).
  - Painéis para: Novas Features, Bugs/Hotfixes, Refatoração.
  - Feed de comunicação A2A em tempo real.
  - Widget de custo (Ollama/OpenRouter) e alertas de disponibilidade/incidente.  
  (`18-dashboard-diretor.md`)

- **Arquitetura do dashboard**
  - Backend: WebSocket server, Aggregator, API REST, Auth JWT.
  - Frontend: painéis, barra de agentes, feed A2A, widget de custo.  
  (`18-dashboard-diretor.md`)

### Integrações

- **Controle de Versão Local**
  - Repositório interno na workspace persistente no Kubernetes.
  - Branching model em disco para controle de revisões.  
  (`15-integracao-sistemas.md`, `20-pre-implementacao.md`)

- **MCP servers adicionais**
  - Filesystem MCP para acesso estruturado ao código alvo.  
  (`15-integracao-sistemas.md`)

### Self_evolution e governança

- **Modo self_evolution**
  - Ativado pelo Diretor via `#evolui`.
  - Agentes propõem mudanças em SOUL, skills, configs via PR; OPA valida escopo; aprovação humana obrigatória.  
  (`06-politicas-primícias.md`, `08-riscos-mitigacoes.md`)

- **Runbooks e resolução de riscos**
  - Runbooks por risco: GPU OOM, loops de agente, custo cloud, contexto corrompido, self_evolution danosa, credenciais vazadas, etc., com procedimentos de diagnóstico e recovery.  
  (`17-resolucao-riscos.md`, `08-riscos-mitigacoes.md`)

---

## Estrutura para desenvolvimento

### Features

- **Core de orquestração e agentes**
  - LangGraph orchestration graph para features.
  - Worker pool com slots por agente.
  - Circuit Breakers e loop detection.
  - A2A endpoint em cada agente (FastAPI).  
  (`16-performance-paralelismo.md`, `12-a2a-contexto-compartilhado.md`, `14-comunicacao-agentes.md`)

- **Inferência**
  - Camada de roteamento (Ollama + OpenRouter).
  - Kill switches por hardware e budget.
  - Setup de modelos Ollama, secrets e configs OpenRouter.  
  (`04-inferencia-ollama-openrouter.md`, `01-stack-tecnica.md`)

- **Memória e contexto**
  - Sistema de arquivos local estruturado para logs e decisões.
  (`12-a2a-contexto-compartilhado.md`, `08-riscos-mitigacoes.md`)

- **Gateway e comunicação externa**
  - OpenClaw gateway; roteamento por hashtag; webhooks; openclaw.json + ConfigMap; CLI e comandos.  
  (`03-integracao-openclaw.md`, `07-config-openclaw.md`, `15-integracao-sistemas.md`)

- **Código e Tarefas**
  - Repositório mantido silenciosamente por um agente.
  (`15-integracao-sistemas.md`, `20-pre-implementacao.md`)

- **Dashboard do Diretor**
  - Backend de streaming (Redis Streams + Aggregator + WebSocket).
  - Frontend completo com os painéis descritos.
  - Configurar autenticação JWT para o Diretor.  
  (`18-dashboard-diretor.md`)

- **Segurança e governança**
  - Políticas de commits e PRs.
  - Secrets management, dependências, self_evolution, escalonamento de conflitos.  
  (`06-politicas-primícias.md`, `17-resolucao-riscos.md`)

### Stories (já implícitas nos docs)

- **Como Diretor**
  - Quer enviar uma mensagem via Telegram com `#dev` ou `#time` para que o time de agentes receba e execute tarefas de desenvolvimento, abrindo PRs e reportando o resultado.  
    (`00-visao-geral.md`, `03-integracao-openclaw.md`, `13-simulacao-time-real.md`)
  - Quer visualizar em um dashboard quais agentes estão ativos, quais tarefas estão em execução, status, dependências e bloqueios, para tomar decisões em tempo real.  
    (`18-dashboard-diretor.md`)
  - Quer ativar o modo `#evolui` e aprovar (ou rejeitar) melhorias propostas pelos agentes nos seus próprios SOULs e configs.  
    (`06-politicas-primícias.md`, `08-riscos-mitigacoes.md`)

- **Como CEO (agente)**
  - Quer consolidar o status do time (issues abertas, PRs em revisão, bloqueios) e enviar um **daily report** ao Diretor em linguagem executiva.  
    (`05-soul-agentes.md`, `13-simulacao-time-real.md`)
  - Quer coordenar fluxos de Novo Produto, Manutenção e Evolução orquestrando PO, Architect, Dev e QA.  
    (`19-fluxos-desenvolvimento.md`)

- **Como PO (agente)**
  - Quer transformar demandas do Diretor em épicos, user stories e critérios de aceite claros para a equipe.  
    (`05-soul-agentes.md`, `13-simulacao-time-real.md`, `19-fluxos-desenvolvimento.md`)
  - Quer priorizar filas de bugs e features com apoio do Architect em temas de risco (por exemplo, BUG crítico de segurança).  
    (`13-simulacao-time-real.md`, `08-riscos-mitigacoes.md`)

- **Como Architect (agente)**
  - Quer definir ADRs de stack, autenticação, WebSocket, performance e segurança, garantindo que Dev e QA sigam essas decisões.  
    (`10-decisoes-estrategicas.md`, `13-simulacao-time-real.md`, `19-fluxos-desenvolvimento.md`)
  - Quer revisar PRs complexos, com foco em segurança e arquitetura, e aprovar/bloquear merges.  
    (`05-soul-agentes.md`, `06-politicas-primícias.md`)

- **Como Developer (agente)**
  - Quer receber issues com critérios de aceite claros, criar branches, implementar código, escrever testes, abrir PRs e iterar com QA e Architect.  
    (`13-simulacao-time-real.md`, `19-fluxos-desenvolvimento.md`, `20-pre-implementacao.md`)

- **Como QA (agente)**
  - Quer testar PRs contra critérios de aceite, bloquear PRs inseguros ou incompletos, e aprovar releases para produção.  
    (`06-politicas-primícias.md`, `13-simulacao-time-real.md`, `19-fluxos-desenvolvimento.md`)

### Tasks (já descritas ou roteirizadas)

- **Infraestrutura e cluster**
  - Validar hardware de referência (CPU, RAM, GPU, disco, SO).
  - Instalar e validar Minikube + `kubectl`.
  - Criar namespaces (`clawdevs-gateway`, `clawdevs-agents`, `clawdevs-infra`, `clawdevs-security`, `clawdevs-monitoring`).
  - Aplicar manifests de `Namespace`, `NetworkPolicy`, `ResourceQuota`, `PVCs`.  
  (`02-arquitetura-kubernetes.md`, `09-plano-de-acao.md`, `20-pre-implementacao.md`)

- **Ollama e modelos**
  - Subir pod Ollama, configurar volumes e recursos.
  - Executar `ollama pull` dos modelos (qwen2.5 coder/geral, Llama, etc.).
  - Validar inferência local (`/api/chat`, `/api/generate`).  
  (`04-inferencia-ollama-openrouter.md`, `01-stack-tecnica.md`)

- **OpenClaw e canais**
  - Configurar `openclaw.json`.
  - Criar `ConfigMap` e `Secret` K8s, injetando tokens e IDs.
  - Configurar Webhook do Orquestrador (`/hooks/agent`).
  - Testar envio de mensagem de teste ao Diretor.  
  (`03-integracao-openclaw.md`, `07-config-openclaw.md`, `15-integracao-sistemas.md`)



- **SOULs**
  - Escrever e validar SOUL do Developer e PO (Fase 1).
  - Escrever e validar SOUL de Architect, QA e CEO (Fase 2).
  - Carregar SOULs como ConfigMaps montados nos pods dos agentes.  
  (`05-soul-agentes.md`, `09-plano-de-acao.md`)

- **Orquestrador e graph**
  - Implementar grafo de tarefas com LangGraph.
  - Integrar SlotManager e Circuit Breaker.
  - Conectar A2A ao contexto compartilhado local.  
  (`16-performance-paralelismo.md`, `12-a2a-contexto-compartilhado.md`)

- **Dashboard**
  - Implementar aggregator interno do tráfego.WebSocket backend e frontend com os painéis descritos.
  - Configurar autenticação JWT para o Diretor.  
  (`18-dashboard-diretor.md`)

- **Segurança, riscos e runbooks**
  - Configurar alertas nativos da infraestrutura K8s.
  - Implementar kill switches de hardware e budget.
  - Implementar loop detector e spend limiter.
  - Criar e validar runbooks R01–R09.  
  (`06-politicas-primícias.md`, `08-riscos-mitigacoes.md`, `17-resolucao-riscos.md`)

- **Self_evolution**
  - Implementar ciclo self_evolution (ativação via hashtag, geração de PRs, validação OPA, aprovação humana, rollback).  
  (`06-politicas-primícias.md`, `08-riscos-mitigacoes.md`)

---

## 5. Próximos Passos (Ação do PO)

1. Decompor os tópicos da Seção 3 e 4 em **Especificações/User Stories** no Workspace.
2. Definir Prioridade 1 (crítico para o MVP) e Prioridade 2 (Nice to have v1.x).
3. Atribuir tags arquiteturais para o Architect validar antes do fluxo de Dev.

---

*Próximo Documento:* [03 — Interface do Diretor →](./03-produto-interface-diretor.md)

