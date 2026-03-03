# Investigação — OpenClaw no pod (doctor e gateway)

Resumo da investigação feita em 2026-03-03 após rodar `openclaw doctor --fix` no pod do gateway.

## 1. Conectividade

| Alvo | Resultado |
|------|------------|
| **Ollama** (`ollama-service.ai-agents.svc.cluster.local:11434`) | OK — pod consegue `fetch` e lista 6 modelos. |
| **Config em runtime** | Gateway usa `/tmp/openclaw.json` (gerado pelo entrypoint a partir do ConfigMap). `~/.openclaw/openclaw.json` existe e foi alterado pelo `doctor`; o processo do gateway **não** usa esse arquivo (usa `OPENCLAW_CONFIG_PATH=/tmp/openclaw.json`). |
| **Redis** | Não usado na config atual do gateway (apenas `session.dmScope`); session store é em disco em `~/.openclaw/agents/`. |

## 2. Problema crítico: modelo do CEO não existe no Ollama

Nos logs do gateway aparece:

```text
[agent/embedded] embedded run agent end: ... error=Ollama API error 404: {"error":"model 'deepseek-r1:14b' not found"}
```

- **Config** (`openclaw-config`): CEO está com `"model": "ollama/deepseek-r1:14b"`.
- **Ollama no cluster** (lista em `GET /api/tags`): não há `deepseek-r1:14b` nem `deepseek-r1:8b`.

Modelos atualmente disponíveis no Ollama do cluster:

- `qwen2.5:3b`
- `qwen3-coder-next:cloud`
- `gpt-oss:20b-cloud`
- `ministral-3:3b-cloud`
- `glm-5:cloud`
- `stewyphoenix19/phi3-mini_v1:latest`

**Consequência:** quando o Diretor manda mensagem no Telegram, o CEO tenta usar `deepseek-r1:14b`, o Ollama devolve 404 e a resposta falha.

**Soluções possíveis:**

1. **Ajustar a config** para usar um modelo que já está no cluster (ex.: CEO com `ollama/glm-5:cloud` ou `ollama/qwen2.5:3b`) até o DeepSeek ser disponibilizado.
2. **Fazer pull do modelo no Ollama do cluster** (ex.: `ollama pull deepseek-r1:14b` dentro do pod do Ollama), mantendo a config atual.

## 3. Doctor no pod

- O `openclaw doctor --fix` rodou e atualizou `~/.openclaw/openclaw.json` (Telegram/Slack enabled, etc.).
- O gateway em si **não** usa esse arquivo; usa apenas `/tmp/openclaw.json`. Os avisos do doctor (gateway not running, session store missing, Ollama fetch failed) referem-se ao ambiente “local” do doctor (config em `~/.openclaw`, conexão 127.0.0.1:18789, etc.) e são esperados quando se roda doctor dentro do pod.
- “Failed to discover Ollama models: fetch failed” no doctor pode ser timing/rede ou o fato de o doctor usar outra config; em todo caso, **o gateway consegue falar com o Ollama** (confirmado via `fetch` no pod).

## 4. Control UI (acesso por http://192.168.49.2:30000)

- Foi adicionado `allowedOrigins: ["http://192.168.49.2:30000"]` no ConfigMap.
- Nos logs ainda aparece: `reason=control ui requires device identity (use HTTPS or localhost secure context)`.
- Ou seja: a origem está permitida, mas a Control UI exige **device identity** (contexto seguro: HTTPS ou localhost). Acesso por HTTP de outro host (ex.: 192.168.49.2:30000) não é considerado seguro pelo OpenClaw.
- Para usar a UI de outro host em HTTP pode ser necessário habilitar algo como `allowInsecureAuth` ou equivalente na config (ver docs OpenClaw). Uso em produção deve preferir HTTPS ou acesso apenas de localhost.

## 5. Sobre o erro na conversa (Telegram 15:22)

O erro **"Ollama API error 404: model 'deepseek-r1:14b' not found"** que apareceu na bolha do CEO no Telegram ocorreu **antes** da correção aplicada no cluster. O deployment foi reiniciado com a config nova (CEO/PO em `glm-5:cloud`) após essa mensagem. Hoje o pod está usando apenas modelos existentes no Ollama do cluster. Se mandar uma nova mensagem ao CEO no Telegram, a resposta deve sair sem 404.

## 6. Resumo de ações recomendadas

1. **Imediato:** Alterar o modelo do CEO (e de outros agentes que usem `deepseek-r1:*`) no ConfigMap para um modelo presente no cluster (ex.: `ollama/glm-5:cloud`), ou fazer pull de `deepseek-r1:14b` no Ollama do cluster.
2. **Control UI:** Se for obrigatório acessar de outro host por HTTP, consultar a documentação OpenClaw para opções de “allow insecure” / device identity; caso contrário, usar HTTPS ou localhost.
3. **Doctor no pod:** Rodar `doctor --fix` no pod é opcional; as alterações em `~/.openclaw` não afetam o gateway que usa o ConfigMap. Pode-se ignorar os avisos do doctor nesse contexto.
