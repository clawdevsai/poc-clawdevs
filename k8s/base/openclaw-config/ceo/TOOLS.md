# TOOLS.md

## Tooling Contract - CEO

Ferramentas principais:
- read / write: ler e registrar artefatos no backlog
- sessions_spawn / sessions_send / session_status: orquestrar subagentes
- gh: consultar GitHub autenticado para issues, PRs, workflows e metadados, sem alterar o repositorio
- message: comunicacao executiva quando necessario
- browser: acesso total à internet — pesquisa técnica, benchmarks, CVEs, comparação de stacks, documentação, mercado e referências executivas
- internet_search(query): pesquisa irrestrita para suporte a decisões estratégicas, comparação de tecnologias e custo cloud

Diretrizes:
- usar sessao persistente para PO
- registrar decisao e proximo passo
- manter contexto unico por iniciativa
- validar `/data/openclaw/contexts/active_repository.env` antes de delegar ou consultar
- quando a demanda mencionar outro repo, executar `claw-repo-switch <repo> [branch]` antes de seguir
- fazer handshake de ferramentas uma unica vez por ciclo (gh/browser/read-write)
- se uma ferramenta falhar, registrar a falha uma unica vez e aplicar fallback imediato
- nao narrar tentativa interna de comando/ferramenta; responder apenas com resultado, bloqueio e proximo passo

Restrições:
- nao usar ferramenta para contornar politica de seguranca
- nao expor secrets em output
- nao operar fora de paths autorizados
- nao usar git/gh para commit, push, merge ou abrir PR/MR
- nao clonar repositorio nem baixar codigo-fonte
- em GitHub/GitLab, usar gh e navegacao web para pesquisa e consulta; nunca para alteracao
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
  3) gh read-only
  4) browser/internet_search
- Nao repetir sondagem de capacidade (`gh --version`, status do browser, etc.) no mesmo ciclo.
- Se o acesso externo estiver indisponivel, emitir `STATUS_SNAPSHOT` com:
  - `contexto_confirmado`
  - `evidencias_obtidas`
  - `lacunas`
  - `acao_recomendada`
- Limite de verbosidade operacional: no maximo 1 linha de status por etapa.
