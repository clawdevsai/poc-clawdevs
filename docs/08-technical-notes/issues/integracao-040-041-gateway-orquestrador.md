# config-perfis / truncamento-finops — Onde chamar cada script (Gateway e orquestrador)

Referência para integrar os scripts e configs (perfis e truncamento/FinOps) no gateway (adapter/OpenClaw) e no orquestrador/workers.

---

## 1. Gateway (adapter HTTP)

### 1.1 Publicação destinada à nuvem

**Arquivo:** `scripts/gateway_redis_adapter.py`

- **Rota:** `POST /publish-to-cloud`
- **Corpo:** `{ "stream": "...", "data": { ... }, "preflight": true, "profile": "ceo"|"po"|"default" }`
- **Comportamento:**
  1. Se `data` tiver chave `payload`, `body` ou `content` (string JSON) e `preflight=true`:
     - Conta interações (`messages`/`history`); se **> PREFLIGHT_SUMMARIZE_MIN_INTERACTIONS** (env, default 3), chama **preflight_summarize** (Ollama local) e substitui o histórico pelo resumo.
  2. Aplica **max tokens** por perfil ao payload:
     - `profile=ceo` → `MAX_TOKENS_PER_REQUEST_CEO`
     - `profile=po` → `MAX_TOKENS_PER_REQUEST_PO`
     - `default` → `MAX_TOKENS_PER_REQUEST_CLOUD_DEFAULT`
  3. Publica no Redis (mesmo fluxo que `/publish`: truncamento na borda, token bucket para `cmd:strategy`).

**Uso pelo OpenClaw:** Em vez de `POST /publish` para eventos que vão disparar chamada à nuvem, usar `POST /publish-to-cloud` com `profile` adequado (ex.: CEO/PO para estratégia, default para outros).

**ConfigMap:** O adapter precisa de `preflight_summarize.py` no mesmo volume; Makefile target `gateway-redis-adapter-configmap` já inclui.

---

## 2. Worker Developer (FinOps antes de processar)

**Arquivo:** `scripts/developer_worker.py`

- **Ponto:** Antes de adquirir o **GPU Lock** em `process_task()`.
- **Fluxo:**
  1. Extrai `issue_id` de `data` (chaves `issue_id`, `issue`, `task_id`).
  2. Se existir, chama **finops_attempt_cost**: `increment_attempt(r, issue_id)` e `should_stop_task(issue_id, attempt, FINOPS_COST_ESTIMATE)`.
  3. Se `should_stop_task` retornar `True`: faz **XACK** (não reprocessar), emite evento `task_returned_to_po` no stream do orquestrador e **retorna sem processar** (não usa GPU).
  4. Caso contrário, segue com GPU Lock e processamento.

**Variáveis de ambiente (opcional):** `FINOPS_COST_ESTIMATE` (default 0.01), `FINOPS_MAX_ATTEMPTS`, `FINOPS_DAILY_CAP` (em `finops-config` ConfigMap).

---

## 3. Working buffer (escrita com TTL)

**Arquivo:** `scripts/redis_buffer_writer.py`

- **Função:** `write_working_buffer(key_suffix, value, ttl_sec=None)`
- **Uso:** Qualquer script ou serviço que **escreva** no Redis um buffer de conversa (ex.: `project:v1:working_buffer:session:123`) deve usar esta função para que a chave tenha TTL (`WORKING_BUFFER_TTL_SEC`).
- **Exemplo:**

  ```python
  from redis_buffer_writer import write_working_buffer
  import json
  write_working_buffer("session:abc", json.dumps(messages))
  ```

- **Config:** `WORKING_BUFFER_KEY_PREFIX`, `WORKING_BUFFER_TTL_SEC` (finops-config).

---

## 4. Validação reversa (PO)

**Arquivo:** `app/features/validate_reverse_po.py` (uso via wrapper na raiz do repo).

- **Quando:** Após **gerar um resumo** que substituirá o buffer (ex.: saída do pre-flight ou de um job de compactação), antes de aceitar esse resumo.
- **Chamada (wrapper, a partir da raiz do repositório):**

  ```bash
  ./scripts/validate_reverse_po_after_summary.sh /caminho/do/resumo.md /caminho/da/issue-com-criterios.md
  ```

  Se **exit 1**: o resumo omitiu critérios; **não substituir** o buffer pelo resumo (reestruturar o bloco ou refazer o resumo).

- **Passo explícito de pipeline:** Após gerar arquivo de resumo (ex.: saída de `preflight_summarize` gravada em arquivo, ou job de compactação que produz resumo), executar o comando acima. Se o script retornar 1, **não aplicar** o truncamento ao buffer. O arquivo de critérios deve conter o bloco `<!-- CRITERIOS_ACEITE -->` (ex.: `docs/03-agents/agents-devs/CRITERIOS_ACEITE-example.md`).
- **Chamada direta (Python):** `python3 app/features/validate_reverse_po.py --summary <resumo.md> --criteria <issue.md>` — mesmo contrato de exit 0/1.

Ref: `docs/soul/PO.md` (Validação reversa).

---

## 5. Compactação segura (DevOps)

**Arquivo:** `scripts/devops_compact_safe.sh` → `scripts/compact_preserve_protected.py`

- **Quando:** Na **higiene de buffers** (cron ou job do DevOps): compactar Markdown preservando blocos `CRITERIOS_ACEITE` e `INVARIANTE_NEGOCIO`.
- **Uso:**

  ```bash
  ./scripts/devops_compact_safe.sh /caminho/do/buffer.md
  ```

  Gera `/caminho/do/buffer.md.compact`; revisar e substituir o original se desejado.
- **Agendamento e CronJob:** Ver [devops-compactacao-buffer.md](devops-compactacao-buffer.md) e exemplo [k8s/development-team/devops-compact-cronjob-example.yaml](../../k8s/development-team/devops-compact-cronjob-example.yaml). Pré-requisito: `make devops-compact-configmap` e PVC para buffers.

---

## 6. Resumo — onde está cada coisa

| Componente            | Onde chama / usa |
|-----------------------|------------------|
| Pre-flight + max tokens | **gateway_redis_adapter**: rota `/publish-to-cloud` |
| FinOps (interromper tarefa) | **developer_worker**: antes do GPU Lock em `process_task` |
| Working buffer TTL    | **redis_buffer_writer.write_working_buffer** — quem escreve buffer no Redis |
| Validação reversa PO  | Pipeline que gera resumo: chamar `validate_reverse_po` antes de aplicar resumo |
| Compactação preservando blocos | DevOps: `devops_compact_safe.sh` no cron de higiene |
| MicroADR             | **slot_revisao_pos_dev**: ao aprovar PR, chama `microadr_generate.py` |

Configs (FinOps, perfis, TTL, tags) vêm dos ConfigMaps **finops-config** e **agent-profiles**; deployments do adapter e OpenClaw já usam `envFrom: finops-config`.
