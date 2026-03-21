# BOOT.md - DBA_DataEngineer

## Sequência de Boot

1. Aguardar gateway OpenClaw (health check com backoff).
2. Montar configuração do agente a partir dos ConfigMaps injetados.
3. Validar INPUT_SCHEMA.json.
4. Verificar `active_repository.env` em `/data/openclaw/contexts/`.
5. Criar diretórios: `/data/openclaw/backlog/database/`.
6. Verificar PATH: psql, flyway/alembic/prisma disponíveis (warn se ausentes, não falhar).
7. Registrar boot: `dba_data_engineer booted successfully`.
