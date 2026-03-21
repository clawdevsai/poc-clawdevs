# TOOLS.md - Dev_Frontend

## tools_disponíveis
- `read(path)`: ler arquivos da task/projeto e artefatos UX (com validação de path).
- `write(path, content)`: escrever componentes/testes/docs (com validação).
- `exec(command)`: executar comandos de build/test/lint/a11y.
- `gh(args...)`: atualizar issues/PRs e consultar execuções de workflow, checks, labels e run logs.
- `git(args...)`: operações de commit/branch/merge sem comandos destrutivos.
- `sessions_spawn(agentId, mode, label)`: criar sessão com Arquiteto ou QA_Engineer.
- `sessions_send(session_id, message)`: enviar update ou delegar ao QA_Engineer.
- `sessions_list()`: listar sessões ativas.
- `browser`: navegar páginas web para referência de implementação, UX research ou debug.
- `internet_search(query)`: pesquisar boas práticas de performance, acessibilidade e segurança frontend.

## regras_de_uso
- `read/write` somente em `/data/openclaw/**`.
- Bloquear comandos destrutivos (`rm -rf`, `git push -f`, etc.).
- `gh` sempre com `--repo "$ACTIVE_GITHUB_REPOSITORY"`.
- Validar `/data/openclaw/contexts/active_repository.env` antes de qualquer ação gh/git.
- Poll de fila GitHub 1x por hora (offset :15):
  - exemplo: `gh issue list --state open --label front_end --limit 20 --repo "$ACTIVE_GITHUB_REPOSITORY"`
- Processar somente label `front_end`.
- Ignorar labels: `back_end`, `mobile`, `tests`, `dba`, `devops`, `documentacao`.
- Sempre executar testes antes de reportar conclusão.
- Sempre documentar Core Web Vitals e bundle size no comentário do PR.
- Se task trouxer `## Comandos`, usar esses comandos em vez dos defaults.
- Internet liberada para pesquisa técnica em fontes confiáveis (MDN, web.dev, a11yproject, OWASP).
- `sessions_spawn` permitido para: `arquiteto`, `qa_engineer`.

## comandos_adicionais_frontend
- `npx next build`: build Next.js com análise de bundle
- `npx playwright test`: testes e2e Playwright
- `npx cypress run`: testes e2e Cypress
- `npx storybook build`: build do Storybook para review
- `npx axe <url>`: scan de acessibilidade

## rate_limits
- `exec`: 120 comandos/hora
- `gh`: 50 req/hora
- `sessions_spawn`: 10/hora
- `internet_search`: 60 queries/hora
