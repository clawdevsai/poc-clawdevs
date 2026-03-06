# 04 — Roadmap de Entregas (MVP v1.0)
> **Objetivo:** Estabelecer a linha do tempo de releases e sprints programadas.
> **Público-alvo:** PO, Scrum Master
> **Ação Esperada:** O PO e o SM devem acompanhar os marcos deste cronograma para priorizar as histórias de usuário e garantir as entregas no prazo acordado.

**v2.0 | Atualizado em: 06 de março de 2026**

---

## Visão do plano (90 dias)

```mermaid
gantt
    title Plano de Ação ClawDevs AI — Março a Maio 2026
    dateFormat  YYYY-MM-DD
    section Fundação (Mês 1)
        Spec hardware e ambiente       :done, hw,    2026-03-06, 3d
        Cluster K8s base               :active, k8s,  2026-03-09, 5d
        Ollama + modelos base           :ollama, 2026-03-14, 4d
        SOUL Developer + PO            :soul1,  2026-03-18, 5d
        OpenClaw + Telegram            :oc,     2026-03-23, 4d
        Primeiro PR gerado por agente  :pr1,    2026-03-27, 4d

    section Expansão (Mês 2)
        SOUL Architect + QA + CEO      :soul2,  2026-04-06, 6d
        Orquestrador com roteamento    :orch,   2026-04-12, 7d
        A2A Redis Streams              :a2a,    2026-04-19, 5d
        Memória vetorial Qdrant        :mem,    2026-04-24, 4d
        Projeto piloto end-to-end      :pilot,  2026-04-28, 3d

    section Polimento (Mês 3)
        Self-evolution habilitado      :evol,   2026-05-04, 5d
        Segurança e auditoria          :sec,    2026-05-09, 5d
        Documentação pública           :docs,   2026-05-14, 7d
        Repositório GitHub público     :gh,     2026-05-21, 4d
        v1.0 tag e release             :rel,    2026-05-25, 3d
```

---

## Fase 1 — Fundação (Março 2026)

```mermaid
flowchart TD
    START(["🚀 Início\n06/03/2026"])

    S1["📋 S1 — Semana 1\nSpec de hardware\nInstalação Minikube\nNamespaces criados"]
    S2["📋 S2 — Semana 2\nOllama rodando como pod\nModelos qwen2.5-coder:14b e qwen2.5:14b\nHealthcheck validado"]
    S3["📋 S3 — Semana 3\nSOUL do Developer escrito e carregado\nSOUL do PO escrito e carregado\nOpenClaw conectado ao Telegram"]
    S4["📋 S4 — Semana 4\nPrimeiro projeto piloto iniciado pelo Diretor\nPrimeiro issue criado pelo PO\nPrimeiro PR aberto pelo Developer\n✅ Marco: PR #1 gerado por agente"]

    CHECK1{"Hardware\nok?"}
    CHECK2{"Ollama\nrespondendo?"}
    CHECK3{"Agentes\nrecebendo tasks?"}
    CHECK4{"PR criado\ncorretamente?"}

    START --> S1 --> CHECK1
    CHECK1 -->|"Não"| LITE["Usar perfil LITE\n4.5GB modelo menor"]
    CHECK1 -->|"Sim"| S2
    LITE --> S2
    S2 --> CHECK2
    CHECK2 -->|"Não"| FIX_OL["Debug Ollama\nchecar VRAM/RAM"]
    CHECK2 -->|"Sim"| S3
    FIX_OL --> S2
    S3 --> CHECK3
    CHECK3 -->|"Não"| FIX_OC["Debug OpenClaw\nverificar token/chat_id"]
    CHECK3 -->|"Sim"| S4
    FIX_OC --> S3
    S4 --> CHECK4
    CHECK4 -->|"Sim"| M1["✅ Marco M1\nFundação concluída"]

    style M1 fill:#05966922,stroke:#059669
    style LITE fill:#D9770622,stroke:#D97706
```

**Entregas concretas da Fase 1:**
- `k8s/` — manifests para todos os namespaces e pods base
- `souls/developer.yaml` e `souls/po.yaml` — SOULs v1
- `config/openclaw.json` — configurado e testado com Telegram
- PR #1 no Gitea local — gerado pelo Developer a partir de issue do PO
- Documento de spec de hardware validada

---

## Fase 2 — Expansão do Time (Abril 2026)

```mermaid
graph TD
    subgraph APRIL["Abril 2026 — Semanas 5 a 8"]
        S5["S5 — SOULs: Architect + QA + CEO\nIdentidades, constraints, modelos configurados\nTeste individual de cada agente"]
        S6["S6 — Orquestrador com roteamento inteligente\nPO issue → Dev implementa → QA testa → Arch revisa\nFluxo completo de PR"]
        S7["S7 — A2A via Redis Streams\nAgentes trocam mensagens diretas\nContexto compartilhado via Qdrant\nMemória de projeto persistente"]
        S8["S8 — Projeto piloto complexo\nApp de exemplo desenvolvido end-to-end\nCEO gerando daily report\nSelf_evolution ativado pela 1ª vez"]
    end

    M1["✅ M1: Fundação\n(Março)"] --> S5 --> S6 --> S7 --> S8 --> M2

    M2["✅ Marco M2\n5 agentes colaborando\nProjeto real entregue\nSelf_evolution em teste"]

    style M2 fill:#05966922,stroke:#059669
```

**Critério de saída da Fase 2:**
O CEO consegue enviar ao Diretor um daily report com: issues abertas, PRs em revisão, bloqueios identificados e próximos passos — sem intervenção humana.

---

## Fase 3 — Polimento e Abertura Pública (Maio 2026)

```mermaid
graph LR
    subgraph MAY["Maio 2026"]
        T1["Self-evolution\nvalidado\n3+ melhorias via PR"]
        T2["Auditoria de segurança\nOWASP · Zero Trust\nFalco rules revisadas"]
        T3["Benchmark de performance\ntokens/hora · latência\ncusto real documentado"]
        T4["Guia de instalação\ntestado por terceiro\n< 4h do zero ao time"]
        T5["README público\nLicença MIT\nContributing guide"]
        T6["🚀 v1.0 Release\nGitHub público\nPrimeiras estrelas"]
    end

    M2["✅ M2\n(Abril)"] --> T1 --> T2 --> T3 --> T4 --> T5 --> T6

    style T6 fill:#7C3AED,stroke:#5B21B6,color:#fff
```

---

## Dependências críticas

```mermaid
graph LR
    HW["Hardware validado\nMáquina de referência"]
    K8S["Cluster K8s\nfuncionando"]
    OLLAMA["Ollama + modelos\nrespondendo"]
    OC["OpenClaw\nconectado ao Telegram"]
    SOULS["SOULs dos agentes\nescritos e testados"]
    ORCH["Orquestrador\nroteando corretamente"]
    A2A["A2A Redis Streams\ncomunicação entre agentes"]
    GITEA["Gitea\nissues + PRs"]
    MEM["Qdrant\nmemória vetorial"]

    HW --> K8S --> OLLAMA & GITEA & OC
    OLLAMA & OC --> SOULS
    SOULS & ORCH --> A2A
    A2A --> MEM
    ORCH --> GITEA

    style HW fill:#DC262622,stroke:#DC2626
    style A2A fill:#D9770622,stroke:#D97706
    style MEM fill:#05966922,stroke:#059669
```

---

## Definição de pronto por entregável

| Entregável | Critério de pronto |
|---|---|
| Cluster K8s base | `kubectl get pods -A` mostra todos os pods Running |
| Ollama funcionando | `curl http://ollama-service:11434/api/tags` retorna lista de modelos |
| SOUL do Developer | Agente cria um arquivo Python válido a partir de uma instrução simples |
| OpenClaw + Telegram | Mensagem enviada pelo Diretor gera resposta do agente em < 30s |
| Fluxo PO → Dev → QA | Issue criada pelo PO vira PR revisado pelo QA sem intervenção humana |
| Self-evolution | Agente propõe PR de melhoria, Diretor aprova, configMap atualizado |
| Guia de instalação | Terceiro segue o guia e sobe o ambiente em < 4 horas |

---

## Recursos necessários por fase

```mermaid
pie title Distribuição de esforço estimado (horas)
    "Infraestrutura K8s e manifests" : 40
    "Desenvolvimento SOULs (5 agentes)" : 30
    "Orquestrador e A2A" : 50
    "OpenClaw + integração" : 20
    "Segurança e auditoria" : 25
    "Documentação pública" : 30
    "Testes e benchmarks" : 25
```

**Total estimado: ~220 horas de desenvolvimento** (~3 meses, 1 desenvolvedor dedicado)

---


