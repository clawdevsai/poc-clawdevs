# [team-devs-ai] Disjuntor de rejeições de rascunho e autocura RAG

**Fase:** 1 — Agentes / 3 — Operações  
**Labels:** governance, po, architect, rag, orchestrator

## Descrição

Implementar **disjuntor** focado na frequência de rejeições de rascunho (draft_rejected) **por épico**: quando a mesma épico receber 3 rejeições consecutivas do Architect, congelar a tarefa e acionar **RAG health check determinístico** (autocura). Objetivo: intervir **antes** da cota global de degradação (10–15%); evitar loop infinito PO–Architect causado por RAG desatualizado.

## Critérios de aceite

- [ ] **Rastreamento por épico:** orquestrador rastreia rejeições **por épico**. Se a **mesma épico** receber **draft_rejected 3 vezes consecutivas**, a tarefa é **congelada imediatamente** no Redis Streams (estancar o loop).
- [ ] **RAG health check (determinístico):** ao acionar o disjuntor, orquestrador instancia **sessão isolada** (subagente) que executa health check **sem LLM**: (1) checar **datas de indexação** dos documentos que o PO usou vs **último commit na main**; (2) checar se a **estrutura de pastas** mencionada na épico existe no disco; (3) se houver conflito não documentado → **forçar atualização da memória local** do orquestrador (base de conhecimento).
- [ ] **Descongelar com contexto saneado:** ao descongelar a épico, o PO recebe a rejeição **envelopada no contexto saneado** (documentação/indexação atualizada). Outras tarefas seguem rodando; não é necessário humano para desbloquear a autocura.
- [ ] Disjuntor atua **antes** da cota global de degradação; não substitui o orçamento de degradação, complementa-o.

## Referências

- [06-operacoes.md](../06-operacoes.md) (Disjuntor de draft_rejected)
- [03-arquitetura.md](../03-arquitetura.md) (Ciclo de rascunho)
- [soul/PO.md](../soul/PO.md)
- [soul/Architect.md](../soul/Architect.md)
