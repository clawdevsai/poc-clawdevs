# 17 — Simulação de Cenários e Resposta do Time
> **Objetivo:** Fornecer provas de conceito e cenários táticos (ex: Novo Produto vs. Sustentação) do comportamento orquestrado do time de agentes.
> **Público-alvo:** Scrum Master, PO
> **Ação Esperada:** Scrum Master usa essas simulações para guiar a condução das reuniões e melhorar o prompt do Diretor.

**v2.0 | Atualizado em: 06 de março de 2026**

---

## Os dois times

```mermaid
graph TD
    subgraph DIRETOR["👤 Diretor (Diego)"]
        D_CMD["Comanda via Telegram\nDefine visão e prioridades"]
    end

    subgraph TIME_NOVO["🚀 Time Alpha — Novo Produto"]
        CEO_A["🎯 CEO — Claw\nConsolida e reporta"]
        PO_A["📋 PO — Priya\nDefine produto do zero"]
        ARCH_A["🏗️ Architect — Axel\nDefine arquitetura inicial"]
        DEV_A["💻 Developer — Dev\nConstrói o core"]
        QA_A["🧪 QA — Quinn\nValida qualidade desde o início"]
    end

    subgraph TIME_SUST["🔧 Time Beta — Sustentação"]
        CEO_B["🎯 CEO — Claw\nGerencia filas de bugs e features"]
        PO_B["📋 PO — Priya\nPrioriza sustentação vs. evolução"]
        ARCH_B["🏗️ Architect — Axel\nGuarda integridade arquitetural"]
        DEV_B["💻 Developer — Dev\nCorrige bugs e implementa melhorias"]
        QA_B["🧪 QA — Quinn\nEvita regressões"]
    end

    D_CMD -->|"#time-alpha"| TIME_NOVO
    D_CMD -->|"#time-beta"| TIME_SUST

    classDef novo fill:#05966922,stroke:#059669
    classDef sust fill:#2563EB22,stroke:#2563EB
    class CEO_A,PO_A,ARCH_A,DEV_A,QA_A novo
    class CEO_B,PO_B,ARCH_B,DEV_B,QA_B sust
```

---

# CENÁRIO 1 — Time Alpha: Novo Produto do Zero

**Projeto:** API de gerenciamento de tarefas com autenticação JWT, WebSocket para notificações em tempo real e deploy containerizado.

---

## Semana 1 — Kickoff e Definição

```mermaid
sequenceDiagram
    actor DIR as 👤 Diego (Diretor)
    participant OC as OpenClaw (Telegram)
    participant CEO as 🎯 Claw (CEO)
    participant PO as 📋 Priya (PO)
    participant ARCH as 🏗️ Axel (Architect)

    Note over DIR,ARCH: Dia 1 — Segunda-feira, 8h00

    DIR->>OC: "#time Novo projeto: API de tasks com JWT + WebSocket.\nStack: Python, FastAPI. Comecem."
    OC->>CEO: dispatch: project_kickoff
    CEO->>PO: A2A: "Novo projeto recebido. Levanta épicos e backlog inicial."
    CEO->>ARCH: A2A: "Defina ADR de stack para FastAPI + JWT + WebSocket"

    par PO trabalha em paralelo
        PO->>PO: cria épicos no Workspace
        PO->>PO: escreve user stories para MVP
    and Architect trabalha em paralelo
        ARCH->>ARCH: analisa stack, escreve ADR-001 (FastAPI + Pydantic)
        ARCH->>ARCH: escreve ADR-002 (JWT com refresh tokens)
        ARCH->>ARCH: escreve ADR-003 (WebSocket via Starlette)
    end

    PO-->>CEO: A2A: "Backlog pronto — 12 especificações criadas, 5 para o sprint 1"
    ARCH-->>CEO: A2A: "ADR-001, ADR-002, ADR-003 publicados no Workspace"
    CEO->>OC: consolidar e reportar
    CEO-->>DIR: via Telegram:\n"✅ Sprint 1 planejado.\n📋 5 issues, 3 ADRs.\n🗺️ Stack definida: FastAPI + JWT + WS\n⏭️ Dev começa amanhã."
```

---

## Semana 1 — Implementação e Primeiros PRs

```mermaid
sequenceDiagram
    participant PO as 📋 Priya
    participant DEV as 💻 Dev
    participant QA as 🧪 Quinn
    participant ARCH as 🏗️ Axel
    participant WK as Workspace

    Note over PO,WK: Dia 2 — Terça-feira

    PO->>DEV: A2A: "Especificação #1 pronta: estrutura base do projeto"
    DEV->>WK: cria branch feature/1-project-structure
    DEV->>DEV: implementa estrutura base\n+ Dockerfile + docker-compose\n+ health endpoint
    DEV->>WK: commit + envia para revisão #1
    DEV->>QA: A2A: "Código #1 pronto. Como testar: docker-compose up, GET /health"
    QA->>QA: roda testes\ndocker-compose up\nvalidação manual
    QA-->>ARCH: A2A: "Código #1 funcional. Revisar estrutura?"
    ARCH->>ARCH: valida Dockerfile\nconfirma padrões do ADR-001
    ARCH-->>DEV: A2A: "Aprovado. Adicionar .dockerignore."
    DEV->>WK: merge código finalizado ✅

    Note over PO,GIT: Dia 3 — Quarta-feira

    PO->>DEV: A2A: "Issue #2: endpoint de autenticação JWT (POST /auth/login)"
    DEV->>DEV: implementa com base no ADR-002\njwt_secret via env var\nrefresh token logic
    DEV->>QA: A2A: "PR #2 pronto. Testes: POST /auth/login com user/pass mock"
    QA->>QA: testa happy path + edge cases\ntoken expirado · credencial inválida · refresh
    QA->>ARCH: A2A: "Funcionando. Validar segurança do JWT?"
    ARCH->>ARCH: verifica: secret via env ✅\nrefresh rotation ✅\nnenhum log do token ✅
    ARCH-->>QA: "Aprovado — conforme ADR-002"
    DEV->>WK: merge código finalizado ✅
```

---

## Semana 2 — WebSocket, Testes e First Deploy

```mermaid
sequenceDiagram
    participant DEV as 💻 Dev
    participant QA as 🧪 Quinn
    participant ARCH as 🏗️ Axel
    participant CEO as 🎯 Claw
    participant DIR as 👤 Diego

    Note over DEV,DIR: Dia 6 — Segunda-feira

    DEV->>DEV: implementa WebSocket\n(issue #4: notificações em tempo real)
    DEV->>QA: A2A: "PR #5 — WebSocket pronto. Testar: ws://localhost:8000/ws/tasks"

    QA->>QA: testa conexão WebSocket\npersistência de sessão · reconexão · auth
    QA-->>ARCH: A2A: "Encontrei issue: WebSocket não valida token JWT. Bloqueando."
    ARCH-->>DEV: A2A: "Confirmado — bug de segurança. PR bloqueado até fix."
    DEV->>DEV: corrige: valida Bearer no\nheader de upgrade do WebSocket
    DEV->>QA: A2A: "Fix no PR #5. Revalidar segurança."
    QA->>ARCH: A2A: "Fix correto. Aguarda aprovação arquitetural."
    ARCH-->>DEV: A2A: "Aprovado ✅"
    DEV->>DEV: merge PR #5

    Note over CEO,DIR: Dia 7 — Daily Report

    CEO->>CEO: consolida: 5 issues fechadas\n2 PRs merged hoje\n1 bug de segurança encontrado e resolvido
    CEO-->>DIR: via Telegram:\n"📊 Daily Report — Dia 7\n\n✅ STATUS: Sprint 1 em dia\n🔒 SEGURANÇA: WebSocket auth fix (Quinn bloqueou e Dev corrigiu)\n📈 PROGRESSO: 5/5 issues do sprint fechadas\n⚠️ BLOQUEIO: Nenhum\n⏭️ PRÓXIMO: Deploy em staging amanhã"
```

---

## Fim da Semana 2 — Release v0.1

```mermaid
graph LR
    ISSUES["5 issues fechadas\n10 PRs merged\n3 ADRs documentados"]
    TESTS["23 testes\n100% passando\n0 vulnerabilidades abertas"]
    DEPLOY["Deploy em Docker\nlocal + staging\nHealthcheck verde"]
    REPORT["CEO enviou\n10 daily reports\n0 escalações ao Diretor"]

    subgraph V01["🎉 v0.1 Released"]
        ISSUES & TESTS & DEPLOY & REPORT
    end

    DIR["👤 Diego recebe:\n'✅ v0.1 pronta.\nAPI funcional com JWT + WebSocket.\nPronto para feedback.'"]

    V01 --> DIR
```

---

# CENÁRIO 2 — Time Beta: Sustentação e Evolução

**Contexto:** O produto (API de tasks) está em produção há 2 meses. Tem usuários reais. Chegaram 3 bugs críticos, 1 pedido de nova feature e 1 issue de performance.

---

## Fila de trabalho inicial

```mermaid
graph TD
    subgraph INBOX["📥 Fila chegando (segunda-feira 8h)"]
        BUG1["🔴 BUG #31 — Crítico\nToken não expira após logout"]
        BUG2["🟠 BUG #32 — Alto\nWebSocket cai após 30min idle"]
        BUG3["🟡 BUG #33 — Médio\nPaginação retorna itens duplicados"]
        FEAT1["🔵 FEATURE #34\nExportar tasks para CSV"]
        PERF1["⚡ PERF #35\nLentidão em listas grandes (> 1000 tasks)"]
    end
```

---

## PO prioriza a fila

```mermaid
sequenceDiagram
    participant CEO as 🎯 Claw
    participant PO as 📋 Priya
    participant ARCH as 🏗️ Axel
    participant DEV as 💻 Dev

    Note over CEO,DEV: Segunda-feira, 8h15

    CEO->>PO: A2A: "5 itens na fila. Priorize para o sprint de sustentação."
    PO->>ARCH: A2A: "BUG #31 token não expira após logout — impacto de segurança?"
    ARCH-->>PO: A2A: "🔴 CRÍTICO. JWT sem blacklist. Deve ser o #1 absoluto."
    PO->>PO: prioriza: #31 (seg) → #32 (ter) → #35 (qua) → #33 (qui) → #34 (sex)
    PO->>DEV: A2A: "BUG #31 é emergência de segurança. Começar agora."
    CEO-->>DIR: via Telegram:\n"⚠️ BUG #31 identificado como falha de segurança.\nDev está atacando agora. ETA: 2h."
```

---

## Resolução do BUG #31 — emergência de segurança

```mermaid
sequenceDiagram
    participant ARCH as 🏗️ Axel
    participant DEV as 💻 Dev
    participant QA as 🧪 Quinn

    ARCH->>DEV: A2A: "Solução: Cache em memória de tokens invalidados.\nConsulte ADR-002 antes de implementar."
    DEV->>DEV: lê ADR-002\nanalisa opções: cache em memória vs short-lived tokens
    DEV->>ARCH: A2A: "ADR-002 não cobre blacklist. Precisamos de ADR-004?"
    ARCH-->>DEV: A2A: "Correto. Vou escrever ADR-004: Token Revocation Strategy."
    ARCH->>ARCH: escreve ADR-004\n(Cache em memória com TTL = token expiry)
    ARCH->>DEV: A2A: "ADR-004 publicado. Implemente conforme ele."
    DEV->>DEV: implementa Memory blacklist\nPOST /auth/logout invalida token\nadd ao blacklist com TTL
    DEV->>QA: A2A: "PR #42 pronto. Crítico: testar logout invalidando token."
    QA->>QA: testa: logout → token blacklistado\ntenta usar token invalidado → 401\nreinicia cache → token expira (TTL)
    QA->>ARCH: A2A: "PR #42 seguro e funcionando."
    ARCH-->>DEV: A2A: "Aprovado ✅ — ADR-004 respeitado."
    DEV->>DEV: merge PR #42 hotfix
    DEV->>CEO: A2A: "BUG #31 resolvido. Deploy de hotfix recomendado."
    CEO-->>DIR: "🔒 BUG #31 corrigido e deployado.\nToken revocation via Cache Memória (ADR-004).\nNenhum usuário afetado na janela de exposição."
```

---

## Semana de sustentação — visão completa

```mermaid
gantt
    title Time Beta — Sprint de Sustentação (1 semana)
    dateFormat  YYYY-MM-DD
    section Bugs Críticos
        BUG 31 - Token logout (hotfix)    :crit, done, b31, 2026-03-09, 1d
        BUG 32 - WebSocket idle timeout   :active, b32, 2026-03-10, 1d
    section Performance
        PERF 35 - Query otimization       :p35, 2026-03-11, 1d
    section Bugs Médios
        BUG 33 - Paginação duplicada      :b33, 2026-03-12, 1d
    section Features
        FEAT 34 - Export CSV              :f34, 2026-03-13, 2d
    section Reviews e ADRs
        ADR-004 Token Revocation          :done, adr4, 2026-03-09, 1d
        ADR-005 WebSocket keepalive       :adr5, 2026-03-10, 1d
        ADR-006 Query optimization        :adr6, 2026-03-11, 1d
```

---

## Quinta-feira — BUG #33 e descoberta de dívida técnica

```mermaid
sequenceDiagram
    participant DEV as 💻 Dev
    participant ARCH as 🏗️ Axel
    participant PO as 📋 Priya
    participant CEO as 🎯 Claw

    DEV->>DEV: analisa BUG #33 (paginação duplicada)
    DEV->>ARCH: A2A: "Encontrei a causa raiz: não é bug de paginação.\nÉ problema de índice no Banco Local. Query sem ORDER BY consistente."
    ARCH-->>DEV: A2A: "Confirmo. Isso também explica a lentidão do PERF #35.\nRaiz comum: ausência de índice composto em (user_id, created_at)."

    ARCH->>PO: A2A: "Descoberta: 2 issues têm raiz comum.\nSugiro fechar #33 e #35 juntos com 1 PR de fix + índice."
    PO-->>ARCH: A2A: "Faz sentido. Atualizo as issues e vínculo ao mesmo PR."

    DEV->>DEV: implementa: índice composto + ORDER BY correto + query refactor
    DEV->>QA: A2A: "PR #45 fecha #33 e #35. Testar: paginação + performance com 10k records."
    QA->>QA: cria dataset de teste 10k tasks\nmede latência antes: 2.3s\nmede latência depois: 180ms ✅
    QA-->>ARCH: A2A: "PR #45 aprovado. Melhoria de 92% na latência."

    CEO->>CEO: atualiza relatório semanal\n2 issues resolvidas com 1 PR
    CEO-->>DIR: "⚡ PERF #35 + BUG #33 resolvidos juntos.\nLatência em listas: 2.3s → 180ms (-92%).\nÍndice composto adicionado (ADR-006)."
```

---

## Sexta-feira — FEAT #34 e self_evolution proposta

```mermaid
sequenceDiagram
    participant DEV as 💻 Dev
    participant QA as 🧪 Quinn
    participant CEO as 🎯 Claw
    participant DIR as 👤 Diego

    DEV->>DEV: implementa exportação CSV\nstreamingResponse para arquivos grandes
    DEV->>QA: A2A: "PR #46 — Export CSV. Testar: GET /tasks/export com auth JWT"
    QA->>QA: testa: arquivo gerado corretamente\nautenticação obrigatória ✅\narquivos grandes (10k tasks) funcionam ✅

    Note over CEO,DIR: Sexta-feira — Daily Report + Proposta de evolução

    CEO->>CEO: consolida semana:\n5 issues fechadas · 5 PRs merged\n4 ADRs novos · 0 escalações
    CEO-->>DIR: "📊 Weekly Report — Time Beta\n\n✅ BUG #31 🔒 #32 🔌 #33 📄 #35 ⚡ fechados\n✅ FEAT #34 entregue\n🆕 ADR-004 005 006 publicados\n\n💡 Proposta do time:\nQA sugere adicionar testes de carga\nao pipeline CI. Quer que ative #evolui?"

    DIR-->>CEO: "#evolui — aprovo. Quinn pode propor os testes de carga."

    CEO->>QA: A2A: "self_evolution ativo. Proponha melhoria de CI com testes de carga."
    QA->>QA: cria PR de evolução:\n+ locust em CI/CD\n+ threshold: p95 < 500ms\n+ alertas automáticos
    QA->>DIR: via CEO + OpenClaw: "PR #evolui-001 pronto para revisão."
    DIR->>DIR: revisa diff
    DIR-->>CEO: "Aprovado ✅"
    CEO->>CEO: merge + atualiza SOUL do QA\nnovas skills: load_testing, ci_integration
```

---

## Comparativo: Time Alpha vs. Time Beta

```mermaid
graph LR
    subgraph ALPHA["🚀 Time Alpha — Novo Produto"]
        A_MINDSET["Mentalidade: exploração\nDecisões arquiteturais abertas\nVelocidade > perfeição no início\nADRs criam a fundação"]
        A_RITMO["Ritmo: sprints de features\nBacklog novo a cada sprint\nCelebra o 'primeiro' de tudo"]
        A_RISCO["Risco principal:\nDecisões ruins de arquitetura\nSão caras de reverter depois"]
    end

    subgraph BETA["🔧 Time Beta — Sustentação"]
        B_MINDSET["Mentalidade: preservação\nDecisões seguem ADRs existentes\nEstabilidade > velocidade\nRegression testing é lei"]
        B_RITMO["Ritmo: fila de bugs + features\nPriorização constante\nCelebra zero regressões"]
        B_RISCO["Risco principal:\nFix de bug introduz novo bug\nDívida técnica acumulada"]
    end

    subgraph SHARED["Compartilhado pelos dois times"]
        S1["SOUL · Políticas · Primícias\nidênticos nos dois times"]
        S2["A2A + Contexto compartilhado\npor projeto, não por time"]
        S3["CEO reporta ao mesmo Diretor\nconsolidado por time"]
    end

    ALPHA & BETA --> SHARED
```

---

## Daily report CEO — formato padrão

```
📊 Daily Report — [Time Alpha/Beta] — [Data]

✅ STATUS: [Em dia / Atrasado / Bloqueado]

📈 PROGRESSO:
• Issues fechadas hoje: N
• PRs merged: N
• ADRs criados: N

🔒 SEGURANÇA: [nenhum incidente / incidente X resolvido]

⚠️ BLOQUEIOS: [nenhum / descreve bloqueio e quem está resolvendo]

💡 DESCOBERTAS: [insights técnicos ou de produto relevantes]

⏭️ PRÓXIMOS PASSOS:
• Amanhã: [Dev implementa issue #X]
• Esta semana: [QA valida milestone Y]
• Atenção: [item que pode precisar de decisão do Diretor]
```

---

## Estados emocionais dos agentes (simulação realista)

O time de agentes não é neutro — cada SOUL tem uma "voz" característica:

| Situação | Claw (CEO) | Priya (PO) | Axel (Architect) | Dev (Developer) | Quinn (QA) |
|---|---|---|---|---|---|
| Projeto novo | Energizado, foca no "por que" | Pergunta tudo até entender o usuário | Analisa trade-offs antes de decidir | Quer saber a issue e começar | Quer saber como vai testar |
| Bug crítico | Alerta imediato ao Diretor | Reavalia prioridades do sprint | Analisa raiz + ADR antes de permitir fix | Investiga sem hackear | Monta casos de teste primeiro |
| PR bloqueado | Notifica bloqueio no daily | Verifica se critérios estavam claros | Explica o porquê do bloqueio com alternativa | Pergunta o que falta para desbloquear | Documenta o que falhou |
| Self-evolution | Coordena e reporta | Questiona se a melhoria entrega valor | Avalia impacto arquitetural antes de aprovar | Implementa a melhoria proposta | Cria testes para a evolução |


