# Por que o Slack demora ou parece travado

Quando a conversa no #all-clawdevsai demora muito ou parece “travada”, as causas mais comuns são as abaixo. Use este doc para diagnóstico e ajustes.

---

## Causas principais

### 1. Modelo em nuvem (qwen3.5:cloud)

- **O que é:** Todas as respostas passam por Ollama no cluster, que chama a **Ollama Cloud** para `qwen3.5:cloud`.
- **Efeito:** Cada turno = ida e volta na rede + fila na nuvem. É normal levar **10–60+ segundos** por resposta, dependendo do tamanho do prompt e da carga.
- **O que fazer:**  
  - Para sentir menos “travado”, ative **streaming** e **ackReaction** (ver abaixo).  
  - Se quiser mais velocidade e puder usar modelo local, troque no config para um modelo local (ex.: `ollama/ministral-3:3b` ou `ollama/phi3-mini`) no `openclaw-config`; a primeira resposta continua mais rápida em máquina com GPU.

### 2. Um turno por vez (gateway + Ollama únicos)

- **O que é:** Um único gateway e um único Ollama atendem **todos** os agentes (CEO, PO, UX, etc.). Quando o UX está respondendo, o PO só começa depois que o turno do UX termina.
- **Efeito:** Várias menções seguidas (@UX depois @PO) = espera em fila; a conversa parece lenta ou parada.
- **O que fazer:** É o desenho atual. Reduzir tamanho das respostas (menos `maxTokens`) ou usar modelo mais leve reduz o tempo de cada turno.

### 3. Sem feedback visual (“travado”)

- **O que é:** O usuário não vê nenhum sinal de que o bot está processando.
- **O que fazer:**  
  - **ackReaction:** Configurado `channels.slack.ackReaction: "eyes"` no OpenClaw: o app reage com 👀 à mensagem assim que começa a processar.  
  - **Streaming:** Com `streaming: "partial"` e escopo `assistant:write` + Agents and AI Apps ativados no app Slack, a resposta aparece aos poucos em vez de só no final (ver [42-slack-tokens-setup.md](../07-operations/42-slack-tokens-setup.md)).

### 4. Log em modo debug

- **O que é:** Gateway com `--log-level debug` gera muito I/O de log.
- **O que fazer:** No entrypoint do OpenClaw está `--log-level info`; em produção evite `debug` a menos que esteja depurando.

### 5. Respostas muito longas (maxTokens)

- **O que é:** Modelo com `maxTokens: 8192` pode gerar respostas bem longas = mais tempo até terminar.
- **O que fazer:** Se quiser respostas mais curtas e rápidas, reduza no config `models.providers.ollama.models[]` o `maxTokens` do modelo em uso (ex.: 2048 ou 4096).

---

## Checklist rápido

| Item | Onde | Ação |
|------|------|------|
| Reação “processando” | `openclaw-config` | `channels.slack.ackReaction: "eyes"` (já configurado). |
| Streaming no Slack | App em api.slack.com | Bot scope `assistant:write`; ativar **Agents and AI Apps** nas configurações do app. |
| Log do gateway | `entrypoint.sh` | Usar `--log-level info` (já ajustado). |
| Tempo por turno | Modelo | qwen3.5:cloud = latência de nuvem; para mais velocidade, considerar modelo local. |
| Tamanho da resposta | Config OpenClaw | Reduzir `maxTokens` do modelo se as respostas forem longas demais. |

---

## Referências

- [42-slack-tokens-setup.md](../07-operations/42-slack-tokens-setup.md) — escopos do Bot (incl. `assistant:write` para streaming).
- [ceo-po-conversa-slack.md](ceo-po-conversa-slack.md) — contexto na thread e bots conversando.
- [OpenClaw — Slack](https://docs.openclaw.ai/channels/slack) — Text streaming, ackReaction, replyToMode.
