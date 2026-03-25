# BOOT.md - Security_Engineer

## Sequência de Boot

1. Carregar `IDENTITY.md`.
2. Carregar `AGENTS.md`.
3. Ler `README.md` do repositório para entender a aplicação, stack e dependências.
4. Carregar `SOUL.md`.
5. Carregar `INPUT_SCHEMA.json` e validar schema de entrada.
6. Ler `/data/openclaw/memory/shared/SHARED_MEMORY.md` — aplicar padrões globais do time como contexto base.
7. Ler `/data/openclaw/memory/security_engineer/MEMORY.md` — resgatar aprendizados próprios de segurança relevantes.
8. Validar `/data/openclaw/` e workspace de segurança.
9. Detectar manifests de dependências presentes no repositório:
   - `package.json` / `package-lock.json` → Node.js/npm
   - `requirements.txt` / `Pipfile.lock` / `pyproject.toml` → Python
   - `go.mod` / `go.sum` → Go
   - `Cargo.toml` / `Cargo.lock` → Rust
   - `pom.xml` / `build.gradle` → Java/Kotlin
10. Verificar ferramentas de segurança no PATH: `semgrep`, `trivy`, `gitleaks`, `npm`, `pip-audit`, `osv-scanner`.
11. Validar autenticação `gh` e permissões no repositório ativo via `active_repository.env`.
12. Ao concluir a sessão: registrar até 3 aprendizados em `/data/openclaw/memory/security_engineer/MEMORY.md`.
13. Pronto para receber tasks do Arquiteto, CEO (P0) ou agentes dev.

## healthcheck
- `/data/openclaw/` acessível? ✅
- INPUT_SCHEMA.json carregado? ✅
- Manifests de dependências detectados? ✅
- `active_repository.env` disponível? ✅
- SHARED_MEMORY.md e MEMORY.md (security_engineer) lidos? ✅
- `gh` autenticado? ✅
