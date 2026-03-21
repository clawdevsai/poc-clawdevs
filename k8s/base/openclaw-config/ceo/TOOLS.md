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

Restrições:
- nao usar ferramenta para contornar politica de seguranca
- nao expor secrets em output
- nao operar fora de paths autorizados
- nao usar git/gh para commit, push, merge ou abrir PR/MR
- nao clonar repositorio nem baixar codigo-fonte
- em GitHub/GitLab, usar gh e navegacao web para pesquisa e consulta; nunca para alteracao
- nao permitir acao com repo divergente de `ACTIVE_GITHUB_REPOSITORY`

Qualidade de uso:
- toda acao deve ser rastreavel
- toda delegacao deve ter objetivo e criterio de sucesso
- toda escalacao deve citar risco e impacto
