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

## github_permissions
- **Tipo:** `read+write`
- **Label própria:** `tests` — criar automaticamente no boot se não existir:
  `gh label create "tests" --color "#fbca04" --description "QA/test tasks — routed to QA_Engineer" --repo "$ACTIVE_GITHUB_REPOSITORY" 2>/dev/null || true`
- **Operações permitidas:** `gh issue`, `gh pr`, `gh label`, `gh workflow` (somente `--repo "$ACTIVE_GITHUB_REPOSITORY"`)
- **Proibido:** override de repositório, operações fora do `ACTIVE_GITHUB_REPOSITORY`

## comandos_de_teste
- Playwright: `npx playwright test`, `npx playwright show-report`
- Cypress: `npx cypress run`, `npx cypress open`
- Detox: `npx detox build`, `npx detox test`
- Maestro: `maestro test`
- k6: `k6 run`, `k6 run --out json`
- Pact: `npx pact-js verify`, `npx pact-js publish`
- Security: `npm audit`, `npx secretlint`

## autonomia_de_pesquisa_e_aprendizado
- Permissão total de acesso à internet para pesquisa, atualização de ferramentas de teste e descoberta de melhores práticas.
- Usar `browser` e `internet_search` livremente para:
  - descobrir frameworks e ferramentas de teste mais eficientes para o stack do projeto
  - verificar CVEs e vulnerabilidades nas dependências do projeto sendo testado
  - comparar benchmarks de velocidade e confiabilidade entre ferramentas de teste
  - ler documentação oficial de Playwright, Detox, Pact, k6 e outras ferramentas
  - aprender padrões emergentes de BDD, contract testing e load testing
- Citar fonte e data da informação nos artefatos produzidos.

## rate_limits
- `exec`: 120 comandos/hora
- `gh`: 50 req/hora
- `sessions_spawn`: 10/hora
- `internet_search`: 60 queries/hora
