# Fase 5 — Self-improvement e memória: escopo e ordem

**Fase:** 5 (050–059)  
**Objetivo:** .learnings/, WAL, Working Buffer, memória Elite (6 camadas), recuperação pós-compactação.

## Issues da fase

| # | Issue | Título | Ordem sugerida |
|---|-------|--------|----------------|
| 050 | [050-workspace-learnings-self-improvement.md](050-workspace-learnings-self-improvement.md) | Workspace e self-improvement (.learnings/) | 1 |
| 051 | [051-protocolo-wal-working-buffer.md](051-protocolo-wal-working-buffer.md) | Protocolo WAL e Working Buffer | 2 ✅ |
| 052 | [052-memoria-elite-seis-camadas.md](052-memoria-elite-seis-camadas.md) | Memória Elite (seis camadas) | 3 ✅ |
| 053 | [053-habilidades-proativas-heartbeat.md](053-habilidades-proativas-heartbeat.md) | Habilidades proativas e heartbeat | 4 ✅ |

## Ordem de implementação

1. **050** — Estrutura do workspace com `.learnings/` (LEARNINGS.md, ERRORS.md, FEATURE_REQUESTS.md), regras de registro e formato documentados; curadoria centralizada (pre-flight + sessão isolada) já descrita em [10-self-improvement-agentes.md](../10-self-improvement-agentes.md) e [03-arquitetura.md](../03-arquitetura.md).
2. **051** — WAL (parar → escrever SESSION-STATE.md → responder), Working Buffer (memory/working-buffer.md) após 60% contexto, integração com gancho de validação de contexto (041).
3. **052** — Seis camadas (Hot RAM/Session State, Warm Store, Cold Store, MEMORY.md + memory/, backup/autoextração opcionais); microADRs no Warm Store; invariantes com tag + regex no script DevOps.
4. **053** — Habilidades proativas e heartbeat (opcional na Fase 5 mínima).

## Dependências

- **041** (truncamento, validação reversa PO, gancho de contexto): já implementado; 051 e 052 referenciam o gancho.
- **040** (perfis, FinOps): concluído na Fase 4.

## Referências

- [docs/10-self-improvement-agentes.md](../10-self-improvement-agentes.md) — Estrutura workspace, quando registrar, formato, curadoria.
- [docs/28-memoria-longo-prazo-elite.md](../28-memoria-longo-prazo-elite.md) — Seis camadas, memorySearch, recall.
- [docs/07-configuracao-e-prompts.md](../07-configuracao-e-prompts.md) — Gancho de validação de contexto, invariantes, microADRs.
