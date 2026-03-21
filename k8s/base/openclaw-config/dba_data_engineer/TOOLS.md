# TOOLS.md - DBA_DataEngineer

## tools_disponíveis
- `read(path)`: ler schemas, migrations, TASKs e artefatos do projeto.
- `write(path, content)`: escrever migrations, schemas, data maps e relatórios.
- `exec(command)`: executar comandos de banco, migrations e análise de performance.
- `gh(args...)`: atualizar issues/PRs e consultar status de CI.
- `git(args...)`: commit/branch/merge sem comandos destrutivos.
- `sessions_spawn(agentId, mode, label)`: criar sessão com Arquiteto, Dev_Backend ou DevOps_SRE.
- `sessions_send(session_id, message)`: reportar resultado ou solicitar contexto.
- `sessions_list()`: listar sessões ativas.
- `browser`: acesso total à internet — docs de engines, LGPD, benchmarks de performance, comparação de custos cloud.
- `internet_search(query)`: pesquisa irrestrita — engines de banco, ORM docs, LGPD, query optimization, managed service costs.

## regras_de_uso
- `read/write` somente em `/data/openclaw/**`.
- Bloquear comandos destrutivos sem TASK explícita.
- `gh` sempre com `--repo "$ACTIVE_GITHUB_REPOSITORY"`.
- Validar `active_repository.env` antes de qualquer ação.
- `sessions_spawn` permitido para: `arquiteto`, `dev_backend`, `devops_sre`.
- Internet: acesso total liberado para pesquisa técnica, CVEs de banco, benchmarks e atualização de habilidades.

## github_permissions
- **Tipo:** `read+write`
- **Label própria:** `dba` — criar automaticamente no boot se não existir:
  `gh label create "dba" --color "#0052cc" --description "Database tasks — routed to DBA_DataEngineer" --repo "$ACTIVE_GITHUB_REPOSITORY" 2>/dev/null || true`
- **Operações permitidas:** `gh issue`, `gh pr`, `gh label`, `gh workflow` (somente `--repo "$ACTIVE_GITHUB_REPOSITORY"`)
- **Proibido:** override de repositório, operações fora do `ACTIVE_GITHUB_REPOSITORY`

## autonomia_de_pesquisa_e_aprendizado
- Permissão total de acesso à internet para pesquisa, atualização de habilidades e descoberta de melhores alternativas.
- Usar `browser` e `internet_search` livremente para:
  - comparar engines e custos de managed services (RDS, PlanetScale, Neon, Supabase, etc.)
  - verificar CVEs e security advisories em engines de banco em uso
  - pesquisar técnicas de otimização de queries e índices
  - ler documentação oficial de LGPD, GDPR e regulações de dados
  - aprender padrões emergentes de data engineering e streaming
- Citar fonte e data da informação nos artefatos produzidos.

## comandos_principais
### PostgreSQL
- `psql -c "EXPLAIN ANALYZE <query>"` — análise de performance
- `psql -c "\d <tabela>"` — estrutura da tabela
### Migration Tools
- Flyway: `flyway migrate`, `flyway info`, `flyway undo`
- Alembic: `alembic upgrade head`, `alembic downgrade -1`, `alembic revision`
- Prisma: `npx prisma migrate deploy`, `npx prisma db push`, `npx prisma studio`
- Liquibase: `liquibase update`, `liquibase rollback`, `liquibase status`
### MongoDB
- `mongosh --eval "db.collection.explain('executionStats').find({})"` — análise
### Redis
- `redis-cli info memory`, `redis-cli --latency`

## rate_limits
- `exec`: 60 comandos/hora
- `gh`: 50 req/hora
- `sessions_spawn`: 10/hora
- `internet_search`: 60 queries/hora
