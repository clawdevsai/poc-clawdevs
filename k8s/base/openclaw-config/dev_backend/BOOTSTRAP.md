# BOOTSTRAP.md - Dev_Backend

1. Carregar env:
   - `GITHUB_ORG`
   - `ACTIVE_GITHUB_REPOSITORY`
   - `OPENCLAW_ENV`
   - `PROJECT_ROOT` (default `/data/openclaw/backlog/implementation`)
2. Ler `README.md` do repositorio para entender a aplicacao, stack e fluxo antes de implementar.
3. Validar estrutura base:
   - `${PROJECT_ROOT}`
   - `${PROJECT_ROOT}/src` ou `${PROJECT_ROOT}/lib`
   - `${PROJECT_ROOT}/tests` ou `${PROJECT_ROOT}/spec`
   - se inexistente, usar fallback `/data/openclaw/backlog/implementation` e marcar contexto como `standby` (sem lançar erro)
4. Detectar linguagem por `technology_stack` da task ou arquivos de build.
   - antes de ler `package.json`/`go.mod`, validar se o arquivo existe
   - se não existir arquivo de build, não falhar; operar por `technology_stack` ou aguardar task
5. Definir comandos padrão (install/test/lint/build) por linguagem.
6. Verificar toolchain da linguagem no PATH.
7. Configurar logger com `task_id` e `language`.
8. Configurar baseline de custo/performance:
   - latencia alvo p95/p99 (quando task nao definir)
   - limite de uso de CPU/memoria
   - custo operacional maximo esperado
9. Habilitar pesquisa técnica na internet para otimização de custo/performance.
10. Validar autenticação `gh` e permissões do repositorio ativo para issues, PRs e merges quando a task exigir.
11. Configurar agendamento:
   - intervalo fixo: 60 minutos
   - origem de trabalho: issues GitHub label `back_end`
12. Pronto.
