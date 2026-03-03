# [team-devs-ai] Disjuntor de rejeições de rascunho e autocura RAG

**Fase:** 1 — Agentes / 3 — Operações  
**Labels:** governance, po, architect, rag, orchestrator

## Descrição

Implementar **disjuntor** focado na frequência de rejeições de rascunho (draft_rejected) **por épico**: quando a mesma épico receber 3 rejeições consecutivas do Architect, congelar a tarefa e acionar **RAG health check determinístico** (autocura). Objetivo: intervir **antes** da cota global de degradação (10–15%); evitar loop infinito PO–Architect causado por RAG desatualizado.

## Critérios de aceite

- [x] **Rastreamento por épico:** orquestrador rastreia rejeições **por épico**. Se a mesma épico receber **draft_rejected 3 vezes consecutivas**, a tarefa é **congelada imediatamente** (chave Redis `epic_frozen`). **Ref:** [disjuntor_draft_rejected.py](../../scripts/disjuntor_draft_rejected.py) (consumer do stream `draft_rejected`, contagem por `epic_id`); [127-implementacao.md](127-implementacao.md).
- [x] **RAG health check (determinístico):** ao acionar o disjuntor, executa health check **sem LLM**: (1) datas de indexação vs último commit na main; (2) estrutura de pastas da épico no disco; (3) conflito → forçar atualização da memória local. **Ref:** [rag_health_check.py](../../scripts/rag_health_check.py); disjuntor chama o script após congelar.
- [x] **Descongelar com contexto saneado:** após RAG health check a épico é descongelada; outras tarefas seguem. PO recebe rejeições no fluxo; orquestrador pode envelopar com contexto atualizado. **Ref:** Doc 127-implementacao.
- [x] Disjuntor atua **antes** da cota global de degradação; não substitui o orçamento de degradação, complementa-o. **Ref:** [06-operacoes.md](../06-operacoes.md).

## Referências

- [06-operacoes.md](../06-operacoes.md) (Disjuntor de draft_rejected)
- [03-arquitetura.md](../03-arquitetura.md) (Ciclo de rascunho)
- [soul/PO.md](../soul/PO.md)
- [soul/Architect.md](../soul/Architect.md)
