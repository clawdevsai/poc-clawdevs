# Índice da documentação ClawDevs (sumário)

**Este arquivo é o sumário** da documentação: referência de todos os documentos por **tema** e por **arquivo**. Para um **resumo completo** do que é o ClawDevs AI e o que você consegue fazer com isso, use o [README.md](README.md).

---

## Por tema

### Visão e objetivo
| Doc | Descrição |
|-----|-----------|
| [00-objetivo-e-maquina-referencia.md](00-objetivo-e-maquina-referencia.md) | Objetivo para agentes, stack, máquina de referência e comandos de verificação |
| [01-visao-e-proposta.md](01-visao-e-proposta.md) | Visão, 9 agentes (resumo), War Room, Chaos Engineering, autonomia nível 4 |

### Agentes e arquitetura
| Doc | Descrição |
|-----|-----------|
| [02-agentes.md](02-agentes.md) | Definição canônica dos 9 agentes: função, responsabilidades, conflitos |
| [03-arquitetura.md](03-arquitetura.md) | Redis Streams, estado global, fluxo de eventos, GPU Lock |
| [04-infraestrutura.md](04-infraestrutura.md) | K8s (65% hardware), Minikube, recursos, Docker multi-stage |
| [02-infra/kubernetes-estrutura-e-apply.md](02-infra/kubernetes-estrutura-e-apply.md) | K8s: estrutura de pastas, ordem de apply, make up, workspace, pré-requisitos |
| [openclaw-sub-agents-architecture.md](openclaw-sub-agents-architecture.md) | OpenClaw + sub-agents + K8s (pods, Redis, Ollama) |

### Segurança
| Doc | Descrição |
|-----|-----------|
| [05-seguranca-e-etica.md](05-seguranca-e-etica.md) | Cibersegurança, Zero Trust, defesa em profundidade, prioridades |
| [14-seguranca-runtime-agentes.md](14-seguranca-runtime-agentes.md) | Validação pré-execução, injeção, SSRF, path traversal |
| [15-seguranca-aplicacao-owasp.md](15-seguranca-aplicacao-owasp.md) | OWASP, auditoria, codificação segura |
| [16-ciso-habilidades.md](16-ciso-habilidades.md) | CISO: auditoria infra, conformidade, resposta a incidentes |
| [20-zero-trust-fluxo.md](20-zero-trust-fluxo.md) | Zero Trust: fluxo em 6 passos, classificação, egress |
| [21-quarentena-disco-pipeline.md](21-quarentena-disco-pipeline.md) | Quarentena de disco: diff, assinaturas, SAST, entropia |
| [27-kill-switch-redis.md](27-kill-switch-redis.md) | Kill switch Redis, gatilhos 80°C/82°C, recuperação |

### Operações e infra
| Doc | Descrição |
|-----|-----------|
| [06-operacoes.md](06-operacoes.md) | Autonomia nível 4, contingência cluster acéfalo, loop de consenso, recuperação |
| [estrategia-uso-hardware-gpu-cpu.md](estrategia-uso-hardware-gpu-cpu.md) | Uso de GPU/CPU, slot único de revisão, batching |
| [38-redis-streams-estado-global.md](38-redis-streams-estado-global.md) | Redis Streams e estado global (detalhado) |
| [39-consumer-groups-pipeline-revisao.md](39-consumer-groups-pipeline-revisao.md) | Consumer groups, slot único code:ready |
| [40-contingencia-cluster-acefalo.md](40-contingencia-cluster-acefalo.md) | Contingência cluster acéfalo (124): heartbeat, branch efêmera, retomada |
| [operacoes-limite-gastos-provedor.md](operacoes-limite-gastos-provedor.md) | Limite de gastos com provedor de nuvem |
| [31-prevencao-riscos-infra.md](31-prevencao-riscos-infra.md) | Prevenção e mitigação de riscos de infra |
| [07-operations/orquestrador-automacao-cluster.md](07-operations/orquestrador-automacao-cluster.md) | Orquestrador (Fase 3): digest, timers cosméticos, autonomia, disjuntor, acéfalo, curador, Slack, aplicar |

### Configuração e setup
| Doc | Descrição |
|-----|-----------|
| [07-configuracao-e-prompts.md](07-configuracao-e-prompts.md) | FinOps, truncamento, perfis por agente, OpenClaw, provedores |
| [09-setup-e-scripts.md](09-setup-e-scripts.md) | Setup "um clique", setup.sh, OpenClaw/Telegram, transcrição áudio |

### Fluxos e exemplos
| Doc | Descrição |
|-----|-----------|
| [08-exemplo-de-fluxo.md](08-exemplo-de-fluxo.md) | Coreografia "Operação 2FA": fases e papéis |
| [fluxo-completo-mermaid.md](fluxo-completo-mermaid.md) | Diagramas Mermaid: componentes, sequência, GPU Lock, governança |
| [42-fluxo-e2e-operacao-2fa.md](42-fluxo-e2e-operacao-2fa.md) | Fluxo E2E Operação 2FA (016): cenário completo |

### Self-improvement e memória
| Doc | Descrição |
|-----|-----------|
| [10-self-improvement-agentes.md](10-self-improvement-agentes.md) | .learnings/, workspace, WAL, promoção para memória |
| [28-memoria-longo-prazo-elite.md](28-memoria-longo-prazo-elite.md) | Memória Elite: 6 camadas, WAL, configuração prática |

### Ferramentas
| Doc | Descrição |
|-----|-----------|
| [11-ferramentas-browser.md](11-ferramentas-browser.md) | agent-browser CLI (navegação, snapshot, sessões) |
| [12-ferramenta-summarize.md](12-ferramenta-summarize.md) | Summarize: URLs, PDFs, áudio, YouTube |
| [20-ferramenta-github-gh.md](20-ferramenta-github-gh.md) | gh CLI: Issues, PRs, CI, API |
| [21-auto-atualizacao-ambiente.md](21-auto-atualizacao-ambiente.md) | Auto-atualização do runtime e skills (cron) |
| [24-busca-web-headless.md](24-busca-web-headless.md) | Busca web headless, extração em markdown |
| [25-api-gateway-integracao-apis.md](25-api-gateway-integracao-apis.md) | API Gateway (Maton): 100+ APIs, OAuth |
| [25-rotacao-tokens-service-account.md](25-rotacao-tokens-service-account.md) | Rotação de tokens, service account |
| [26-dados-watchlist-alertas-simulacao.md](26-dados-watchlist-alertas-simulacao.md) | Dados, watchlist, alertas, simulação (paper) |
| [27-ferramenta-markdown-converter.md](27-ferramenta-markdown-converter.md) | markitdown: PDF, Word, etc. → Markdown |
| [30-exa-web-search.md](30-exa-web-search.md) | Exa Web Search (MCP): busca neural |
| [31-ollama-local.md](31-ollama-local.md) | Ollama local: modelos, chat, embeddings, tool-use |
| [33-opencode-controller.md](33-opencode-controller.md) | OpenCode Controller: sessões, Plan/Build, Developer |

### Skills e capacidades transversais
| Doc | Descrição |
|-----|-----------|
| [17-escrita-humanizada.md](17-escrita-humanizada.md) | Remoção de padrões de texto de IA, voz natural |
| [18-expertise-documentacao.md](18-expertise-documentacao.md) | Árvore de decisão, busca em docs, citação |
| [19-descoberta-instalacao-skills.md](19-descoberta-instalacao-skills.md) | Descoberta e instalação de skills (Zero Trust) |
| [22-modelos-gratuitos-openrouter-freeride.md](22-modelos-gratuitos-openrouter-freeride.md) | Modelos gratuitos OpenRouter (FreeRide) |
| [23-frontend-design.md](23-frontend-design.md) | Frontend: design thinking, SuperDesign |
| [29-criacao-de-skills.md](29-criacao-de-skills.md) | Criação e evolução de skills |
| [32-ui-ux-pro-max.md](32-ui-ux-pro-max.md) | UI/UX Pro Max: triagem, design system, heurísticas |
| [34-mcp-github-publico.md](34-mcp-github-publico.md) | MCP GitHub público; Zero Trust em código baixado |
| [35-governance-proposer.md](35-governance-proposer.md) | Governance Proposer: rules, soul, skills (PR para Diretor) |
| [13-habilidades-proativas.md](13-habilidades-proativas.md) | Habilidades proativas: WAL, persistência, ADL/VFM |

### Deploy e fases
| Doc | Descrição |
|-----|-----------|
| [37-deploy-fase0-telegram-ceo-ollama.md](37-deploy-fase0-telegram-ceo-ollama.md) | Deploy Fase 0: CEO via Telegram + Ollama no K8s |
| [41-fase1-agentes-soul-pods.md](41-fase1-agentes-soul-pods.md) | Fase 1: Agentes, SOUL, pods |
| [42-slack-tokens-setup.md](42-slack-tokens-setup.md) | Slack: tokens e um app por agente |
| [43-autonomia-nivel-4-matriz-escalonamento.md](43-autonomia-nivel-4-matriz-escalonamento.md) | Autonomia nível 4 (017): matriz, CEO desempate, digest |
| [43-fluxo-slack-all-clawdevsai-tema-analise.md](43-fluxo-slack-all-clawdevsai-tema-analise.md) | Fluxo Slack (canal all-clawdevsai), tema e análise |
| [44-fase2-seguranca-automacao.md](44-fase2-seguranca-automacao.md) | Fase 2: Segurança e automação, phase2-config |

### Meta e referência
| Doc | Descrição |
|-----|-----------|
| [revisoes-analistas-e-termos.md](revisoes-analistas-e-termos.md) | Revisões pós-crítica dos analistas e termos-chave. |

### Auto-evolução e governança
| Doc | Descrição |
|-----|-----------|
| [36-auto-evolucao-clawdevs.md](36-auto-evolucao-clawdevs.md) | Auto-evolução: #self_evolution, só Diretor inicia/para |

---

## Pastas de referência

| Pasta | Conteúdo |
|-------|----------|
| [issues/](issues/README.md) | Backlog de desenvolvimento (64 issues), ordenado por fases |
| [agents-devs/](agents-devs/README.md) | Docs operacionais: templates, protocolos, checklists (SESSION-STATE, WAL, MEMORY, QA auditor) |
| [soul/](soul/README.md) | Identidade de cada agente (SOUL): alma, tom, valores, frase de efeito |
| [scripts/](scripts/) | Scripts referenciados (verify-gpu-cluster, m4a_to_md, gpu_lock, verify-machine) |

---

## Lista por prefixo numérico (arquivos na raiz de docs/)

Alguns números têm mais de um arquivo (ex.: 25, 27, 31, 42, 43); o nome completo do arquivo desambigua.

| Prefixo | Arquivos |
|---------|----------|
| 00 | 00-objetivo-e-maquina-referencia.md |
| 01 | 01-visao-e-proposta.md |
| 02–09 | 02-agentes, 03-arquitetura, 04-infraestrutura, 05-seguranca-e-etica, 06-operacoes, 07-configuracao-e-prompts, 08-exemplo-de-fluxo, 09-setup-e-scripts |
| 10–19 | 10-self-improvement, 11-ferramentas-browser, 12-ferramenta-summarize, 13-habilidades-proativas, 14-seguranca-runtime, 15-seguranca-owasp, 16-ciso-habilidades, 17-escrita-humanizada, 18-expertise-documentacao, 19-descoberta-instalacao-skills |
| 20–21 | 20-zero-trust-fluxo, 20-ferramenta-github-gh • 21-quarentena-disco-pipeline, 21-auto-atualizacao-ambiente |
| 22–30 | 22-modelos-freeride, 23-frontend-design, 24-busca-web-headless, 25-api-gateway, 25-rotacao-tokens • 26-dados-watchlist, 27-kill-switch-redis, 27-ferramenta-markdown-converter • 28-memoria-longo-prazo, 29-criacao-de-skills, 30-exa-web-search |
| 31–36 | 31-prevencao-riscos-infra, 31-ollama-local • 32-ui-ux-pro-max, 33-opencode-controller, 34-mcp-github-publico, 35-governance-proposer, 36-auto-evolucao-clawdevs |
| 37–44 | 37-deploy-fase0, 38-redis-streams, 39-consumer-groups, 40-contingencia-cluster-acefalo, 41-fase1-agentes, 42-slack-tokens-setup, 42-fluxo-e2e-operacao-2fa, 43-autonomia-nivel-4, 43-fluxo-slack-all-clawdevsai, 44-fase2-seguranca |

Documentos sem número: `estrategia-uso-hardware-gpu-cpu.md`, `fluxo-completo-mermaid.md`, `openclaw-sub-agents-architecture.md`, `operacoes-limite-gastos-provedor.md`.
