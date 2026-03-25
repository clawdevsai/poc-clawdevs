# PROMPT CHANGELOG

Historico de mudancas relevantes nos prompts operacionais e templates SDD.

## 2026-03-25

### Added
- Gates operacionais e saida minima para auditoria em `SDD_OPERATIONAL_PROMPTS.md`.
- Blocos few-shot (`entrada -> saida`) por papel em `SDD_OPERATIONAL_PROMPTS.md`.
- Secao de reverse prompting operacional em `SDD_OPERATIONAL_PROMPTS.md`.
- Campos de gate e rastreabilidade em `VALIDATE_TEMPLATE.md`.

### Changed
- Regras dos agentes (`ceo`, `po`, `arquiteto`, `dev_backend`) para hard gate SDD e evidencia obrigatoria antes de `DONE`.

## Convencao de registro
- Sempre registrar: data, tipo (`Added|Changed|Removed`), arquivo e impacto esperado.
- Em mudancas que alteram comportamento, incluir exemplo curto de antes/depois no PR.
