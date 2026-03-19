# TOOLS.md - Dev_Backend

## tools_disponiveis
- `read(path)`: ler arquivos da task/projeto (com validação de path).
- `write(path, content)`: escrever código/testes/docs (com validação).
- `exec(command)`: executar comandos de build/test/lint.
- `gh(args...)`: atualizar issues/PRs e consultar execuções de workflow, checks, labels e run logs (gh run view/rerun/list).
- `git(args...)`: operações de commit/branch/merge sem comandos destrutivos.
- `sessions_spawn(agentId, mode, label)`: criar sessão com Arquiteto.
- `sessions_send(session_id, message)`: enviar update.
- `sessions_list()`: listar sessões.
- `browser`: navegar paginas web quando houver necessidade de referencia externa durante implementacao ou debug.
- `internet_search(query)`: pesquisar arquiteturas, protocolos e boas práticas para custo/performance.

## regras_de_uso
- `read/write` somente em `/data/openclaw/**`.
- Bloquear comandos destrutivos (`rm -rf`, `git push -f`, etc.).
- `gh` sempre com `--repo "$GITHUB_REPOSITORY"`.
- `gh` com paridade operacional ao Arquiteto para leitura/atualização de CI, issues e PRs (sem operações destrutivas).
- Poll de fila GitHub 1x por hora:
  - exemplo: `gh issue list --state open --label back_end --limit 20 --repo "$GITHUB_REPOSITORY"`
- Processar somente label `back_end`.
- Ignorar labels: `front_end`, `tests`, `dba`, `devops`, `documentacao`.
- Sempre executar testes antes de reportar conclusão.
- Sempre reportar impacto de custo/performance da solução implementada.
- Se task trouxer `## Comandos`, usar esses comandos em vez de defaults.
- Internet liberada para pesquisa técnica em fontes confiáveis (docs oficiais, OWASP, CNCF, cloud docs).
- Rate limits:
  - `exec`: 120 comandos/hora
  - `gh`: 50 req/hora
  - `sessions_spawn`: 10/hora
  - `internet_search`: 60 queries/hora
