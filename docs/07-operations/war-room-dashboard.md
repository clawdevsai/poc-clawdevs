# War Room — Dashboard de orquestração

Interface visual em que cada agente aparece como avatar ativo: estado do CEO (pesquisa em tempo real), Developer (branch em edição), CyberSec (alertas). Objetivo: tornar a automação **auditável e visual** para o Diretor. Ref: [01-visao-e-proposta.md](../01-core/01-visao-e-proposta.md).

---

## Conceito

- **9 agentes** em vista única: CEO, PO, DevOps, Architect, Developer, QA, CyberSec, UX, DBA.
- **Estado por agente:** `idle` | `working` | `alerta`.
- **Indicador de atividade:** texto curto (ex.: "CEO pesquisando", "Developer em branch feature/123", "CyberSec: 2 alertas").
- Atualização **periódica** (ex.: 30 s) ou **tempo real** (WebSocket/SSE) conforme implementação.

---

## Fontes de dados

| Fonte | Uso | Como obter |
|-------|-----|------------|
| **Redis** | Estado da fila (cmd:strategy, task:backlog), GPU Lock, working buffer | Conexão ao Redis do cluster (`REDIS_HOST`, streams XRANGE/XINFO). |
| **Pods (K8s)** | Status dos pods por agente (Running, tempo de atividade) | `kubectl get pods -n ai-agents -l app=openclaw` (gateway); pods por agente quando `replicas: 1` (developer, devops, etc.). |
| **Logs** | Atividade recente (última ação, erros) | `kubectl logs deployment/openclaw -n ai-agents --tail=50` ou agregador de logs. |
| **API de status (futuro)** | Endpoint HTTP no gateway ou orquestrador que exponha estado agregado | Ex.: `GET /status/agents` retornando JSON com estado por agente. |

Implementação mínima viável: ler Redis (streams, chaves de lock) e listar pods; opcionalmente um job ou sidecar que escreve estado em um stream ou ConfigMap para o dashboard consumir.

---

## Uso pelo Diretor

1. **Abrir o dashboard** (mock estático em `war-room-mock/` ou instância do Kanban/dashboard quando integrado).
2. **Ler o estado** dos 9 agentes de relance (idle/working/alerta).
3. **Clicar ou passar o mouse** em um agente para ver detalhe (atividade atual, último evento, alertas).
4. **Próximos passos (opcionais):** alertas sonoros ou notificação quando estado `alerta`; histórico de estados (timeline ou log) para auditoria.

---

## Próximos passos (roadmap)

- **Alertas:** notificar o Diretor (Telegram, digest) quando algum agente entrar em `alerta` (ex.: CyberSec com N vulnerabilidades, DevOps com falha de deploy).
- **Histórico:** persistir transições de estado (Redis ou log) e exibir timeline por agente ou por período.
- **Integração com Kanban:** reutilizar stack do `kanban-ui/` (Next.js) para servir o War Room na mesma aplicação, consumindo Redis e/ou API de status.

---

## Referências

- [01-visao-e-proposta.md](../01-core/01-visao-e-proposta.md) — War Room na visão do projeto.
- [120-war-room-dashboard.md](../08-technical-notes/issues/120-war-room-dashboard.md) — Issue e critérios de aceite.
- Redis Streams e estado: [03-arquitetura.md](../01-core/03-arquitetura.md), [005-redis-streams-estado-global.md](../08-technical-notes/issues/005-redis-streams-estado-global.md).
