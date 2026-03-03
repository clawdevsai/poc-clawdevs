# [team-devs-ai] Workspace OpenClaw e self-improvement (.learnings/)

**Fase:** 5 — Self-improvement e memória  
**Labels:** memory, self-improvement, openclaw

## Descrição

Estrutura do workspace OpenClaw: AGENTS.md, SOUL.md, TOOLS.md, SESSION-STATE, MEMORY.md, memory/, .learnings/ (LEARNINGS.md, ERRORS.md, FEATURE_REQUESTS.md). Fluxo de registro (quando registrar em cada arquivo) e **promoção para memória via curadoria centralizada** — sem promoção orgânica direta pelos agentes, para evitar conflitos entre nove agentes em paralelo (learnings contraditórios e corrupção do arquivo de identidade central).

## Critérios de aceite

- [x] Estrutura de diretórios e arquivos criada (ou documentada para criação pelo setup): workspace com AGENTS.md, SOUL.md, TOOLS.md, SESSION-STATE.md, MEMORY.md, memory/, .learnings/ com LEARNINGS.md, ERRORS.md, FEATURE_REQUESTS.md. **No repo:** template em [config/openclaw/workspace-ceo/.learnings/](../../config/openclaw/workspace-ceo/.learnings/) (LEARNINGS.md, ERRORS.md, FEATURE_REQUESTS.md com cabeçalho e formato). Setup local usa `config/openclaw/workspace-ceo` como workspace; criar `.learnings/` lá se não existir (já presente no template).
- [x] Regras de quando registrar: falha de comando → ERRORS.md; correção do Diretor → LEARNINGS.md (category: correction); pedido de capacidade inexistente → FEATURE_REQUESTS.md; knowledge_gap/best_practice → LEARNINGS.md. Documentado em [10-self-improvement-agentes.md](../10-self-improvement-agentes.md) (tabela "Quando registrar").
- [x] Formato de registros (ID, data, categoria, conteúdo) documentado em [10-self-improvement-agentes.md](../10-self-improvement-agentes.md) (ID LRN/ERR/FEAT, campos por arquivo).
- [x] **Curadoria centralizada:** Nenhum agente promove diretamente para SOUL.md, AGENTS.md ou TOOLS.md. Promoção é **processo formal de merge request** com (1) **protocolo de consenso (pre-flight):** sumarização prévia e avaliação por agentes guardiões (QA + CyberSec); (2) **sessão isolada (CronJob):** agente curador (Architect ou CyberSec) em janela dedicada. **Documentado** em [03-arquitetura.md](../03-arquitetura.md) (Merge de conhecimento) e [10-self-improvement-agentes.md](../10-self-improvement-agentes.md) (protocolo pre-flight e injeção segura). Implementação operacional (CronJob curador, script pre-flight) pode ser tarefa dedicada ou integrada a 051/052.
- [x] Revisão de .learnings/ antes de tarefas maiores e ao concluir features; elegibilidade para curadoria conforme critérios acima. Documentado em [10-self-improvement-agentes.md](../10-self-improvement-agentes.md) ("Revisar .learnings/ antes de tarefas maiores e ao concluir features").

## Referências

- [10-self-improvement-agentes.md](../10-self-improvement-agentes.md)
- [03-arquitetura.md](../03-arquitetura.md) (Merge de conhecimento)
