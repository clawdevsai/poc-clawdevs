# BOOTSTRAP.md - Dev_Frontend

1. Carregar env:
   - `GITHUB_ORG`
   - `ACTIVE_GITHUB_REPOSITORY`
   - `OPENCLAW_ENV`
   - `PROJECT_ROOT` (default `/data/openclaw/backlog/implementation`)
2. Ler `README.md` do repositório para entender aplicação, stack e fluxo antes de implementar.
3. Validar estrutura base:
   - `${PROJECT_ROOT}`
   - `${PROJECT_ROOT}/src` ou `${PROJECT_ROOT}/app` (Next.js App Router)
   - `${PROJECT_ROOT}/components` ou `${PROJECT_ROOT}/src/components`
4. Detectar framework por arquivos de build:
   - `next.config.js` / `next.config.ts` → Next.js
   - `vite.config.ts` → Vite / React
   - `nuxt.config.ts` → Nuxt
   - `package.json` → verificar campo `"scripts"` para inferir framework
5. Definir comandos padrão (install/test/lint/build) por framework.
6. Verificar toolchain no PATH: `node`, `npm`, `npx`.
7. Verificar presença de Playwright ou Cypress para e2e.
8. Configurar logger com `task_id` e `framework`.
9. Configurar baseline de performance:
   - Core Web Vitals: LCP < 2.5s, FID < 100ms, CLS < 0.1
   - Bundle size budget: documentar por page/component
10. Verificar presença de artefatos UX em `/data/openclaw/backlog/ux/` antes da implementação.
11. Habilitar pesquisa técnica na internet para otimização de performance e acessibilidade.
12. Validar autenticação `gh` e permissões do repositório ativo.
13. Configurar agendamento:
    - intervalo fixo: 60 minutos (offset: :15 de cada hora)
    - origem de trabalho: issues GitHub label `front_end`
14. Pronto.
