# Referência: evolucao-memoria-openclaw.pdf × repositório

**Fonte:** `evolucao-memoria-openclaw.pdf` (Bruno Okamoto, Fev/2026). Este doc mapeia as recomendações do PDF ao estado atual do ClawDevs para que nada fique sem registro.

## Configuração openclaw.json (Fases 3 e 4 do PDF)

| Recomendação PDF | Onde no repo | Estado |
|------------------|--------------|--------|
| **compaction** + memoryFlush (40k tokens, prompt categorizado) | [k8s/management-team/openclaw/configmap.yaml](../../k8s/management-team/openclaw/configmap.yaml) — bloco `compaction` | Implementado |
| **contextPruning** (TTL 6h, keepLastAssistants: 3) | Mesmo ConfigMap — bloco `contextPruning` | Implementado |
| **memorySearch** híbrido (BM25 + Vector, vectorWeight/textWeight 0.5) | Mesmo ConfigMap — bloco `memorySearch` | Implementado |

## Estrutura de workspace (memória por domínio + shared)

| Recomendação PDF | Onde no repo | Estado |
|------------------|--------------|--------|
| **memory/** por agente (decisions, projects, **people**, lessons, pending, journal) | [k8s/management-team/openclaw/init-memory-configmap.yaml](../../k8s/management-team/openclaw/init-memory-configmap.yaml) + Job init-memory-structure. PDF Fase 3: people.md = equipe e contatos. | Implementado |
| **/workspace/shared/memory/** (strategy, architecture, backlog, incidents) | Mesmo init-memory | Implementado |
| **.learnings/** (LEARNINGS.md, ERRORS.md, FEATURE_REQUESTS.md) | Mesmo init-memory (criado no bootstrap) | Implementado |

## Fluxo de aprendizado e curadoria

| Recomendação PDF / doc | Onde no repo | Estado |
|------------------------|--------------|--------|
| Curadoria em sessão isolada (CronJob, Architect/CyberSec) | [k8s/orchestrator/cronjob-curator.yaml](../../k8s/orchestrator/cronjob-curator.yaml), configmap-curator-env, configmap-curator-scripts | Implementado |
| Init-memory no fluxo de subida | [Makefile](../../Makefile) — target `up` chama init-memory após deploy OpenClaw | Implementado |
| Placeholder **{agentId}** no prompt de compaction | Documentado em [openclaw-config-ref.md](openclaw-config-ref.md) § Compaction e memory flush | Documentado |

## O que pode “passar” (validar ou opcional)

- **memorySearch.provider / embeddings:** O PDF pode citar provedor de embeddings (ex.: Voyage, OpenAI) para busca vetorial. No config atual há `memorySearch.query.hybrid`; se o OpenClaw exigir `provider` ou chaves (ex. `OPENAI_API_KEY`) para o híbrido funcionar, configurar conforme [28-memoria-longo-prazo-elite.md](../07-operations/28-memoria-longo-prazo-elite.md) § Configuração prática.
- **Camadas opcionais (Cold Store, cloud, autoextração):** Doc 28 descreve seis camadas; no repo estão cobertas as camadas de arquivo (memory/, shared, .learnings) e o flush pré-compaction. Git-Notes, backup nuvem e Mem0/autoextração são opcionais e podem ser adicionados depois.
- **Pre-flight automatizado (QA + CyberSec antes do curador):** O protocolo em [10-self-improvement-agentes.md](../03-agents/10-self-improvement-agentes.md) descreve filtro sanitário e agentes guardiões; a automação desse pre-flight pode ser tarefa futura (hoje o CronJob só dispara o Architect com o prompt de curadoria).

## Resumo

Nada do escopo principal do PDF (compaction, contextPruning, memorySearch, estrutura memory + shared + .learnings, curadoria em sessão isolada, init no `up`, placeholder {agentId}) ficou sem implementação ou documentação. Os itens acima na seção “O que pode passar” são refinamentos ou opcionais para validar conforme o uso.
