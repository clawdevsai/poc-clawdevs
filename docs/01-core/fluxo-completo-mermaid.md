# Fluxo completo do enxame (Mermaid)

Este documento consolida os fluxos do time de desenvolvimento autônomo em diagramas **Mermaid**, para visualização da arquitetura, da sequência de eventos e das válvulas de proteção e governança. Referência: [03-arquitetura.md](03-arquitetura.md), [06-operacoes.md](06-operacoes.md), [08-exemplo-de-fluxo.md](08-exemplo-de-fluxo.md).

---

## 1. Visão de componentes e fluxo de dados

```mermaid
flowchart LR
  subgraph humano [Humano]
    Diretor[Diretor]
  end
  subgraph cloud [Nuvem]
    CEO[Agente CEO]
    PO[Agente PO]
  end
  subgraph borda [Borda]
    Trunca["Truncamento por tokens"]
  end
  subgraph redis [Redis]
    State[Estado Global]
    Stream[Streams]
  end
  subgraph local [Minikube Local]
    DevOps[DevOps]
    Dev[Developer]
    Arch[Architect]
    QA[QA]
    Sec[CyberSec]
    UX[UX]
    DBA[DBA]
  end
  Diretor -->|Telegram/OpenClaw| CEO
  CEO -->|cmd:strategy| Trunca
  Trunca --> Stream
  Stream --> PO
  PO -->|task:backlog / draft| State
  PO --> Stream
  Stream --> DevOps
  DevOps -->|autoriza GPU| Stream
  Stream --> Dev
  Dev -->|code:ready| Trunca
  Trunca --> Stream
  Stream --> Arch
  Stream --> QA
  Stream --> Sec
  Stream --> UX
  Stream --> DBA
  Dev --> State
  Arch --> State
  DBA --> State
```

---

## 2. Sequência do fluxo de valor (estratégia → entrega)

```mermaid
sequenceDiagram
  participant D as Diretor
  participant CEO as Agente CEO
  participant Redis as Redis Streams
  participant PO as Agente PO
  participant Arch as Architect
  participant DevOps as DevOps
  participant Dev as Developer
  participant QA as QA
  participant Sec as CyberSec
  participant UX as UX
  participant DBA as DBA

  D->>CEO: Pedido (ex.: "Implementar 2FA")
  CEO->>Redis: cmd:strategy
  Redis->>PO: consome
  PO->>Redis: draft.2.issue
  Redis->>Arch: consome draft
  alt draft_rejected
    Arch->>Redis: draft_rejected
    Redis->>PO: PO reescreve tarefa
  else aprovado
    Arch->>Redis: aprovado
    PO->>Redis: task:backlog
    Redis->>DevOps: tarefa nova
    DevOps->>DevOps: verifica GPU
    DevOps->>Redis: autoriza Developer
    Redis->>Dev: consome tarefa
    Dev->>Dev: adquire GPU Lock
    Dev->>Dev: implementa (Ollama)
    Dev->>Dev: libera GPU Lock
    Dev->>Redis: code:ready
    par Revisores
      Redis->>Arch: consome (GPU Lock)
      Redis->>QA: consome (GPU Lock)
      Redis->>Sec: consome (GPU Lock)
      Redis->>UX: consome (GPU Lock)
      Redis->>DBA: consome (GPU Lock)
    end
    Arch->>Redis: aprova ou rejeita PR
    QA->>Redis: testes pass/fail
    Sec->>Redis: auditoria segurança
    UX->>Redis: revisão frontend
    DBA->>Redis: revisão dados/performance
    Redis->>CEO: relatório final
    CEO->>D: notifica (ex.: "2FA pronto")
  end
```

---

## 3. Ciclo de rascunho (PO → Architect) e fila de desenvolvimento

```mermaid
flowchart TB
  subgraph ciclo [Ciclo de rascunho]
    PO_escreve[PO escreve draft.2.issue]
    Arch_consome[Architect consome]
    Arch_decide{Viável?}
    Rejeita[draft_rejected]
    Aprovado[task:backlog]
    PO_escreve --> Arch_consome
    Arch_consome --> Arch_decide
    Arch_decide -->|não| Rejeita
    Rejeita --> PO_reescreve[PO reescreve]
    PO_reescreve --> PO_escreve
    Arch_decide -->|sim| Aprovado
  end
  Aprovado --> Fila[Fila GPU / Developer]
  Fila --> Dev_pega[Developer pega tarefa]
```

---

## 4. Validação pré-GPU (CPU), batching e GPU Lock

Antes de disputar o lock, o artefato passa por **validação em CPU** (sintaxe, lint, SOLID via SLM). O Architect pode realizar **revisão em lote (batching)** de micro-PRs com uma janela de contexto única. Em seguida, a fila e o GPU Lock controlam o acesso à GPU.

```mermaid
flowchart LR
  subgraph preGPU [Pré-GPU]
    CPUVal["Validação CPU\nsintaxe, lint, SOLID"]
    Batch["Revisão em lote\n(batching opcional)"]
  end
  subgraph agentes [Agentes que usam GPU]
    Dev[Developer]
    Arch[Architect]
    QA[QA]
    Sec[CyberSec]
    UX[UX]
    DBA[DBA]
  end
  subgraph lock [Controle]
    Fila[Fila Consumer Group]
    RedisLock["Redis SETNX\nTTL dinâmico"]
    K8sTimeout["K8s hard timeout\n(ex.: 120 s)"]
  end
  subgraph ollama [Inferência]
    Ollama[Ollama / GPU]
  end
  CPUVal --> Batch
  Batch --> Fila
  Fila --> RedisLock
  RedisLock --> Ollama
  Dev --> Fila
  Arch --> Fila
  QA --> Fila
  Sec --> Fila
  UX --> Fila
  DBA --> Fila
  Ollama --> K8sTimeout
  K8sTimeout -->|"pod morto"| Fila
```

---

## 5. Truncamento na borda (disjuntor não-LLM)

```mermaid
flowchart LR
  Payload[Payload bruto]
  Script["Script borda\n(conta tokens)"]
  Limite{"> limite?\n(ex.: 4000)"}
  Trunca["Trunca bruto\n(cabeçalho + causa raiz)"]
  Envia[Enfileira no Stream]
  Payload --> Script
  Script --> Limite
  Limite -->|sim| Trunca
  Limite -->|não| Envia
  Trunca --> Envia
  Envia --> Agentes[Agentes consomem]
```

---

## 6. Governança: Five Strikes (fallback contextual) e aprovação por omissão (apenas cosmético)

```mermaid
flowchart TB
  subgraph fiveStrikes [Five Strikes e fallback]
    Conflito[Developer x Architect no mesmo PR]
    Conta[Orquestrador conta iterações]
    S2["2º strike?"]
    Compromisso["Prompt compromisso: Architect gera código aprovável"]
    S5["5º strike?"]
    Escala["Empacota contexto, roteia arbitragem nuvem"]
    Abandon["PR bloqueado, só se escalação falhar"]
    Proxima[Developer próxima tarefa]
    Conflito --> Conta
    Conta --> S2
    S2 -->|sim| Compromisso
    Compromisso --> S5
    S5 -->|sim| Escala
    Escala --> Abandon
    Abandon --> Proxima
    S2 -->|não| Conflito
    S5 -->|não| Conflito
  end

  subgraph aprovOmissao [Aprovação por omissão apenas cosmético]
    CEO_alerta["CEO envia alerta"]
    Tipo["Tipo do diff determinístico"]
    Cosmetic["Somente CSS, UI isolada ou markdown"]
    Logic["Código lógico ou backend"]
    Timer["Timer ex.: 6 h"]
    Diretor_responde["Diretor responde?"]
    CEO_aprova["CEO aprova por omissão"]
    MEMORY["Registra em MEMORY.md"]
    FilaBloq["Issue volta ao backlog do PO; PO + Architect analisam histórico e solução; tarefa retorna ao desenvolvimento"]
    CEO_alerta --> Tipo
    Tipo --> Cosmetic
    Tipo --> Logic
    Cosmetic --> Timer
    Timer --> Diretor_responde
    Diretor_responde -->|não| CEO_aprova
    CEO_aprova --> MEMORY
    Diretor_responde -->|sim| FimNorm[Fluxo normal]
    Logic --> FilaBloq
  end
```

---

## 7. Execução segura do Developer (sandbox air-gap)

```mermaid
flowchart TB
  subgraph dev [Agente Developer]
    Pedido[Pedido npm/pip ou código 3º]
  end
  subgraph orquestrador [Orquestrador]
    CriaSandbox[Cria container sandbox\nair-gapped]
    Destroi[Destrói container]
  end
  subgraph sandbox [Sandbox efêmero]
    Proxy["Proxy reverso\nwhitelist hashes"]
    Exec[Executa comando]
  end
  Disco[Disco apagado]
  Pedido --> CriaSandbox
  CriaSandbox --> Proxy
  Proxy --> Exec
  Exec --> Destroi
  Destroi --> Disco
```

---

## 8. Fluxo completo resumido (uma página)

```mermaid
flowchart TB
  Diretor[Diretor] -->|1| CEO[CEO]
  CEO -->|2 cmd:strategy| Borda[Borda: truncamento]
  Borda --> Stream[Redis Streams]
  Stream -->|3| PO[PO]
  PO -->|4 draft| ArchDraft[Architect]
  ArchDraft -->|5| Backlog[task:backlog]
  Backlog -->|6| DevOps[DevOps autoriza GPU]
  DevOps --> Dev[Developer]
  Dev -->|7 GPU Lock| Ollama[Ollama]
  Dev -->|8 code:ready| Stream
  Stream -->|9| Rev[Architect, QA, CyberSec, UX, DBA]
  Rev -->|10| CEO
  CEO -->|11| Diretor

  subgraph escape [Válvulas de escape]
    FiveStrikes["Five strikes: 2º compromisso, 5º arbitragem nuvem; abandono só se falhar"]
    AprovOmissao["Aprovação por omissão cosmética 6h MEMORY.md"]
  end
```

---

## Referências

- [01-visao-e-proposta.md](01-visao-e-proposta.md) — Autonomia nível 4, matriz de escalonamento
- [02-agentes.md](02-agentes.md) — Definição dos nove agentes
- [03-arquitetura.md](03-arquitetura.md) — Redis Streams, estado global, estágio de borda
- [04-infraestrutura.md](04-infraestrutura.md) — GPU Lock, hard timeout, truncamento na borda
- [05-seguranca-e-etica.md](05-seguranca-e-etica.md) — Sandbox air-gap, proxy, análise estática
- [06-operacoes.md](06-operacoes.md) — Five strikes, aprovação por omissão cosmética, prevenção
- [07-configuracao-e-prompts.md](07-configuracao-e-prompts.md) — Pipeline de truncamento
- [08-exemplo-de-fluxo.md](08-exemplo-de-fluxo.md) — Exemplo 2FA
