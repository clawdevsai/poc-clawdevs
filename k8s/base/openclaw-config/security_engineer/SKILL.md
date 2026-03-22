---
name: security_engineer_scan
description: Skill de segurança para scans proativos de CVEs, SAST, detecção de secrets e patches autônomos
---

# Skills do Security_Engineer

---

## Fluxo Principal de Segurança

### 1. Auditoria de Dependências (Manifests)

Executar em todos os manifests detectados no repositório:

```bash
# Node.js / npm
npm audit --json > /data/openclaw/backlog/security/scans/npm-audit.json

# Python
pip-audit --json -o /data/openclaw/backlog/security/scans/pip-audit.json

# Go, Rust, e outros (via OSV)
osv-scanner --json --recursive . > /data/openclaw/backlog/security/scans/osv-scan.json

# Cobertura ampla com Trivy
trivy fs --json --exit-code 0 . > /data/openclaw/backlog/security/scans/trivy-fs.json
```

Consolidar resultados: agrupar CVEs por CVSS score, pacote e versão afetada.

---

### 2. SAST — Análise Estática

```bash
# Regras de segurança amplas (multi-linguagem)
semgrep --config=p/security-audit --config=p/owasp-top-ten \
  --json -o /data/openclaw/backlog/security/scans/semgrep.json .

# Python específico
bandit -r . -f json -o /data/openclaw/backlog/security/scans/bandit.json

# JavaScript/TypeScript (via ESLint security plugin)
npx eslint --ext .js,.ts,.jsx,.tsx \
  --plugin security --rule '{"security/detect-object-injection": "error"}' \
  --format json -o /data/openclaw/backlog/security/scans/eslint-security.json .
```

Classificar findings por severidade: critical → high → medium → low.

---

### 3. DAST — Análise Dinâmica (quando URL disponível)

```bash
# OWASP ZAP em modo headless
docker run --rm owasp/zap2docker-stable zap-baseline.py \
  -t "$TARGET_URL" \
  -J /data/openclaw/backlog/security/scans/zap-baseline.json
```

Verificar:
- OWASP Top 10 (injeção, autenticação, exposição de dados, etc.)
- Headers de segurança: CSP, HSTS, X-Frame-Options, X-Content-Type-Options
- Endpoints sensíveis sem autenticação
- Configurações TLS/SSL

---

### 4. Detecção de Secrets

```bash
# Histórico completo do repositório
trufflehog git file://. --json > /data/openclaw/backlog/security/scans/trufflehog.json

# Commits recentes (últimos 10)
gitleaks detect --source . --log-opts HEAD~10..HEAD \
  --report-format json \
  --report-path /data/openclaw/backlog/security/scans/gitleaks.json
```

Se secret encontrado:
1. Logar `secret_exposure_detected` com referência ao arquivo e commit (NÃO o valor).
2. Notificar Arquiteto imediatamente via `sessions_send`.
3. Criar issue `security` com severidade P0.
4. Recomendar revogação e rotação imediata da credencial.

---

### 5. Para Cada CVE Encontrado

#### 5.1 Classificar CVSS

| Score | Severidade | Ação |
|-------|-----------|------|
| >= 9.0 | Crítico (P0) | Patch autônomo imediato + escalar ao CEO |
| 7.0–8.9 | Alto (P1) | Patch autônomo no ciclo atual + notificar Arquiteto |
| 4.0–6.9 | Médio (P2) | Issue security + recomendar fix no próximo sprint |
| < 4.0 | Baixo (P3) | Registrar no relatório periódico |

#### 5.2 Buscar Alternativa ou Patch

```bash
# Verificar versão segura disponível
npm info <pacote> versions --json  # Node.js
pip index versions <pacote>        # Python

# Pesquisar alternativas (internet_search)
# Query: "CVE-YYYY-XXXXX patch available" OR "<pacote> security advisory"
# Fontes: NVD, OSV, GHSA, Snyk Advisor, pkg.go.dev/vuln
```

#### 5.3 Aplicar Fix Autônomo (CVSS >= 7.0)

```bash
# Criar branch de segurança
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

#### 5.4 Conteúdo obrigatório do PR

```markdown
## Vulnerabilidade de Segurança

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
> Arquiteto notificado. Não é necessária aprovação prévia para merge.
```

---

### 6. Auditoria de Supply Chain

```bash
# Gerar SBOM
syft . -o cyclonedx-json > /data/openclaw/backlog/security/scans/sbom.json

# Verificar vulnerabilidades no SBOM
grype sbom:/data/openclaw/backlog/security/scans/sbom.json \
  --output json > /data/openclaw/backlog/security/scans/grype.json
```

Alertar sobre:
- Pacotes comprometidos (typosquatting, maintainer takeover)
- Pacotes abandonados com CVEs conhecidos e sem patch
- Dependências transitivas com CVSS >= 7.0

---

### 7. Relatório de Segurança

Formato de `SECURITY_REPORT-YYYY-MM-DD.md`:

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

### 8. Escalação P0 ao CEO

```
1. Enviar via sessions_send ao CEO imediatamente
2. Incluir: CVE ID, CVSS score, sistemas afetados, vetor de ataque, impacto de negócio estimado
3. Incluir: plano de mitigação imediata (patch em andamento ou workaround)
4. Comunicar status a cada hora até resolução
5. Post-mortem em /data/openclaw/backlog/security/incidents/
```

---

## Guardrails

- Nunca commitar secrets ou credenciais.
- Nunca ignorar CVE sem documentação formal de aceite de risco.
- Sempre incluir CVE ID, CVSS score e evidências nos PRs.
- Sempre executar testes antes de abrir PR de patch.
- CVSS >= 9.0: escalar ao CEO sem esperar próximo ciclo.
