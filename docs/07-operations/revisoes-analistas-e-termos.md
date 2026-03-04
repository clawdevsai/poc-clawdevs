# Revisões pós-crítica dos analistas e termos-chave

Este documento concentra os **ajustes pós-crítica** incorporados à documentação e os **termos-chave** para evitar ambiguidade. Para o índice completo dos documentos, use [INDEX.md](INDEX.md). Para visão geral do projeto, use [README.md](README.md).

---

## Revisões pós-crítica dos analistas

A documentação foi revisada conforme críticas dos analistas para reduzir riscos estruturais:

- **Gargalo GPU:** Validação pré-GPU em CPU (SLM para sintaxe, lint e SOLID antes do lock); batching de PRs; **pipeline explícito e slot único de revisão** (um consumidor GPU por etapa). Ver [03-arquitetura.md](03-arquitetura.md), [04-infraestrutura.md](04-infraestrutura.md), [06-operacoes.md](06-operacoes.md), [estrategia-uso-hardware-gpu-cpu.md](estrategia-uso-hardware-gpu-cpu.md), [issues/125-pipeline-explicito-slot-unico-revisao.md](issues/125-pipeline-explicito-slot-unico-revisao.md).

- **Zero Trust / fadiga de alertas:** Sandbox para URLs/APIs desconhecidas; acelerador preditivo de tokens; freio $5/dia e auditoria mantidos. Ver [05-seguranca-e-etica.md](05-seguranca-e-etica.md), [14-seguranca-runtime-agentes.md](14-seguranca-runtime-agentes.md), [07-configuracao-e-prompts.md](07-configuracao-e-prompts.md), [22-modelos-gratuitos-openrouter-freeride.md](22-modelos-gratuitos-openrouter-freeride.md).

- **Governança CEO:** Fitness function no raciocínio (VFM_CEO_score.json, issue 129); token bucket para eventos de estratégia; degradação por eficiência; $5/dia como freio de emergência. Ver [07-configuracao-e-prompts.md](07-configuracao-e-prompts.md), [05-seguranca-e-etica.md](05-seguranca-e-etica.md), [03-arquitetura.md](03-arquitetura.md), [soul/CEO.md](soul/CEO.md), [issues/129-ceo-vfm-fitness-no-raciocinio.md](issues/129-ceo-vfm-fitness-no-raciocinio.md).

- **Quarentena de código de terceiros:** Matriz de confiança (assinaturas), SAST leve, entropia contextual; Zero Trust em código baixado (MCP GitHub, Exa, etc.). Ver [05-seguranca-e-etica.md](05-seguranca-e-etica.md), [14-seguranca-runtime-agentes.md](14-seguranca-runtime-agentes.md), [34-mcp-github-publico.md](34-mcp-github-publico.md).

- **Loop PO–Architect (draft_rejected):** Disjuntor por épico (3 rejeições → congelar, RAG health check). Ver [06-operacoes.md](06-operacoes.md), [03-arquitetura.md](03-arquitetura.md), [soul/PO.md](soul/PO.md), [soul/Architect.md](soul/Architect.md).

- **Five strikes:** Fallback contextual (2º strike → Architect; 5º → arbitragem nuvem); aprovação por omissão só cosmética (6 h). Ver [06-operacoes.md](06-operacoes.md), [01-visao-e-proposta.md](01-visao-e-proposta.md), [07-configuracao-e-prompts.md](07-configuracao-e-prompts.md), [soul/Architect.md](soul/Architect.md).

- **Autoaprendizado e curadoria:** Promoção de `.learnings/` via merge request formal (pre-flight QA+CyberSec, CronJob curador). Ver [10-self-improvement-agentes.md](10-self-improvement-agentes.md), [03-arquitetura.md](03-arquitetura.md).

- **Limites VFM e ADL:** Funções de aptidão e auditoria determinística; microADR com regex contra justificativas fracas. Ver [13-habilidades-proativas.md](13-habilidades-proativas.md), [07-configuracao-e-prompts.md](07-configuracao-e-prompts.md), [05-seguranca-e-etica.md](05-seguranca-e-etica.md), [soul/CEO.md](soul/CEO.md).

- **Persistência + FinOps:** Diversidade de ferramenta (bloqueio após 2 falhas consecutivas); contador no Gateway; degradação graciosa. Ver [13-habilidades-proativas.md](13-habilidades-proativas.md), [06-operacoes.md](06-operacoes.md), [10-self-improvement-agentes.md](10-self-improvement-agentes.md).

- **Contingência cluster acéfalo:** Protocolo 100% local; branch efêmera, LanceDB, retomada automática (health check, 3 ciclos); notificação assíncrona. Ver [06-operacoes.md](06-operacoes.md), [issues/124-contingencia-cluster-acefalo.md](issues/124-contingencia-cluster-acefalo.md).

- **Segregação critérios de aceite:** Tag de proteção ou payload duplo; PO sempre recebe critérios intactos. Ver [07-configuracao-e-prompts.md](07-configuracao-e-prompts.md), [28-memoria-longo-prazo-elite.md](28-memoria-longo-prazo-elite.md), [issues/041-truncamento-contexto-finops.md](issues/041-truncamento-contexto-finops.md).

- **Loop de consenso e recuperação:** Pré-freio (QA+Architect); relatório de degradação; comando explícito de desbloqueio. Ver [06-operacoes.md](06-operacoes.md), [issues/017-autonomia-nivel-4-matriz-escalonamento.md](issues/017-autonomia-nivel-4-matriz-escalonamento.md).

---

## Termos-chave

| Termo | Definição |
|-------|-----------|
| **Evento de estratégia** | Evento do CEO no stream com tag de comando/diretriz (ex.: canal `cmd:strategy`). |
| **Token bucket** | Mecanismo no Gateway que limita eventos de estratégia por janela (ex.: 5/hora). |
| **Degradação por eficiência** | Razão ideias CEO vs tarefas aprovadas pelo PO; abaixo do limiar → CEO em modelo local CPU. |
| **Disjuntor (draft_rejected)** | Mesma épico com 3 rejeições consecutivas de rascunho → congelar tarefa e RAG health check. |
| **RAG health check (determinístico)** | Verificação sem LLM: datas de indexação vs main, estrutura de pastas; conflito → atualizar orquestrador. |
| **SAST leve (sandbox)** | Análise estática (ex.: semgrep) no sandbox, regras estritas. |
| **Entropia (contextual)** | Analisador com whitelist de extensões (.map, .wasm, .min.js); matriz de confiança pode dispensar. |
| **Relação entre mecanismos** | Freio $5/dia = último recurso; token bucket e degradação = controle primário. Disjuntor atua por épico antes da cota global. Quarentena: diff → assinaturas → SAST → entropia. |

---

## Terminologia geral

- **Criador do ClawDevs:** Diego Silva Morais.
- **Diretor:** Humano decisor; único ponto de aprovação para decisões críticas.
- **Agente CEO:** Estratégia e interface com o Diretor.
- **OpenClaw:** Orquestrador e interface (voz/chat); pods CEO e PO.
- **Ollama:** Inferência local no cluster (Developer, Architect, QA, etc.).
- **OpenRouter:** API de modelos em nuvem (ex.: FreeRide). Provedores ClawDevs = apenas os integrados OpenClaw (Ollama cloud, OpenRouter, Qwen, Moonshot AI, OpenAI, Hugging Face).
- **OpenCode:** Geração de código no pod do Developer.
- **ClawDevs:** Nome do ecossistema — enxame de 9 agentes em K8s com OpenClaw.
- **Enxame:** Os nove agentes de IA do ClawDevs no cluster.
- **draft.2.issue:** Evento de rascunho PO→Architect; PO publica rascunho para Architect validar viabilidade. Ver [02-agentes.md](02-agentes.md) e [03-arquitetura.md](03-arquitetura.md).
