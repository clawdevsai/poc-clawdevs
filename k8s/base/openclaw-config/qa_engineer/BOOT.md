# BOOT.md - QA_Engineer

## Sequência de Boot

1. Carregar `IDENTITY.md`.
2. Carregar `AGENTS.md`.
3. Ler `README.md` do repositório para entender a aplicação e stack de testes.
4. Carregar `SOUL.md`.
5. Carregar `INPUT_SCHEMA.json`.
6. Ler `/data/openclaw/memory/shared/SHARED_MEMORY.md` — aplicar padrões globais do time como contexto base.
7. Ler `/data/openclaw/memory/qa_engineer/MEMORY.md` — resgatar aprendizados próprios de qualidade relevantes.
8. Validar `/data/openclaw/` e workspace de testes.
9. Detectar tipo de aplicação (web/mobile/api) pelo projeto ou task.
10. Verificar toolchain de testes no PATH:
    - Web: `npx playwright`, `npx cypress`
    - Mobile: `npx detox`, `maestro`
    - Carga: `k6`, `locust`
    - Contrato: `pact`
11. Verificar presença de SPEC para tasks delegadas (`/data/openclaw/backlog/specs/`).
12. Ao concluir a sessão: registrar até 3 aprendizados em `/data/openclaw/memory/qa_engineer/MEMORY.md`.
13. Pronto para receber delegação do Arquiteto ou dev agents.

## healthcheck
- `/data/openclaw/` acessível? ✅
- INPUT_SCHEMA.json carregado? ✅
- Tipo de aplicação detectado? ✅
- SHARED_MEMORY.md e MEMORY.md (qa_engineer) lidos? ✅
- `ACTIVE_GITHUB_REPOSITORY` definido? ✅
