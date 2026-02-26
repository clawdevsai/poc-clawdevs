# [team-devs-ai] Definição canônica dos nove agentes

**Fase:** 1 — Agentes  
**Labels:** agents, spec

## Descrição

Implementar a definição canônica dos nove agentes: função, responsabilidades, permissões/restrições, line-up (gestão vs técnico vs guardiões) e pontos de falha. Cada agente deve ter comportamento e restrições codificados (config ou prompts) conforme a doc.

## Critérios de aceite

- [ ] CEO: estratégia, interface com Diretor, sem código, sem aprovar PRs; **filtrar** ideias e tarefas antes de enviar ao PO (opera em modelos nuvem caros — falha se não filtrar = colapso financeiro da API).
- [ ] PO: backlog, Issues GitHub, Kanban, RAG para tarefas; risco de **alucinação de escopo** quando RAG falha (tarefas impossíveis na base atual); **ciclo de rascunho** (draft.2.issue → Architect valida viabilidade → draft_rejected ou aprovado); **não alterar requisitos em desenvolvimento exceto** sob evento **technical_blocker** do Architect; sem internet pública; não cria repositórios.
- [ ] DevOps/SRE: IaC, CI/CD, repositórios, FinOps, code review de infra; admin repos; monitoramento 65%; **zero binários** em skills (apenas texto claro).
- [ ] Architect: **avalia rascunhos** (draft.2.issue), emite draft_rejected ou aprova; **formaliza technical_blocker** quando tarefa em desenvolvimento for inviável; code review, Fitness Functions, ADRs, merge de PRs; não reescreve código; exige testes; rejeita skills com binários (zero binários).
- [ ] Developer: implementação via OpenCode; não faz merge; não altera infra; segue code review.
- [ ] QA: testes, E2E, sandbox; não conserta bugs (cria Issues); bloqueia merge em falhas críticas.
- [ ] CyberSec: segurança, OWASP, SAST/DAST, auditoria de PRs; bloqueia chaves expostas e deps não homologadas.
- [ ] UX: frontend, acessibilidade, code review de UI; não altera estrutura de banco sem consultar Architect.
- [ ] DBA: validação de boas práticas e normativa de banco; prioridade a alta performance e baixíssimo custo de hardware/espaço; queries precisas e configuração; code review da camada de dados (migrations, schema, queries, índices); bloqueio de merge quando violação grave de padrões ou risco de performance.
- [ ] Tabela de conflitos e soluções implementada ou documentada (quem barra o quê), incluindo "**Timing loop, nada entregue**" para mudança de escopo (PO no meio da sprint) e exceção technical_blocker.

## Referências

- [02-agentes.md](../02-agentes.md)
