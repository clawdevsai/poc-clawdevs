# Investigação — logs do CEO (OpenClaw gateway)

Onde e como aparecem os logs do agente CEO e do gateway OpenClaw no cluster.

## 1. Onde os logs saem

| Fonte | Comando | Conteúdo |
|-------|---------|----------|
| **stdout do container** | `kubectl logs -n ai-agents deploy/openclaw -c gateway [--tail=N]` | Mensagens em texto: `[slack]`, `[ceo]`, `[agent/embedded]`, `[diagnostic]`, `[gateway]`, `[ws]`. Após **restart** do deployment, só aparecem logs a partir do novo pod. |
| **Arquivo JSON no pod** | `kubectl exec -n ai-agents deploy/openclaw -c gateway -- cat /tmp/openclaw/openclaw-2026-03-04.log` | Log estruturado (JSON por linha); path indicado no startup: `log file: /tmp/openclaw/openclaw-2026-03-04.log`. Inclui subsistema (ex.: `gateway/channels/slack`, `gateway`). |

## 2. O que aparece relacionado ao CEO

- **Startup:** `[slack] [ceo] starting provider` — confirma que o provider do CEO no Slack subiu.
- **Sessão/agente:** Quando há mensagem no canal/DM do CEO, o gateway enfileira e processa; em modo diagnóstico podem aparecer linhas como:
  - `[diagnostic] lane enqueue: lane=session:agent:ceo:slack:channel:...`
  - `[agent/embedded] embedded run start: ... sessionId=... provider=ollama model=glm-5:cloud`
  - `[agent/embedded] embedded run agent end: runId=... isError=false`
- **Exec (ferramenta):** O resultado de `exec` (ex.: saída do `git clone`) é devolvido ao modelo e pode ser enviado ao Slack; **não** há linha dedicada no log tipo `[exec] stdout=...`. Erros de comando (ex.: `Permission denied`, `fatal: Could not read from remote repository`) vêm na resposta da tool para o agente, não como log separado.
- **Slack:** Erros de API Slack aparecem como `[slack] channel resolve failed; using config entries. Error: An API error occurred: missing_scope` — são avisos de permissão/scope do app Slack, não do CEO em si.

## 3. Limitações

- **Restart zera o buffer:** `kubectl logs` só mostra o que o pod atual escreveu em stdout. Após `kubectl rollout restart`, as tentativas de clone (e qualquer log de exec) **anteriores** ao restart não ficam mais acessíveis por `kubectl logs`.
- **Sem log explícito de stdout/stderr do exec:** O OpenClaw não grava em log o stdout/stderr de cada chamada à tool `exec`; isso volta só na resposta ao modelo (e no que o CEO envia de volta ao Slack).
- **Arquivo de log:** O arquivo em `/tmp/openclaw/` é sobretudo o mesmo fluxo em JSON; não há subsistema separado que registre “exec do CEO” com a saída do comando.

## 4. Comandos úteis para investigar

```bash
# Últimas 200 linhas do gateway (CEO, Slack, agent runs)
kubectl logs -n ai-agents deploy/openclaw -c gateway --tail=200

# Filtrar por ceo, agent, exec, erro
kubectl logs -n ai-agents deploy/openclaw -c gateway --tail=500 | grep -E "ceo|agent/embedded|exec|diagnostic|Error|error"

# Log JSON no pod (ex.: linhas com ceo)
kubectl exec -n ai-agents deploy/openclaw -c gateway -- grep -E "ceo|agent" /tmp/openclaw/openclaw-2026-03-04.log | tail -50
```

## 5. Resumo

- **CEO está a responder** quando há `[slack] [ceo] starting provider` e, após uma mensagem no canal, linhas `[agent/embedded] embedded run ...` para a sessão do CEO.
- **O que aconteceu com o clone:** O CEO chamou `exec` com `git clone` via SSH; o comando falhou com `Permission denied (publickey)` no GitHub. Essa falha não fica registada como linha de log própria; conclui-se pelo comportamento (workspace vazio) e pelo teste manual de `git clone` no pod.
- Para **ver falhas de comandos** no futuro, depende do que o CEO enviar de volta ao Slack (ex.: colar a saída do comando) ou de testes manuais com `kubectl exec ... -- git clone ...`.

## Referências

- [investigacao-openclaw-pod.md](investigacao-openclaw-pod.md) — doctor, modelos, session store.
- [workspace-compartilhado-repositorio-ceo.md](workspace-compartilhado-repositorio-ceo.md) — onde o CEO grava e por que o repo pode não aparecer no host.
