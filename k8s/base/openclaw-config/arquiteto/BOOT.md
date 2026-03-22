# BOOT.md - Arquiteto

Ao iniciar:
1. Carregar `IDENTITY.md`.
2. Carregar `AGENTS.md` (regras, capabilities e validações).
3. Ler `README.md` do repositorio para entender a estrutura e o contrato do projeto antes de planejar.
4. Carregar `SOUL.md` (postura e limites rígidos).
5. Carregar schema de input em `INPUT_SCHEMA.json`.
6. Validar acesso a `/data/openclaw/backlog` (e subpastas: `idea`, `user_story`, `tasks`, `architecture`, `briefs`, `implementation/docs`, `session_finished`).
7. Verificar ferramentas disponíveis (read, write, exec, sessions_spawn, sessions_send, sessions_list) e comandos `gh`, `web-search` e `web-read` via `exec`.
8. Validar variáveis de ambiente (GITHUB_ORG, ACTIVE_GITHUB_REPOSITORY, GITHUB_TOKEN se disponível).
9. Carregar allowlists e limites de segurança.
10. Pronto para receber input do PO.

## healthcheck
- Diretório `/data/openclaw/backlog` existe e é gravável? ✅
- Diretórios `/data/openclaw/backlog/implementation/docs` e `/data/openclaw/backlog/session_finished` disponíveis? ✅
- Ferramentas disponíveis? ✅
- Schema `INPUT_SCHEMA.json` carregado? ✅
- `GITHUB_ORG` definido? ✅
- `ACTIVE_GITHUB_REPOSITORY` definido? ✅ (necessário para GitHub integration)
- Regras de allowlist/rate limit carregadas? ✅
