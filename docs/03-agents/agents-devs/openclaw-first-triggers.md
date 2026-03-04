# Triggers OpenClaw-first (ClawDevs)

Este documento descreve a arquitetura **openclaw-first**: os scripts de pipeline **não** rodam LLM nem agent loop; apenas consomem Redis e **enviam mensagens aos agentes no OpenClaw Gateway**. Toda a lógica (quebrar estratégia em issues, revisar draft, implementar tarefa, revisão em 6 papéis, deploy, auditoria) roda **dentro do OpenClaw**, com os agentes usando ferramentas (adapter Redis, gh, issue_state).

Ref: [.cursor/rules/openclaw-first.mdc](../../.cursor/rules/openclaw-first.mdc), [docs.openclaw.ai](https://docs.openclaw.ai/llms.txt).

## Visão geral

| Stream / evento   | Trigger (script)           | Ação do trigger                         | Agente OpenClaw | O que o agente faz (via ferramentas) |
|-------------------|----------------------------|----------------------------------------|-----------------|--------------------------------------|
| cmd:strategy      | po_worker.py               | XREAD → monta mensagem → sessions.send → XACK | PO              | Lê Memoria, cria issues no GitHub, grava project:v1:issue:{id}, publica draft.2.issue |
| draft.2.issue     | architect_draft_consumer.py| XREAD → mensagem → sessions.send → XACK | Architect       | Aprova → Ready + task:backlog; rejeita → draft_rejected + Refinamento |
| task:backlog      | developer_worker.py        | Lock, InProgress, sessions.send → XACK | Developer       | Implementa; publica code:ready, libera dev_lock |
| code:ready        | slot_revisao_pos_dev.py    | Para cada papel: sessions.send (wait) → persiste review; se todos aprovam → merge → event:devops | Architect, QA, CyberSec, DBA, UX, PO | Revisam; respondem APPROVED ou REJECTED: motivo |
| event:devops      | devops_worker.py           | sessions.send → XACK                   | DevOps          | Estado Deployed, feature_complete em orchestrator:events |
| audit:queue       | audit_runner.py            | Para cada papel: sessions.send → XACK  | QA, DBA, CyberSec, UX | Auditoria; criam Issue se acharem problema |

## Pré-requisitos

1. **OpenClaw Gateway** rodando (ex.: pod `openclaw` no cluster), com `agents.list` configurado (ceo, po, architect, developer, qa, cybersec, dba, ux, devops).
2. **Variáveis de ambiente** nos pods dos triggers:
   - `OPENCLAW_GATEWAY_WS`: URL WebSocket do Gateway (ex.: `ws://openclaw.ai-agents.svc.cluster.local:18789`).
   - `OPENCLAW_GATEWAY_TOKEN`: (opcional) token de autenticação do Gateway.
   - `OPENCLAW_CLI_PATH`: (opcional) caminho do binário `openclaw`; se ausente, usa `openclaw` do PATH.
3. **OpenClaw CLI** disponível nos pods que rodam os triggers (para `openclaw gateway call sessions.send`). Alternativa futura: cliente WebSocket mínimo em Python que fale o protocolo do Gateway.

## Sessões dos agentes

Por padrão os triggers usam as chaves de sessão:

- PO: `agent:po:main`
- Architect: `agent:architect:main`
- Developer: `agent:developer:main`
- DevOps: `agent:devops:main`
- QA, DBA, UX, CyberSec: `agent:qa:main`, `agent:dba:main`, `agent:ux:main`, `agent:cybersec:main`

Override por env: `OPENCLAW_PO_SESSION_KEY`, `OPENCLAW_ARCHITECT_SESSION_KEY`, etc. (no slot de revisão: `OPENCLAW_ARCHITECT_SESSION_KEY`, `OPENCLAW_QA_SESSION_KEY`, …).

## Ferramentas que os agentes devem usar

Os agentes no OpenClaw precisam de ferramentas (ou uso do **gateway tool** / HTTP) para:

- **Ler/gravar Redis**: estratégia (`project:v1:strategy_doc`), issue (`project:v1:issue:{id}`), estado (`issue_state` ou chave `project:v1:issue:{id}:state`).
- **Publicar em streams**: chamar o **gateway-redis-adapter** (HTTP) com POST /publish (stream, payload). Ex.: PO publica em `draft.2.issue`; Architect em `task:backlog` ou `draft_rejected`; Developer em `code:ready`; DevOps em `orchestrator:events` (feature_complete).
- **Liberar dev_lock**: quando o Developer publicar em `code:ready`, o adapter (ou uma ferramenta) pode apagar a chave `project:v1:issue:{id}:dev_lock` para liberar a próxima tarefa. (Implementação opcional no adapter.)
- **GitHub**: criar issues, PRs, merge via `gh` ou ferramenta que chame `gh`.

O **gateway-redis-adapter** já expõe POST /publish e POST /write-strategy; os agentes chamam esse serviço (ex.: `http://gateway-redis-adapter.ai-agents.svc.cluster.local:5000`) via ferramenta HTTP ou gateway tool configurada no OpenClaw.

## Script de chamada ao Gateway

`scripts/openclaw_gateway_call.py`:

- `gateway_call(method, params, timeout_sec)` — chama `openclaw gateway call <method> --url <OPENCLAW_GATEWAY_WS> --params '<json>' --json`.
- `send_to_session(session_key, message, timeout_sec=0)` — atalho para `sessions.send` com `sessionKey` e `message`; `timeout_sec > 0` espera conclusão da run.

Se o OpenClaw CLI não estiver instalado no pod, o trigger falha com mensagem clara; a solução é incluir o CLI na imagem do trigger ou prover um sidecar/serviço que exponha a chamada ao Gateway.

## O que foi removido (openclaw-first)

- **po_worker**: chamadas a Ollama (`break_into_issues_via_ollama`), criação de issues via `gh` no script. Agora só envia contexto ao agente PO.
- **architect_draft_consumer**: `review_draft_via_ollama`, lógica de aprovar/rejeitar e publicar em task:backlog/draft_rejected. Agora só envia ao agente Architect.
- **developer_worker**: stub com GPULock e “processar tarefa” (sleep). Agora só adquire lock, seta InProgress e envia ao agente Developer; o agente publica code:ready e libera o lock via ferramentas.
- **slot_revisao_pos_dev**: todas as chamadas a Ollama para os 6 papéis; substituídas por `send_to_session(agent:{role}:main, ...)` com espera pela resposta (APPROVED/REJECTED). Merge (`gh pr merge`) permanece no script (ação determinística).
- **devops_worker**: set_issue_state e emit_event feature_complete no script. Agora só envia ao agente DevOps; o agente faz estado e evento via ferramentas.
- **audit_runner**: stub `run_audit_step` e `create_github_issue` no script. Agora só envia a cada papel (QA, DBA, Security, UX) ao Gateway; os agentes fazem a auditoria e criam issues se necessário.

## Scripts removidos (openclaw-first)

- **slot_agent_single.py** — removido; o slot único `revisao-pos-dev` faz os 6 papéis via Gateway. Pods architect/qa/cybersec/dba (014) estão deprecated; usar revisao-pos-dev.
- **consensus_loop_runner.py** — removido (chamadas Ollama); CronJob `consensus-loop-runner` suspenso até existir versão via Gateway.

## Referências

- [Gateway protocol](https://docs.openclaw.ai/gateway/protocol)
- [Session Tools](https://docs.openclaw.ai/concepts/session-tool) (sessions_send, etc.)
- [Multi-Agent](https://docs.openclaw.ai/concepts/multi-agent)
- [docs/38-redis-streams-estado-global.md](../38-redis-streams-estado-global.md)
- [docs/agents-devs/state-machine-issues.md](state-machine-issues.md)
