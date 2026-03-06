# 05 — Fluxos de Trabalho e Ciclo de Vida
> **Objetivo:** Definir o Definition of Done (DoD), o workflow do board, code review e estratégias de CI/CD para novos produtos, manutenção e evolução.
> **Público-alvo:** Scrum Master, Devs
> **Ação Esperada:** SM deve garantir que as transições de estado sigam estes fluxos. Devs e QA devem consultar as responsabilidades e *gates* de auditoria.

**v2.0 | Atualizado em: 06 de março de 2026**

---

## Visão Geral dos Três Fluxos

```mermaid
graph LR
    subgraph NOVO["🆕 Novo Produto"]
        NP["Ideia → PRD → Arq →\nDev → QA → Deploy → Monitor"]
    end
    subgraph MANUT["🔧 Manutenção"]
        M["Alerta → Triage → Root Cause\n→ Fix → QA → Deploy → RCA"]
    end
    subgraph EVOL["🚀 Evolução"]
        E["Feedback → Feature →\nSprint → Dev → QA → Flag → A/B → Release"]
    end

    CLAW["Claw (CEO)\nPriya (PO)\nAxel (Arch)\nDev (Dev)\nQuinn (QA)"]

    CLAW -->|orquestra| NOVO & MANUT & EVOL
```

---

## Fluxo Completo — Desenvolvimento de um novo software (do zero)

```mermaid
flowchart TD
    A[Ideia ou oportunidade de produto] --> B[Research de mercado e usuários]
    B --> C[Definição de visão do produto]
    C --> D[Product Requirements Document PRD]
    D --> E[Revisão executiva / aprovação]
    E --> F[Definição de arquitetura]
    F --> G[Planejamento técnico e backlog]

    G --> H[Design UX UI]
    G --> I[Setup de infraestrutura]

    H --> J[Desenvolvimento de features]
    I --> J

    J --> K[Code Review]
    K --> L[Testes automatizados]

    L --> M[Integração contínua CI]
    M --> N[Build do sistema]

    N --> O[Testes de integração]
    O --> P[Testes de segurança]

    P --> Q[Deploy em ambiente staging]
    Q --> R[Testes de QA]

    R --> S[Deploy produção CD]
    S --> T[Monitoramento e observabilidade]

    T --> U[Coleta de métricas]
    U --> V[Feedback de usuários]

    V --> W[Iteração do produto]
    W --> J
```

### Painel de tarefas — Desenvolvimento de um novo software (do zero)

```mermaid
flowchart LR

subgraph Ideacao
A1[Ideia do produto]
A2[Pesquisa de mercado]
A3[Definição da visão]
end

subgraph Planejamento
B1[PRD - Documento de requisitos]
B2[Definição da arquitetura]
B3[Criação do backlog]
end

subgraph Design
C1[UX Research]
C2[Design de interface]
C3[Prototipo]
end

subgraph Desenvolvimento
D1[Setup do repositório]
D2[Infraestrutura cloud]
D3[Desenvolvimento de features]
end

subgraph Qualidade
E1[Testes automatizados]
E2[Testes integração]
E3[QA manual]
end

subgraph Deploy
F1[Build CI]
F2[Deploy Staging]
F3[Deploy Produção]
end

subgraph Monitoramento
G1[Observabilidade]
G2[Logs e métricas]
G3[Feedback usuários]
end

A1 --> A2 --> A3
A3 --> B1 --> B2 --> B3
B3 --> C1 --> C2 --> C3
C3 --> D1 --> D2 --> D3
D3 --> E1 --> E2 --> E3
E3 --> F1 --> F2 --> F3
F3 --> G1 --> G2 --> G3
```

### Responsabilidade por Agente — Novo Produto

```mermaid
graph TD
    subgraph CEO_ZONE["🎯 Claw — CEO"]
        A1["Valida ideia e oportunidade"]
        A2["Aprova PRD e visão"]
        A3["Revisão executiva / go/no-go"]
        A4["Aprovação final de arquitetura"]
        A5["Aprova deploy produção"]
        A6["Analisa métricas e decide iteração"]
    end

    subgraph PO_ZONE["📋 Priya — PO"]
        B1["Research de mercado e usuários"]
        B2["Escreve PRD completo"]
        B3["Cria backlog + épicos + stories"]
        B4["Prioriza features no sprint"]
        B5["Coleta e organiza feedback de usuários"]
        B6["Define critérios de aceite"]
    end

    subgraph ARCH_ZONE["🏗️ Axel — Architect"]
        C1["Define arquitetura do sistema"]
        C2["Cria ADRs para decisões técnicas"]
        C3["Setup de infraestrutura (K8s, DB, CI)"]
        C4["Planejamento técnico do backlog"]
        C5["Review de arquitetura em cada PR complexo"]
        C6["Configura pipeline CI/CD"]
    end

    subgraph DEV_ZONE["👨‍💻 Dev — Developer"]
        D1["Implementa features do sprint"]
        D2["Escreve testes unitários"]
        D3["Cria branches e commits no Gitea"]
        D4["Abre PRs para review"]
        D5["Corrige issues do code review"]
        D6["Resolve bugs apontados pelo QA"]
    end

    subgraph QA_ZONE["🧪 Quinn — QA"]
        E1["Define estratégia de testes"]
        E2["Escreve testes de integração"]
        E3["Executa testes de segurança"]
        E4["Review de PRs (qualidade)"]
        E5["Testes de QA em staging"]
        E6["Aprova release para produção"]
        E7["Monitora qualidade pós-deploy"]
    end
```

### Sequência A2A — Novo Produto (fase crítica: PRD → Implementação)

```mermaid
sequenceDiagram
    participant DIR as 👤 Diretor
    participant CEO as Claw (CEO)
    participant PO as Priya (PO)
    participant ARCH as Axel (Arch)
    participant DEV as Dev
    participant QA as Quinn

    DIR->>CEO: "#ceo novo produto: app de gestão de times"
    CEO->>PO: A2A: TASK_DELEGATE — research_market(app gestão times)
    CEO->>ARCH: A2A: TASK_DELEGATE — feasibility_check(app gestão times)

    Note over PO,ARCH: Trabalho paralelo (slots independentes)

    PO-->>CEO: A2A: TASK_RESULT — research(concorrentes, dores, TAM)
    ARCH-->>CEO: A2A: TASK_RESULT — feasibility(tech_stack, riscos, estimativa)

    CEO->>DIR: "✅ Research e feasibility prontos. Aprovação para PRD?"
    DIR->>CEO: "Aprovado, siga"

    CEO->>PO: A2A: TASK_DELEGATE — write_prd(produto, constraints)
    PO-->>CEO: A2A: TASK_RESULT — prd_draft.md (Gitea issue #1)
    CEO->>DIR: "📄 PRD criado — PR #1 para revisão"

    DIR->>CEO: "#ceo PRD aprovado"
    CEO->>ARCH: A2A: TASK_DELEGATE — design_architecture(prd)
    ARCH-->>CEO: A2A: TASK_RESULT — ADR-001.md + system_design.md

    CEO->>PO: A2A: TASK_DELEGATE — create_backlog(prd, arch)
    PO-->>CEO: A2A: TASK_RESULT — 23 issues criados no Gitea, Sprint 1 planejado

    CEO->>DEV: A2A: TASK_DELEGATE — implement(sprint_1_issues)
    DEV->>QA: A2A: CONTEXT_REQUEST — test_strategy(sprint_1)
    QA-->>DEV: A2A: CONTEXT_UPDATE — test_plan_s1.md

    loop Sprint 1
        DEV->>DEV: Implementa issue, cria PR
        DEV->>QA: A2A: TASK_DELEGATE — review_pr(PR#N)
        QA-->>DEV: A2A: TASK_RESULT — approved/changes_requested
        DEV->>ARCH: A2A: TASK_DELEGATE — arch_review_pr(PR#N) se complexo
    end

    DEV-->>CEO: A2A: TASK_RESULT — sprint_1_complete (5 PRs merged)
    CEO->>QA: A2A: TASK_DELEGATE — staging_qa(branch: main)
    QA-->>CEO: A2A: TASK_RESULT — qa_report_v1 (passed: 94%)
    CEO->>DIR: "🚀 Sprint 1 pronto para deploy em staging"
```

### Artefatos Produzidos por Etapa

| Etapa | Artefato | Agente Responsável | Onde |
|-------|----------|-------------------|------|
| Research | `research-report.md` | Priya (PO) | Gitea issue |
| PRD | `prd-v1.md` | Priya (PO) | Gitea issue #1 |
| Arquitetura | `ADR-001.md`, `system-design.md` | Axel (Arch) | Gitea repo /docs |
| Backlog | Issues Gitea + Milestones | Priya (PO) | Gitea issues |
| Infra | K8s manifests, CI config | Axel (Arch) | Gitea repo /infra |
| Feature | Branch + commits + PR | Dev | Gitea repo |
| Tests | `test_*.py`, cobertura | Quinn (QA) | Gitea repo /tests |
| Security | SAST report, `pentest.md` | Quinn (QA) | Gitea security tab |
| Deploy | Changelog, release tag | Dev + CEO | Gitea releases |
| Observability | Dashboards Grafana, alertas | Axel (Arch) | Grafana |

---

## Fluxo Completo — Manutenção de software

```mermaid
flowchart TD

A[Monitoramento do sistema] --> B[Alerta ou incidente detectado]

B --> C[Triage do problema]

C --> D{Tipo de problema}

D -->|Bug| E[Abertura de ticket]
D -->|Performance| F[Análise de métricas]
D -->|Infraestrutura| G[Investigação DevOps]

E --> H[Reprodução do bug]
F --> H
G --> H

H --> I[Análise da causa raiz]

I --> J[Correção do código]

J --> K[Code Review]
K --> L[Testes automatizados]

L --> M[Build e CI]

M --> N[Deploy em staging]

N --> O[Testes QA]

O --> P[Deploy produção]

P --> Q[Monitoramento pós deploy]

Q --> R[Encerramento do incidente]
```

### Painel de tarefas — Manutenção de software

```mermaid
flowchart LR

subgraph Monitoramento
A1[Monitoramento sistema]
A2[Alerta detectado]
A3[Abertura de incidente]
end

subgraph Analise
B1[Triage do problema]
B2[Reprodução do bug]
B3[Análise causa raiz]
end

subgraph Correção
C1[Correção do código]
C2[Code Review]
C3[Testes automatizados]
end

subgraph Validacao
D1[Build CI]
D2[Deploy Staging]
D3[Testes QA]
end

subgraph Resolucao
E1[Deploy Produção]
E2[Monitoramento pós deploy]
E3[Encerramento incidente]
end

A1 --> A2 --> A3
A3 --> B1 --> B2 --> B3
B3 --> C1 --> C2 --> C3
C3 --> D1 --> D2 --> D3
D3 --> E1 --> E2 --> E3
```

### Responsabilidade por Agente — Manutenção

```mermaid
graph LR
    subgraph TRIAGE["🚨 Triage (Claw + Priya)"]
        T1["Claw: classifica severidade\n(CRITICAL/HIGH/MEDIUM/LOW)"]
        T2["Priya: cria ticket no Gitea\ncom contexto e impacto"]
        T3["Claw: aciona agente certo\nbug→Dev · perf→Arch · infra→Arch"]
    end

    subgraph ROOT_CAUSE["🔍 Root Cause (Dev + Arch)"]
        R1["Dev: reproduz o bug\n(branch hotfix/*)"]
        R2["Arch: analisa logs e métricas\nPrometheus + Grafana"]
        R3["Dev+Arch: identifica causa raiz\ndocumenta no ticket"]
    end

    subgraph FIX["🔨 Fix (Dev)"]
        F1["Dev: implementa correção\nbranch hotfix/issue-N"]
        F2["Dev: testa localmente\npassa unit tests"]
        F3["Dev: abre PR para review"]
    end

    subgraph VALIDATION["✅ Validação (Quinn + CEO)"]
        V1["Quinn: review do PR\n(foco em regressão)"]
        V2["Quinn: testes de regressão\nauto em staging"]
        V3["CEO: aprova deploy produção\npara CRITICAL/HIGH"]
    end

    subgraph POSTMORTEM["📋 Post-mortem (CEO + PO)"]
        P1["CEO: write post-mortem\nraiz, impacto, resolução"]
        P2["Priya: cria issue de prevenção\n(previne recorrência)"]
        P3["Axel: propõe melhorias\nna arquitetura se sistêmico"]
    end

    TRIAGE --> ROOT_CAUSE --> FIX --> VALIDATION --> POSTMORTEM
```

### SLA por Severidade

```mermaid
graph TD
    CRIT["🔴 CRITICAL\nSistema down · Data loss · Breach"]
    HIGH["🟠 HIGH\nFeature quebrada · Degradação >30%"]
    MED["🟡 MEDIUM\nBug com workaround · Perf leve"]
    LOW["⚪ LOW\nCosmético · Docs · Tech debt"]

    CRIT -->|"SLA: 15min → ação\n2h → produção"| C_FLOW["CEO notificado imediato\nDev+Arch em paralelo\nHotfix sem sprint planning"]
    HIGH -->|"SLA: 2h → ação\n24h → produção"| H_FLOW["CEO notificado\nNext slot disponível\nSprint prioridade máxima"]
    MED -->|"SLA: 24h → ação\n1 semana → produção"| M_FLOW["Priya prioriza no backlog\nPróximo sprint disponível"]
    LOW -->|"SLA: 1 semana → ação\nBacklog"| L_FLOW["Priya adiciona ao backlog\nQuando houver slack no sprint"]
```

### Sequência A2A — Incidente Crítico (CRITICAL)

```mermaid
sequenceDiagram
    participant PROM as 📊 Prometheus
    participant ORCH as Orquestrador
    participant CEO as Claw (CEO)
    participant ARCH as Axel (Arch)
    participant DEV as Dev
    participant QA as Quinn
    participant DIR as 👤 Diretor

    PROM->>ORCH: Alert: 500_error_rate > 10% (5min)
    ORCH->>CEO: A2A: BROADCAST_ALERT — incident(severity: CRITICAL)

    CEO->>DIR: "🚨 CRITICAL: taxa de erro >10% em produção"

    CEO->>ARCH: A2A: TASK_DELEGATE — investigate_metrics(last_30min)
    CEO->>DEV: A2A: TASK_DELEGATE — reproduce_bug(error_logs)

    Note over ARCH,DEV: Root cause paralelo

    ARCH-->>CEO: A2A: TASK_RESULT — "Deploy 14:32 alterou config Redis TTL → session expiry"
    DEV-->>CEO: A2A: TASK_RESULT — "Reproduzido: logout forçado a cada 60s"

    CEO->>DIR: "Root cause: config Redis TTL. Solução: rollback config ou hotfix. Autoriza hotfix?"
    DIR->>CEO: "Hotfix, pode ir"

    CEO->>DEV: A2A: TASK_DELEGATE — hotfix(fix_redis_ttl, priority: CRITICAL)
    DEV-->>CEO: A2A: TASK_RESULT — PR#52 aberto (hotfix/redis-ttl)

    CEO->>QA: A2A: TASK_DELEGATE — review_pr(52, fast_track: true)
    QA-->>CEO: A2A: TASK_RESULT — approved (regression: pass)

    CEO->>DIR: "✅ Hotfix pronto. Autoriza deploy produção?"
    DIR->>CEO: "Deploy"

    CEO->>ARCH: A2A: TASK_DELEGATE — deploy_hotfix(PR#52, env: production)
    ARCH-->>CEO: A2A: TASK_RESULT — deployed (v1.4.1-hotfix)

    CEO->>PROM: Monitor 5min pós-deploy
    PROM-->>CEO: error_rate: 0.2% (normal)

    CEO->>DIR: "✅ Incidente resolvido. Escrevo post-mortem?"
    DIR->>CEO: "Sim"
    CEO->>CEO: Gera post-mortem + issue de prevenção
```

---

## Fluxo Completo — Evolução de software (novas features)

```mermaid
flowchart TD

A[Feedback de usuários] --> B[Análise de dados do produto]
B --> C[Identificação de oportunidades]

C --> D[Definição de nova feature]

D --> E[Prioritização no roadmap]

E --> F[Planejamento de sprint]

F --> G[Design UX]

G --> H[Especificação técnica]

H --> I[Desenvolvimento da feature]

I --> J[Code Review]

J --> K[Testes automatizados]

K --> L[Integração contínua CI]

L --> M[Deploy em staging]

M --> N[Testes QA]

N --> O[Feature Flag ativada]

O --> P[Lançamento gradual]

P --> Q[A/B Testing]

Q --> R[Análise de métricas]

R --> S{Feature bem sucedida}

S -->|Sim| T[Release global]
S -->|Não| U[Iterar melhoria]

U --> I
```

### Painel de tarefas — Evolução de software (novas features)

```mermaid
flowchart LR

subgraph Descoberta
A1[Feedback usuários]
A2[Análise de dados]
A3[Identificação de oportunidade]
end

subgraph Produto
B1[Definição da feature]
B2[Priorização roadmap]
B3[Planejamento sprint]
end

subgraph Design
C1[UX Design]
C2[Protótipo]
C3[Validação]
end

subgraph Engenharia
D1[Implementação]
D2[Code Review]
D3[Testes automatizados]
end

subgraph Release
E1[Build CI]
E2[Deploy Staging]
E3[Testes QA]
end

subgraph Experimento
F1[Feature Flag]
F2[A/B Test]
F3[Análise métricas]
end

subgraph Resultado
G1[Release global]
G2[Iteração melhoria]
end

A1 --> A2 --> A3
A3 --> B1 --> B2 --> B3
B3 --> C1 --> C2 --> C3
C3 --> D1 --> D2 --> D3
D3 --> E1 --> E2 --> E3
E3 --> F1 --> F2 --> F3
F3 --> G1
F3 --> G2
```

### Feature Flag + A/B Testing com Agentes

```mermaid
sequenceDiagram
    participant PO as Priya (PO)
    participant DEV as Dev
    participant QA as Quinn
    participant ARCH as Axel (Arch)
    participant CEO as Claw (CEO)
    participant DIR as 👤 Diretor

    Note over PO: Feature #88: Notificações push

    PO->>DEV: A2A: TASK_DELEGATE — implement(issue#88, with_feature_flag: true)
    DEV->>DEV: Implementa com flag FEAT_PUSH_NOTIFICATIONS=false

    DEV->>QA: A2A: TASK_DELEGATE — review_pr(PR#61)
    QA-->>DEV: A2A: TASK_RESULT — approved

    DEV->>ARCH: A2A: TASK_DELEGATE — deploy_staging(PR#61)
    ARCH-->>DEV: A2A: TASK_RESULT — deployed to staging

    QA->>QA: Testes QA completos em staging
    QA-->>CEO: A2A: TASK_RESULT — qa_passed (cobertura: 89%)

    CEO->>ARCH: A2A: TASK_DELEGATE — enable_feature_flag(FEAT_PUSH_NOTIFICATIONS, pct: 5)
    Note over ARCH: Canary: 5% dos usuários

    ARCH-->>CEO: A2A: TASK_RESULT — flag enabled (5% canary)
    CEO->>DIR: "🚩 Feature flag ativa para 5% dos usuários. Monitorando 48h."

    Note over ARCH: Coleta métricas 48h

    ARCH->>CEO: A2A: TASK_DELEGATE — analyze_ab_metrics(feature: push_notif, duration: 48h)
    CEO->>CEO: Analisa: CTR +23%, retenção +8%, nenhum erro novo

    CEO->>DIR: "📈 A/B: CTR +23%, retenção +8%. Recomendo release global."
    DIR->>CEO: "Aprovado"

    CEO->>ARCH: A2A: TASK_DELEGATE — enable_feature_flag(FEAT_PUSH_NOTIFICATIONS, pct: 100)
    ARCH-->>CEO: A2A: TASK_RESULT — released globally

    CEO->>PO: A2A: TASK_DELEGATE — update_changelog_release_notes(feature#88)
    PO-->>CEO: A2A: TASK_RESULT — CHANGELOG.md atualizado, release tag v1.5.0
```

---

## Mapa Consolidado: Agente × Etapa × Ferramenta

| Etapa | Fluxo | Agente Principal | Agentes de Suporte | Ferramenta/MCP |
|-------|-------|-----------------|-------------------|----------------|
| Research de mercado | Novo | Priya (PO) | Claw (CEO) | WebSearch, Qdrant RAG |
| Definição de visão | Novo | Claw (CEO) | Priya (PO) | Gitea issue |
| PRD | Novo + Evol | Priya (PO) | Claw (CEO) | Gitea issue, mcp-filesystem |
| Aprovação executiva | Novo + Evol | Claw (CEO) | Diretor | Telegram (OpenClaw) |
| Arquitetura / ADR | Novo | Axel (Arch) | Claw (CEO) | Gitea repo, mcp-gitea |
| Setup infra / CI | Novo | Axel (Arch) | — | K8s manifests, Gitea CI |
| Design UX | Novo + Evol | Priya (PO) | Dev | Gitea issue (spec) |
| Especificação técnica | Evol | Axel (Arch) | Dev | Gitea issue, ADR |
| Planejamento backlog | Todos | Priya (PO) | Claw (CEO) | Gitea issues/milestones |
| Desenvolvimento | Todos | Dev | Axel (Arch) | mcp-gitea, mcp-filesystem |
| Code Review | Todos | Quinn (QA) | Axel (Arch) | mcp-gitea |
| Testes automáticos | Todos | Quinn (QA) | Dev | CI pipeline, Gitea Actions |
| Build / CI | Todos | Axel (Arch) | Quinn (QA) | Gitea Actions, K8s |
| Testes de segurança | Novo + Evol | Quinn (QA) | Axel (Arch) | SAST tools |
| Deploy staging | Todos | Axel (Arch) | Dev | K8s, mcp-gitea |
| QA staging | Todos | Quinn (QA) | — | Gitea, testes E2E |
| Deploy produção | Todos | Axel (Arch) | Claw (CEO) | K8s CD, aprovação CEO |
| Feature Flag | Evol | Axel (Arch) | Claw (CEO) | Feature flag service |
| A/B Testing | Evol | Claw (CEO) | Axel (Arch) | Métricas Prometheus |
| Monitoramento | Todos | Axel (Arch) | Quinn (QA) | Grafana, Prometheus |
| Triage incidente | Manutenção | Claw (CEO) | Priya (PO) | Prometheus alerts |
| Root cause analysis | Manutenção | Dev + Axel | Quinn (QA) | Logs Loki, Prometheus |
| Hotfix | Manutenção | Dev | Quinn (QA) | mcp-gitea, fast-track |
| Post-mortem | Manutenção | Claw (CEO) | Priya (PO) | Gitea issue |
| Coleta de feedback | Todos | Priya (PO) | Claw (CEO) | Dados produto, Telegram |

---

## Estados do Produto e Transições

```mermaid
stateDiagram-v2
    [*] --> CONCEITO : Ideia recebida

    CONCEITO --> PLANEJAMENTO : PRD aprovado pelo CEO
    PLANEJAMENTO --> DESENVOLVIMENTO : Sprint planejado
    DESENVOLVIMENTO --> REVISAO : PR aberto
    REVISAO --> DESENVOLVIMENTO : Changes requested
    REVISAO --> TESTES : Code review aprovado
    TESTES --> DESENVOLVIMENTO : Testes falharam
    TESTES --> STAGING : Testes passaram
    STAGING --> TESTES : QA falhou
    STAGING --> PRODUCAO : QA aprovado + CEO sign-off

    PRODUCAO --> MONITORAMENTO : Deploy completo
    MONITORAMENTO --> INCIDENTE : Alerta crítico
    INCIDENTE --> HOTFIX : Triage → root cause
    HOTFIX --> PRODUCAO : Hotfix aprovado + deploy

    MONITORAMENTO --> EVOLUCAO : Feedback + oportunidade
    EVOLUCAO --> PLANEJAMENTO : Feature definida

    PRODUCAO --> DESCONTINUADO : Decisão estratégica CEO
    [*] --> DESCONTINUADO
```

---

## Regras de Governança nos Fluxos

```mermaid
graph TD
    subgraph BLOQUEIOS["🔒 Bloqueios obrigatórios (gate reviews)"]
        G1["Gate 1: PRD aprovado pelo CEO\nAntes de qualquer linha de código"]
        G2["Gate 2: Arquitetura aprovada\nAntes de criar backlog"]
        G3["Gate 3: Code review aprovado\nAntes de testes"]
        G4["Gate 4: QA staging aprovado\nAntes de deploy produção"]
        G5["Gate 5: CEO sign-off\nDeploy CRITICAL e HIGH em prod"]
    end

    subgraph BYPASS["⚡ Fast-track (incidentes críticos)"]
        F1["CRITICAL: CEO pode autorizar\ndeploy sem Gate 2"]
        F2["HIGH: Gate 2 simplificado\n(arquitetura implícita)"]
        F3["Todos os outros gates\nmantidos mesmo em fast-track"]
    end

    subgraph AUDITORIA["📋 Audit trail obrigatório"]
        A1["Toda aprovação logada\nno PostgreSQL audit_log"]
        A2["Toda rejeição com motivo\nno Gitea PR comment"]
        A3["Post-mortem obrigatório\npara todo CRITICAL"]
    end
```

---

## Templates de Issues por Fluxo

### Template: Bug Report (Manutenção)

```markdown
<!-- Criado automaticamente por Claw (CEO) ao receber alerta -->
## 🐛 Bug Report #{{NUMBER}}

**Severidade:** {{CRITICAL|HIGH|MEDIUM|LOW}}
**Detectado em:** {{staging|production}}
**Data/hora:** {{TIMESTAMP}}

### Descrição
{{DESCRIÇÃO DO BUG}}

### Impacto
- Usuários afetados: {{N}}
- Funcionalidades afetadas: {{LISTA}}
- SLA de resolução: {{PRAZO}}

### Como reproduzir
1. {{PASSO 1}}
2. {{PASSO 2}}

### Logs relevantes
```
{{STACK TRACE / LOG}}
```

### Root cause (preenchido por Dev/Arch)
{{A PREENCHER}}

### Correção aplicada
{{A PREENCHER}}

**Assignee:** @dev-dev
**Reviewer:** @quinn-qa
**Aprovação deploy:** @claw-ceo (se CRITICAL/HIGH)
```

### Template: Feature Request (Evolução)

```markdown
<!-- Criado por Priya (PO) após análise de feedback -->
## ✨ Feature #{{NUMBER}}: {{NOME}}

**Épico:** {{EPICO}}
**Sprint:** {{SPRINT}}
**Story Points:** {{SP}}

### Por que (Why)
{{PROBLEMA QUE RESOLVE}}

### O que (What)
{{DESCRIÇÃO DA FEATURE}}

### Critérios de aceite
- [ ] {{CRITÉRIO 1}}
- [ ] {{CRITÉRIO 2}}
- [ ] {{CRITÉRIO 3}}

### Design UX
{{LINK PARA SPEC}}

### Notas técnicas (Arch)
{{A PREENCHER POR AXEL}}

### Feature flag
- [ ] Implementar com flag `FEAT_{{NOME_UPPER}}`
- [ ] A/B test planejado? {{SIM/NÃO}}

**Assignee:** @dev-dev
**Reviewer:** @quinn-qa
```

---

## Métricas de Saúde dos Fluxos (dashboard)

```mermaid
graph LR
    subgraph DORA["Métricas DORA"]
        D1["Deployment Frequency\nMeta: ≥ 1/semana"]
        D2["Lead Time for Changes\nMeta: < 3 dias"]
        D3["MTTR\n(Mean Time to Recovery)\nMeta: < 2h para CRITICAL"]
        D4["Change Failure Rate\nMeta: < 10%"]
    end

    subgraph QUALITY["Qualidade"]
        Q1["Cobertura de testes\nMeta: ≥ 80%"]
        Q2["PR cycle time\nMeta: < 4h"]
        Q3["Bugs em produção/semana\nMeta: < 3"]
    end

    subgraph VELOCITY["Velocidade do Time"]
        V1["Story points/sprint\n(baseline após Sprint 3)"]
        V2["Taxa de rework\nMeta: < 15%"]
        V3["Bloqueios/sprint\nMeta: < 2"]
    end
```

---


