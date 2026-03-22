# TOOLS.md - UX_Designer

## tools_disponíveis
- `read(path)`: ler User Stories, SPECs e referências de produto.
- `write(path, content)`: escrever artefatos UX (UX-XXX.md) em `/data/openclaw/backlog/ux/`.
- `sessions_spawn(agentId, mode, label)`: criar sessão. Validar `agentId in {'po', 'arquiteto', 'dev_frontend', 'dev_mobile'}`.
- `sessions_send(session_id, message)`: enviar artefato UX ao PO ou Arquiteto.
- `sessions_list()`: listar sessões ativas.
- `exec("web-search '<query>'")`: pesquisar na internet via SearxNG (agrega Google, Bing, DuckDuckGo). Retorna até 10 resultados. Exemplo: `web-search "WCAG 2.2 contrast ratio guidelines"`
- `exec("web-read '<url>'")`: ler qualquer página web como markdown limpo via Jina Reader. Exemplo: `web-read "https://m3.material.io/components/buttons/guidelines"`
- `exec("gh <args>")`: consultar issues e PRs para contexto de produto; sem commit ou push.

## regras_de_uso
- `read/write` somente em `/data/openclaw/backlog/**`.
- Comandos GitHub devem usar `exec('gh ... --repo "$ACTIVE_GITHUB_REPOSITORY"')`.
- Validar `active_repository.env` antes de consultas GitHub.
- `sessions_spawn` permitido para: `po`, `arquiteto`, `dev_frontend`, `dev_mobile`.
- NÃO criar issues ou PRs — apenas artefatos UX.
- Poll de fila GitHub a cada 4h: `gh issue list --state open --label ux --limit 20 --repo "$ACTIVE_GITHUB_REPOSITORY"`.

## github_permissions
- **Tipo:** `read+write`
- **Label própria:** `ux` — criar automaticamente no boot se não existir:
  `gh label create "ux" --color "#5319e7" --description "UX design tasks — routed to UX_Designer" --repo "$ACTIVE_GITHUB_REPOSITORY" 2>/dev/null || true`
- **Operações permitidas:** `gh issue`, `gh pr`, `gh label`, `gh workflow` (somente `--repo "$ACTIVE_GITHUB_REPOSITORY"`)
- **Proibido:** override de repositório, operações fora do `ACTIVE_GITHUB_REPOSITORY`

## autonomia_de_pesquisa_e_aprendizado
- Permissão total de acesso à internet para pesquisa, atualização de padrões UX e descoberta de melhores práticas.
- Usar `exec("web-search '...'")` e `exec("web-read '...'")` livremente para:
  - descobrir padrões de UX para o domínio do produto (e-commerce, SaaS, fintech, etc.)
  - verificar guidelines de acessibilidade WCAG atualizadas
  - comparar design systems (Material, Ant Design, Chakra, Radix) para fit com o projeto
  - ler documentação oficial de plataformas mobile (iOS HIG, Android Material)
  - aprender padrões emergentes de UX writing e micro-interactions
- Citar fonte e data da informação nos artefatos produzidos.

## rate_limits
- `write`: 10 arquivos/hora
- `gh`: 30 req/hora
- `sessions_spawn`: 5/hora
- `web-search`: 60 queries/hora
