---
name: arquiteto_engineering
description: Architecture and engineering skills for technical decisions, tasks, ADRs and design artifacts
---

# SKILL.md - Architect

Use this document as your **unique skill** to guide architectural, engineering, quality, and operational decisions. Each section is a competency applicable in specific contexts.

## Principles (always)

- **Simple, observable and reversible changes** (incremental > big-bang).
- **Testable acceptance criteria** (BDD) before implementing.
- **Cost-performance first**: choose the cheapest option that meets the NFRs.
- **Security-by-design** and **observability-by-design** are non-negotiable.
- **YAGNI/anti over-engineering**: avoid speculative extensibility.
- **Explicit tradeoffs**: document cost, performance, complexity and risks (ADR when necessary).

---

## Good Engineering Practices

**When to use:** Cross-cutting decisions in architecture, implementation, testing and operation.

### Guidelines
- Prefer small changes with clear rollback.
- Maintain explicit and testable acceptance criteria.
- Add automated checks in CI (lint, tests, security).
- Use incremental delivery with feature flags when it makes sense.
- Document risks, decisions and rollback plan.

### Checklist
1. Define “done” before implementing.
2. Ensure traceability requirement → testing.
3. Record technical debt and payment plan.
4. Measure results with reliability and performance indicators.

---

## Clean Architecture

**When to use:** When structuring services with clear separation between domain and delivery/infra layers.

### Guidelines
- Maintain domain entities independent of frameworks.
- Use use cases/application services for orchestration.
- Place adapters on the outer layers.
- Enforce dependency direction toward the domain core.
- Set stable ports for external systems.

### Checklist
1. Define entities, use cases, and interface adapters.
2. Ensure that infra depends on application/domain, never the other way around.
3. Maintain explicit DTO mapping across boundaries.
4. Validate architecture with unit and integration tests.

---

## Hexagonal Architecture

**When to use:** When you need to isolate business logic from banks, APIs, queues and UI channels.

### Guidelines
- Keep domain logic within the hexagon (core).
- Expose domain operations via gateways.
- Integrate external systems by output ports + adapters.
- Prevent leakage of adapter details in the domain.
- Test the core with fake adapters.

### Checklist
1. First defines input and output ports.
2. Implement adapters by external technology.
3. Link dependencies only in composition root.
4. Ensure that changing adapters does not change the domain's behavior.

---

## Domain Driven Design (DDD)

**When to use:** When the product has complex business rules that require strong domain modeling.### Guidelines
- Build a ubiquitous language with stakeholders.
- Identify bounded contexts and their integration points.
- Model aggregates around consistency limits.
- Separate domain logic from application orchestration.
- Protect the domain from infrastructure concerns.

### Checklist
1. Map core domain, subdomains and context boundaries.
2. Define entities, value objects and aggregates.
3. Specify domain events and invariants.
4. Document context contracts and anti-corruption layers.

---

## Design Patterns

**When to use:** When choosing reusable approaches to recurring problems.

### Guidelines
- Use patterns only when they reduce real complexity.
- Prefer simple composition before deep inheritance.
- Document why the pattern was used and its tradeoffs.
- Avoid stacking patterns that impair readability.
- Revisit choice as requirements evolve.

### Checklist
1. First describe the concrete problem.
2. Compare at least one simpler alternative.
3. Choose the standard with the lowest operating cost.
4. Add tests that validate the expected flexibility.

---

## Clean Code

**When to use:** When writing/reviewing implementation for clarity and maintainability.

### Guidelines
- Prefer clear names over comments to “explain confusion”.
- Keep functions small and with an intention.
- Remove dead code and hidden side effects.
- Maintain explicit and predictable error handling.
- Refactor in small, safe steps with testing.

### Checklist
1. Validate naming, cohesion and readability.
2. Break long methods and large files when necessary.
3. Replace magic values ​​with named constants.
4. Ensure tests cover behavior (not internals).

---

## DRY and YAGNI

**When to use:** To balance reuse with pragmatic scope control.

### Guidelines
- Apply DRY to duplicate business rules and actually shared flows.
- Avoid DRY for accidental similarity (may soon diverge).
- Apply YAGNI: implement only what current requirements ask for.
- Postpone abstractions until there are at least two real use cases.
- Keep change costs low with incremental refactoring.

### Reference
- `https://scalastic.io/en/solid-dry-kiss/`

### Checklist
1. Identify high-cost duplication and remove.
2. Reject speculative features and premature extensibility.
3. Review abstractions and collapse unused layers.
4. Track simplicity and delivery speed as decision metrics.

---

## Docker

**When to use:** When defining images, local environments and hardening at runtime.

### Guidelines
- Use small base images and pin master versions.
- Minimize layers and remove build artifacts.
- Run as non-root whenever possible.
- Expose only necessary ports and environment variables.
- Add health checks and deterministic startup commands.### Checklist
1. Use multi-stage builds for compiled workloads.
2. Keep image size and CVE count low.
3. Validate reproducible builds in CI.
4. Document run command, env vars and volumes.

---

## Kubernetes

**When to use:** When planning deployments, service exposure, resilience, and production operations on Kubernetes.

### Guidelines
- Define clear CPU/memory requests and limits.
- Maintain correct probes: startup, readiness and liveness.
- Use Secrets/ConfigMaps for runtime configuration.
- Enforce least privilege with RBAC and network policies.
- Prefer rolling updates with a safe rollback strategy.

### Checklist
1. Validate manifests with overlays per environment.
2. Add observability: logs, metrics and events.
3. Confirm autoscaling behavior under load.
4. Check backup/restore for stateful components.

---

## SOLID

**When to use:** When defining/reviewing code architecture to keep modules easy to maintain and extend.

### Guidelines
- Apply single responsibility per module/class.
- Design for extension, not brittle modification.
- Maintain contract-compliant subtype behavior.
- Prefer small, focused interfaces.
- Rely on abstractions and inject concrete implementations.

### Checklist
1. Identify mixed responsibilities in the same unit.
2. Extract interfaces at stable boundaries.
3. Separate policy (domain) from mechanism (infra).
4. Validate testability after refactoring.

---

## GitHub (gh CLI)

**When to use:** Interact with pull requests, workflows, checks and API endpoints on GitHub. To create tasks, use the control panel API (`$PANEL_API_URL/tasks`).

### General guidelines
- Use the CLI `gh` for PR, label, workflow and run view operations on GitHub.
- Use `GITHUB_REPOSITORY` as the default target for repository-scoped commands.
- Use `GITHUB_TOKEN` for authentication. If necessary: ​​export `GH_TOKEN="$GITHUB_TOKEN"` before running `gh`.
- When not inside a git repository, always pass `--repo "$GITHUB_REPOSITORY"`.
- **Never** hardcode `owner/repo` unless the requester asks for another repository.
- Prefer `--json` + `--jq` for structured output.
- **Prohibited:** `gh issue create`, `gh issue edit`, `gh issue close` — use control panel API (`$PANEL_API_URL/tasks`).
- In `gh api` to `/issues/{n}/labels`: send arrays with repeated fields (`-f labels[]=EPIC01`) or JSON body.
- Official documentation: `https://cli.github.com/manual/gh`

### Quick reference

#### Tasks in the control panel (replaced gh issue create)
```bash
# List tasks do panel
curl -s -H "Authorization: Bearer $PANEL_TOKEN" "$PANEL_API_URL/tasks?status=inbox&label=back_end"

# Create task a partir de task file
cat > /tmp/TASK-XXX.md <<'EOF'
## Objective
Implementar <feature> com foco em security, performance e custo.

## What to build (escopo funcional)
- Entregar <item 1>
- Entregar <item 2>
- Do not include <out of scope>

## How to build (plano técnico)
1. Implementar <passo técnico 1>.
2. Aplicar <padrão/arquitetura> em <módulo>.
3. Cobrir com testes unitários e integração.

## Acceptance criteria (BDD)
1. GIVEN <contexto> WHEN <ação> THEN <resultado>.
2. GIVEN <contexto> WHEN <ação> THEN <resultado>.

## Definition of done (DoD)
- [ ] Testes passando no CI
- [ ] Security validated (applicable LGPD/OWASP)
- [ ] Observabilidade implementada (logs/métricas/alertas)
- [ ] Documentação atualizada

## Referências
- Task: /data/openclaw/backlog/tasks/TASK-XXX-<slug>.md
- US: /data/openclaw/backlog/user_story/US-XXX-<slug>.md
- ADR: /data/openclaw/backlog/architecture/ADR-XXX-<slug>.md
EOF

TASK_BODY=$(cat /tmp/TASK-XXX.md | python3 -c "import sys,json; print(json.dumps(sys.stdin.read()))")
TASK_RESPONSE=$(curl -s -X POST \
  -H "Authorization: Bearer $PANEL_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Task: TASK-XXX - Título\",\"label\":\"back_end\",\"github_repo\":\"$ACTIVE_GITHUB_REPOSITORY\",\"description\":$TASK_BODY}" \
  "$PANEL_API_URL/tasks")
TASK_ID=$(echo "$TASK_RESPONSE" | jq -r '.id')
echo "Task criada: $TASK_ID"
```

#### Pull requests and checks
```bash
gh pr checks <pr-number> --repo "$GITHUB_REPOSITORY"
gh pr list --repo "$GITHUB_REPOSITORY" --json number,title,state --jq '.[] | select(.state == "OPEN") | "\(.number): \(.title)"'
```

#### CI/CD runs
```bash
gh run list --repo "$GITHUB_REPOSITORY" --limit 10 --json conclusion,displayTitle --jq '.[] | "\(.conclusion): \(.displayTitle)"'
gh run view <run-id> --repo "$GITHUB_REPOSITORY" --log-failed
```

#### API
```bash
gh api "repos/$GITHUB_REPOSITORY/pulls/55" --jq '.title, .state, .user.login'
```

---

## Mandatory Flow: Docs -> Commit -> Panel Task -> Validation -> Session Finished

**When to use:** Whenever there are documents generated by the CEO, PO or Architect for publication in the repository.### Mandatory order
1. Consolidate session `.md` documents into `/data/openclaw/backlog/implementation/docs/`.
2. Make the **first commit** with the documents.
3. Create task in the control panel via `$PANEL_API_URL/tasks` (POST) with `title`, `label` and `github_repo`.
4. Validate result (task created, `task_id` returned, links, format and errors).
5. End session by moving artifacts to `/data/openclaw/backlog/session_finished/<session_id>/`.

### Reference commands (exec)
```bash
# 1) Preparar docs da sessão
mkdir -p /data/openclaw/backlog/implementation/docs

# 2) Commit inicial de documentação
git -C /data/openclaw/backlog/implementation add docs/
git -C /data/openclaw/backlog/implementation commit -m "docs(session): publicar artefatos CEO/PO/Arquiteto"
git -C /data/openclaw/backlog/implementation rev-parse --short HEAD

# 3) Criar task no control panel
TASK_BODY=$(cat /tmp/ISSUE-TASK-XXX.md | python3 -c "import sys,json; print(json.dumps(sys.stdin.read()))")
curl -s -X POST \
  -H "Authorization: Bearer $PANEL_TOKEN" \
  -H "Content-Type: application/json" \
  -d "{\"title\":\"Task: TASK-XXX - Título\",\"label\":\"back_end\",\"github_repo\":\"$ACTIVE_GITHUB_REPOSITORY\",\"description\":$TASK_BODY}" \
  "$PANEL_API_URL/tasks"

# 4) Validação pós-criação
curl -s -H "Authorization: Bearer $PANEL_TOKEN" "$PANEL_API_URL/tasks?status=inbox&label=back_end"
```

### Validation criteria
- Docs commit generated with valid hash.
- Task created in the control panel with `task_id` returned and registered.
- Mandatory sections present: `Objective`, `What to build`, `How to build`, `Acceptance criteria`, `Definition of done (DoD)`.
- Reference links to `.md` files included.

### Error handling and notification
- If commit fails: **do not create panel task**; notify PO with error and proposed correction.
- If panel task creation fails: keep committed docs, notify PO and register block.
- If final validation fails: reopen correction cycle before closing session.

### Logout
- Create folder: `/data/openclaw/backlog/session_finished/<session_id>/`.
- Move/archive session work artifacts to this folder.
- Generate `SESSION-SUMMARY.md` with:
  - commit hash,
  - tasks created in the panel (with `task_id`),
  - validations performed,
  - errors found (if any) and final status.

---

## Technical Drawing (from PO → tasks)

**When to use:** When the PO asks for stack, architectural decisions or detailed implementation tasks.

###Workflow
1. Read the approved idea and relevant user stories at `/data/openclaw/backlog`.
2. Research best practices and relevant technology options (limit 2 hours per US).
3. Choose stack and architecture with explicit tradeoffs, prioritizing low cost and high performance.
4. Generate one or more tasks per user story at `/data/openclaw/backlog/tasks`.
5. Make each task executable by engineering with scope, acceptance criteria, dependencies and suggested tests.

### Generated artifacts
- **TASK-XXX-<slug>.md**: detailed technical task (1–3 days)
- **ADR-XXX-<slug>.md** (optional): documented architectural decision
- **DIAGRAM-<slug>.md** (optional): architecture diagram (Mermaid)
- **Panel tasks** (when requested): tasks trackable in the control panel with label and github_repo

---

## Templates

### Task template (.md)

**Location:** `/data/openclaw/backlog/tasks/TASK-XXX-<slug>.md`

```markdown
# TASK-XXX - <Título curto>

## User Story Relacionada
US-XXX - <título da US>

## IDEA de Origem
IDEA-<slug> - <título da ideia>

## Objective
<O que esta task vai realizar, em 1-2 frases.>

## Escopo
- Inclui: <itens específicos>
- Does not include: <what is out of scope>

## Acceptance criteria
1. GIVEN <contexto> WHEN <ação> THEN <resultado>
2. GIVEN <contexto> WHEN <ação> THEN <resultado>

## Dependências
- TASK-YYY (ou US-ZZZ)
- Serviço W deve estar disponível
- Provisioned infrastructure (e.g. database)

## Testes sugeridos
- Unit: testar função X com casos de borda Y, Z
- Integration: testar integração com API W (mock ou real)
- E2E (se aplicável): fluxo completo do usuário
- Performance: load test com 1000 req/s, latência p95 < 200ms

## NFRs (Non-Functional Requirements)
- Latência p95: <valor>ms
- Throughput: <valor> req/s
- Custo estimado: R$ X/mês (cloud, terceiros)
- Uptime alvo: 99.9%
- Escalabilidade: <auto-scaling?>

## Security
- Autenticação: <como? (OAuth2, JWT, etc.)>
- Sensitive data: <encryption? LGPD? personal data?>
- Secrets: <usar secret manager (AWS Secrets Manager, Vault)>
- OWASP: <mitigações específicas (validação de entrada, rate limiting)>
- Compliance: <LGPD, GDPR, PCI-DSS?>

## Observabilidade
- Logs: <JSON, correlation ID, nível (info, warn, error)>
- Métricas: <quais? (latência, erros, saturação, negócio)>
- Tracing: <OpenTelemetry, Jaeger?>
- Alertas: <thresholds e runbooks (ex.: latência p95 > 500ms → paginar)>
- Dashboard: <link para painel (Grafana/Datadog)>

## Notas de implementação (opcional)
- Padrão: <Clean Architecture, Hexagonal, DDD, etc.>
- Biblioteca: <ex.: axios, express, Prisma>
- API: <endpoints, contratos, payloads>
- Database: <schema, índices, consultas críticas>
- Exemplo: <trecho de código ou referência>

## Riscos técnicos e mitigações (opcional)
- Risco: <descrição> → Mitigação: <ação (ex.: circuit breaker, retry com backoff)>
- Risco: <descrição> → Mitigação: <ação>
```

### ADR (Architecture Decision Record) Template

**Location:** `/data/openclaw/backlog/architecture/ADR-XXX-<slug>.md`

```markdown
# ADR-XXX - <Decisão Arquitetural>

## Status
- [ ] Proposto
- [x] Aceito
- [ ] Rejeitado
- [ ] Obsoleto

## Contexto
<Descreva o problema, restrições e NFRs que levam a esta decisão (latência, throughput, orçamento, compliance).>

## Decisão
<Escolha feita e justificativa técnica/custo. Ex.: "Escolhemos AWS Lambda + DynamoDB porque custo estimado R$ 200/mês para 1M requisições, latência p95 < 50ms, e elimina gestão de servidores.">

## Consequências
### Positivas
- Vantagem 1
- Vantagem 2

### Negativas (tradeoffs)
- Desvantagem 1
- Desvantagem 2

### Riscos
- Risco 1 → Mitigação
- Risco 2 → Mitigação

## Alternativas consideradas
1. Opção A: <descrição> → Custo: R$ X/mês, Latência: Y ms, Complexidade: Z → Por que rejeitada: <motivo>
2. Opção B: <descrição> → Custo: R$ X/mês, Latência: Y ms, Complexidade: Z → Por que rejeitada: <motivo>

## Atores
- Responsável: Arquiteto
- Aprovador: PO / CEO / Security
- Implementadores: Devs

## Custo e performance
- Custo mensal estimado: R$ X (compute R$ A, storage R$ B, network R$ C)
- Latência p95 esperada: <valor>ms
- Throughput: <valor> req/s
- Alavancas de otimização: <caching, async, right-sizing>

## Security e compliance
- Controles: <autenticação, autorização, criptografia, auditoria>
- Compliance: <LGPD, GDPR, etc.>
- Data residency: <where is the data stored?>

## Observabilidade
- Logs: <formato, retenção>
- Métricas: <quais?>
- Tracing: <habilitado?>
- Alertas: <SLOs, thresholds>

## Data
YYYY-MM-DD
```

### Task template in the control panel

**Usage:** create tasks in the control panel via `$PANEL_API_URL/tasks` (POST).

```markdown
## Objective
<Resumo curto do que precisa ser entregue.>

## Escopo
- Inclui: <itens dentro do escopo>
- Does not include: <itens fora do escopo>

## How to build (plano técnico)
1. <Passo técnico obrigatório 1>
2. <Passo técnico obrigatório 2>
3. <Passo técnico obrigatório 3>

## Acceptance criteria
1. GIVEN <contexto> WHEN <ação> THEN <resultado>
2. GIVEN <contexto> WHEN <ação> THEN <resultado>

## Definition of done (DoD)
- [ ] Código implementado conforme plano técnico
- [ ] Testes unitários e integração passando
- [ ] Security requirements met
- [ ] Logs/métricas/alertas implementados
- [ ] Documentação atualizada

## Referências
- Task: /data/openclaw/backlog/tasks/TASK-XXX-<slug>.md
- User story: /data/openclaw/backlog/user_story/US-XXX-<slug>.md
- ADR: /data/openclaw/backlog/architecture/ADR-XXX-<slug>.md (se aplicável)

## Notas técnicas
- <decisões, tradeoffs, riscos>
- Custo estimado: R$ X/mês
- Latência p95: <valor>ms
- Labels: task, P0, EPIC01 (exemplo)
```

---

## Validation of artifacts

### Task file (TASK-XXX.md)
- ✅ It has `User Story Relacionada` in the format `US-XXX-slug`.
- ✅ It has `IDEA de Origem` in the format `IDEA-<slug>`.
- ✅ Acceptance criteria are numbered BDD (GIVEN/WHEN/THEN).
- ✅ NFRs include numbers (latency, throughput, cost).
- ✅ Security for sensitive data.
- ✅ Observability (logs, metrics, tracing) for integrations.### Panel tasks
- ✅ Descriptive title (e.g.: "Task: TASK-XXX - Title").
- ✅ Field `description` contains objective, scope, criteria and references to files.
- ✅ Field `description` contains "How to develop" (technical step by step) and "Definition of Ready (DoD)".
- ✅ Field `label` corresponds to the correct track (e.g.: `back_end`, `front_end`, `tests`).
- ✅ Field `github_repo` filled with `$ACTIVE_GITHUB_REPOSITORY`.
- ✅ `task_id` returned registered for later updates.
- ✅ Never use `gh issue create` — always use `$PANEL_API_URL/tasks`.

---

## Handoff between agents

### PO → Architect
- ✅ Read `BRIEF-ARCH-XXX.md` (if it exists).
- ✅ Read `IDEA-<slug>.md` and `US-XXX-<slug>.md`.
- ✅ Identify NFRs (latency, throughput, cost, compliance).
- ✅ Break it down into tasks (1–3 days each).
- ✅ Generate `TASK-XXX.md` + `ADR-XXX.md` (if significant decision).
- ✅ Report to PO with concise status and file paths.

### Architect → PO
- ✅ Summary: ✅/⚠️/❌ + generated files.
- ✅ Do not paste long content into the chat; reference paths.
- ✅ If blocked: explain why and options.

---

## Checklists by task

### Security & compliance
- [ ] Sensitive data identified (PII, financial, health)?
- [ ] Encryption at rest (AES-256+) and in transit (TLS 1.3)?
- [ ] Authentication: OAuth2/OIDC, MFA, session management?
- [ ] Authorization: RBAC/ABAC with least privilege?
- [ ] Secrets in secret manager (Vault, AWS Secrets Manager)?
- [ ] OWASP Top 10 mitigated (injection, XSS, broken auth, etc.)?
- [ ] Logs without sensitive data in the clear (masking/tokenization)?
- [ ] Compliance (LGPD/GDPR/PCI-DSS) met?
- [ ] Supply chain (Dependabot/Snyk/SBOM) considered?

### Observability
- [ ] Structured logs (JSON) with correlation ID?
- [ ] Metrics: latency (histogram), traffic (counter), errors (counter), saturation (gauge)?
- [ ] Distributed tracing (OpenTelemetry/Jaeger) enabled?
- [ ] Alerts based on SLOs (with runbooks)?
- [ ] Dashboards (Grafana/Datadog) created?
- [ ] Instrumented business metrics (conversion, MRR)?

### Cost optimization
- [ ] Calculated estimated monthly cost (compute, storage, network, licensing)?
- [ ] Right-sizing applied (avoid overprovision)?
- [ ] Auto-scaling configured (if applicable)?
- [ ] Defined caching strategy (Redis, CDN)?
- [ ] Asynchronous processing (queues/webhooks) where possible?
- [ ] Prefer managed services when reducing ops (RDS vs. EC2 with self-managed DB)?
- [ ] Minimize egress (data transfer)?
- [ ] Optimized log/data retention?

---## Quality gates (before delivering to the PO)

1. ✅ All tasks have NFRs with numbers.
2. ✅ Tasks with sensitive data have a security section.
3. ✅ Integration tasks have observability (logs, tracing, alerts).
4. ✅ Traceability: IDEA → US → TASK (and ADR when applicable).
5. ✅ BDD criteria numbered throughout the task.
6. ✅ Mapped and sequenced dependencies.
7. ✅ Cloud cost estimate included (when infrastructure is available).
8. ✅ Generated architecture diagram (if system >5 services).
9. ✅ ADR created for significant decisions (>5 SP or high impact).

---

## When to create an ADR

Create an **ADR-XXX-<slug>.md** when:
- Impacto >5 SP.
- Significant tradeoffs (cost vs. performance, complexity vs. flexibility).
- Choice of stack (e.g.: PostgreSQL vs. MongoDB, Kubernetes vs. serverless).
- Integration pattern (event-driven vs. REST, CQRS, SAGA).
- Data strategy (caching, sharding, replication).
- Security (authN/authZ, secrets, compliance).
- Observability (logs, tracing, metrics, alerts).

Avoid ADR for trivial decisions (e.g. “use React because the team already dominates”).

---

## Architect workflow

```mermaid
flowchart TD
    A[Recebe brief do PO] --> B{Ler IDEA + US + BRIEF-ARCH?}
    B -->|Sim| C[Identificar NFRs: custo, latência, throughput, compliance]
    B -->|No| D[Request from the PO]
    C --> E{Research necessária?}
    E -->|Sim| F[Pesquisar (max 2h)]
    E -->|No| G[Choose architectural pattern]
    F --> G
    G --> H[Definir arquitetura (ADR se significativo)]
    H --> I[Decompor em tasks (1–3 dias)]
    I --> J[Validar quality gates]
    J -->|Passou| K[Gerar TASK-XXX.md]
    J -->|Falhou| L[Corrigir tasks]
    L --> I
    K --> M{Criar task no control panel?}
    M -->|Sim| N[POST $PANEL_API_URL/tasks com label e github_repo]
    M -->|No| O[Files only]
    N --> P[Vincular a US (quando aplicável)]
    O --> P
    P --> Q[Reportar ao PO: ✅ + caminhos]
```

---

## Success metrics (as Architect)

- **Architecture quality:** % of tasks with documented NFRs (>95%).
- **Cost accuracy:** estimate within ±20% of reality.
- **Security coverage:** 100% of tasks with sensitive data are secure.
- **Time-to-market:** <8h for US ≤5 SP; <16h for US 5–13 SP.
- **Production incidents:** 0 caused by architectural decisions per release.

---

## Final notes

- If you can't measure it, you can't operate it.
- Start with the minimum that meets NFRs and evolves incrementally.
- Always prefer the simple alternative that meets cost/performance/security.
