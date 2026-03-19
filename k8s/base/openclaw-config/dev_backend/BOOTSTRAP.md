# BOOTSTRAP.md - Dev_Backend

1. Carregar env:
   - `GITHUB_REPOSITORY`
   - `OPENCLAW_ENV`
   - `PROJECT_ROOT` (default `/data/openclaw/backlog/implementation`)
2. Validar estrutura base:
   - `${PROJECT_ROOT}`
   - `${PROJECT_ROOT}/src` ou `${PROJECT_ROOT}/lib`
   - `${PROJECT_ROOT}/tests` ou `${PROJECT_ROOT}/spec`
3. Detectar linguagem por `technology_stack` da task ou arquivos de build.
4. Definir comandos padrão (install/test/lint/build) por linguagem.
5. Verificar toolchain da linguagem no PATH.
6. Configurar logger com `task_id` e `language`.
7. Configurar baseline de custo/performance:
   - latencia alvo p95/p99 (quando task nao definir)
   - limite de uso de CPU/memoria
   - custo operacional maximo esperado
8. Habilitar pesquisa técnica na internet para otimização de custo/performance.
9. Validar autenticação `gh` e permissões do repositorio para issues, PRs e merges quando a task exigir.
10. Configurar agendamento:
   - intervalo fixo: 60 minutos
   - origem de trabalho: issues GitHub label `back_end`
11. Pronto.
