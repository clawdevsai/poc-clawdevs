# [team-devs-ai] Exemplo de fluxo end-to-end: Operação 2FA

**Fase:** 1 — Agentes  
**Labels:** agents, e2e, demo

## Descrição

Implementar (ou documentar como teste E2E) o fluxo completo "Operação 2FA": do pedido do Diretor até a notificação de conclusão, passando por CEO → PO → DevOps → Developer → Architect → CyberSec → DBA → QA → UX → CEO.

## Critérios de aceite

- [ ] Cenário documentado: "Implementar login com 2FA via e-mail".
- [ ] Fases implementadas ou automatizadas: (1) Planejamento (CEO, PO em nuvem), (2) **Validação de rascunho** (PO publica draft.2.issue → Architect avalia viabilidade → draft_rejected ou aprovado; só então tarefa vai para desenvolvimento), (3) Preparação (DevOps, branch, GPU Lock com TTL dinâmico), (4) Execução (Developer, OpenCode), (5) Revisão (Architect, CyberSec, DBA — schema/queries quando houver camada de dados), (6) Validação (QA, UX), (7) Fechamento (CEO notifica Diretor).
- [ ] Estado e eventos via Redis (diretriz no Redis, Issues no GitHub, draft.2.issue, draft_rejected, code:ready, etc.).
- [ ] Pontos de risco documentados (ex.: loop Architect/Developer; CyberSec barrando falta de TTL; DBA barrando migrations/queries fora do padrão ou com risco de performance). Mudança de escopo em tarefa já em desenvolvimento é **proibida** (exceto sob technical_blocker formalizado pelo Architect).

## Referências

- [08-exemplo-de-fluxo.md](../08-exemplo-de-fluxo.md)
