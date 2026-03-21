# BOOTSTRAP.md - DBA_DataEngineer

## Inicialização de Ambiente

1. Carregar variáveis de ambiente.
2. Inicializar diretório `/data/openclaw/backlog/database/`.
3. Configurar cron de 4h (offset :30) para poll de issues com label `dba`.
4. Verificar conectividade com banco de desenvolvimento se disponível.
5. Registrar estado: `dba_data_engineer ready`.
