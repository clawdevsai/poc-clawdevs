# [team-devs-ai] Redis Streams e estado global (Event Bus)

**Fase:** 0 — Fundação  
**Labels:** foundation, architecture, redis

## Descrição

Implementar a orquestração orientada a eventos com estado centralizado em Redis Streams. Agentes não se chamam diretamente; ficam em idle e são acordados por eventos. Estado da verdade (The Global State) em chaves Redis; transmissão de ID de transação em vez de JSONs grandes.

## Critérios de aceite

- [ ] Redis Streams configurado com canais/streams para eventos (ex.: `cmd:strategy`, `task:backlog`, `code:ready`, **`draft.2.issue`**, **`draft_rejected`** para ciclo de rascunho PO/Architect).
- [ ] Convenção de chaves para estado (ex.: `project:v1:issue:42`) documentada e usada pelo PO e Developer.
- [ ] Consumidores (agentes) assinam os streams e processam em reação a eventos (sem polling ocupado).
- [ ] **Ciclo de rascunho:** PO publica `draft.2.issue`; Architect avalia viabilidade técnica; se impossível, retorna `draft_rejected` e o PO reescreve antes da tarefa ir para `task:backlog`/desenvolvimento.
- [ ] Documentação do fluxo de dados (diagrama ou texto): CEO → PO → (draft → Architect → aprovado/rejeitado) → DevOps → Developer → Architect/QA/CyberSec/UX.
- [ ] Blackboard: se um pod cair, a tarefa permanece na fila e pode ser retomada.
- [ ] **Semântica idempotente:** consumidor **não** envia ACK até o trabalho estar **100% concluído em disco**; em pausa brusca (ex.: 82°C) a mensagem permanece pendente e é reentregue na retomada. Ver [06-operacoes.md](../06-operacoes.md).
- [ ] **Evento de checkpoint aos 80°C:** DevOps injeta evento de prioridade máxima no Redis para **commit do estado atual em branch efêmera de recuperação** (ex.: `recovery-failsafe-<timestamp>`) no repositório de trabalho (antes do Q-Suite térmico). Retomada: checkout limpo; Architect resolve conflitos na branch de recuperação quando aplicável. Ver [06-operacoes.md](../06-operacoes.md) e [027-kill-switch-networkpolicy.md](027-kill-switch-networkpolicy.md).

## Referências

- [03-arquitetura.md](../03-arquitetura.md)
