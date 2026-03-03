# url-sandbox-cron — Cloudflare Worker (Cron)

Worker que dispara o Job **url-sandbox** no cluster em horário agendado (Cron). O Worker faz `POST /trigger` no serviço **url-sandbox-trigger** exposto no cluster (via Cloudflare Tunnel).

## Pré-requisitos

1. **Cluster** com o trigger no ar: `make url-sandbox-trigger-apply` (RBAC + Deployment + Service).
2. **Cloudflare Tunnel** encaminhando um hostname (ex. `url-sandbox-trigger.seudominio.com`) para o Service `url-sandbox-trigger:8080` no namespace `ai-agents`.
3. **Conta Cloudflare** e Wrangler instalado (`npm i -g wrangler`).

## Configuração

### 1. No cluster

```bash
# Aplicar o serviço de trigger (RBAC + Deployment + Service)
make url-sandbox-trigger-apply

# Opcional: autenticar POST /trigger com um token
kubectl create secret generic url-sandbox-trigger-secret -n ai-agents \
  --from-literal=TRIGGER_SECRET='seu-token-seguro'
```

### 2. Cloudflare Tunnel

Exponha o Service `url-sandbox-trigger` (porta 8080). Exemplo com `cloudflared`:

- No cluster: use Ingress ou um tunnel sidecar que encaminha para `url-sandbox-trigger.ai-agents.svc.cluster.local:8080`.
- Ou tunnel local: `cloudflared tunnel --url http://localhost:8080` e configure um hostname no dashboard para esse tunnel.

O Worker vai chamar `https://<seu-hostname>/trigger`.

### 3. Secrets do Worker

Defina os secrets (não commitar):

```bash
cd cloudflare/url-sandbox-cron

# URL base do trigger (sem /trigger no final)
wrangler secret put TRIGGER_ENDPOINT
# Ex.: https://url-sandbox-trigger.seudominio.com

# URL que o Job url-sandbox vai buscar (agendada)
wrangler secret put URL_SANDBOX_TARGET
# Ex.: https://exemplo.com

# Mesmo valor que TRIGGER_SECRET no Secret do cluster (opcional)
wrangler secret put TRIGGER_SECRET
```

### 4. Deploy do Worker

```bash
cd cloudflare/url-sandbox-cron
wrangler deploy
```

O Cron está definido em `wrangler.toml`: `0 18 * * *` (diário às 18:00 UTC). Para alterar, edite `[triggers] crons` e rode `wrangler deploy` de novo.

## Testar

- **Trigger manual (curl):**  
  `curl -X POST https://<TRIGGER_ENDPOINT>/trigger -H "Content-Type: application/json" -d '{"url":"https://exemplo.com"}'`  
  (adicione `-H "Authorization: Bearer <TRIGGER_SECRET>"` se configurou o Secret no cluster.)

- **Health do trigger:**  
  `curl https://<TRIGGER_ENDPOINT>/health`

- **Cron local (Wrangler):**  
  `wrangler dev` e em outro terminal:  
  `curl "http://localhost:8787/cdn-cgi/handler/scheduled?cron=*+*+*+*+*"`

## Alterar a URL agendada

A URL que o Job busca vem do secret `URL_SANDBOX_TARGET`. Para mudar sem redeploy do Worker:

1. `wrangler secret put URL_SANDBOX_TARGET` e informe a nova URL; ou  
2. Use Cloudflare KV: bind do Worker a um namespace KV, leia a URL de uma chave no `scheduled` e configure no dashboard.

## Referências

- Trigger no cluster: [k8s/security/url-sandbox-trigger-deployment.yaml](../../k8s/security/url-sandbox-trigger-deployment.yaml), [scripts/url_sandbox_trigger.py](../../scripts/url_sandbox_trigger.py)
- Job url-sandbox: [k8s/security/job-url-sandbox.yaml](../../k8s/security/job-url-sandbox.yaml)
- [Cloudflare Cron Triggers](https://developers.cloudflare.com/workers/configuration/cron-triggers/)
