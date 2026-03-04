# Investigação: logs e resposta dos agentes (OpenClaw)

**Data:** 2026-03-04

## Status do gateway OpenClaw

- **Pod:** `openclaw-5f4c87d84c-j5npc` — **Running** (1/1).
- **Gateway:** escutando em `ws://0.0.0.0:18789`, modelo `ollama/ministral-3:14b-cloud`.
- **Slack:** todos os providers iniciados (ceo, po, devops, architect, developer, qa, cybersec, ux, dba) e **socket mode connected** (várias conexões).
- **Telegram:** provider iniciado (@ClawDevsAIBot).

Conclusão: **o gateway está no ar e os canais Slack estão conectados**; os agentes estão em condições de receber e responder mensagens.

## Avisos nos logs (não impedem resposta)

1. **Slack `missing_scope`:**  
   `channel resolve failed; using config entries. Error: An API error occurred: missing_scope`  
   O gateway segue usando as entradas de config e o **socket mode connected** aparece em seguida. Ou seja, mensagens podem ser recebidas e enviadas; o aviso indica apenas que algum scope da Slack API está faltando (ex.: listagem de canais), não que o bot não responda.

2. **Doctor OpenClaw:**  
   Sugestão de rodar `openclaw doctor --fix` (migração de `channels.slack` para `channels.slack.accounts.default`). Opcional; não bloqueia resposta dos agentes.

3. **Gateway em não-loopback:**  
   Aviso de garantir autenticação ao expor em rede. Esperado em ambiente de desenvolvimento.

## Como verificar se os agentes estão respondendo

1. **Logs em tempo real (stdout do container):**
   ```bash
   kubectl logs -n ai-agents deployment/openclaw -c gateway -f --tail=50
   ```

2. **Arquivo de log dentro do pod (mais detalhado):**
   ```bash
   kubectl exec -n ai-agents deploy/openclaw -c gateway -- tail -f /tmp/openclaw/openclaw-2026-03-04.log
   ```

3. **Teste no Slack:**  
   Enviar mensagem em DM para o app do DevOps (ex.: “@DevOps olá”) e observar se há resposta e se no log aparecem linhas relacionadas a mensagem/request/agent.

4. **Ollama:**  
   Se o agente não responder, verificar se o modelo está carregado e se o Ollama está acessível a partir do pod do OpenClaw:
   ```bash
   kubectl get pods -n ai-agents -l app=ollama-gpu
   kubectl exec -n ai-agents deploy/openclaw -c gateway -- wget -qO- http://ollama-service:11434/api/tags 2>/dev/null | head -20
   ```

## Job init-memory-structure (RunContainerError)

- **Causa:** o job usa a imagem `bash:5.2-alpine3.19` com `command: ["/bin/bash", "/scripts/init-memory.sh"]`, mas nessa imagem não existe `/bin/bash` (o binário está em outro path, ex.: em `PATH` como `bash`).
- **Correção aplicada:** em `k8s/management-team/openclaw/init-memory-job.yaml` o comando foi alterado para `["bash", "/scripts/init-memory.sh"]` para usar o `bash` do `PATH`.
- **Próximo passo:** reaplicar o job e conferir se completa:
  ```bash
  kubectl delete job init-memory-structure -n ai-agents --ignore-not-found=true
  kubectl apply -f k8s/management-team/openclaw/init-memory-job.yaml
  kubectl wait --for=condition=complete job/init-memory-structure -n ai-agents --timeout=120s
  ```

## Resumo

| Item                    | Status |
|-------------------------|--------|
| Gateway OpenClaw        | OK, no ar |
| Providers Slack (agentes) | OK, iniciados e socket connected |
| Telegram provider       | OK, iniciado |
| Avisos (missing_scope, doctor) | Não impedem resposta |
| Resposta dos agentes    | A verificar via teste no Slack e logs acima |
| Job init-memory-structure | Corrigido (uso de `bash` no comando); reaplicar e validar |

Para confirmar que “os agentes estão respondendo”, o passo prático é: enviar mensagem no Slack (ex.: para o DevOps) e acompanhar os logs com os comandos indicados; em seguida, checar conectividade com o Ollama se não houver resposta.
