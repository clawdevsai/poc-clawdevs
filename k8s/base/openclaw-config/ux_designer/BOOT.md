# BOOT.md - UX_Designer

## Sequência de Boot

1. Aguardar gateway OpenClaw estar disponível (health check em loop com backoff).
2. Montar configuração do agente a partir dos ConfigMaps injetados.
3. Validar INPUT_SCHEMA.json.
4. Verificar `active_repository.env` em `/data/openclaw/contexts/`.
5. Criar diretórios necessários: `/data/openclaw/backlog/ux/`.
6. Registrar boot: `ux_designer booted successfully`.
