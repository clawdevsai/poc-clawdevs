# BOOT.md - Arquiteto

## Sequência de Boot

1. Carregar `IDENTITY.md`.
2. Carregar `AGENTS.md` (regras, capabilities e validações).
3. Ler `README.md` do repositório para entender estrutura, stack e contratos antes de planejar.
4. Carregar `SOUL.md` (postura e limites rígidos).
5. Carregar `INPUT_SCHEMA.json`.
6. Ler `/data/openclaw/memory/shared/SHARED_MEMORY.md` — aplicar padrões globais do time como contexto base.
7. Ler `/data/openclaw/memory/arquiteto/MEMORY.md` — resgatar aprendizados próprios de arquitetura relevantes.
8. Validar acesso a `/data/openclaw/backlog` e subpastas: `idea/`, `user_story/`, `tasks/`, `architecture/`, `briefs/`, `implementation/docs/`, `session_finished/`, `specs/`, `ux/`.
9. Verificar ferramentas disponíveis: `read`, `write`, `exec`, `sessions_spawn`, `sessions_send`, `sessions_list`.
10. Verificar comandos via `exec`: `gh`, `web-search`, `web-read`.
11. Validar variáveis via `/data/openclaw/contexts/active_repository.env`: `GITHUB_ORG`, `ACTIVE_GITHUB_REPOSITORY`.
12. Inicializar diretórios operacionais se ausentes: `/data/openclaw/backlog/status/`, `/data/openclaw/backlog/audit/`, `/data/openclaw/backlog/session_finished/`.
13. Carregar allowlists e limites de segurança (labels permitidas, rate limits, path whitelist).
14. Ao concluir a sessão: registrar até 3 aprendizados em `/data/openclaw/memory/arquiteto/MEMORY.md`.
15. Pronto para receber input do PO.

## healthcheck
- `/data/openclaw/backlog/` existe e é gravável? ✅
- `implementation/docs/` e `session_finished/` disponíveis? ✅
- Ferramentas `read`, `write`, `exec`, `sessions_spawn` disponíveis? ✅
- INPUT_SCHEMA.json carregado? ✅
- `GITHUB_ORG` definido? ✅
- `ACTIVE_GITHUB_REPOSITORY` definido? ✅
- SHARED_MEMORY.md e MEMORY.md (arquiteto) lidos? ✅
- Allowlists e rate limits carregados? ✅

## Preparação de labels GitHub (boot único)
```bash
gh label create "task"      --color "#0075ca" --description "Technical tasks — owned by Arquiteto"    --repo "$ACTIVE_GITHUB_REPOSITORY" 2>/dev/null || true
gh label create "ADR"       --color "#e4e669" --description "Architecture Decision Record"             --repo "$ACTIVE_GITHUB_REPOSITORY" 2>/dev/null || true
gh label create "security"  --color "#d93f0b" --description "Security tasks — routed to Security_Eng" --repo "$ACTIVE_GITHUB_REPOSITORY" 2>/dev/null || true
gh label create "back_end"  --color "#1d76db" --description "Backend tasks — routed to Dev_Backend"   --repo "$ACTIVE_GITHUB_REPOSITORY" 2>/dev/null || true
gh label create "front_end" --color "#0e8a16" --description "Frontend tasks — routed to Dev_Frontend" --repo "$ACTIVE_GITHUB_REPOSITORY" 2>/dev/null || true
gh label create "mobile"    --color "#5319e7" --description "Mobile tasks — routed to Dev_Mobile"     --repo "$ACTIVE_GITHUB_REPOSITORY" 2>/dev/null || true
gh label create "tests"     --color "#f9d0c4" --description "QA tasks — routed to QA_Engineer"        --repo "$ACTIVE_GITHUB_REPOSITORY" 2>/dev/null || true
gh label create "devops"    --color "#006b75" --description "DevOps tasks — routed to DevOps_SRE"     --repo "$ACTIVE_GITHUB_REPOSITORY" 2>/dev/null || true
gh label create "dba"       --color "#b60205" --description "DBA tasks — routed to DBA_DataEngineer"  --repo "$ACTIVE_GITHUB_REPOSITORY" 2>/dev/null || true
gh label create "ux"        --color "#e99695" --description "UX tasks — routed to UX_Designer"        --repo "$ACTIVE_GITHUB_REPOSITORY" 2>/dev/null || true
```
