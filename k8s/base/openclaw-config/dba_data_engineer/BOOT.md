# BOOT.md - DBA_DataEngineer

## Sequência de Boot

1. Carregar `IDENTITY.md`.
2. Carregar `AGENTS.md`.
3. Ler `README.md` do repositório para entender a aplicação, stack e modelo de dados antes de modelar.
4. Carregar `SOUL.md`.
5. Carregar `INPUT_SCHEMA.json` e validar schema de entrada.
6. Ler `/data/openclaw/memory/shared/SHARED_MEMORY.md` — aplicar padrões globais do time como contexto base.
7. Ler `/data/openclaw/memory/dba_data_engineer/MEMORY.md` — resgatar aprendizados próprios de banco de dados relevantes.
8. Validar `/data/openclaw/` e workspace de banco de dados.
9. Verificar `active_repository.env` em `/data/openclaw/contexts/`.
10. Criar diretório de trabalho: `/data/openclaw/backlog/database/`.
11. Verificar PATH: `psql`, `flyway`, `alembic`, `prisma` disponíveis (warn se ausentes, não falhar).
12. Ao concluir a sessão: registrar até 3 aprendizados em `/data/openclaw/memory/dba_data_engineer/MEMORY.md`.
13. Pronto para receber tasks do Arquiteto ou Dev_Backend.

## healthcheck
- `/data/openclaw/` acessível? ✅
- INPUT_SCHEMA.json carregado? ✅
- `active_repository.env` disponível? ✅
- Diretório `database/` criado? ✅
- SHARED_MEMORY.md e MEMORY.md (dba_data_engineer) lidos? ✅
