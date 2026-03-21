# BOOT.md - QA_Engineer

Ao iniciar:
1. Carregar `IDENTITY.md`.
2. Carregar `AGENTS.md`.
3. Ler `README.md` do repositório para entender a aplicação e stack de testes.
4. Carregar `SOUL.md`.
5. Carregar `INPUT_SCHEMA.json`.
6. Validar `/data/openclaw` e workspace de testes.
7. Detectar tipo de aplicação (web/mobile/api) pelo projeto ou task.
8. Verificar toolchain de testes no PATH:
   - Web: `npx playwright`, `npx cypress`
   - Mobile: `npx detox`, `maestro`
   - Carga: `k6`, `locust`
   - Contrato: `pact`
9. Verificar presença de SPEC para tasks delegadas (`/data/openclaw/backlog/specs/`).
10. Pronto para receber delegação do Arquiteto ou dev agents.
