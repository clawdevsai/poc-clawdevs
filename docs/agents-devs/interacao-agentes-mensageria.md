# Interação entre agentes — um OpenClaw, mensageria como gatilho

Referência para todos os agentes (CEO, PO, DevOps, Architect, Developer, QA, CyberSec, UX, DBA). Garante que a comunicação entre agentes não dependa de DM nem de dois agentes falando ao mesmo tempo.

---

## Princípio

- **Um único OpenClaw** com múltiplos agentes no K8s.
- A **mensageria** (Slack, Telegram, canal) é **apenas um gatilho** para acordar o agente.
- A **conversa** entre agentes acontece na **conversa compartilhada** (o canal ou thread onde a mensagem chegou).
- **Um agente por vez:** não pode haver dois agentes falando ao mesmo tempo; quando for sua vez, fale e encerre seu turno.

---

## Regras (obrigatórias para todos os agentes)

| Regra | Descrição |
|-------|-----------|
| **Mensageria = gatilho** | A mensagem no Slack/canal só serve para **acordar** o agente. Não use a mensageria para "conversar" com outro agente (ex.: não tente enviar DM ao PO ou ao CEO). |
| **Conversa compartilhada** | Quando você for acordado, vá para a **conversa compartilhada**: responda **no mesmo canal ou na mesma thread** onde a mensagem foi postada. É ali que a discussão ocorre. |
| **Um agente por vez** | Só um agente fala em cada momento. Após enviar sua resposta, seu turno está **encerrado**. Não envie segunda mensagem no mesmo turno; a próxima fala é do Diretor ou de outro agente. |
| **Nunca DM entre agentes** | Não tente enviar mensagem direta (DM) a outro agente. Você não tem "conversa privada" com PO, CEO ou outros — a interação é sempre no canal/thread compartilhado. |

---

## Fluxo resumido

1. **Gatilho:** Uma mensagem no canal (ex.: #all-clawdevsai) ou menção acorda o agente certo.
2. **Conversa compartilhada:** O agente acordado lê o contexto do canal/thread e responde **nesse mesmo canal/thread**.
3. **Turno único:** O agente dá **uma** resposta e encerra o turno; não complementa nem envia follow-up no mesmo turno.
4. **Próximo:** O Diretor ou outro agente (acionado por orquestração/ordem definida) fala em seguida na mesma conversa.

### CEO → Memoria + evento para PO

Após análise, o CEO deve: (1) gravar o documento estratégico na Memoria via Gateway `POST /write-strategy` (body do documento); (2) publicar evento para o PO via `POST /publish` com `stream: "cmd:strategy"` e dados mínimos (`directive`, `source=ceo`). O PO worker consome `cmd:strategy`, lê o contexto em `project:v1:strategy_doc`, cria Issues no GitHub e publica em `draft.2.issue`.

### Feature concluída (PO → CEO → Diretor)

Quando uma feature está Deployed, o DevOps worker emite evento `feature_complete` no stream `orchestrator:events`. O consumer Slack envia ao canal do Diretor a mensagem de entrega final (issue, repo, resumo, link). Ver [state-machine-issues.md](state-machine-issues.md).

---

## Integração via Redis

O **gatilho** que acorda cada agente pode vir de duas superfícies, no mesmo OpenClaw:

| Superfície | Papel | Onde a “conversa” acontece |
|------------|--------|-----------------------------|
| **Slack / canal** | Gatilho para **conversa** (ex.: tema para análise, teste rápido com PO). O gateway recebe a mensagem e roteia para o agente certo. | **Canal ou thread** no Slack — todos leem e respondem no mesmo lugar (conversa compartilhada). Um agente por vez = regra na SOUL. |
| **Redis Streams** | Gatilho para o **pipeline de trabalho** (estratégia → backlog → desenvolvimento → revisão). O gateway (ou o próprio agente) publica no stream; o worker do agente consome e executa. | **Stream + chaves de estado.** O “contexto compartilhado” pode ser o **working buffer** no Redis (TTL) e as chaves `project:v1:issue:{id}`. Um agente por vez = **uma mensagem consumida por vez** (consumer groups, slot único). |

### Fluxo Redis (resumo)

1. **Gatilho:** Algo (OpenClaw após resposta do CEO/PO, ou orquestrador) faz `POST /publish` (ou `/publish-to-cloud`) no **Gateway Redis Adapter** com `stream` + `data`. O adapter faz `XADD` no Redis.
2. **Acordar agente:** O pod do agente (PO, Developer, Architect, etc.) está em **XREADGROUP** no stream correspondente; quando chega uma mensagem, **um** consumer processa (um agente por vez por stream).
3. **Conversa compartilhada (contexto):** O agente lê o estado em chaves Redis (`project:v1:issue:{id}`, etc.). Se houver contexto de conversa a persistir entre turnos, usar **working buffer** com TTL (`redis_buffer_writer.write_working_buffer`). Ver [integracao-040-041-gateway-orquestrador.md](../issues/integracao-040-041-gateway-orquestrador.md).
4. **Turno único no pipeline:** Cada mensagem no stream é processada por **um** consumer; após XACK, a mensagem sai da fila. Não há dois agentes processando a mesma mensagem ao mesmo tempo (consumer group + slot único de revisão).

### Streams principais (referência)

| Stream | Quem publica | Quem consome | Uso |
|--------|----------------|--------------|-----|
| **cmd:strategy** | CEO (via gateway) | PO | Diretriz estratégica; PO gera backlog. |
| **task:backlog** | PO (via gateway) | DevOps, Developer | Tarefa pronta para desenvolvimento. |
| **draft.2.issue** | PO | Architect | Rascunho para validação técnica. |
| **draft_rejected** | Architect | PO | Rejeição; PO reescreve. |
| **code:ready** | Developer | Revisão pós-Dev (slot único) | Código pronto para Architect → QA → CyberSec → DBA. |

Config e criação dos streams: [38-redis-streams-estado-global.md](../38-redis-streams-estado-global.md), [k8s/redis/streams-configmap.yaml](../../k8s/redis/streams-configmap.yaml), `./scripts/redis-streams-init.sh`.

---

## Referências

- [38-redis-streams-estado-global.md](../38-redis-streams-estado-global.md) — Streams, chaves de estado, consumer groups.
- [integracao-040-041-gateway-orquestrador.md](../issues/integracao-040-041-gateway-orquestrador.md) — Gateway adapter (`/publish`, `/publish-to-cloud`), working buffer TTL.
- [43-fluxo-slack-all-clawdevsai-tema-analise.md](../43-fluxo-slack-all-clawdevsai-tema-analise.md) — Ordem das opiniões (DevOps → Architect → … → CEO) no tema para análise.
- [openclaw-config-ref.md](../openclaw-config-ref.md) — Config OpenClaw (tudo no K8s); canal #all-clawdevsai e conversa no canal/thread.
