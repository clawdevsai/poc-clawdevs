# Deploy Fase 0: CEO via Telegram + Ollama no Kubernetes

Entrega mínima: **Diretor fala com o CEO no Telegram**; CEO usa **um único modelo local (Ollama)** no cluster. OpenClaw com sub-agents fica pronto para expandir (PO, Developer, etc.) depois.

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

## 4. OpenClaw (ConfigMap + Workspace CEO + Deployment)

O agente CEO obedece ao **perfil SOUL** ([docs/soul/CEO.md](soul/CEO.md)): o ConfigMap `openclaw-workspace-ceo` fornece `SOUL.md` no workspace; o OpenClaw injeta esse conteúdo no system prompt. Assim o CEO responde em tom executivo e direto, na **mesma língua** que o Diretor usar, e segue as restrições (nunca escrever código, nunca aprovar PRs, etc.). Aplicar também o workspace do CEO:

```bash
kubectl apply -f k8s/openclaw/workspace-ceo-configmap.yaml
```

A imagem padrão no deployment é um placeholder (`node:22-bookworm-slim` com `sleep infinity`). Para o CEO responder de fato no Telegram você precisa:

**Opção A — Imagem OpenClaw oficial (quando disponível):**  
Altere `k8s/openclaw/deployment.yaml` e use a imagem que executa `openclaw gateway`, com entrypoint apontando para `/config/config.yaml`.

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
kubectl apply -f k8s/openclaw/configmap.yaml
kubectl apply -f k8s/openclaw/workspace-ceo-configmap.yaml
kubectl apply -f k8s/openclaw/deployment.yaml
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

## Resumo da arquitetura (Fase 0)

| Componente   | Função                                      |
|-------------|----------------------------------------------|
| **openclaw**| Gateway: canal Telegram → agente CEO → Ollama|
| **ollama-gpu** | Modelo local (ex.: stewyphoenix19/phi3-mini_v1:latest, ministral-3:3b) |
| **redis**   | Disponível para estado/streams (fase futura) |
| **openclaw-workspace-ceo** | SOUL.md no workspace → CEO segue perfil [soul/CEO.md](soul/CEO.md) |

Doc de arquitetura: [openclaw-sub-agents-architecture.md](openclaw-sub-agents-architecture.md).

---

## Otimização de latência (Telegram)

Para **reduzir o tempo de resposta** no chat do Telegram sem aumentar hardware:

- **Modelo do CEO:** O CEO está configurado para usar **stewyphoenix19/phi3-mini_v1:latest** (modelo mais leve) com `contextWindow: 4096` e `maxTokens: 1024` no OpenClaw — respostas curtas e objetivas saem mais rápido. Ver `k8s/openclaw/configmap.yaml` e `config/openclaw/openclaw.local.json5`.
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
