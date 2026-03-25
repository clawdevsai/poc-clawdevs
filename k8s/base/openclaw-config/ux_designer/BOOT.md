# BOOT.md - UX_Designer

## Sequência de Boot

1. Carregar `IDENTITY.md`.
2. Carregar `AGENTS.md` (regras, capabilities e validações).
3. Ler `README.md` do repositório para entender o produto, usuários-alvo e plataformas.
4. Carregar `SOUL.md`.
5. Carregar `INPUT_SCHEMA.json` e validar schema de entrada.
6. Ler `/data/openclaw/memory/shared/SHARED_MEMORY.md` — aplicar padrões globais do time como contexto base.
7. Ler `/data/openclaw/memory/ux_designer/MEMORY.md` — resgatar aprendizados próprios de UX relevantes.
8. Validar `/data/openclaw/` e workspace de design.
9. Verificar `active_repository.env` em `/data/openclaw/contexts/`.
10. Criar diretório de trabalho: `/data/openclaw/backlog/ux/`.
11. Ao concluir a sessão: registrar até 3 aprendizados em `/data/openclaw/memory/ux_designer/MEMORY.md`.
12. Pronto para receber delegação do PO.

## healthcheck
- `/data/openclaw/` acessível? ✅
- INPUT_SCHEMA.json carregado? ✅
- `active_repository.env` disponível? ✅
- Diretório `ux/` criado? ✅
- SHARED_MEMORY.md e MEMORY.md (ux_designer) lidos? ✅
