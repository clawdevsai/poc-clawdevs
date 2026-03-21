# BOOTSTRAP.md - Security_Engineer

1. Carregar env:
   - `GITHUB_ORG`
   - `ACTIVE_GITHUB_REPOSITORY`
   - `OPENCLAW_ENV`
   - `PROJECT_ROOT`
2. Ler `README.md` do repositório para entender stack, linguagens e frameworks utilizados.
3. Inicializar diretórios de trabalho de segurança:
   - `/data/openclaw/backlog/security/` → relatórios de segurança e CVEs
   - `/data/openclaw/backlog/security/scans/` → resultados de scans SAST/DAST
   - `/data/openclaw/backlog/security/patches/` → evidências de patches aplicados
4. Detectar manifests de dependências no repositório:
   - `package.json` → `npm audit`
   - `requirements.txt` / `pyproject.toml` → `pip-audit`
   - `go.mod` → `osv-scanner`
   - `Cargo.toml` → `cargo audit` / `osv-scanner`
   - `pom.xml` / `build.gradle` → `trivy fs`
5. Configurar cache de ferramentas de segurança:
   - Atualizar banco de dados do Trivy: `trivy image --download-db-only`
   - Atualizar regras do Semgrep: `semgrep --update`
   - Verificar banco de dados local do OSV
6. Verificar toolchain no PATH: `semgrep`, `trivy`, `gitleaks`, `trufflehog`, `osv-scanner`, `npm`, `pip-audit`.
7. Configurar logger com `task_id`, `scan_type` e `cvss_threshold`.
8. Habilitar acesso total à internet para consulta a CVE databases, NVD, OSV, GHSA e Snyk Advisor.
9. Validar autenticação `gh` e permissões para criar PRs e issues no repositório ativo.
10. Configurar agendamento:
    - intervalo fixo: 6 horas (cron: `0 */6 * * *`)
    - origem de trabalho: cron + issues GitHub com label `security` + mensagens de dev agents
11. Pronto.
