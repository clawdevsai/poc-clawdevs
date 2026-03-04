# Disjuntor draft_rejected e RAG health check (127) — Implementação

**Rastreamento por épico:** [scripts/disjuntor_draft_rejected.py](../../scripts/disjuntor_draft_rejected.py) consome o stream `draft_rejected`; usa `epic_id` (ou `issue_id`) para contagem consecutiva em Redis (`project:v1:orchestrator:draft_rejected_consecutive:{epic_id}`). Ao atingir **3 consecutivas**, congela a épico (`epic_frozen`) e aciona RAG health check.

**RAG health check (determinístico):** [scripts/rag_health_check.py](../../scripts/rag_health_check.py) — sem LLM: (1) datas de indexação vs último commit na main; (2) estrutura de pastas da épico no disco; (3) se conflito → forçar atualização da memória local. Disjuntor chama o script após congelar; ao terminar, descongela e reseta contagem.

**Descongelar com contexto saneado:** Após RAG health check, a épico é descongelada; outras tarefas seguem. PO recebe rejeições no fluxo normal; o orquestrador pode envelopar com contexto atualizado (documentação/indexação) conforme integração.

**Ordem:** Disjuntor atua antes da cota global de degradação (06-operacoes); complementa orçamento de degradação.

Ref: [127-disjuntor-draft-rejected-rag-health-check.md](127-disjuntor-draft-rejected-rag-health-check.md), [06-operacoes.md](../06-operacoes.md).
