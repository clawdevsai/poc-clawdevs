# Consumer Groups e pipeline slot único de revisão (007 + 125)

**007** — Consumer groups no Redis Streams: um consumidor por vez para uso de GPU; fila de prioridade e ordem de serviço. **125** — Pipeline explícito: evento `code:ready` aciona **um único** job "Revisão pós-Dev", que adquire o GPU Lock uma vez e executa Architect → QA → CyberSec → DBA em sequência.

Ref: [estrategia-uso-hardware-gpu-cpu.md](estrategia-uso-hardware-gpu-cpu.md), [03-arquitetura.md](03-arquitetura.md), [38-redis-streams-estado-global.md](38-redis-streams-estado-global.md), [issues/007-consumer-groups-fila-prioridade.md](issues/007-consumer-groups-fila-prioridade.md), [issues/125-pipeline-explicito-slot-unico-revisao.md](issues/125-pipeline-explicito-slot-unico-revisao.md).

---

## 1. Consumer groups por stream

| Stream | Consumer group | Consumidor(es) | Uso de GPU |
|--------|----------------|----------------|------------|
| **cmd:strategy** | clawdevs | PO | Nuvem/CPU (não disputa GPU Lock) |
| **task:backlog** | clawdevs | DevOps, Developer | Developer disputa GPU Lock; DevOps não |
| **draft.2.issue** | clawdevs | Architect | Architect disputa GPU Lock |
| **draft_rejected** | clawdevs | PO | Não |
| **code:ready** | **revisao-pos-dev** | **Um único job "Revisão pós-Dev"** | Slot único: adquire lock uma vez, executa Architect→QA→CyberSec→DBA em sequência |

- **DevOps e UX:** consomem streams em CPU (node selectors); não competem pelo GPU Lock. Ver [04-infraestrutura.md](04-infraestrutura.md) (node selectors).
- **Fila de prioridade:** O grupo `revisao-pos-dev` no stream `code:ready` garante que apenas **um** consumidor (o slot) processe cada mensagem; ordem de entrega é a ordem do stream.

---

## 2. Slot único de revisão (125)

- **Evento:** `code:ready` (Developer publica quando o código está pronto para revisão).
- **Consumidor:** Um único job/pod **"Revisão pós-Dev"** que:
  1. Lê mensagens do stream `code:ready` com `XREADGROUP GROUP revisao-pos-dev`.
  2. **Adquire o GPU Lock** uma vez ([scripts/gpu_lock.py](../scripts/gpu_lock.py)).
  3. Carrega **um** modelo e executa **em sequência** (sem liberar o lock) os **6 papéis**: Architect → QA → CyberSec → DBA → UX → PO. Persiste resultado em `project:v1:issue:{id}:review:{role}` (approved/rejected).
  4. **Só quando todos os 6 aprovarem:** estado → Approved; Arquiteto executa **merge** (`gh pr merge`); estado → Merged. Se algum rejeitar: evento `review_rejected` e não faz merge.
  5. Libera o lock e envia **XACK** só após **100% concluído em disco** (semântica idempotente).
- **Hard timeout:** O Job tem `activeDeadlineSeconds: 300` (5 min) para cobrir a duração total do slot; evita lock órfão. Ver [04-infraestrutura.md](04-infraestrutura.md) e [k8s/development-team/gpu-lock-hard-timeout-example.yaml](../k8s/development-team/gpu-lock-hard-timeout-example.yaml).

---

## 3. Ordem de serviço (quem usa GPU)

- **Developer:** único consumidor designado de "tarefa pronta para desenvolvimento"; adquire GPU Lock, codifica, publica `code:ready`, libera.
- **Revisão pós-Dev:** único consumidor de `code:ready` (group `revisao-pos-dev`); adquire GPU Lock uma vez, executa as quatro etapas, libera.
- **DevOps, UX:** apenas CPU (node selectors); não entram na fila do GPU Lock.
- **Architect (draft):** consome `draft.2.issue`; quando acordado, disputa GPU Lock para avaliar viabilidade técnica.

---

## 4. Inicialização

- Criar o consumer group **revisao-pos-dev** no stream **code:ready** (uma vez): usar [scripts/redis-streams-init.sh](../scripts/redis-streams-init.sh) (que cria também `revisao-pos-dev` para `code:ready`) ou [k8s/redis/job-init-streams.yaml](../k8s/redis/job-init-streams.yaml).
- ConfigMap [k8s/redis/streams-configmap.yaml](../k8s/redis/streams-configmap.yaml) expõe `CONSUMER_GROUP_REVISAO` e `SLOT_REVISAO_TIMEOUT_SEC`.

---

## 5. Deployment "Revisão pós-Dev"

- Manifesto: [k8s/development-team/revisao-pos-dev/deployment.yaml](../k8s/development-team/revisao-pos-dev/deployment.yaml) (1 replica, consumidor long-running). ConfigMap de env: [k8s/development-team/revisao-pos-dev/configmap-env.yaml](../k8s/development-team/revisao-pos-dev/configmap-env.yaml). Para tempo máximo por execução do slot (ex.: 300 s), ver [04-infraestrutura.md](04-infraestrutura.md) e [k8s/development-team/gpu-lock-hard-timeout-example.yaml](../k8s/development-team/gpu-lock-hard-timeout-example.yaml).
- Script do slot: [scripts/slot_revisao_pos_dev.py](../scripts/slot_revisao_pos_dev.py) (lê `code:ready`, adquire lock, executa as quatro etapas em sequência, libera, ACK). ConfigMap dos scripts: `make revisao-slot-configmap` ou ver [k8s/development-team/revisao-pos-dev/README.md](../k8s/development-team/revisao-pos-dev/README.md).
- Integração com [scripts/gpu_lock.py](../scripts/gpu_lock.py) (006) e Redis Streams (005).
- **Fase 3 (032):** O Architect é chamado **via Ollama** quando `OLLAMA_BASE_URL` está definido (ex.: no cluster, ConfigMap `revisao-pos-dev-env`). O slot envia prompt de code review (perfil Architect), lê o contexto da issue em `project:v1:issue:{id}` e interpreta a resposta (APPROVED vs REJECTED/REJEITADO). Quando o modelo **rejeita**, o slot chama `record_architect_rejection(r, issue_id)` (strikes; 2º → trigger_architect_fallback; 5º → issue_back_to_po). Payload de `code:ready` deve incluir `issue_id`. Variáveis: `OLLAMA_BASE_URL`, `ARCHITECT_MODEL` (default `glm-5:cloud`), `ARCHITECT_TIMEOUT_SEC` (120), `ARCHITECT_ON_ERROR` (reject|approve em falha de rede). Para testes: `SIMULATE_ARCHITECT_REJECT=1` ou `simulate_reject=1` no payload. Ver [06-operacoes.md](06-operacoes.md) (Five strikes).
