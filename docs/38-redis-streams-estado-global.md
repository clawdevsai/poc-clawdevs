# Redis Streams e estado global (Event Bus)

Orquestração orientada a eventos com **estado centralizado em Redis Streams**. Agentes não se chamam diretamente; ficam em *idle* e são acordados por eventos. Estado da verdade (The Global State) em **chaves Redis**; transmissão de **ID de transação** em vez de JSONs grandes.

Ref: [03-arquitetura.md](03-arquitetura.md), [06-operacoes.md](06-operacoes.md), [issues/005-redis-streams-estado-global.md](issues/005-redis-streams-estado-global.md).

---

## 0. Mensageria como gatilho e integração Redis

Há **um único OpenClaw** com vários agentes; a **mensageria** é só **gatilho** para acordar quem deve falar ou trabalhar. Dois caminhos:

- **Slack/canal:** gatilho para **conversa** (ex.: tema para análise no #all-clawdevsai). A conversa compartilhada é o próprio canal/thread; um agente por vez é regra na SOUL.
- **Redis Streams:** gatilho para o **pipeline** (cmd:strategy → PO, task:backlog → Developer, etc.). O Gateway Redis Adapter recebe `POST /publish` (ou `/publish-to-cloud`) e faz XADD; o pod do agente consome com XREADGROUP — **um agente por vez** por stream (consumer groups). Contexto compartilhado pode usar **working buffer** (chaves com TTL). Detalhes: [agents-devs/interacao-agentes-mensageria.md](agents-devs/interacao-agentes-mensageria.md) (§ Integração via Redis).

---

## 1. Streams (canais de eventos)

| Stream | Produtor | Consumidor(es) | Uso |
|--------|----------|----------------|-----|
| **cmd:strategy** | CEO | PO | Diretriz estratégica; PO gera backlog. |
| **task:backlog** | PO | DevOps, Developer | Tarefas prontas para desenvolvimento. |
| **draft.2.issue** | PO | Architect (draft consumer) | Rascunho para validação técnica; Architect consome e aprova → task:backlog ou rejeita → draft_rejected. |
| **draft_rejected** | Architect | PO | Rascunho rejeitado; PO reescreve antes de publicar em task:backlog. |
| **code:ready** | Developer | Architect, QA, CyberSec, DBA (slot único) | Código pronto para revisão; job "Revisão pós-Dev" consome uma vez e executa a sequência. |

Criar streams e consumer groups (uma vez após o Redis estar no ar):

- **Script (host com port-forward):** `REDIS_HOST=127.0.0.1 REDIS_PORT=6379 ./scripts/redis-streams-init.sh`
- **Kubernetes (dentro do cluster):** `kubectl apply -f k8s/redis/job-init-streams.yaml` ou executar os comandos via `kubectl exec -n ai-agents deploy/redis -- redis-cli XGROUP CREATE ...`

---

## 2. Contrato de publicação (produtores — Fase 1, issue 018)

**Quem publica:** O gateway OpenClaw (após resposta do CEO ou do PO) ou um orquestrador deve publicar nos streams conforme o fluxo. Para testes manuais ou E2E, use o script [app/publish_event_redis.py](../app/publish_event_redis.py).

| Stream | Publicado por | Campos mínimos da mensagem (exemplo) | Observação |
|--------|----------------|--------------------------------------|------------|
| **cmd:strategy** | CEO (via gateway) | `directive` (texto da diretriz), `source=ceo`, `ts` (opcional) | PO consome e gera backlog / draft.2.issue. |
| **draft.2.issue** | PO (via gateway) | `issue_id`, `title`, `summary` (resumo para Architect), `ts` (opcional) | PO deve gravar antes em `project:v1:issue:{id}`; Architect valida viabilidade. |
| **task:backlog** | PO (via gateway) | `issue_id` (obrigatório), `priority` (opcional), `ts` (opcional) | Publicar só após ciclo de rascunho aprovado (ou dispensa). PO grava especificação em `project:v1:issue:{id}`. |
| **draft_rejected** | Architect | `issue_id`, `reason`, `ts` (opcional) | PO consome e reescreve; 3 consecutivos por épico → disjuntor (RAG health check). |
| **code:ready** | Developer | `issue_id`, `branch` (opcional), `ts` (opcional) | Slot Revisão pós-Dev consome (Architect→QA→CyberSec→DBA). |

Formato Redis: cada campo é um par `key value` no XADD; valores em UTF-8. O orquestrador pode usar `*` para auto-gerar ID da mensagem.

---

## 3. Convenção de chaves (estado global)

O **estado da verdade** fica em chaves Redis; o stream carrega apenas **ID de transação** (ex.: `issue_id`), não o payload completo.

| Padrão | Exemplo | Uso |
|--------|---------|-----|
| **project:v1:strategy_doc** | `project:v1:strategy_doc` | Documento estratégico do CEO (Memoria/SharedMemory). CEO grava via Gateway `POST /write-strategy`; PO e outros leem. Opcional: `project:v1:strategy:{project_id}` se multi-projeto. |
| **project:v1:issue:{id}** | `project:v1:issue:42` | Especificação da issue/tarefa (PO grava; Developer/Architect leem). |
| **project:v1:issue:{id}:state** | `project:v1:issue:42:state` | Estado da issue na máquina de estados: Backlog, Refinamento, Ready, InProgress, InReview, Approved, Merged, Deployed, Monitoring, Done. Ver [agents-devs/state-machine-issues.md](agents-devs/state-machine-issues.md). |
| **project:v1:issue:{id}:dev_lock** | — | Lock exclusivo por story (SETNX + TTL); apenas um Dev trabalha na issue por vez. |
| **project:v1:backlog** | — | Metadado ou lista de IDs no backlog (conforme orquestrador). |
| **project:v1:working_buffer:{suffix}** | `project:v1:working_buffer:session:abc` | Buffer de conversa/contexto compartilhado entre turnos; usar TTL (ex.: `redis_buffer_writer.write_working_buffer`). Ver [integracao-040-041-gateway-orquestrador.md](issues/integracao-040-041-gateway-orquestrador.md). |
| **gpu:lock** | — | GPU Lock (SETNX + TTL dinâmico); ver [scripts/gpu_lock.md](scripts/gpu_lock.md). |

O PO grava a especificação em `project:v1:issue:42`; o Developer recebe no stream apenas `{"issue_id": "42"}` e lê o conteúdo pela chave.

---

## 4. Fluxo de dados (resumo)

```
CEO → cmd:strategy → PO
PO → draft.2.issue → Architect (valida viabilidade técnica)
  → draft_rejected → PO (reescreve)
  → aprovado → task:backlog
task:backlog → DevOps / Developer
Developer → code:ready → [Revisão pós-Dev: Architect → QA → CyberSec → DBA]
```

- **Ciclo de rascunho:** PO publica `draft.2.issue`; Architect avalia; se impossível, retorna `draft_rejected`; PO reescreve; só então a tarefa vai para `task:backlog`/desenvolvimento.
- **Disjuntor:** mesma épico com 3 `draft_rejected` consecutivos → orquestrador congela a tarefa e aciona RAG health check; ver [06-operacoes.md](06-operacoes.md).

---

## 5. Semântica idempotente e ACK

- Consumidores tratam mensagens como **transações idempotentes**.
- **Não** enviar ACK até o trabalho estar **100% concluído em disco**.
- Em pausa brusca (ex.: 82°C), a mensagem permanece pendente na fila e é **reentregue** na retomada. Ver [06-operacoes.md](06-operacoes.md) e [03-arquitetura.md](03-arquitetura.md).

---

## 6. Checkpoint aos 80°C (pausa térmica)

DevOps **injeta evento de prioridade máxima** no Redis ordenando **commit do estado atual em branch efêmera de recuperação** (ex.: `recovery-failsafe-<timestamp>`) no repositório de trabalho, **antes** do Q-Suite térmico (82°C). Retomada: checkout limpo; Architect resolve conflitos na branch de recuperação quando aplicável. Ver [06-operacoes.md](06-operacoes.md) e [04-infraestrutura.md](04-infraestrutura.md).

---

## 7. Blackboard e resiliência

Se um pod cair, a tarefa permanece na fila; ao reiniciar, o agente retoma. Toda tarefa interrompida é **devolvida ao backlog do PO**; a issue não é descartada.

---

## 8. Referência no Kubernetes

- **ConfigMap:** [k8s/redis/streams-configmap.yaml](../k8s/redis/streams-configmap.yaml) — nomes dos streams e prefixos de chave (variáveis de ambiente para os deployments).
- **Job opcional:** [k8s/redis/job-init-streams.yaml](../k8s/redis/job-init-streams.yaml) — cria os streams e o consumer group `clawdevs` uma vez; aplicar após o Redis estar no ar.
