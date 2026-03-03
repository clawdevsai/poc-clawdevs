# Memória Elite (seis camadas) — Implementação no repositório

Mapeamento das **seis camadas** para artefatos, scripts e documentação (issue 052). Modelo completo em [28-memoria-longo-prazo-elite.md](../28-memoria-longo-prazo-elite.md).

---

## Camada 1: Hot RAM (Session State)

| Requisito | Artefato no repo |
|-----------|-------------------|
| SESSION-STATE.md com estado ativo; sobrevive à compactação | [SESSION-STATE.example.md](SESSION-STATE.example.md); workspace: `config/openclaw/workspace-ceo/` (SOUL + soul-merge para outros agentes) |
| Gancho de validação de contexto (intenções/regras sem tag → Session State) | [scripts/context_validation_hook.py](../../scripts/context_validation_hook.py) |
| Validação reversa PO (resumo vs critérios de aceite; rejeitar truncamento) | [scripts/validate_reverse_po_after_summary.sh](../../scripts/validate_reverse_po_after_summary.sh), [validate_reverse_po.py](../../scripts/validate_reverse_po.py) |
| Invariantes de negócio com tag; script de limpeza que nunca remove linhas tagadas | Tag `<!-- INVARIANTE_NEGOCIO -->` em SESSION-STATE; [scripts/compact_preserve_protected.py](../../scripts/compact_preserve_protected.py) (regex preserva bloco) |
| WAL (escrever antes de responder) | [protocolo-wal-working-buffer.md](protocolo-wal-working-buffer.md) |

Ref: [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md) §2.2 e §2.3.

---

## Camada 2: Warm Store (vetores / LanceDB)

| Requisito | Artefato no repo |
|-----------|-------------------|
| Busca semântica (memory_search) configurada ou documentada | [28-memoria-longo-prazo-elite.md](../28-memoria-longo-prazo-elite.md) — Configuração prática §1 (memorySearch.enabled, provider, minScore, maxResults) |
| Higiene (memory_forget) para remover ruído | Doc 28 — Higiene de memória; Warm Store: listar e remover vetores irrelevantes |
| MicroADRs do Architect (imutáveis, nunca sumarizados) anexados ao Warm Store | [scripts/microadr_generate.py](../../scripts/microadr_generate.py); [slot_revisao_pos_dev.py](../../scripts/slot_revisao_pos_dev.py) chama ao aprovar; Redis `project:v1:microadr:{issue_id}` (Warm Store/LanceDB consome quando habilitado) |
| Template microADR | [microADR-template.json](microADR-template.json) (se existir) ou estrutura em microadr_generate.py |

Ref: [07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md) §2.3.

---

## Camada 3: Cold Store (Git-Notes) — opcional

Decisões estruturadas branch-aware. Documentado em [28-memoria-longo-prazo-elite.md](../28-memoria-longo-prazo-elite.md) (Camada 3). Implementação: script/tool Git-Notes no workspace ou skill externa; instalação conforme [19-descoberta-instalacao-skills.md](../19-descoberta-instalacao-skills.md) e Zero Trust.

---

## Camada 4: Arquivo curado (MEMORY.md + memory/)

| Requisito | Artefato no repo |
|-----------|-------------------|
| MEMORY.md (memória curada, decisões, lições, preferências) | [MEMORY.md](MEMORY.md) (decisões por omissão cosmética); template em doc 28 §3; workspace: [config/openclaw/workspace-ceo/MEMORY.md](../../config/openclaw/workspace-ceo/MEMORY.md) |
| memory/ (diários, destilação) | `memory/working-buffer.md` em workspace-ceo; doc 28: memory/logs, projects, groups, system |
| Instruções por momento da sessão | [28-memoria-longo-prazo-elite.md](../28-memoria-longo-prazo-elite.md) — "Instruções por momento da sessão" (início, durante, encerramento) |

Ref: [10-self-improvement-agentes.md](../10-self-improvement-agentes.md), [13-habilidades-proativas.md](../13-habilidades-proativas.md).

---

## Camadas 5 e 6: Cloud backup e autoextração — opcionais

- **Camada 5 (Cloud backup):** SuperMemory; documentado em doc 28; configurar só com aprovação do Diretor e credenciais seguras.
- **Camada 6 (Autoextração):** Mem0 para redução de tokens; documentado em doc 28; `MEM0_API_KEY` em ambiente controlado.

---

## Troubleshooting e recall no início da sessão

| Regra | Onde está |
|-------|-----------|
| "Não tenho essa informação" só **após** memory_search | [28-memoria-longo-prazo-elite.md](../28-memoria-longo-prazo-elite.md) — Instruções no início da sessão: ler SESSION-STATE, executar memory_search, verificar diário |
| Instruções para AGENTS.md (recall) | Doc 28 — Configuração prática §5 (memory_search, memory_get, confiança baixa → informar que verificou) |
| Por que a memória falha (tabela) | Doc 28 — "Por que a memória falha (e como corrigir)" |
| Troubleshooting memorySearch | Doc 28 — Configuração prática §6 (busca não funciona, resultados irrelevantes, erros de provedor) |

---

## Resumo de scripts e configs

| Script / config | Uso |
|----------------|-----|
| `compact_preserve_protected.py` | Compactar buffer preservando CRITERIOS_ACEITE e INVARIANTE_NEGOCIO |
| `context_validation_hook.py` | Propor extração de intenções/regras para SESSION-STATE antes da sumarização |
| `validate_reverse_po_after_summary.sh` / `validate_reverse_po.py` | Validação reversa PO (resumo vs critérios) |
| `microadr_generate.py` | Gerar e armazenar microADR no Redis (slot chama ao aprovar) |
| `slot_revisao_pos_dev.py` | Revisão pós-dev; gera microADR ao aprovar |
| ConfigMap `finops-config` | Tags e limites (TTL, regex) para truncamento e invariantes |

Ref: [issues/052-memoria-elite-seis-camadas.md](../issues/052-memoria-elite-seis-camadas.md).
