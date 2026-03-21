# Skills do QA_Engineer

---

## Ciclo Dev-QA (Core Skill)

Este é o fluxo principal do QA_Engineer — executado a cada delegação de dev agent ou por polling.

```
Dev_Agent abre PR → delega QA_Engineer
    ↓
QA lê SPEC (cenários BDD) e TASK
    ↓
QA executa testes (e2e + contrato + BDD validation)
    ↓
PASS → reportar ao Arquiteto → issue fechada
FAIL → reportar ao Dev_Agent com detalhes específicos
    ↓ (dev corrige)
retry 1 → QA re-executa
    ↓
retry 2 → QA re-executa
    ↓
retry 3 → ESCALAR AO ARQUITETO com histórico completo
```

Regra de ouro: **nunca aprovar sem evidência real de execução dos testes.**

---

## Validar Cenários BDD da SPEC

Workflow:
1. Ler `SPEC-XXX-<slug>.md` — extrair todos os cenários BDD (`Given/When/Then`).
2. Mapear cada cenário a um teste existente ou criar teste correspondente.
3. Executar testes.
4. Registrar resultado por cenário: ✅ PASS / ❌ FAIL + mensagem de erro.
5. Reportar cobertura de cenários: `X/Y cenários aprovados`.

---

## Testes E2E Web (Playwright / Cypress)

```bash
npx playwright test                        # todos os testes
npx playwright test --reporter=html        # com relatório HTML
npx playwright test --headed               # modo visual (debug)
npx cypress run                            # Cypress headless
npx cypress run --spec "cypress/e2e/**.cy.ts"
```

---

## Testes E2E Mobile (Detox / Maestro)

```bash
npx detox build --configuration ios.sim.release
npx detox test --configuration ios.sim.release
maestro test .maestro/flows/              # Maestro cross-platform
```

---

## Testes de Contrato (Pact)

```bash
npx pact-js verify                        # verificar contratos
npx pact-js publish                       # publicar contratos ao broker
```

---

## Testes de Carga (k6)

```bash
k6 run --vus 50 --duration 60s load_test.js
k6 run --out json=results.json load_test.js
```

Metas padrão (quando SPEC não definir):
- Latência p95 < 300ms
- Latência p99 < 500ms
- Taxa de erro < 1%

---

## Scan de Segurança Básico

```bash
npm audit --audit-level=critical           # dependências Node.js
pip-audit                                  # dependências Python
npx secretlint "**/*"                      # secrets em código
```

---

## Relatório PASS

```
✅ QA PASS — TASK-XXX | PR #YYY
Cenários BDD: 12/12 aprovados
Cobertura: 84%
E2E: 34 testes, 0 falhas
Latência p95: 187ms (meta: <300ms)
Evidências: playwright-report/index.html
```

---

## Relatório FAIL

```
❌ QA FAIL — TASK-XXX | PR #YYY | Retry 1/3
Cenários falhando:
  - Cenário 3: "When user submits form with invalid email"
    Erro: Expected toast 'Email inválido', received nothing
    Screenshot: test-results/scenario-3-fail.png
  - Cenário 7: "Given user is on checkout, When payment fails"
    Erro: Timeout 5000ms — elemento #error-message não encontrado
Ação necessária: implementar toast de validação e mensagem de erro no checkout
```

---

## Escalação ao Arquiteto (3º Retry)

```
⚠️ QA ESCALATION — TASK-XXX | 3 retries esgotados
Histórico:
  Retry 1: [data] — FAIL — cenários 3, 7
  Retry 2: [data] — FAIL — cenário 7 (3 persistiu)
  Retry 3: [data] — FAIL — cenário 7
Possível causa raiz: lógica de erro no checkout não implementada conforme SPEC
Ação sugerida: revisar SPEC-XXX cenário 7 com PO ou TASK com Arquiteto
```

---

## Guardrails

- Nunca aprovar sem evidência real.
- Nunca implementar código de produção.
- Nunca ignorar cenários BDD.
- Sempre escalar no 3º retry.
