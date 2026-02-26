# Deploy Fase 0: CEO via Telegram + Ollama no Kubernetes

Entrega mínima: **Diretor fala com o CEO no Telegram**; CEO usa **um único modelo local (Ollama)** no cluster. OpenClaw com sub-agents fica pronto para expandir (PO, Developer, etc.) depois.

## Pré-requisitos

- Minikube (ou cluster K8s) com **NVIDIA GPU** disponível para o pod Ollama.
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
# kubectl exec -n ai-agents deploy/ollama-gpu -- ollama pull phi3:mini
```

Para puxar o modelo a partir do host (com port-forward):

```bash
kubectl port-forward -n ai-agents svc/ollama-service 11434:11434 &
ollama pull phi3:mini
kill %1
```

## 3. Secret Telegram (obrigatório)

**Não** commitar `secret.yaml` com valores reais. Criar o secret manualmente:

```bash
kubectl create secret generic openclaw-telegram -n ai-agents \
  --from-literal=TELEGRAM_BOT_TOKEN='SEU_BOT_TOKEN' \
  --from-literal=TELEGRAM_CHAT_ID='SEU_CHAT_ID_NUMERICO'
```

Ou copie `k8s/openclaw/secret.yaml.example` para `secret.yaml`, preencha e aplique (e adicione `secret.yaml` ao `.gitignore`):

```bash
cp k8s/openclaw/secret.yaml.example k8s/openclaw/secret.yaml
# Editar e colar token e chat id
kubectl apply -f k8s/openclaw/secret.yaml
```

## 4. OpenClaw (ConfigMap + Deployment)

A imagem padrão no deployment é um placeholder (`node:22-bookworm-slim` com `sleep infinity`). Para o CEO responder de fato no Telegram você precisa:

**Opção A — Imagem OpenClaw oficial (quando disponível):**  
Altere `k8s/openclaw/deployment.yaml` e use a imagem que executa `openclaw gateway`, com entrypoint apontando para `/config/config.yaml`.

**Opção B — Rodar OpenClaw no host (teste rápido):**  
Use a config do ConfigMap localmente e aponte `OLLAMA_HOST` para o serviço no cluster (port-forward):

```bash
kubectl port-forward -n ai-agents svc/ollama-service 11434:11434
export OLLAMA_HOST=http://127.0.0.1:11434
export TELEGRAM_BOT_TOKEN='...'
openclaw gateway
```

Aplicar ConfigMap e Deployment no cluster (mesmo com imagem placeholder, para deixar o fluxo pronto):

```bash
kubectl apply -f k8s/openclaw/configmap.yaml
kubectl apply -f k8s/openclaw/deployment.yaml
```

## 5. Expor o OpenClaw para o Telegram (webhook ou polling)

O OpenClaw precisa receber mensagens do Telegram. Em ambiente local (host), **long polling** funciona sem expor porta. No cluster:

- **Webhook:** Expor o serviço OpenClaw (Ingress ou LoadBalancer) e configurar no OpenClaw `channels.telegram.webhookUrl` + `webhookSecret`.
- **Polling:** Se o gateway rodar em um pod com internet, o polling já é o padrão; garantir que o pod consiga acessar `api.telegram.org`.

Ref: [Telegram — OpenClaw](https://docs.openclaw.ai/channels/telegram).

## 6. Pairing (primeiro acesso do Diretor)

Com `dmPolicy: pairing`:

1. Diretor envia uma mensagem em DM para o bot no Telegram.
2. No host/pod onde o gateway está rodando: `openclaw pairing list telegram`
3. Aprovar: `openclaw pairing approve telegram <CODE>`
4. A partir daí o Diretor pode conversar com o CEO.

## Resumo da arquitetura (Fase 0)

| Componente   | Função                                      |
|-------------|----------------------------------------------|
| **openclaw**| Gateway: canal Telegram → agente CEO → Ollama|
| **ollama-gpu** | Modelo local (ex.: phi3:mini)             |
| **redis**   | Disponível para estado/streams (fase futura) |

Doc de arquitetura: [openclaw-sub-agents-architecture.md](openclaw-sub-agents-architecture.md).
