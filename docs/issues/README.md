# Issues — ClawDevs (team-devs-ai)

Backlog de desenvolvimento do **ClawDevs** (team-devs-ai): time de desenvolvimento 100% autônomo com nove agentes de IA (CEO, PO, DevOps/SRE, Architect, Developer, QA, CyberSec, UX, DBA) orquestrados em Kubernetes (Minikube), OpenClaw, Ollama e OpenCode — **na máquina do Diretor, pronto para trabalhar 24 por 7**.

**Prioridades do projeto (avaliar em toda issue):** **custo baixíssimo** e **performance segura e altíssima**. Decisões de arquitetura, provedores, pipelines e operação devem ser consistentes com esse critério.

**Revisão pós-crítica dos analistas:** O backlog incorpora ajustes de resiliência e **ajustes de segurança determinísticos** conforme feedback. **(1) Retomada automática (cluster acéfalo):** health check contínuo (ping a cada 5 min, sem tokens); quando conectividade estável por **3 ciclos consecutivos**, retomada **automática** (checkout limpo, Architect se conflitos, restaura fila); **nenhum comando humano** para destravar; Diretor apenas notificado (issue 124). **(2) Entropia contextual e assinaturas (quarentena):** **matriz de confiança** (hash/assinatura vs registro oficial → se ok, dispensar entropia restritiva); **whitelist de extensões** (.map, .wasm, .min.js com tolerância maior); **análise dinâmica** (CyberSec) em pico de entropia em arquivo tolerado; evita falsos positivos em pacotes modernos (issue 128). **(3) Fitness function no raciocínio do CEO:** CEO gera **VFM_CEO_score.json** e descarta internamente eventos com threshold negativo **antes** de enviar ao Gateway; economia na raiz cognitiva; token bucket e $5/dia permanecem como rede de proteção redundante (issue 129). Demais ajustes: validação pré-GPU em CPU e batching de PRs (redução do gargalo GPU); sandbox para URLs/APIs desconhecidas e acelerador preditivo de tokens (Zero Trust sem fadiga de alertas); **five strikes** com fallback contextual e escalação para arbitragem na nuvem (evitar abandono de tarefas críticas); **aprovação por omissão apenas cosmética** (timer **6 h**; impasses de código lógico/backend → 5 strikes, issue volta ao backlog do PO; **PO analisa histórico com Architect e tarefa retorna ao desenvolvimento**); **whitelist global estática** de egress e **verificação de reputação de domínio** (não depender da autodeclaração da skill no manifesto); **quarentena de disco** e **análise determinística de diff** entre sandbox e repositório; Architect revisa **apenas diffs do PR** (nunca volume compartilhado). **CEO:** filtrar ideias e tarefas para não estourar orçamento de API (modelos nuvem caros). **PO:** risco de **alucinação de escopo** quando o RAG falha; ciclo de rascunho e technical_blocker como mitigação. **Mudança de escopo em sprint:** consequência = timing loop, nada entregue; regra inalterável exceto technical_blocker. **Curadoria centralizada de learnings:** promoção de .learnings/ para SOUL/AGENTS/TOOLS via merge request formal, pre-flight (QA + CyberSec) e CronJob em sessão isolada (Architect ou CyberSec como curador). **VFM/ADL quantitativos:** fitness function (vfmscore.json, limite no Gateway) e auditoria de desvio no microADR por regex (lista negra de justificativas fracas). **Persistência + FinOps:** diversidade de ferramenta (bloqueio após 2 falhas consecutivas mesma ferramenta/motivo); contador de tentativas integrado ao Gateway (penalidade progressiva); degradação graciosa (devolver tarefa ao PO, liberar GPU). **Orçamento de degradação (limite matemático de tolerância a falhas):** orquestrador conta eventos de **5ª strike** e de aprovações por omissão **cosmética** de forma acumulativa; ao atingir 10–15%, primeiro **loop de consenso automatizado (pré-freio de mão)** — QA + Architect propõem ajuste temporário e testam em uma tarefa crítica; só se falhar → DevOps dispara alerta crítico e aciona **freio de mão** (**pausa a esteira**). **Workflow de recuperação:** relatório de degradação gerado automaticamente ao pausar; Diretor revisa MEMORY.md e config; retomada **somente** com **comando explícito de desbloqueio** (script/CLI) — nenhum agente reativa por conta própria. QA foca testes exploratórios estritamente nas áreas onde a aprovação por omissão **cosmética** foi acionada, atuando como **auditor da dívida técnica**. **Contingência cluster acéfalo (issue 124):** timeout configurável sem comando estratégico do CEO no Redis → DevOps local: **commit em branch efêmera de recuperação** (ex.: `recovery-failsafe-<timestamp>`), persistência fila no LanceDB, pausa consumo GPU; script de retomada (**checkout limpo**; se conflitos, **Architect prioridade zero** resolve na branch de recuperação); notificação ao Diretor (Telegram/Slack). **Sandbox efêmero (issue 028):** restrições a nível de kernel (**seccomp/eBPF**) no container do sandbox — bloqueio de **execve** e **socket** durante instalação de dependências (npm/pip). **Gancho de validação de contexto (operado localmente, antes da sumarização na nuvem):** modelo local (ex.: Llama 3) varre o buffer de trabalho buscando **exclusivamente intenções do usuário ou regras informais que não ganharam tag** → proposta de extração para o **Session State**; preserva valor de negócio sem gastar API. **Validação reversa (PO):** logo após a sumarização, PO compara o resumo recém-gerado com os **critérios de aceite originais**; se omitir critério fundamental, PO **rejeita o truncamento** e o sistema é forçado a **reestruturar o bloco** — garantia de qualidade na memória do enxame. **Pipeline de quarentena automatizada:** quando o Developer pedir pacote novo, orquestrador **provisiona sandbox isolado instantaneamente** (em vez de mensagem no Telegram); não interrompe a sprint; agente guardião (ex.: CyberSec) roda varredura (Snyk/Trivy) e testes de injeção; se score impecável, aprovação temporária para uso imediato; humano **notificado de forma assíncrona só no resumo diário** (audita depois, sem travar o código). **Zonas de confiança de autores:** pacotes **assinados criptograficamente por publicadores da matriz** (Google, Vercel, Microsoft) — DevOps instala sem aprovação direta; **Diretor reservado só para bibliotecas comunitárias desconhecidas** onde o risco real existe (Diretor volta a ser estrategista em vez de apertador de botão de aprovação). **Governança CEO (issue 126):** **token bucket** para eventos de estratégia no Gateway (ex.: máx. 5/hora); **degradação por eficiência** (razão ideias CEO vs aprovadas PO) com rebaixamento para modelo local em CPU; $5/dia mantido como freio de emergência. **Disjuntor PO–Architect (issue 127):** mesma épico com **3 draft_rejected consecutivos** → congelar tarefa; **RAG health check** determinístico (datas de indexação, estrutura de pastas); descongelar com rejeição + contexto saneado; atua antes da cota global de degradação. **Quarentena SAST + entropia contextual (issue 128):** além do diff de caminhos, **matriz de confiança (assinaturas)**, **SAST leve (semgrep)** e **analisador de entropia contextual** (whitelist de extensões, CyberSec dinâmico se pico); evita falsos positivos em minificados/.wasm/.map. **CEO fitness no raciocínio (issue 129):** VFM_CEO_score.json e descarte interno se threshold negativo antes do Gateway.

As issues estão ordenadas **do zero ao avançado**, por fases. Cada arquivo `.md` nesta pasta corresponde a uma issue para o time implementar.

---

## Ordem sugerida (fases)

| Fase | Número  | Nome curto | Conteúdo |
|------|---------|------------|----------|
| **0** | 001–009, **124**, **125** | Fundação | Máquina de referência, setup, Minikube, Redis, Ollama, arquitetura (Redis Streams, **truncamento na borda**, **pre-flight Summarize**, **TTL Redis** para working buffer, **validação pré-GPU em CPU** e **batching de PRs**, GPU Lock com **TTL dinâmico** + **hard timeout K8s** e node selectors DevOps/UX em CPU), **pipeline explícito e slot único de revisão** (issue 125; ver [estrategia-uso-hardware-gpu-cpu.md](../estrategia-uso-hardware-gpu-cpu.md)), **checkpoint 80°C** (evento Redis → commit em branch efêmera de recuperação) e **Redis idempotente** (ACK só após disco), **contingência cluster acéfalo** (heartbeat Redis, **branch efêmera de recuperação**, LanceDB, **retomada automática** — health check 5 min, 3 ciclos estáveis, checkout limpo + Architect para conflitos, sem comando Diretor; notificação assíncrona — issue 124), ResourceQuota |
| **1** | 010–019 | Agentes | Definição dos 9 agentes, SOUL (identidade), prompts, line-up, código de conduta, fluxo evento-driven |
| **2** | 020–029, **126**, **128** | Segurança | Zero Trust, **score de confiança e quarentena** para skills validadas, **sandbox para URLs/APIs desconhecidas** (container efêmero, resultado no digest), **pipeline de quarentena automatizada** (sandbox isolado + **quarentena de disco**, diff + **assinaturas criptográficas** + **SAST leve/semgrep** + **entropia contextual** — issue 128), **CEO fitness no raciocínio (VFM antes do Gateway)** — issue 129, **zonas de confiança de autores** (Google, Vercel, Microsoft sem aprovação direta; Diretor só para comunitárias desconhecidas), **restrições a nível de kernel (seccomp/eBPF)** no sandbox efêmero — issue 028 (bloqueio execve e socket na instalação de dependências), **acelerador preditivo de tokens/orçamento** (rotear para CPU quando prever estouro), **token bucket e degradação por eficiência** (issue 126; eventos de estratégia CEO, razão CEO/PO), segurança em runtime, **service account zerada** do roteador, **whitelist global estática** de egress e **verificação de reputação de domínio** (não autodeclaração da skill), **sandbox air-gap** e **proxy de dependências** para Developer, **Architect revisa apenas diffs do PR**, **análise estática em git hooks** (SonarQube), OWASP, CISO, skills de terceiros, egress, rotação de tokens |
| **3** | 030–039, **127** | Operações | Manual de primeiros socorros (**exceção**; recuperação padrão automática: checkpoint 80°C com branch efêmera + Redis ACK + checkout limpo e Architect para conflitos), prevenção, **disjuntor draft_rejected** (issue 127: 3 rejeições consecutivas por épico → congelar + RAG health check; descongelar com contexto saneado), **five strikes com fallback contextual** (2º strike: Architect gera código aprovável; 5º strike: escalação para arbitragem na nuvem; abandono só se escalação falhar), **aprovação por omissão cosmética** (timer **6 h**, MEMORY.md; lógica/backend → 5 strikes, issue ao backlog PO; **PO + Architect solução, tarefa retorna ao desenvolvimento**), **orçamento de degradação** (métrica acumulativa; **loop de consenso pré-freio de mão** — QA + Architect; freio de mão só se loop falhar), **QA auditor da dívida técnica** (testes exploratórios onde houve aprovação por omissão cosmética), autonomia nível 4, **matriz de escalonamento com CEO desempate** e **digest diário** |
| **4** | 040–049 | Configuração | Perfis por agente, OpenClaw, **controle FinOps no Gateway** (max tokens/request), **pre-flight Summarize**, **truncamento na borda** (script, limite tokens), **segregação dos critérios de aceite** (tag de proteção + regex no script DevOps ou payload duplo — issue 041), **gancho de validação de contexto** (local, antes da nuvem: intenções/regras sem tag → Session State), **validação reversa PO** (resumo vs critérios de aceite originais; rejeitar truncamento → reestruturar bloco), **microADR e invariantes de negócio** (tag + regex), **TTL Redis** working buffer, FinOps, provedores (Gemini + Ollama) |
| **5** | 050–059 | Self-improvement e memória | .learnings/, WAL, Working Buffer, memória Elite (6 camadas, **microADRs** no Warm Store, **invariantes** protegidos por regex), recuperação pós-compactação |
| **6** | 060–069 | Habilidades transversais | Escrita humanizada, expertise em documentação, habilidades proativas |
| **7** | 070–089 | Ferramentas | Browser, summarize, gh CLI, markdown converter, Ollama (skill), OpenCode Controller |
| **8** | 090–099 | Skills e ambiente | Descoberta/instalação de skills, criação de skills, auto-atualização, FreeRide (OpenRouter) |
| **9** | 100–109 | Integrações | API Gateway (Maton), dados/watchlist/alertas, Exa Web Search, busca web headless |
| **10** | 110–119 | Frontend e UX | Frontend design, UI/UX Pro Max, acessibilidade |
| **11** | 120–129 | Avançado | War Room (dashboard), Chaos Engineering, evolução adicional de balanceamento GPU/CPU (PriorityClasses, evict gracioso), **roteamento hierárquico** (nuvem → GPU → CPU) e **estado de pausa no LanceDB** — TTL dinâmico e node selectors já na Phase 0 |

---

## Como usar

- **Para PO:** Importar ou criar issues no GitHub (ou outro tracker) a partir dos arquivos desta pasta; priorizar por fase.
- **Para o time:** Cada issue referencia o(s) documento(s) em `docs/agents-devs/` que descrevem o escopo e os critérios de aceite.
- **Projeto:** Nome do repositório/initiative: **team-devs-ai**.

---

## Índice das issues (por arquivo)

| # | Arquivo | Título curto |
|---|---------|--------------|
| 001 | 001-maquina-referencia-e-verificacao.md | Máquina de referência e script de verificação |
| 002 | 002-setup-um-clique.md | Setup "um clique" (setup.sh) |
| 003 | 003-minikube-redis-ollama-65.md | Minikube, Redis e Ollama com limite 65% |
| 004 | 004-resource-quota-limitrange.md | ResourceQuota e LimitRange |
| 005 | 005-redis-streams-estado-global.md | Redis Streams e estado global |
| 006 | 006-gpu-lock-script.md | Script de GPU Lock + hard timeout K8s; validação pré-GPU, batching de PRs |
| 007 | 007-consumer-groups-fila-prioridade.md | Consumer Groups e fila de prioridade |
| 008 | 008-docker-multi-stage-imagens-agentes.md | Docker multi-stage e imagens enxutas |
| 009 | 009-transcricao-audio-m4a-to-md.md | Transcrição de áudio (m4a → .md) |
| 010 | 010-definicao-oito-agentes.md | Definição canônica dos nove agentes |
| 011 | 011-soul-identidade-prompts.md | SOUL — identidade e prompts |
| 012 | 012-pods-ceo-po-nuvem-openclaw.md | Pods CEO e PO (nuvem) com OpenClaw |
| 013 | 013-pods-tecnicos-developer-opencode.md | Pod Developer com OpenCode e Ollama |
| 014 | 014-pods-architect-qa-cybersec-ux.md | Pods Architect, QA, CyberSec e UX |
| 015 | 015-codigo-conduta-e-restricoes.md | Código de conduta e restrições |
| 016 | 016-exemplo-fluxo-operacao-2fa.md | Exemplo de fluxo E2E: Operação 2FA |
| 017 | 017-autonomia-nivel-4-matriz-escalonamento.md | Autonomia nível 4, CEO desempate, digest diário, **five strikes** (fallback + arbitragem nuvem), **orçamento de degradação** (freio de mão, recalibragem prompts/critérios PO), **QA auditor da dívida técnica**, aprovação por omissão **cosmética** 6 h (MEMORY.md) |
| 020 | 020-zero-trust-fluxo-classificacao.md | Zero Trust: fluxo, classificação, score de confiança e quarentena, **pipeline de quarentena automatizada** (sandbox instantâneo, notificação assíncrona), **zonas de confiança de autores** (Google, Vercel, Microsoft), sandbox URL/API, acelerador preditivo, **whitelist global egress** |
| 021 | 021-seguranca-runtime-validacao.md | Segurança em runtime (validação), **quarentena de disco**, **Architect só diffs do PR** |
| 022 | 022-owasp-auditoria-codificacao-segura.md | OWASP e codificação segura |
| 023 | 023-ciso-habilidades.md | Habilidades CISO |
| 024 | 024-skills-terceiros-checklist-egress.md | Skills de terceiros, **whitelist global estática** e **verificação de reputação de domínio** (egress) |
| 025 | 025-rotacao-tokens-sandbox-roteador.md | Rotação de tokens, sandbox e service account do roteador |
| 026 | 026-detecao-injecao-prompt.md | Detecção de injeção de prompt |
| 027 | 027-kill-switch-networkpolicy.md | Kill switch (Q-Suite), checkpoint 80°C (branch efêmera), Redis idempotente, recuperação automática (checkout limpo + Architect) |
| 028 | 028-sandbox-seccomp-ebpf-kernel.md | Sandbox efêmero: **seccomp/eBPF** (bloqueio execve e socket na fase de instalação de dependências) |
| 030 | 030-manual-primeiros-socorros-gpu.md | Manual de primeiros socorros (GPU); recuperação padrão automática (branch efêmera + checkout limpo + Architect) |
| 031 | 031-prevencao-riscos-infra.md | Prevenção e mitigação de riscos |
| 040 | 040-perfis-agente-manifesto-config.md | Perfis por agente (manifesto) |
| 041 | 041-truncamento-contexto-finops.md | Truncamento na borda, **gancho de validação de contexto** (local, intenções/regras sem tag → Session State), **validação reversa PO** (critérios de aceite originais; rejeitar truncamento → reestruturar bloco), microADR, invariantes (tag + regex), max tokens, pre-flight Summarize, TTL Redis, FinOps |
| 050 | 050-workspace-learnings-self-improvement.md | Workspace e self-improvement (.learnings/) |
| 051 | 051-protocolo-wal-working-buffer.md | Protocolo WAL e Working Buffer |
| 052 | 052-memoria-elite-seis-camadas.md | Memória Elite (seis camadas) |
| 053 | 053-habilidades-proativas-heartbeat.md | Habilidades proativas e heartbeat |
| 060 | 060-escrita-humanizada.md | Escrita humanizada |
| 061 | 061-expertise-documentacao.md | Expertise em documentação |
| 070 | 070-ferramentas-browser-agent-browser.md | Ferramentas de browser (agent-browser) |
| 071 | 071-ferramenta-summarize.md | Ferramenta summarize |
| 072 | 072-ferramenta-github-gh-cli.md | Ferramenta GitHub (gh CLI) |
| 073 | 073-ferramenta-markdown-converter.md | Ferramenta Markdown Converter |
| 074 | 074-ollama-local-skill.md | Ollama Local (skill) |
| 075 | 075-opencode-controller.md | OpenCode Controller |
| 090 | 090-descoberta-instalacao-skills.md | Descoberta e instalação de skills |
| 091 | 091-criacao-de-skills.md | Criação de skills |
| 092 | 092-auto-atualizacao-ambiente.md | Auto-atualização do ambiente |
| 093 | 093-modelos-gratuitos-openrouter-freeride.md | FreeRide: fallbacks hierárquicos, hook de pausa, estado no LanceDB |
| 100 | 100-api-gateway-maton.md | API Gateway (Maton) |
| 101 | 101-dados-watchlist-alertas-simulacao.md | Dados, watchlist, alertas e simulação |
| 102 | 102-exa-web-search.md | Exa Web Search |
| 103 | 103-busca-web-headless.md | Busca web headless |
| 110 | 110-frontend-design-diretrizes.md | Frontend design (diretrizes) |
| 111 | 111-ui-ux-pro-max.md | UI/UX Pro Max |
| 120 | 120-war-room-dashboard.md | Dashboard War Room |
| 121 | 121-chaos-engineering-ia.md | Chaos Engineering para IA |
| 122 | 122-balanceamento-dinamico-gpu-cpu.md | Balanceamento dinâmico GPU/CPU, roteamento hierárquico, LanceDB |
| 123 | 123-falhas-riscos-fracasso-projeto.md | Falhas e riscos (diagnóstico; itens 1, 4, 5 com especificação e issues 124, 041, 017) |
| 124 | 124-contingencia-cluster-acefalo.md | Contingência cluster acéfalo: heartbeat Redis, **branch efêmera**, LanceDB, **retomada automática** (health check, 3 ciclos, checkout limpo + Architect), notificação assíncrona |
| 125 | 125-pipeline-explicito-slot-unico-revisao.md | Pipeline explícito GPU e slot único de revisão (estrategia uso hardware) |
| 126 | 126-token-bucket-degradacao-eficiencia.md | **Token bucket** para eventos de estratégia e **degradação por eficiência** (Gateway/CEO) |
| 127 | 127-disjuntor-draft-rejected-rag-health-check.md | **Disjuntor** de rejeições de rascunho e **autocura RAG** (3 draft_rejected → congelar + health check) |
| 128 | 128-sast-entropia-quarentena.md | **SAST (semgrep)** e **entropia contextual** no pipeline de quarentena (assinaturas, whitelist extensões, CyberSec dinâmico) |
| 129 | 129-ceo-vfm-fitness-no-raciocinio.md | **CEO:** fitness de custo-benefício no raciocínio (VFM_CEO_score, descarte interno se negativo antes do Gateway) |

**Total:** 62 issues para o projeto **team-devs-ai**.
