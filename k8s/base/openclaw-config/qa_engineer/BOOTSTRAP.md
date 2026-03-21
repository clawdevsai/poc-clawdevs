# BOOTSTRAP.md - QA_Engineer

1. Carregar env:
   - `GITHUB_ORG`
   - `ACTIVE_GITHUB_REPOSITORY`
   - `OPENCLAW_ENV`
   - `PROJECT_ROOT` (default `/data/openclaw/backlog/implementation`)
2. Ler `README.md` do repositório para entender stack e comandos de teste.
3. Detectar tipo de app:
   - `next.config.js` / `vite.config.ts` → web (Playwright/Cypress)
   - `app.json` / `expo.json` → mobile (Detox/Maestro)
   - `package.json` + `express` / `fastapi` → API (k6 + Pact)
4. Verificar toolchain no PATH por tipo.
5. Configurar logger com `task_id` e `test_type`.
6. Configurar retry_counter storage (em memória ou `/data/openclaw/backlog/qa/retries/`).
7. Validar autenticação `gh` para atualização de issues/PRs.
8. Configurar agendamento:
   - intervalo fixo: 60 minutos (offset: :45 de cada hora)
   - origem de trabalho: issues GitHub label `tests`
9. Pronto.
