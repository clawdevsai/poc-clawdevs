# BOOT.md - PO

## Sequência de Boot

1. Carregar `IDENTITY.md`.
2. Carregar `AGENTS.md` (regras, capabilities e validações).
3. Ler `README.md` do repositório para entender o escopo do projeto antes de estruturar backlog.
4. Carregar `SOUL.md` (postura e limites rígidos).
5. Carregar `INPUT_SCHEMA.json`.
6. Ler `/data/openclaw/memory/shared/SHARED_MEMORY.md` — aplicar padrões globais do time como contexto base.
7. Ler `/data/openclaw/memory/po/MEMORY.md` — resgatar aprendizados próprios de produto relevantes.
8. Validar acesso a `/data/openclaw/backlog` e subpastas: `idea/`, `user_story/`, `specs/`, `briefs/`, `tasks/`, `status/`.
9. Verificar ferramentas disponíveis: `read`, `write`, `exec`, `sessions_spawn`, `sessions_send`, `sessions_list`.
10. Verificar comandos via `exec`: `gh`, `web-search`, `web-read`.
11. Validar variáveis via `/data/openclaw/contexts/active_repository.env`: `GITHUB_ORG`, `ACTIVE_GITHUB_REPOSITORY`.
12. Carregar rate limits e allowlists de segurança.
13. Ao concluir a sessão: registrar até 3 aprendizados em `/data/openclaw/memory/po/MEMORY.md`.
14. Pronto para receber input do CEO.

## healthcheck
- `/data/openclaw/backlog/` existe e é gravável? ✅
- Ferramentas `read`, `write`, `exec`, `sessions_spawn` disponíveis? ✅
- INPUT_SCHEMA.json carregado? ✅
- `GITHUB_ORG` definido? ✅
- `ACTIVE_GITHUB_REPOSITORY` definido? ✅
- SHARED_MEMORY.md e MEMORY.md (po) lidos? ✅
- Regras de allowlist e rate limit carregadas? ✅
