# 06 — Políticas Rígidas de Engenharia
> **Objetivo:** Estabelecer a "constituição" do projeto. Nenhum agente, prazo ou pressão de negócio sobrepõe essas primícias.
> **Público-alvo:** Devs, Scrum Master
> **Ação Esperada:** Devs e SM devem usar isso como checklist no *Definition of Ready* e *Definition of Done*. Arquitetos usarão para aprovar PRs.

**v2.0 | Atualizado em: 06 de março de 2026**

---

## Primícias — Ordem de prioridade absoluta

```mermaid
graph TD
    P1["🔒 PRIORIDADE 1\nCIBERSEGURANÇA\n\nZero Trust — nenhum componente\nconfia em outro por padrão\n\nDefesa em profundidade:\nmúltiplas camadas de controle\n\nOWASP Top 10 em todo código\nque toca dados de usuário\n\nNenhum atalho por prazo ou custo"]

    P2["💰 PRIORIDADE 2\nCUSTO ZERO NO NÚCLEO\n\nO núcleo roda com custo de cloud\nzero — energia excluída\n\nToda dependência cloud: opcional\ne com teto de gasto definido\n\nPreferência absoluta por\nalternativas open source self-hosted"]

    P3["⚡ PRIORIDADE 3\nPERFORMANCE SUSTENTÁVEL\n\nTime produtivo sem colapsar recursos\n\nCPU whitelist por agente\nKill switch por temperatura GPU\n\nAnálise estática obrigatória\nantes de qualquer merge"]

    RULE["⚠️ REGRA FUNDAMENTAL\nEsta ordem nunca é invertida.\nSegurança precede custo.\nCusto precede performance.\nSempre."]

    P1 -->|"só então avaliamos"| P2
    P2 -->|"só então avaliamos"| P3
    RULE -.-> P1

    style P1 fill:#DC262622,stroke:#DC2626,color:#DC2626
    style P2 fill:#D9770622,stroke:#D97706,color:#D97706
    style P3 fill:#05966922,stroke:#059669,color:#059669
    style RULE fill:#7C3AED22,stroke:#7C3AED,color:#7C3AED
```

---

## Modelo Zero Trust entre agentes

```mermaid
graph TD
    subgraph TRUST["Níveis de confiança (Zero Trust)"]
        N0["🔑 Nível 0 — Diretor (humano)\nAcesso total via OpenClaw\nSoberano absoluto do cluster"]
        N1["🎯 Nível 1 — CEO\nLeitura geral · Broadcast · Relatórios\nNão escreve código, não mergeia PRs"]
        N2A["📋 Nível 2 — PO\nLeitura/escrita em issues e milestones"]
        N2B["🏗️ Nível 2 — Architect\nLeitura de código · ADRs · Aprova/bloqueia PRs"]
        N3A["💻 Nível 3 — Developer\nEscrita de código · Testes · Abre PRs"]
        N3B["🧪 Nível 3 — QA\nValidação · Aprova PRs · Cria bugs"]
        N4["🗄️ Nível 4 — Serviços de infra\nAcesso restrito ao próprio namespace"]
    end

    N0 -->|"controla"| N1
    N1 -->|"coordena"| N2A & N2B
    N2A & N2B -->|"dirige"| N3A & N3B
    N3A & N3B -->|"acessa"| N4

    RULES["Regras imutáveis:\n❌ Agente N não eleva permissões de N+1\n❌ Nenhum agente acessa internet diretamente\n✅ Toda escrita gera log imutável no PostgreSQL\n✅ kubectl é read-only para todos (exceto DevOps, fase 2)"]

    style N0 fill:#4A90D9,stroke:#2563EB,color:#fff
    style N1 fill:#7C3AED,stroke:#5B21B6,color:#fff
    style N2A fill:#2563EB,stroke:#1D4ED8,color:#fff
    style N2B fill:#2563EB,stroke:#1D4ED8,color:#fff
    style N3A fill:#059669,stroke:#047857,color:#fff
    style N3B fill:#059669,stroke:#047857,color:#fff
    style N4 fill:#6B7280,stroke:#4B5563,color:#fff
```

---

## Políticas operacionais

### Ciclo de vida de uma feature

```mermaid
flowchart LR
    ISSUE["📋 Issue criada\npelo PO\ncom DoD e\ncritérios de aceite"]
    BRANCH["🌿 Branch criada\npelo Developer\nfeature/<id>-nome"]
    IMPL["💻 Implementação\n+ testes unitários\n+ docs inline"]
    PR["🔃 Pull Request\ndescrição + como testar\n+ issue vinculada"]
    QA_REV["🧪 Revisão QA\ntestes passam?\ncritérios cobertos?\nregressão OK?"]
    ARCH_REV["🏗️ Revisão Architect\nsegurança?\npadrões?\nADR necessário?"]
    MERGE["✅ Merge\ncommit assinado\ntag de versão"]
    CLOSE["📌 Issue fechada\nPO valida entrega"]

    ISSUE --> BRANCH --> IMPL --> PR
    PR --> QA_REV
    QA_REV -->|"❌ falha"| IMPL
    QA_REV -->|"✅ aprovado"| ARCH_REV
    ARCH_REV -->|"❌ bloqueia"| IMPL
    ARCH_REV -->|"✅ aprovado"| MERGE
    MERGE --> CLOSE

    style MERGE fill:#05966922,stroke:#059669
    style QA_REV fill:#2563EB22,stroke:#2563EB
    style ARCH_REV fill:#D9770622,stroke:#D97706
```

---

### Política de commits

```
✅ Todo commit deve ser assinado         git commit -s
✅ Formato:                              tipo(escopo): descrição curta
✅ Tipos válidos:                        feat · fix · refactor · test · docs · chore · sec
❌ Nenhum commit direto em main/develop  somente via PR
❌ Sem secrets, tokens ou credenciais   use K8s Secrets ou env vars
```

**Exemplos de commit válidos:**
```
feat(auth): add JWT refresh token endpoint
fix(api): handle null response from Ollama timeout
sec(deps): update requests to 2.32.3 (CVE-2024-XXX)
test(login): add edge cases for invalid tokens
```

---

### Política de Pull Requests

```mermaid
graph LR
    REQ["Requisitos obrigatórios de um PR\n\n☑ Descrição da mudança\n☑ Como testar (passo a passo)\n☑ Issue vinculada (#ID)\n☑ Testes passando localmente\n☑ Sem secrets no código\n☑ Sem debug prints / código comentado"]

    REVIEW["Revisões obrigatórias\n\n🧪 QA — validação funcional\n🏗️ Architect — validação arquitetural\n\nMerge somente após AMBAS aprovações"]

    BLOCK["Causas de bloqueio\n\n❌ Falha em teste crítico\n❌ Vulnerabilidade de segurança\n❌ Violação de princípios\n❌ Sem issue correspondente\n❌ Dependência com CVE conhecido"]

    REQ --> REVIEW --> BLOCK
```

---

### Política de secrets

| Regra | Detalhe |
|---|---|
| **Zero secrets em código** | Sempre via K8s Secrets ou env vars |
| **Rotação automática** | Tokens rotacionam a cada 30 dias |
| **Auditoria** | Falco monitora acesso a secrets em tempo real |
| **Scan obrigatório** | git-secrets ou truffleHog antes de todo merge |
| **Sem secrets em logs** | Mascaramento obrigatório em todos os outputs |

---

### Política de dependências

```mermaid
flowchart TD
    ADD["Desenvolver quer adicionar\nnova dependência"]
    CVE{"CVE ou vulnerabilidade\nconhecida?"}
    ALT_LOCAL{"Existe alternativa\nopen source self-hosted?"}
    LOCK{"Lock de versão\ndefinido?"}
    APPROVE["✅ Dependência aprovada\nregistrar em ADR se relevante"]
    BLOCK_DEP["❌ Bloqueado\nbuscar alternativa segura"]
    PREFER["⚠️ Preferir alternativa local\ndocumentar se usar cloud"]

    ADD --> CVE
    CVE -->|"Sim"| BLOCK_DEP
    CVE -->|"Não"| ALT_LOCAL
    ALT_LOCAL -->|"Sim"| PREFER
    ALT_LOCAL -->|"Não — cloud necessário"| LOCK
    PREFER --> LOCK
    LOCK -->|"Não"| BLOCK_DEP
    LOCK -->|"Sim"| APPROVE

    style APPROVE fill:#05966922,stroke:#059669
    style BLOCK_DEP fill:#DC262622,stroke:#DC2626
    style PREFER fill:#D9770622,stroke:#D97706
```

---

## Política de self_evolution

```mermaid
stateDiagram-v2
    [*] --> Normal

    Normal --> EvolutionRequested : Diretor envia #evolui via OpenClaw
    EvolutionRequested --> AgentsPropose : CEO ativa modo self_evolution

    AgentsPropose --> PRCreated : Agentes propõem melhorias via PR\n(SOUL, skills, configs, regras)
    PRCreated --> HumanReview : PR notificado ao Diretor no Telegram

    HumanReview --> Merged : Diretor aprova PR
    HumanReview --> Rejected : Diretor rejeita PR
    HumanReview --> AgentsPropose : Diretor pede revisão

    Merged --> Normal : SOUL/config atualizado no cluster
    Rejected --> Normal : PR fechado, log registrado

    note right of AgentsPropose: Nenhuma mudança aplicada\ndiretamente — sempre via PR
    note right of HumanReview: Aprovação humana\nobrigatória para todo merge
    note right of Merged: Log imutável de toda\nmudança no PostgreSQL
```

**Regras imutáveis do self_evolution:**
- Modo ativado apenas pelo Diretor — nunca pelo próprio time
- Toda proposta vira PR — nunca aplicada diretamente
- Aprovação humana obrigatória antes de qualquer merge
- Log completo de mudanças propostas, aprovadas e rejeitadas
- Rollback imediato disponível para qualquer mudança de SOUL

---

## Escalação e resolução de conflitos

```mermaid
flowchart TD
    CONFLICT["Conflito detectado"]

    CONFLICT --> TYPE{"Tipo de conflito"}

    TYPE -->|"técnico\n(arquitetura, stack, código)"| ARCH_ARB["🏗️ Architect arbitra\n1 ciclo de discussão"]
    TYPE -->|"produto\n(prioridade, escopo, features)"| PO_ARB["📋 PO arbitra\n1 ciclo de discussão"]
    TYPE -->|"comportamento anômalo\nde agente"| ANOMALY["🚨 CEO notifica Diretor\nimediatamente"]
    TYPE -->|"violação de\npolítica de segurança"| SEC_BLOCK["🔒 Operação bloqueada\nautomaticamente"]

    ARCH_ARB --> RESOLVED_TECH{"Resolvido?"}
    PO_ARB --> RESOLVED_PROD{"Resolvido?"}

    RESOLVED_TECH -->|"Sim"| OK["✅ Continua"]
    RESOLVED_TECH -->|"Não"| CEO_ESC["🎯 CEO consolida\n2 opções claras\nescala ao Diretor"]

    RESOLVED_PROD -->|"Sim"| OK
    RESOLVED_PROD -->|"Não"| CEO_ESC

    ANOMALY --> ISOLATE["Agente entra em\nmodo de isolamento\naté revisão humana"]
    SEC_BLOCK --> ALERT["Alerta Telegram\n+ log com evidência\n+ aguarda instrução do Diretor"]

    CEO_ESC --> DIR_DECIDE["👤 Diretor decide"]
    DIR_DECIDE --> OK

    style OK fill:#05966922,stroke:#059669
    style SEC_BLOCK fill:#DC262622,stroke:#DC2626
    style ANOMALY fill:#DC262622,stroke:#DC2626
    style ALERT fill:#DC262622,stroke:#DC2626
```

---

