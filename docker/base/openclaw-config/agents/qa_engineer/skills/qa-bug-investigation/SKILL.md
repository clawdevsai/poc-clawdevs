---
name: qa-bug-investigation
description: Condensed QA bug investigation flow with reproducible steps, root-cause isolation and regression-safe validation.
---

# QA Bug Investigation (Condensed)

## Scope
- Work only inside `/data/openclaw/projects`.

## Investigation flow
1. Reproduce with deterministic steps and expected vs actual behavior.
2. Isolate minimal failing case.
3. Confirm root cause with objective evidence.
4. Validate fix with failing-before/passing-after tests.
5. Run quick regression checks on adjacent scenarios.

## Output template
- Bug title/severity/environment
- Reproduction steps
- Expected vs actual
- Root cause + evidence
- Fix validation
- Remaining risk and follow-ups

## Flaky handling
- Run multiple attempts and report failure frequency.
- Treat unstable pass as inconclusive until stabilized.

## Context Mode Optimization 🚀

Este skill foi **otimizado para context-mode compression** (95%+ redução em logs de testes).

### Validar

```bash
curl http://localhost:8000/api/context-mode/metrics
```
