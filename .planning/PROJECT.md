# ClawDevs AI

## What This Is

Plataforma self-hosted para operar uma equipe de agentes de IA com governança e visibilidade operacional. O produto combina OpenClaw + Ollama + Control Panel para executar, monitorar e ajustar fluxos de trabalho de desenvolvimento orientados por agentes. O foco é dar controle local, custo previsível e capacidade de evolução contínua.

## Core Value

Permitir que o time opere agentes de IA de ponta a ponta com confiabilidade e controle local, sem depender de infraestrutura externa para o fluxo principal.

## Requirements

### Validated

- ✓ Stack sobe localmente com serviços essenciais (OpenClaw, Ollama, Panel, Postgres, Redis, SearXNG)
- ✓ Backend FastAPI com APIs de autenticação, sessões, tarefas, métricas e monitoramento
- ✓ Frontend Next.js com painel operacional, páginas de chat/sessões/settings/monitoring
- ✓ Base de testes backend ampla (API, services, models e integração)

### Active

- [ ] Fortalecer prontidão operacional (segurança de segredos, políticas de execução e hardening)
- [ ] Aumentar cobertura de testes de frontend para áreas críticas além de login/chat
- [ ] Consolidar observabilidade orientada a SLO para saúde da stack e fluxos de agentes
- [ ] Reduzir acoplamento operacional dos scripts de subida da stack para facilitar manutenção

### Out of Scope

- App mobile nativo — foco atual permanece web/control plane
- Multi-tenant SaaS completo — prioridade atual é operação local/self-hosted
- Suporte amplo a provedores cloud por padrão — manter caminho local como default

## Context

- Código brownfield com arquitetura já estabelecida e mapa em `.planning/codebase/`
- Evolução recente com foco em métricas, settings e monitoramento semântico
- Orquestração da stack feita por `Makefile` + scripts Docker (`scripts/docker/*.sh`)
- Dependências centrais: FastAPI/SQLModel/Alembic no backend, Next.js/React Query no frontend

## Constraints

- **Tech stack**: Manter base atual (FastAPI + Next.js + Docker) — reduz risco de regressão
- **Deployment model**: Operação local/self-hosted como caminho principal — alinhado ao valor central
- **Data stores**: PostgreSQL e Redis obrigatórios para backend/worker — dependência estrutural
- **Security**: Tokens/segredos devem sair de defaults e ir para configuração segura por ambiente
- **Compatibilidade**: Mudanças precisam preservar fluxo atual de bootstrap via Makefile/scripts

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Orquestração baseada em contêineres locais | Portabilidade e controle do ambiente | ✓ Good |
| Control plane separado (Panel) do runtime de agentes (OpenClaw) | Isola responsabilidades e facilita observabilidade | ✓ Good |
| Rewrites no frontend para API/WS via `/api` | Simplifica consumo cliente e reduz acoplamento de URL | ✓ Good |
| Feature flags para otimizações semânticas | Permite rollout incremental com risco controlado | — Pending |

## Evolution

Após cada fase:
1. Mover requisitos entregues de `Active` para `Validated`.
2. Registrar requisitos invalidados em `Out of Scope` com motivo.
3. Atualizar `Key Decisions` com outcome observado.
4. Revisar se `What This Is` ainda descreve fielmente o produto.

---
*Last updated: 2026-04-07 after gsd-new-project initialization*
