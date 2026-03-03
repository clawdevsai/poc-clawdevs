# [team-devs-ai] Memória de longo prazo Elite (seis camadas)

**Fase:** 5 — Self-improvement e memória  
**Labels:** memory, elite

## Descrição

Implementar (ou configurar) o sistema de memória em seis camadas: Hot RAM (SESSION-STATE.md / **Session State**), Warm Store (LanceDB/vetores), Cold Store (Git-Notes opcional), Arquivo curado (MEMORY.md + memory/), Backup em nuvem opcional, Autoextração opcional. Configuração prática: memorySearch, MEMORY.md, memory/logs|projects|groups|system, diários, recall em AGENTS.md. Integrar **gancho de validação de contexto operado localmente** (antes da sumarização na nuvem): modelo local varre o buffer buscando **intenções do usuário ou regras informais que não ganharam tag** → proposta de extração para o **Session State**. E **validação reversa pelo PO**: logo após a sumarização, comparar resumo com **critérios de aceite originais**; se omitir critério fundamental, **PO rejeita o truncamento** e o sistema **reestrutura o bloco** — garantia de qualidade na memória do enxame. Ver [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md).

## Critérios de aceite

- [x] Camada 1 (Hot RAM / Session State): SESSION-STATE.md com estado ativo; sobrevive à compactação. Integração com **gancho de validação de contexto** e **validação reversa (PO)**. **Invariantes de negócio** com tag no estado da sessão; script de limpeza com regex. **Ref:** [memoria-elite-seis-camadas-implementacao.md](../agents-devs/memoria-elite-seis-camadas-implementacao.md) (Camada 1), [SESSION-STATE.example.md](../agents-devs/SESSION-STATE.example.md), [context_validation_hook.py](../../scripts/context_validation_hook.py), [validate_reverse_po_after_summary.sh](../../scripts/validate_reverse_po_after_summary.sh), [compact_preserve_protected.py](../../scripts/compact_preserve_protected.py); [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md) (seção 2.3).
- [x] Camada 2 (Warm Store): busca semântica (memory_search) e higiene (memory_forget) documentadas em [28-memoria-longo-prazo-elite.md](../28-memoria-longo-prazo-elite.md). **MicroADRs** do Architect anexados ao Warm Store (Redis `project:v1:microadr:{id}`; [microadr_generate.py](../../scripts/microadr_generate.py), [slot_revisao_pos_dev.py](../../scripts/slot_revisao_pos_dev.py)). **Ref:** [memoria-elite-seis-camadas-implementacao.md](../agents-devs/memoria-elite-seis-camadas-implementacao.md) (Camada 2), [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md) §2.3.
- [x] Camada 3 (Cold Store): opcional; decisões branch-aware (Git-Notes) documentadas em [28-memoria-longo-prazo-elite.md](../28-memoria-longo-prazo-elite.md) e em [memoria-elite-seis-camadas-implementacao.md](../agents-devs/memoria-elite-seis-camadas-implementacao.md).
- [x] Camada 4: MEMORY.md e memory/ (diários, destilação); instruções por momento da sessão em doc 28. **Ref:** [MEMORY.md](../agents-devs/MEMORY.md), [config/openclaw/workspace-ceo/MEMORY.md](../../config/openclaw/workspace-ceo/MEMORY.md), [memory/working-buffer.md](../../config/openclaw/workspace-ceo/memory/working-buffer.md), doc 28 "Instruções por momento da sessão".
- [x] Camadas 5 e 6 opcionais documentadas (cloud backup, autoextração) em [28-memoria-longo-prazo-elite.md](../28-memoria-longo-prazo-elite.md) e em [memoria-elite-seis-camadas-implementacao.md](../agents-devs/memoria-elite-seis-camadas-implementacao.md).
- [x] Troubleshooting e recall no início da sessão ("não tenho essa informação" só após memory_search) em [28-memoria-longo-prazo-elite.md](../28-memoria-longo-prazo-elite.md) (instruções início da sessão, Configuração prática §5 e §6, tabela "Por que a memória falha"); resumo em [memoria-elite-seis-camadas-implementacao.md](../agents-devs/memoria-elite-seis-camadas-implementacao.md) §Troubleshooting.

## Referências

- [28-memoria-longo-prazo-elite.md](../28-memoria-longo-prazo-elite.md)
- [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md) (Gancho de validação de contexto, validação reversa PO)
