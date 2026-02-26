# [team-devs-ai] Workspace OpenClaw e self-improvement (.learnings/)

**Fase:** 5 — Self-improvement e memória  
**Labels:** memory, self-improvement, openclaw

## Descrição

Estrutura do workspace OpenClaw: AGENTS.md, SOUL.md, TOOLS.md, SESSION-STATE, MEMORY.md, memory/, .learnings/ (LEARNINGS.md, ERRORS.md, FEATURE_REQUESTS.md). Fluxo de registro (quando registrar em cada arquivo) e **promoção para memória via curadoria centralizada** — sem promoção orgânica direta pelos agentes, para evitar conflitos entre nove agentes em paralelo (learnings contraditórios e corrupção do arquivo de identidade central).

## Critérios de aceite

- [ ] Estrutura de diretórios e arquivos criada (ou documentada para criação pelo setup): workspace com AGENTS.md, SOUL.md, TOOLS.md, SESSION-STATE.md, MEMORY.md, memory/, .learnings/ com LEARNINGS.md, ERRORS.md, FEATURE_REQUESTS.md.
- [ ] Regras de quando registrar: falha de comando → ERRORS.md; correção do Diretor → LEARNINGS.md (category: correction); pedido de capacidade inexistente → FEATURE_REQUESTS.md; knowledge_gap/best_practice → LEARNINGS.md.
- [ ] Formato de registros (ID, data, categoria, conteúdo) documentado.
- [ ] **Curadoria centralizada:** Nenhum agente promove diretamente para SOUL.md, AGENTS.md ou TOOLS.md. Promoção é **processo formal de merge request** com (1) **protocolo de consenso (pre-flight):** sumarização prévia e avaliação por agentes guardiões (QA + CyberSec) para garantir que o learning não viole OWASP/limites do projeto; itens rejeitados não entram na fila do curador; (2) **sessão isolada (CronJob):** agente curador (Architect ou CyberSec) em janela dedicada, lê .learnings/ não processados, resolve contradições, gera artefato consolidado e injeta de forma segura nos arquivos globais. Ver [03-arquitetura.md](../03-arquitetura.md) (Merge de conhecimento).
- [ ] Revisão de .learnings/ antes de tarefas maiores e ao concluir features; elegibilidade para curadoria conforme critérios acima.

## Referências

- [10-self-improvement-agentes.md](../10-self-improvement-agentes.md)
- [03-arquitetura.md](../03-arquitetura.md) (Merge de conhecimento)
