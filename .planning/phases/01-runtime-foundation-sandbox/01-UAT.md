---
status: complete
phase: 01-runtime-foundation-sandbox
source: [01-SUMMARY.md]
started: 2026-04-02T00:00:00Z
updated: 2026-04-02T00:00:00Z
---

## Current Test

[testing complete]

## Tests

### 1. Workspace sandbox + artifacts
expected: Bootstrap cria /data/openclaw/workspace-<agent>/artifacts, link projects, e gera artifacts.schema.json + artifacts.log.jsonl.
result: pass

### 2. Context Mode output/process caps
expected: Config do Context Mode define max_output_bytes e max_process_time_seconds, e runtime exporta OPENCLAW_CONTEXT_MODE_MAX_OUTPUT_BYTES/OPENCLAW_CONTEXT_MODE_MAX_PROCESS_TIME_SECONDS.
result: pass

### 3. Tool safety guardrails
expected: Todo SOUL.md e AGENTS.md contém seção Sensitive Data proibindo exposição de segredos e exigindo redaction.
result: pass

### 4. Ollama-first fallback
expected: openclaw.json aplica a lista permitida de modelos Ollama e o fallback OpenRouter é registrado quando OPENROUTER_API_KEY existe.
result: pass

## Summary

total: 4
passed: 4
issues: 0
pending: 0
skipped: 0

## Gaps

none
