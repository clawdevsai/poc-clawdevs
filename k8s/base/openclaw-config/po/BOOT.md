# BOOT.md - PO

Ao iniciar:
1. Carregar `IDENTITY.md`.
2. Carregar `AGENTS.md` (regras, capabilities e validações).
3. Carregar `SOUL.md` (postura e limites rígidos).
4. Carregar schema de input em `INPUT_SCHEMA.json`.
5. Validar acesso a `/data/openclaw/backlog`.
6. Verificar ferramentas disponíveis (read, write, sessions_spawn, sessions_send, sessions_list, internet_search, gh).
7. Carregar rate limits e allowlists de segurança.
8. Pronto para receber input do CEO.

## healthcheck
- Diretório `/data/openclaw/backlog` existe e é gravável? ✅
- Ferramentas disponíveis? ✅
- Schema `INPUT_SCHEMA.json` carregado? ✅
- `GITHUB_REPOSITORY` definido? ✅ (para GitHub integration)
- Regras de allowlist e rate limit carregadas? ✅
