# BOOT.md - Security_Engineer

Ao iniciar:
1. Carregar `IDENTITY.md`.
2. Carregar `AGENTS.md`.
3. Ler `README.md` do repositório para entender a aplicação, stack e dependências.
4. Carregar `SOUL.md`.
5. Carregar `INPUT_SCHEMA.json` e validar schema de entrada.
6. Aguardar gateway de sessão estar disponível (`sessions_list()` retorna OK).
7. Montar diretório de configuração: verificar `/data/openclaw/` acessível.
8. Detectar manifests de dependências presentes no repositório:
   - `package.json` / `package-lock.json` → Node.js/npm
   - `requirements.txt` / `Pipfile.lock` / `pyproject.toml` → Python
   - `go.mod` / `go.sum` → Go
   - `Cargo.toml` / `Cargo.lock` → Rust
   - `pom.xml` / `build.gradle` → Java/Kotlin
9. Verificar ferramentas de segurança no PATH: `semgrep`, `trivy`, `gitleaks`, `npm`, `pip-audit`, `osv-scanner`.
10. Validar autenticação `gh` e permissões de leitura/escrita no repositório ativo.
11. Verificar acesso ao repositório ativo via `active_repository.env`.
12. Pronto para receber tasks do Arquiteto, CEO (P0) ou agentes dev.
