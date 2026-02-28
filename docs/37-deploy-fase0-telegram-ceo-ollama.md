# Deploy Fase 0: CEO via Telegram + Ollama no Kubernetes

Entrega mínima: **Diretor fala com o CEO no Telegram**; CEO usa **um único modelo local (Ollama)** no cluster. **Slack (opcional):** todos os agentes podem conversar no Slack; discussões entre agentes no Slack usam **Ollama local GPU obrigatório**. Política: apenas o CEO usa Telegram; demais agentes só Slack. Todos compartilham o mesmo workspace.

## Pré-requisitos

- **GPU:** Host com driver NVIDIA instalado; Docker com acesso à GPU; Minikube iniciado **com suporte a GPU** (ex.: `minikube start --driver=docker --addons=nvidia-device-plugin ...` — ver `make prepare` / `make up`). Se o Ollama rodar em CPU, verifique: (1) addon ativo: `minikube addons list | grep nvidia`; (2) pod com GPU alocada: `kubectl describe pod -n ai-agents -l app=ollama` e confira em Limits/Requests se `nvidia.com/gpu: 1` aparece e se não há eventos de falha de scheduling. O deployment define `CUDA_VISIBLE_DEVICES=0` para forçar uso da GPU no container.
- `kubectl` configurado.
- **Telegram Bot Token**: criar em [@BotFather](https://t.me/BotFather) com `/newbot`.  
  **Importante:** Nunca commitar o token. Se foi exposto em chat, **revogue no BotFather** (`/revoke`) e crie outro.
- **Telegram Chat ID** (opcional para Fase 0): se usar `dmPolicy: allowlist`, informe o ID numérico do Diretor (obter com `getUpdates` ou pairing).

## 1. Namespace e Redis

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/redis/deployment.yaml
```

## 2. Ollama (GPU)

Garanta que o Minikube tenha o device plugin NVIDIA e que o modelo esteja disponível (ou puxe depois):

```bash
kubectl apply -f k8s/ollama/deployment.yaml
# Aguardar pod Running; depois, puxar o modelo (em outro terminal, port-forward ou exec):
# kubectl exec -n ai-agents deploy/ollama-gpu -- ollama pull stewyphoenix19/phi3-mini_v1:latest
```

Para puxar o modelo a partir do host (com port-forward):

```bash
kubectl port-forward -n ai-agents svc/ollama-service 11434:11434 &
ollama pull stewyphoenix19/phi3-mini_v1:latest
kill %1
```

### 2.1. Ollama Cloud (modelos glm-5:cloud etc.) — login obrigatório no `make up`

Se existir `k8s/ollama/secret.yaml` (com `OLLAMA_API_KEY`), o **`make up`** aplica o secret e em seguida **exige** que você conclua o login no Ollama Cloud antes de continuar:

1. O script `scripts/ollama-ensure-cloud-auth.sh` verifica se o pod já está autenticado (teste com um modelo cloud).
2. Se **já autenticado** (credenciais no volume do pod): nada é pedido e o fluxo segue.
3. Se **não autenticado**: é exibido um link `https://ollama.com/connect?name=...&key=...`. Você deve **abrir o link no navegador**, fazer login em ollama.com (se precisar) e autorizar o dispositivo. Em seguida **pressionar ENTER** no terminal para o `make up` continuar (OpenClaw, etc.).

A autenticação fica gravada no volume do Ollama (`/root/.ollama`); nos próximos `make up` o script detecta que já está autenticado e não pede o link de novo. Para gerar um novo link manualmente: `./scripts/ollama-signin.sh`.

## 3. Secret Telegram (obrigatório)

**Não** commitar `secret.yaml` com valores reais. Criar o secret manualmente:

```bash
kubectl create secret generic openclaw-telegram -n ai-agents \
  --from-literal=TELEGRAM_BOT_TOKEN='SEU_BOT_TOKEN' \
  --from-literal=TELEGRAM_CHAT_ID='SEU_CHAT_ID_NUMERICO'
```

Ou copie `k8s/management-team/openclaw/secret.yaml.example` para `secret.yaml`, preencha e aplique (e adicione `secret.yaml` ao `.gitignore`):

```bash
cp k8s/management-team/openclaw/secret.yaml.example k8s/management-team/openclaw/secret.yaml
# Editar e colar token e chat id
kubectl apply -f k8s/management-team/openclaw/secret.yaml
```

### 3.1. Secret a partir do .env (Telegram + Slack)

Para criar ou atualizar o secret **a partir do seu `.env`** (evitando copiar tokens à mão):

```bash
./scripts/k8s-openclaw-secret-from-env.sh
```

O script lê `.env` na raiz do repo e aplica `openclaw-telegram` no namespace `ai-agents` com as chaves definidas (TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID, SLACK_APP_TOKEN, SLACK_BOT_TOKEN, SLACK_DIRECTOR_USER_ID, SLACK_ALLOWED_USER_IDS). Depois: `kubectl rollout restart deployment/openclaw -n ai-agents`.

### 3.2. Slack (opcional)

Para habilitar o canal **Slack** (todos os agentes podem conversar; discussões = Ollama local GPU), adicione ao mesmo secret `openclaw-telegram` (ou use o script acima com .env já preenchido):

- **SLACK_APP_TOKEN** (xapp-...) — App Token com Socket Mode. Criar app em [Slack API](https://api.slack.com/apps) para o workspace (ex.: clawdevsai), habilitar Socket Mode, criar App Token com `connections:write`.
- **SLACK_BOT_TOKEN** (xoxb-...) — Bot Token (após instalar o app no workspace).
- **SLACK_DIRECTOR_USER_ID** (opcional) — ID do Diretor no Slack (ex.: U01234ABCD) para allowlist em DMs. Se omitido, usar pairing: `openclaw pairing approve slack <CODE>`.

Documentação do canal Slack: [OpenClaw — Slack](https://docs.openclaw.ai/channels/slack).

```bash
kubectl patch secret openclaw-telegram -n ai-agents -p '{"stringData":{"SLACK_APP_TOKEN":"xapp-...","SLACK_BOT_TOKEN":"xoxb-...","SLACK_DIRECTOR_USER_ID":"U01234ABCD"}}'
# Ou recriar o secret incluindo TELEGRAM_* e SLACK_*
```

## 4. OpenClaw (ConfigMap + Workspace CEO + Deployment)

O agente CEO obedece ao **perfil SOUL** ([docs/soul/CEO.md](soul/CEO.md)): o ConfigMap `openclaw-workspace-ceo` fornece `SOUL.md` no workspace; o OpenClaw injeta esse conteúdo no system prompt. Assim o CEO responde em tom executivo e direto, na **mesma língua** que o Diretor usar, e segue as restrições (nunca escrever código, nunca aprovar PRs, etc.). Aplicar também o workspace do CEO:

```bash
kubectl apply -f k8s/management-team/openclaw/workspace-ceo-configmap.yaml
```

A imagem padrão no deployment é um placeholder (`node:22-bookworm-slim` com `sleep infinity`). Para o CEO responder de fato no Telegram você precisa:

**Opção A — Imagem OpenClaw oficial (quando disponível):**  
Altere `k8s/management-team/openclaw/deployment.yaml` e use a imagem que executa `openclaw gateway`, com entrypoint apontando para `/config/config.yaml`.

**Opção B — Rodar OpenClaw no host (teste rápido):**  
Use o script `scripts/run-openclaw-telegram-ollama.sh`, que faz port-forward do Ollama e inicia o gateway com a config `config/openclaw/openclaw.local.json5`. **Para o bot responder no perfil CEO** (tom executivo, pt-BR, SOUL), essa config define `agents.defaults.workspace: "config/openclaw/workspace-ceo"`, onde está o `SOUL.md` do CEO; o script deve ser executado **na raiz do repositório** para que esse caminho exista. Sem o workspace configurado, o modelo recebe apenas o prompt genérico e responde como assistente, não como CEO.

```bash
# Na raiz do repo (obrigatório para workspace CEO)
./scripts/run-openclaw-telegram-ollama.sh
```

Ou manualmente (port-forward + config com workspace):

```bash
kubectl port-forward -n ai-agents svc/ollama-service 11434:11434 &
export TELEGRAM_BOT_TOKEN='...'
export OPENCLAW_CONFIG_PATH="$(pwd)/config/openclaw/openclaw.local.json5"
# CWD deve ser a raiz do repo (workspace CEO = config/openclaw/workspace-ceo)
openclaw gateway
```

Aplicar ConfigMap, workspace CEO e Deployment no cluster (mesmo com imagem placeholder, para deixar o fluxo pronto):

```bash
kubectl apply -f k8s/management-team/openclaw/configmap.yaml
kubectl apply -f k8s/management-team/openclaw/workspace-ceo-configmap.yaml
kubectl apply -f k8s/management-team/openclaw/deployment.yaml
```

## 5. Expor o OpenClaw para o Telegram (webhook ou polling)

O OpenClaw precisa receber mensagens do Telegram. Em ambiente local (host), **long polling** funciona sem expor porta. No cluster:

- **Webhook:** Expor o serviço OpenClaw (Ingress ou LoadBalancer) e configurar no OpenClaw `channels.telegram.webhookUrl` + `webhookSecret`.
- **Polling:** Se o gateway rodar em um pod com internet, o polling já é o padrão; garantir que o pod consiga acessar `api.telegram.org`.

**Correlação mensagem–resposta:** O gateway deve enviar cada resposta apenas à mensagem que a provocou (1:1); não misturar respostas entre mensagens. Ver [07-configuracao-e-prompts.md](07-configuracao-e-prompts.md) (Canais) e [issues/130-telegram-correlacao-mensagem-resposta.md](issues/130-telegram-correlacao-mensagem-resposta.md).

Ref: [Telegram — OpenClaw](https://docs.openclaw.ai/channels/telegram).

## 6. Pairing (primeiro acesso do Diretor)

Com `dmPolicy: pairing`:

1. Diretor envia uma mensagem em DM para o bot no Telegram.
2. No host/pod onde o gateway está rodando: `openclaw pairing list telegram`
3. Aprovar: `openclaw pairing approve telegram <CODE>`
4. A partir daí o Diretor pode conversar com o CEO.

## 7. Testar no Minikube com Slack (conversa e pergunta ao Diretor)

Para **subir os agentes no Minikube** e **testar a conexão com o Slack** (incluindo dar a ordem de conversar no Slack e perguntar algo ao Diretor):

### 7.1. Subir o cluster e o Ollama

```bash
# Na raiz do repositório
make up
```

Aguarde o namespace `ai-agents`, Redis, Ollama e OpenClaw (ConfigMaps/Deployment). O Ollama faz preload dos modelos (incluindo `qwen2.5:3b` para conversa no Slack). Se o Ollama usar Cloud e pedir login, conclua no navegador e pressione ENTER no terminal.

### 7.2. Gateway no host com Slack (recomendado para teste)

Para testar o Slack com os tokens do `.env` (Socket Mode), rode o **gateway no host** com port-forward para o Ollama do cluster. Opcionalmente desligue o gateway no cluster para evitar dois listeners:

```bash
kubectl scale deployment openclaw -n ai-agents --replicas=0
```

Garanta no **`.env`** na raiz do repo:

- `TELEGRAM_BOT_TOKEN` e `TELEGRAM_CHAT_ID` (Telegram, CEO)
- `SLACK_APP_TOKEN`, `SLACK_BOT_TOKEN` e, se quiser allowlist em DM, `SLACK_DIRECTOR_USER_ID`

Depois:

```bash
./scripts/run-openclaw-telegram-ollama.sh
```

O script faz port-forward do `svc/ollama-service` para `127.0.0.1:11434` e inicia o gateway com a config local (todos os agentes, modelo `qwen2.5:3b` para Slack). Quando aparecer "Slack habilitado. Envie mensagem no Slack ou no Telegram para testar.", o gateway está pronto.

### 7.3. Testar no Slack: conversar e perguntar ao Diretor

No workspace **ClawDevsAi** (Slack):

1. Abra um **DM com o app** (ex.: ClawdevsAI) ou um canal onde o bot foi adicionado.
2. Envie uma mensagem que peça para **conversar no Slack e perguntar algo ao Diretor**, por exemplo:
   - *"Pergunta ao Diretor: Qual a prioridade desta semana?"*
   - *"Converse no Slack e pergunte ao Diretor: podemos adiar a entrega do módulo X?"*
   - Ou mencione o bot e faça a pergunta: *"@ClawdevsAI Pergunte ao Diretor: [sua pergunta]"*

O gateway roteia a mensagem para o agente (CEO ou o agente que atender no Slack); a resposta usa o Ollama do cluster (port-forward) com o modelo configurado para Slack (`qwen2.5:3b`). Se você configurou `SLACK_DIRECTOR_USER_ID`, apenas o Diretor pode iniciar DM; em canal, todos podem mencionar o bot.

**Primeiro acesso no Slack (pairing):** Se não tiver `SLACK_DIRECTOR_USER_ID` no `.env`, no primeiro DM o gateway pode pedir aprovação. No terminal onde o script está rodando: `openclaw pairing list slack` e depois `openclaw pairing approve slack <CODE>`.

Ref: [42-slack-tokens-setup.md](42-slack-tokens-setup.md), [config/openclaw/README.md](../config/openclaw/README.md).

## Resumo da arquitetura (Fase 0)

| Componente   | Função                                      |
|-------------|----------------------------------------------|
| **openclaw**| Gateway: canal Telegram → agente CEO → Ollama|
| **ollama-gpu** | Modelo local (ex.: stewyphoenix19/phi3-mini_v1:latest, ministral-3:3b) |
| **redis**   | Disponível para estado/streams (fase futura) |
| **openclaw-workspace-ceo** | SOUL.md no workspace → CEO segue perfil [soul/CEO.md](soul/CEO.md) |

Doc de arquitetura: [openclaw-sub-agents-architecture.md](openclaw-sub-agents-architecture.md).

---

## Management-team com provedor nuvem (Fase 1 — 019)

Para usar **CEO e PO com LLM em nuvem** (Ollama Cloud, OpenRouter, OpenAI, etc.):

1. **ConfigMap de provedores:** [k8s/llm-providers-configmap.yaml](../k8s/llm-providers-configmap.yaml) define uma chave por agente (`agent_ceo`, `agent_po`, etc.). Valores: `ollama_local` (padrão) | `ollama_cloud` | `openrouter` | `openai` | `qwen_oauth` | `moonshot_ai` | `huggingface_inference`.
2. **Alterar para nuvem:** Edite o ConfigMap e defina, por exemplo, `agent_ceo: "ollama_cloud"` e `agent_po: "openrouter"`. Aplique: `kubectl apply -f k8s/llm-providers-configmap.yaml`.
3. **Secrets:** Crie no namespace `ai-agents` os secrets exigidos pelo provedor (ex.: `OPENROUTER_API_KEY`, `OPENAI_API_KEY`). Para Ollama Cloud use `k8s/ollama/secret.yaml` com `OLLAMA_API_KEY` (o `make up` já aplica se o arquivo existir).
4. **Config do OpenClaw:** O gateway lê o ConfigMap `clawdevs-llm-providers` e deve rotear cada agente ao provedor correspondente; os modelos (IDs) por agente ficam no config do OpenClaw (ex.: `k8s/management-team/openclaw/configmap.yaml`). Ajuste os IDs de modelo (ex.: `ollama/glm-5:cloud`, `openrouter/model-id`) conforme a documentação do OpenClaw.
5. **Reiniciar o deployment:** `kubectl rollout restart deployment/openclaw -n ai-agents` (ou `deployment/openclaw-management` se usar `make up-management`).

Validação e line-up sugerido por agente: [issues/validacao-fase1-019.md](issues/validacao-fase1-019.md) e [41-fase1-agentes-soul-pods.md](41-fase1-agentes-soul-pods.md) (§ Line-up).

---

## Otimização de latência (Telegram)

Para **reduzir o tempo de resposta** no chat do Telegram sem aumentar hardware:

- **Modelo do CEO:** O CEO está configurado para usar **stewyphoenix19/phi3-mini_v1:latest** (modelo mais leve) com `contextWindow: 4096` e `maxTokens: 1024` no OpenClaw — respostas curtas e objetivas saem mais rápido. Ver `k8s/management-team/openclaw/configmap.yaml` (gateway) e `config/openclaw/openclaw.local.json5`.
- **OLLAMA_KEEP_ALIVE:** O deployment do Ollama usa `5m` para manter o modelo na VRAM entre mensagens; evita latência de reload. Ver `k8s/ollama/deployment.yaml`.
- **OLLAMA_CONTEXT_LENGTH:** Opcionalmente definido (ex.: 8192) no deployment para limitar contexto global e uso de VRAM; alinha com o SOUL compacto do CEO. Ver [04-infraestrutura.md](04-infraestrutura.md).
- **SOUL do CEO:** Manter a versão compacta em `openclaw-workspace-ceo` (respostas curtas, uma linha para cumprimentos).
- **Streaming:** Se o OpenClaw e o canal Telegram suportarem resposta em streaming, habilitar reduz a **latência percebida** (texto aparecendo aos poucos); consultar a documentação do OpenClaw.

Garantir que o modelo do CEO esteja puxado no cluster: `kubectl exec -n ai-agents deploy/ollama-gpu -- ollama pull stewyphoenix19/phi3-mini_v1:latest` (ou via port-forward).

---

## Próximas etapas (após Fase 0)

| Fase | Conteúdo principal |
|------|---------------------|
| **1** | SOUL dos outros agentes (PO, DevOps, Architect, etc.), integração com OpenClaw, line-up, fluxo evento-driven — [issues/README.md](issues/README.md) (010–019). |
| **2** | Segurança: Zero Trust, token bucket e degradação por eficiência (CEO), quarentena, sandbox, OWASP, CISO — (020–029, 126, 128). |
| **3** | Operações: manual de primeiros socorros, five strikes, aprovação por omissão cosmética, orçamento de degradação — (030–039, 127). |
| **4+** | Configuração FinOps no Gateway, truncamento/sumarização, memória Elite, habilidades transversais, ferramentas, integrações — ver [issues/README.md](issues/README.md). |
