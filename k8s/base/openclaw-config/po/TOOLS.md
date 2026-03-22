# TOOLS.md - PO

## tools_disponiveis
- `read(path)`: Ler arquivo concreto. Validar que `path` inicia com `/data/openclaw/backlog` e não contém `..`.
- `write(path, content)`: Escrever artefato. Validar schema/estrutura antes de persistir.
- `sessions_spawn(agentId, mode, label)`: Criar sessão. Validar `agentId in {'arquiteto', 'ux_designer'}`, `mode in {'session','task'}`, `label` ASCII e <= 50 chars.
- `sessions_send(session_id, message)`: Enviar para sessão existente do Arquiteto ou UX_Designer.
- `sessions_list()`: Listar sessões ativas.
- `exec("gh <args>")`: Consultar GitHub autenticado para issues, labels, milestones, PRs e workflows; sem commit, push ou abertura de PR.
- `exec("web-search '<query>'")`: pesquisar na internet via SearxNG (agrega Google, Bing, DuckDuckGo). Retorna até 10 resultados. Exemplo: `web-search "UX patterns fintech 2025"`
- `exec("web-read '<url>'")`: ler qualquer página web como markdown limpo via Jina Reader. Exemplo: `web-read "https://www.nngroup.com/articles/ux-best-practices"`

## regras_de_uso
- `read/write` somente em `/data/openclaw/backlog/**`; bloquear qualquer path fora da allowlist.
- Todas as chamadas de ferramenta devem ser auditadas (timestamp, tool, args sanitizados).
- Comandos GitHub devem usar `exec('gh ... --repo "$ACTIVE_GITHUB_REPOSITORY"')`; não permitir override de repositório.
- Validar `/data/openclaw/contexts/active_repository.env` antes de consultas GitHub.
- Se demanda mencionar outro repo, solicitar troca de contexto ao CEO antes de continuar.
- Labels GitHub permitidas: `task`, `P0`, `P1`, `P2`, `EPIC`, `bug`, `security`.
- Corpo de issue não pode referenciar caminhos fora de `/data/openclaw/backlog`.

## github_permissions
- **Tipo:** `read-only`
- **Operações permitidas:** `gh issue list`, `gh pr list`, `gh workflow list`, `gh run view`, `gh label list` — consulta apenas
- **Proibido:** `gh issue create/edit/close`, `gh pr create/merge`, `gh label create/edit/delete`, `gh workflow run`, qualquer operação de escrita

- Rate limits:
  - `write`: 10 arquivos/minuto
  - `gh`: 30 requisições/hora
  - `sessions_spawn`: 5 sessões/hora
