# TOOLS.md - QA_Engineer

## tools_disponíveis
- `read(path)`: ler SPEC, TASK, artefatos de teste e código do projeto.
- `write(path, content)`: escrever testes automatizados e relatórios QA.
- `exec(command)`: executar testes, scans e validações.
- `gh(args...)`: comentar em PRs, atualizar issues, consultar status de CI.
- `git(args...)`: checkout de branches para executar testes (sem commits destrutivos).
- `sessions_spawn(agentId, mode, label)`: criar sessão com Arquiteto para escalação.
- `sessions_send(session_id, message)`: reportar PASS/FAIL ao dev agent delegante ou ao Arquiteto.
- `sessions_list()`: listar sessões ativas.
- `browser`: acessar relatórios de CI/CD ou documentação de ferramentas de teste.
- `internet_search(query)`: boas práticas de testes, padrões BDD, ferramentas.

## regras_de_uso
- `read/write` somente em `/data/openclaw/**` e workspace de testes do projeto.
- Bloquear comandos destrutivos.
- `gh` sempre com `--repo "$ACTIVE_GITHUB_REPOSITORY"`.
- `sessions_spawn` permitido para: `arquiteto`, `dev_backend`, `dev_frontend`, `dev_mobile`.
- NÃO commitar código de produção — apenas testes e scripts de validação.
- Poll de fila GitHub 1x por hora (offset :45):
  - `gh issue list --state open --label tests --limit 20 --repo "$ACTIVE_GITHUB_REPOSITORY"`
- Processar somente label `tests`.
- Armazenar retry_count em `/data/openclaw/backlog/qa/retries/{issue_id}.json`.

## comandos_de_teste
- Playwright: `npx playwright test`, `npx playwright show-report`
- Cypress: `npx cypress run`, `npx cypress open`
- Detox: `npx detox build`, `npx detox test`
- Maestro: `maestro test`
- k6: `k6 run`, `k6 run --out json`
- Pact: `npx pact-js verify`, `npx pact-js publish`
- Security: `npm audit`, `npx secretlint`

## rate_limits
- `exec`: 120 comandos/hora
- `gh`: 50 req/hora
- `sessions_spawn`: 10/hora
- `internet_search`: 60 queries/hora
