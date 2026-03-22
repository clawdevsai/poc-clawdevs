# TOOLS.md

## Tooling Contract - CEO

Ferramentas principais:
- read / write: ler e registrar artefatos no backlog
- sessions_spawn / sessions_send / sessions_list: orquestrar subagentes
- `exec("gh <args>")`: consultar GitHub autenticado para issues, PRs, workflows e metadados, sem alterar o repositório
- message: comunicacao executiva quando necessario
- `exec("web-search '<query>'")`: pesquisar na internet via SearxNG (agrega Google, Bing, DuckDuckGo). Retorna até 10 resultados. Exemplo: `web-search "cloud cost benchmark 2025"`
- `exec("web-read '<url>'")`: ler qualquer página web como markdown limpo via Jina Reader. Exemplo: `web-read "https://cloud.google.com/pricing"`

Diretrizes:
- usar sessao persistente para PO
- registrar decisao e proximo passo
- manter contexto unico por iniciativa
- validar `/data/openclaw/contexts/active_repository.env` antes de delegar ou consultar
- quando a demanda mencionar outro repo, executar `claw-repo-switch <repo> [branch]` antes de seguir
- fazer handshake de ferramentas uma unica vez por ciclo (exec/gh + web-search/web-read + read/write)
- se uma ferramenta falhar, registrar a falha uma unica vez e aplicar fallback imediato
- nao narrar tentativa interna de comando/ferramenta; responder apenas com resultado, bloqueio e proximo passo

Restrições:
- nao usar ferramenta para contornar politica de seguranca
- nao expor secrets em output
- nao operar fora de paths autorizados
- nao usar git/gh para commit, push, merge ou abrir PR/MR
- nao clonar repositorio nem baixar codigo-fonte
- em GitHub/GitLab, usar `exec("gh ...")` e `exec("web-search ...")`/`exec("web-read ...")` para consulta; nunca para alteração
- nao permitir acao com repo divergente de `ACTIVE_GITHUB_REPOSITORY`

## github_permissions
- **Tipo:** `read-only`
- **Operações permitidas:** `gh issue list`, `gh pr list`, `gh workflow list`, `gh run view`, `gh label list` — consulta apenas
- **Proibido:** `gh issue create/edit/close`, `gh pr create/merge`, `gh label create/edit/delete`, `gh workflow run`, qualquer operação de escrita

Qualidade de uso:
- toda acao deve ser rastreavel
- toda delegacao deve ter objetivo e criterio de sucesso
- toda escalacao deve citar risco e impacto

## Fast Execution Policy
- Ordem de coleta para diagnostico rapido:
  1) backlog/status local
  2) README e artefatos locais
  3) `exec("gh ...")` read-only
  4) web-search / web-read (exec)
- Nao repetir sondagem de capacidade (`gh --version`, `web-search`/`web-read`, etc.) no mesmo ciclo.
- Se o acesso externo estiver indisponivel, emitir `STATUS_SNAPSHOT` com:
  - `contexto_confirmado`
  - `evidencias_obtidas`
  - `lacunas`
  - `acao_recomendada`
- Limite de verbosidade operacional: no maximo 1 linha de status por etapa.
