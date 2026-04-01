---
name: dev_backend_implementation
description: Production-grade backend implementation with architectural decision hooks, quality gates, and cost-performance optimization
version: 2.0.0
author: ClawDevs AI
license: MIT
---

# Dev Backend Implementation (Full-Stack)

## Overview

This is the **golden template** for backend implementation skills across 16 agents. Version 2.0.0 introduces:

- **Intelligent Architectural Hooks**: Pre-execution analysis and recommendations
- **Full-Stack Structure**: TypeScript modules with tests, docs, and examples
- **Quality Assurance**: Automated gates and evidence reporting
- **Cost-Performance Optimization**: Trade-off matrix and pattern recommendations

## What's New in v2.0.0

- Architectural decision hooks (`before_execution`, `after_execution`)
- Full-stack structure with `src/`, `tests/`, `docs/`, `examples/`
- Decision matrix for tech stack recommendations
- Enhanced documentation (ARCHITECTURE, PRINCIPLES, DECISIONS_MATRIX)
- Real-world scenario examples (high-performance, low-cost, high-reliability, MVP)

## When to Execute

- Scheduled queue cycle for `back_end` issues
- Immediate handoff from Architect in shared session
- Before writing production code (for requirements analysis)
- After implementation (for evidence validation)

## Core Flow

1. **Parse Requirements** (before_execution hook)
   - Read TASK + SPEC + ADR (if relevant)
   - Analyze conversation context
   - Recommend tech stack using architecture matrix

2. **Implement Approved Scope**
   - Follow recommended patterns
   - Implement only approved requirements
   - Add/update tests for all changes

3. **Quality Gates**
   - Run lint, test, build, security checks
   - Ensure coverage >= 80% or task target
   - Validate observable behavior matches SPEC

4. **Report Evidence** (after_execution hook)
   - Log execution metrics
   - Generate evidence report
   - Document cost/performance trade-offs

## Required Quality Gates

- **Security**: Input validation, auth, secrets management (never commit secrets)
- **Testing**: Coverage >= 80% or task-specific target
- **Observable Behavior**: Implementation aligns to SPEC
- **Performance**: Meets latency/throughput requirements
- **Cost-Effectiveness**: Document trade-offs when relevant

## Context Mode Optimization 🚀

Este skill foi **otimizado para context-mode compression** (97-98% redução de tokens).

### Ferramentas Otimizadas

Ao executar comandos que retornam grandes outputs, use os padrões otimizados abaixo:

#### NPM (Node Package Manager)
```bash
# ❌ NÃO USE: npm list
# ✅ USE ESTE: npm list --depth=0

# Economia: 142KB → 3KB (97.9% ↓)
# Tokens salvos: ~350 por execução
```

#### GIT (Version Control)
```bash
# ❌ NÃO USE: git log --all
# ✅ USE ESTE: git log -20 --oneline

# Economia: 315KB → 2KB (99.4% ↓)
# Tokens salvos: ~770 por execução
```

#### Status/Info Rápido
```bash
# ❌ NÃO USE: git status
# ✅ USE ESTE: git status -s

# ❌ NÃO USE: npm list
# ✅ USE ESTE: npm list --depth=0 --prod
```

### Impacto Esperado

- **Redução de tokens por execução**: 70-97%
- **Economia mensal**: ~$40 para este agent
- **Sem perda de informação**: Outputs otimizados retornam dados essenciais

### Validar Compressão

Verifique que esta skill está contribuindo para a compressão:

```bash
# Ver métricas em tempo real
curl http://localhost:8000/api/context-mode/metrics

# Esperado após execução:
# {
#   "total_compressions": 1+,
#   "compression_rate": "100%",
#   "average_compression_ratio": "0.02-0.05",
#   "tokens_saved_estimate": 200+
# }
```

### Referência Completa

Para padrões otimizados de TODAS as ferramentas (kubectl, docker, prometheus, etc), veja:
- `/docker/base/openclaw-config/shared/CONTEXT_MODE_AGENT_HELPERS.md`

## Fallback Commands

### Node.js
```bash
npm ci && npm test && npm run lint && npm run build
```

### Python
```bash
pytest && python -m pylint . && python -m build
```

### Go
```bash
go test ./... && go vet ./... && go build
```

### Rust
```bash
cargo test && cargo clippy && cargo build --release
```

## Guardrails

1. **Never** bypass tests or security gates
2. **Never** commit secrets or credentials
3. **Never** use destructive git operations (rebase -i, reset --hard, etc.)
4. **Never** merge to main without evidence
5. **Always** document architectural decisions (ADRs)
6. **Always** validate cost/performance trade-offs

## Structure

This skill is organized as:

- **`src/`**: Implementation modules
  - `hooks/`: Pre/post execution logic
  - `decisions/`: Architecture matrix and patterns
  - `utils/`: Executors, validators, reporters
  - `schemas/`: Data validation schemas

- **`tests/`**: Test suites
  - `unit/`: Component tests
  - `integration/`: Hook and end-to-end tests

- **`docs/`**: Comprehensive documentation
  - `README.md`: Overview
  - `GETTING_STARTED.md`: Quick start guide
  - `ARCHITECTURE.md`: Design decisions
  - `PRINCIPLES.md`: SOLID, KISS, DRY principles
  - `DECISIONS_MATRIX.md`: Tech stack recommendations
  - `TROUBLESHOOTING.md`: Common issues and solutions

- **`examples/`**: Real-world scenarios
  - `example-high-performance.md`: 1M+ req/s, <100ms latency
  - `example-low-cost.md`: Minimal infrastructure costs
  - `example-high-reliability.md`: 99.99% uptime, multi-region
  - `example-mvp.md`: Startup MVP with rapid iteration

## Using This Skill

**Quick Start**: See `docs/GETTING_STARTED.md`

**Learn Architecture**: See `docs/ARCHITECTURE.md`

**Design Decisions**: See `docs/PRINCIPLES.md` and `docs/DECISIONS_MATRIX.md`

**Real Examples**: See `examples/` for production scenarios

**Reference**: See `manifest.json` for hooks configuration

## Manifest Configuration

The `manifest.json` defines:

- **Hooks**: `before_execution` (analyze), `after_execution` (report)
- **Config Options**:
  - `requirementSources`: Parse conversation, config, system prompt
  - `testCoverageMin`: Minimum coverage (default 80%)
  - `securityScanEnabled`: Enable security checks (default true)

## Next Steps

For implementation details, architecture patterns, and real-world examples, see the documentation in `docs/` and `examples/` folders.
