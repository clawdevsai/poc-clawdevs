---
name: security_engineer_scan
description: Security skill for proactive scans of CVEs, SAST, secret detection and autonomous patches
---

# Security_Engineer Skills

---

## Main Security Flow

### 1. Dependency Audit (Manifests)

Run on all detected manifests in the repository:

```bash
# Node.js / npm
npm audit --json > $OPENCLAW_DATA/backlog/security/scans/npm-audit.json

# Python
pip-audit --json -o $OPENCLAW_DATA/backlog/security/scans/pip-audit.json

# Go, Rust, e outros (via OSV)
osv-scanner --json --recursive . > $OPENCLAW_DATA/backlog/security/scans/osv-scan.json

# Cobertura ampla com Trivy
trivy fs --json --exit-code 0 . > $OPENCLAW_DATA/backlog/security/scans/trivy-fs.json
```

Consolidate results: group CVEs by CVSS score, package and affected version.

---

### 2. SAST — Static Analysis

```bash
# Broad security rules (multi-language)
semgrep --config=p/security-audit --config=p/owasp-top-ten \
  --json -o $OPENCLAW_DATA/backlog/security/scans/semgrep.json .

# Python específico
bandit -r . -f json -o $OPENCLAW_DATA/backlog/security/scans/bandit.json

# JavaScript/TypeScript (via ESLint security plugin)
npx eslint --ext .js,.ts,.jsx,.tsx \
  --plugin security --rule '{"security/detect-object-injection": "error"}' \
  --format json -o $OPENCLAW_DATA/backlog/security/scans/eslint-security.json .
```

Sort findings by severity: critical → high → medium → low.

---

### 3. DAST — Dynamic Analysis (when URL available)

```bash
# OWASP ZAP em modo headless
docker run --rm owasp/zap2docker-stable zap-baseline.py \
  -t "$TARGET_URL" \
  -J $OPENCLAW_DATA/backlog/security/scans/zap-baseline.json
```

Check:
- OWASP Top 10 (injection, authentication, data exposure, etc.)
- Security Headers: CSP, HSTS, X-Frame-Options, X-Content-Type-Options
- Sensitive endpoints without authentication
- TLS/SSL Settings

---

### 4. Secret Detection

```bash
# Histórico completo do repositório
trufflehog git file://. --json > $OPENCLAW_DATA/backlog/security/scans/trufflehog.json

# Commits recentes (últimos 10)
gitleaks detect --source . --log-opts HEAD~10..HEAD \
  --report-format json \
  --report-path $OPENCLAW_DATA/backlog/security/scans/gitleaks.json
```

If secret found:
1. Log `secret_exposure_detected` with reference to the file and commit (NOT the value).
2. Notify Architect immediately via `sessions_send`.
3. Create issue `security` with severity P0.
4. Recommend immediate credential revocation and rotation.

---

### 5. For Each CVE Found

#### 5.1 Classify CVSS

| Score | Severity | Action |
|-------|-----------|------|
| >= 9.0 | Critical (P0) | Immediate standalone patch + escalate to CEO |
| 7.0–8.9 | High (P1) | Standalone patch in current cycle + notify Architect |
| 4.0–6.9 | Medium (P2) | Issue security + recommend fix in next sprint |
| < 4.0 | Low (P3) | Register in the periodic report |

#### 5.2 Search for Alternative or Patch

```bash
# Check versão segura disponível
npm info <pacote> versions --json  # Node.js
pip index versions <pacote>        # Python

# Pesquisar alternativas (internet_search)
# Query: "CVE-YYYY-XXXXX patch available" OR "<pacote> security advisory"
# Fontes: NVD, OSV, GHSA, Snyk Advisor, pkg.go.dev/vuln
```

#### 5.3 Apply Standalone Fix (CVSS >= 7.0)

```bash
# Create branch de security
git checkout -b security/fix-CVE-YYYY-XXXXX

# Atualizar dependência (exemplo Node.js)
npm install <pacote>@<versao-segura>

# Executar testes
npm test  # ou: pytest / go test ./... / cargo test

# Commit com evidências
git add package.json package-lock.json
git commit -m "security: fix CVE-YYYY-XXXXX in <pacote> (CVSS <score>)

- Vulnerability: CVE-YYYY-XXXXX (CVSS: <score>)
- Package: <pacote> <versao-vulneravel> -> <versao-segura>
- Risk: <descricao-do-risco>
- Reference: https://nvd.nist.gov/vuln/detail/CVE-YYYY-XXXXX"

# Abrir PR
gh pr create \
  --repo "$ACTIVE_GITHUB_REPOSITORY" \
  --title "security: fix CVE-YYYY-XXXXX in <pacote> (CVSS <score>)" \
  --body "..." \
  --label security
```

#### 5.4 Mandatory PR content

```markdown
## Security Vulnerability

**CVE ID**: CVE-YYYY-XXXXX
**CVSS Score**: X.X (Crítico/Alto)
**Pacote Afetado**: <pacote> @ <versao-vulneravel>
**Versão Segura**: <versao-segura>

## Descrição do Risco
<descrição clara do risco e vetor de ataque>

## Mudança Aplicada
- `<pacote>`: `<versao-vulneravel>` → `<versao-segura>`

## Resultado dos Testes
- Suite de testes executada: PASS / FAIL (detalhar se FAIL)

## Referências
- https://nvd.nist.gov/vuln/detail/CVE-YYYY-XXXXX
- <link ao advisory original>

> Patch aplicado autonomamente pelo Security_Engineer (CVSS >= 7.0).
> Architect notified. Prior approval for merge is not required.
```

---

### 6. Supply Chain Audit

```bash
# Generate SBOM
syft . -o cyclonedx-json > $OPENCLAW_DATA/backlog/security/scans/sbom.json

# Check vulnerabilidades no SBOM
grype sbom:$OPENCLAW_DATA/backlog/security/scans/sbom.json \
  --output json > $OPENCLAW_DATA/backlog/security/scans/grype.json
```

Alert about:
- Compromised packages (typosquatting, maintainer takeover)
- Abandoned packages with known and unpatched CVEs
- Transitive dependencies with CVSS >= 7.0

---

### 7. Security Report

`SECURITY_REPORT-YYYY-MM-DD.md` Format:

```markdown
# SECURITY_REPORT-2025-03-21

## Resumo Executivo
- CVEs encontrados: X (críticos: Y, altos: Z)
- PRs com patch abertos: N
- Secrets detectados: 0
- Status geral: VERDE / AMARELO / VERMELHO

## CVEs por Severidade

### Críticos (CVSS >= 9.0)
| CVE ID | Pacote | CVSS | Status |
|--------|--------|------|--------|
| CVE-YYYY-XXX | pacote@versao | 9.8 | Corrigido (PR #42) |

### Altos (CVSS 7.0–8.9)
...

## Findings SAST
...

## Recomendações
1. [Alta prioridade] ...
2. [Média prioridade] ...

## Tendências vs Relatório Anterior
- CVEs críticos: -2 (melhora)
- Cobertura de audit: 100%
```

---

### 8. Escalation P0 to CEO

```
1. Enviar via sessions_send ao CEO imediatamente
2. Incluir: CVE ID, CVSS score, sistemas afetados, vetor de ataque, impacto de negócio estimado
3. Incluir: plano de mitigation imediata (patch em andamento ou workaround)
4. Comunicar status a cada hora até resolução
5. Post-mortem em $OPENCLAW_DATA/backlog/security/incidents/
```

---

## Guardrails

- Never commit secrets or credentials.
- Never ignore CVE without formal risk acceptance documentation.
- Always include CVE ID, CVSS score and evidence in PRs.
- Always run tests before opening patch PR.
- CVSS >= 9.0: escalate to CEO without waiting for the next cycle.
