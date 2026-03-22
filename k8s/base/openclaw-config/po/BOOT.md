# BOOT.md - PO

Ao iniciar:
1. Carregar `IDENTITY.md`.
2. Carregar `AGENTS.md` (regras, capabilities e validações).
3. Ler `README.md` do repositorio para entender o escopo do projeto antes de estruturar backlog.
4. Carregar `SOUL.md` (postura e limites rígidos).
5. Carregar schema de input em `INPUT_SCHEMA.json`.
6. Validar acesso a `/data/openclaw/backlog`.
7. Verificar ferramentas disponíveis (read, write, exec, sessions_spawn, sessions_send, sessions_list) e comandos `gh`, `web-search` e `web-read` via `exec`.
8. Carregar rate limits e allowlists de segurança.
9. Pronto para receber input do CEO.

## healthcheck
- Diretório `/data/openclaw/backlog` existe e é gravável? ✅
- Ferramentas disponíveis? ✅
- Schema `INPUT_SCHEMA.json` carregado? ✅
- `GITHUB_ORG` definido? ✅
- `ACTIVE_GITHUB_REPOSITORY` definido? ✅ (para GitHub integration)
- Regras de allowlist e rate limit carregadas? ✅
