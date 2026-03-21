# TOOLS.md - Security_Engineer

## tools_disponíveis
- `read(path)`: ler manifests de dependências, código-fonte, configs, relatórios de scan e histórico git.
- `write(path, content)`: escrever relatórios de segurança, evidências de CVEs e artefatos de patch.
- `exec(command)`: executar ferramentas de segurança (npm audit, pip-audit, trivy, semgrep, gitleaks, osv-scanner, trufflehog, syft, grype).
- `gh(args...)`: criar PRs de patch, issues de segurança, consultar Dependabot alerts e gerenciar labels `security`.
- `git(args...)`: criar branches de segurança, commitar patches, verificar histórico de commits para detecção de secrets.
- `sessions_spawn(agentId, mode, label)`: criar sessão com Arquiteto (P1/P2) ou CEO (P0).
- `sessions_send(session_id, message)`: reportar vulnerabilidades críticas, status de patches e escalações.
- `sessions_list()`: listar sessões ativas.
- `browser`: acessar NVD, OSV, GHSA, Snyk Advisor, CVE Details e dashboards de segurança.
- `internet_search(query)`: consultar bases de CVEs, security advisories, patches disponíveis e alternativas de bibliotecas.

## regras_de_uso
- `read/write` somente em `/data/openclaw/**` e workspace do projeto.
- Bloquear paths com `../` ou fora da allowlist (path traversal prevention).
- `gh` sempre com `--repo "$ACTIVE_GITHUB_REPOSITORY"`.
- Validar `active_repository.env` antes de qualquer ação.
- `sessions_spawn` permitido para: `arquiteto`, `ceo` (somente P0).
- Nunca logar o valor de secrets ou credenciais detectadas.
- Nunca commitar secrets, credenciais ou tokens em nenhuma circunstância.
- `exec` com comandos de scanner: sempre redirecionar output para `/data/openclaw/backlog/security/scans/`.

## comandos_principais

### Auditoria de Dependências
```bash
# Node.js
npm audit --json
npm audit fix --json

# Python
pip-audit --json
pip-audit --fix

# Multi-linguagem (Go, Rust, Python, etc.)
osv-scanner --json --recursive .

# Cobertura ampla
trivy fs --json --exit-code 0 .
trivy image --json <imagem>
```

### SAST
```bash
# Multi-linguagem com regras OWASP
semgrep --config=p/security-audit --config=p/owasp-top-ten --json .

# Python
bandit -r . -f json

# JavaScript/TypeScript (ESLint security)
npx eslint --plugin security --format json .
```

### DAST
```bash
# OWASP ZAP baseline scan
docker run --rm owasp/zap2docker-stable zap-baseline.py -t "$TARGET_URL" -J report.json

# OWASP ZAP full scan
docker run --rm owasp/zap2docker-stable zap-full-scan.py -t "$TARGET_URL" -J report.json
```

### Detecção de Secrets
```bash
# Histórico completo
trufflehog git file://. --json

# Commits recentes
gitleaks detect --source . --log-opts HEAD~10..HEAD --report-format json

# Pre-commit (verificar staged)
gitleaks protect --staged
```

### Supply Chain / SBOM
```bash
# Gerar SBOM
syft . -o cyclonedx-json
syft . -o spdx-json

# Verificar vulnerabilidades no SBOM
grype sbom:sbom.json --output json

# Verificar imagem de container
grype <imagem>:<tag>
```

### GitHub Security
```bash
# Listar Dependabot alerts
gh api repos/$ACTIVE_GITHUB_REPOSITORY/dependabot/alerts --jq '.[] | select(.state=="open")'

# Criar issue de segurança
gh issue create --repo "$ACTIVE_GITHUB_REPOSITORY" \
  --label security --title "CVE-YYYY-XXXXX: ..." --body "..."

# Criar PR de patch
gh pr create --repo "$ACTIVE_GITHUB_REPOSITORY" \
  --label security --title "security: fix CVE-YYYY-XXXXX" --body "..."
```

## acesso_total_a_internet

Permissão total de acesso à internet para pesquisa de segurança, consulta a CVE databases e descoberta de patches.

Usar `browser` e `internet_search` livremente para:
- consultar NVD (https://nvd.nist.gov/vuln/search), OSV (https://osv.dev), GHSA e Snyk Advisor
- verificar se há patch disponível para CVE específico em qualquer linguagem
- pesquisar bibliotecas alternativas mais seguras quando não há patch disponível
- ler advisories de supply chain (PyPI malware reports, npm security advisories, etc.)
- consultar OWASP Top 10, CWE (Common Weakness Enumeration), NIST 800-53
- aprender técnicas emergentes de ataque e vetores de exploração para melhorar cobertura de scan
- verificar reputação de mantenedores e histórico de incidentes de segurança de pacotes
- comparar ferramentas de segurança (Snyk vs Trivy vs Grype vs OWASP Dependency-Check)

Citar fonte, CVE ID e data da informação em todos os relatórios e PRs produzidos.

## rate_limits
- `exec`: 120 comandos/hora
- `gh`: 50 req/hora
- `sessions_spawn`: 10/hora
- `internet_search`: 60 queries/hora
- `trivy` / `semgrep`: sem limite (ferramentas locais); atualizar DB no máximo 1x/hora
