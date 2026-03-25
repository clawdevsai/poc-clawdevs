# BOOT.md - Dev_Frontend

## Sequência de Boot

1. Carregar `IDENTITY.md`.
2. Carregar `AGENTS.md`.
3. Ler `README.md` do repositório para entender a aplicação, stack e fluxo antes de implementar.
4. Carregar `SOUL.md`.
5. Carregar `INPUT_SCHEMA.json`.
6. Ler `/data/openclaw/memory/shared/SHARED_MEMORY.md` — aplicar padrões globais do time como contexto base.
7. Ler `/data/openclaw/memory/dev_frontend/MEMORY.md` — resgatar aprendizados próprios de frontend relevantes.
8. Validar `/data/openclaw/` e workspace de implementação.
9. Detectar framework frontend pelo `technology_stack` da task ou por arquivos do projeto (`package.json`, `next.config.js`, `vite.config.ts`).
10. Carregar comandos padrão por framework.
11. Validar ferramentas: `read`, `write`, `exec`, `git`, `sessions_send`.
12. Verificar comandos via `exec`: `gh`, `web-search`, `web-read`.
13. Carregar metas de performance: Core Web Vitals (LCP < 2.5s, FID < 100ms, CLS < 0.1) e bundle budget.
14. Verificar presença de artefatos UX em `/data/openclaw/backlog/ux/` para tasks com escopo visual.
15. Ao concluir a sessão: registrar até 3 aprendizados em `/data/openclaw/memory/dev_frontend/MEMORY.md`.
16. Pronto para receber task do Arquiteto.

## healthcheck
- `/data/openclaw/` acessível? ✅
- INPUT_SCHEMA.json carregado? ✅
- Framework frontend detectado? ✅
- Ferramentas `read`, `write`, `exec`, `git` disponíveis? ✅
- SHARED_MEMORY.md e MEMORY.md (dev_frontend) lidos? ✅
- `ACTIVE_GITHUB_REPOSITORY` definido? ✅
