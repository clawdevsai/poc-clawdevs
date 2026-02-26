# [team-devs-ai] Memória de longo prazo Elite (seis camadas)

**Fase:** 5 — Self-improvement e memória  
**Labels:** memory, elite

## Descrição

Implementar (ou configurar) o sistema de memória em seis camadas: Hot RAM (SESSION-STATE.md / **Session State**), Warm Store (LanceDB/vetores), Cold Store (Git-Notes opcional), Arquivo curado (MEMORY.md + memory/), Backup em nuvem opcional, Autoextração opcional. Configuração prática: memorySearch, MEMORY.md, memory/logs|projects|groups|system, diários, recall em AGENTS.md. Integrar **gancho de validação de contexto operado localmente** (antes da sumarização na nuvem): modelo local varre o buffer buscando **intenções do usuário ou regras informais que não ganharam tag** → proposta de extração para o **Session State**. E **validação reversa pelo PO**: logo após a sumarização, comparar resumo com **critérios de aceite originais**; se omitir critério fundamental, **PO rejeita o truncamento** e o sistema **reestrutura o bloco** — garantia de qualidade na memória do enxame. Ver [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md).

## Critérios de aceite

- [ ] Camada 1 (Hot RAM / Session State): SESSION-STATE.md com estado ativo; sobrevive à compactação. Integração com **gancho de validação de contexto** (modelo local varre buffer buscando intenções/regras sem tag → proposta de extração para o Session State antes da sumarização na nuvem) e com **validação reversa (PO)** (resumo vs critérios de aceite originais; rejeitar truncamento → reestruturar bloco). Ver [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md). **Invariantes de negócio** com tag especial no estado da sessão; script de limpeza do DevOps com regex para nunca remover linhas tagadas. Ver [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md) (seção 2.3).
- [ ] Camada 2 (Warm Store): busca semântica (memory_search) configurada ou documentada; higiene (memory_forget) para remover ruído. **MicroADRs** do Architect (imutáveis, nunca sumarizados) anexados diretamente ao Warm Store. Ver [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md) (seção 2.3).
- [ ] Camada 3 (Cold Store): opcional; decisões estruturadas branch-aware (Git-Notes ou equivalente).
- [ ] Camada 4: MEMORY.md e memory/ (diários, destilação); instruções por momento da sessão documentadas.
- [ ] Camadas 5 e 6 opcionais documentadas (cloud backup, autoextração).
- [ ] Troubleshooting e recall no início da sessão ("não tenho essa informação" só após memory_search) documentados.

## Referências

- [28-memoria-longo-prazo-elite.md](../28-memoria-longo-prazo-elite.md)
- [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md) (Gancho de validação de contexto, validação reversa PO)
