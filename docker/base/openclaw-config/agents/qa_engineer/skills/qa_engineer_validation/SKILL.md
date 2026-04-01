---
name: qa_engineer_validation
description: Condensed QA validation skill for BDD, e2e validation, and evidence-based PASS/FAIL reporting.
---

# QA Validation (Condensed)

## Core cycle
1. Read SPEC + TASK.
2. Map BDD scenarios to tests.
3. Run tests and collect evidence.
4. Report PASS/FAIL.
5. On 3rd retry failure, escalate to Architect.

## PASS criteria
- All required scenarios executed.
- No critical failures.
- Evidence attached (logs/report/screenshots/traces).

## FAIL criteria
- List exact failing scenarios and error messages.
- Include reproduction/evidence path.
- Provide next action for dev agent.

## Default tools
- Web e2e: Playwright/Cypress
- Mobile e2e: Detox/Maestro
- Contract: Pact
- Load: k6
- Security baseline: dependency + secret checks

## Guardrails
- Never approve without evidence.
- Never skip BDD scenario validation.
- Never modify production code.

## Context Mode Optimization 🚀

Este skill foi **otimizado para context-mode compression** (95-98% redução em logs de testes).

### Otimizações Aplicadas

#### Test Logs (Playwright/Cypress/Detox)
```bash
# ❌ NÃO USE: Logs completos (300KB+)
npx playwright test > full-report.txt

# ✅ USE ESTE: Apenas failures e resumo
npx playwright test 2>&1 | grep -E "✓|×|FAIL" | tail -50

# ✅ Para reports HTML (resumido)
npx playwright test --reporter=list  # vs default html (5MB)
```

#### Load Test Results (k6)
```bash
# ❌ NÃO USE: Todas as requisições (200KB+)
# ✅ USE ESTE: Resumo com p95/p99
k6 run script.js --summary-export=summary.json  # JSON compacto

# Economia: 200KB → 10KB (95% ↓)
```

#### GitHub Issues Queries
```bash
# ❌ NÃO USE: gh issue list (retorna tudo)
# ✅ USE ESTE: Filtrado
gh issue list --state open --label bug --json number,title --limit 20

# Economia: 280KB → 5KB (98% ↓)
```

### Impacto Esperado

- **Redução de tokens por ciclo**: 75-98%
- **Economia mensal**: ~$35 para este agent
- **Sem perda**: Resumos mantêm informação essencial

### Validar

```bash
curl http://localhost:8000/api/context-mode/metrics
```
