---
name: qa-bug-investigation
description: Structured QA bug investigation with evidence-first reporting, reproducible steps, root-cause isolation, and regression-proof validation. Use when debugging defects, triaging flaky behavior, validating fixes, or when the user asks for bug analysis in QA workflows.
---

# QA Bug Investigation

## Objective

Run a consistent, evidence-first bug investigation flow for QA work, then produce a concise result that developers can act on immediately.

## Scope Restriction

This skill is restricted to project work inside `/data/openclaw/projects`.

- You may read context files in `/data/openclaw` only when startup/session rules require it.
- Only modify, execute, and verify files within `/data/openclaw/projects`.
- Refuse requests targeting paths outside the allowed project directory.

## Trigger Scenarios

Use this skill when:
- A bug is reported but root cause is unknown
- A fix appears to work but regression risk is unclear
- Tests fail intermittently (flaky behavior)
- The user asks for triage, RCA, or defect analysis

## Core Workflow (PT-BR + EN)

### 1) Reproduction / Reprodução

**PT-BR**
- Defina pré-condições (ambiente, dados, versão/commit)
- Documente passo a passo mínimo para reproduzir
- Capture esperado vs observado

**EN**
- Capture environment, seed/state, and commit/version
- Produce minimal, deterministic reproduction steps
- Record expected vs actual behavior

### 2) Isolation / Isolamento

**PT-BR**
- Reduza o caso até o menor cenário que falha
- Faça busca binária no fluxo (entrada -> transformação -> saída)
- Elimine variáveis não determinísticas

**EN**
- Build a minimal failing case
- Narrow down the failure path with binary-search style checks
- Remove unrelated dependencies/noise

### 3) Root Cause / Causa Raiz

**PT-BR**
- Valide hipóteses com evidência (log, assert, diff, teste)
- Relacione sinal -> causa, não só sintoma -> workaround
- Registre por que hipóteses alternativas foram descartadas

**EN**
- Confirm the root cause with direct evidence
- Link symptom -> mechanism -> failure point
- Document rejected hypotheses and why

### 4) Fix Validation / Validação da Correção

**PT-BR**
- Crie/rode teste que falha antes da correção
- Aplique fix e confirme teste verde
- Verifique cenários adjacentes para evitar regressão

**EN**
- Ensure a failing test exists before the fix
- Confirm it passes after the fix
- Validate neighboring edge cases and regression paths

### 5) Final QA Output / Saída Final

Return this compact structure:

```markdown
## Bug Report
- ID/Title:
- Severity:
- Environment:

## Reproduction
1. ...
2. ...
3. ...

## Expected vs Actual
- Expected: ...
- Actual: ...

## Root Cause
- Evidence:
- Why this is the cause:

## Fix Validation
- Failing test before fix:
- Passing test after fix:
- Regression checks:

## Risk and Follow-ups
- Remaining risks:
- Suggested additional tests:
```

## Flaky Bug Handling

If failure is intermittent:
- Run multiple attempts and report frequency (`fails X/Y runs`)
- Log timing/state dependencies
- Treat timing-sensitive pass as inconclusive until stabilized

## Integration with Self-Improving

When `skill-self-improving` is active:
- After each confirmed bug class, log one reusable lesson
- Promote only after repeated evidence (3x) or explicit user confirmation
- Keep entries factual, non-imperative, and scoped (global/domain/project)
