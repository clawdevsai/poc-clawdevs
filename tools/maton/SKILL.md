# 🔌 maton — API Gateway para serviços externos

**Objetivo:** Integrar o enxame a 100+ APIs externas (Google Workspace, Slack, Notion, HubSpot, Stripe, etc.) via gateway Maton com OAuth gerenciado.  
**Quando usar:** Quando um agente precisar ler ou escrever dados em serviços de terceiros homologados.  
**Referência:** `docs/25-api-gateway-integracao-apis.md`

---

## ⚠️ Segurança Zero Trust

- **MATON_API_KEY:** Deve ser armazenada em Secret K8s (`clawdevs-secrets`). **NUNCA** expor em logs, chat ou código.
- **Escopo Mínimo:** Ao autorizar uma conexão OAuth via Maton, selecione apenas os escopos estritamente necessários para a tarefa.
- **Aprovação:** O DevOps configura a conexão após aprovação do Diretor. Agentes não criam novas conexões OAuth sozinhos.

---

## Pré-requisitos

```bash
# Verificar se a chave está configurada no ambiente do pod
echo $MATON_API_KEY

# Base URL do Gateway
# https://api.maton.ai/v1
```

---

## Passos para uso

### 1. Listar conexões autorizadas

```bash
# Exemplo de chamada via curl (o agente usa httpx/requests internamente)
curl -H "Authorization: Bearer $MATON_API_KEY" \
     https://api.maton.ai/v1/connections
```

### 2. Integrar com Google Workspace (exemplo CEO/PO)

```python
import requests
import os

MATON_KEY = os.getenv("MATON_API_KEY")

def list_google_drive_files(connection_id: str):
    url = f"https://api.maton.ai/v1/services/google_drive/proxy/v3/files?connection_id={connection_id}"
    resp = requests.get(url, headers={"Authorization": f"Bearer {MATON_KEY}"})
    return resp.json()
```

### 3. Integrar com Slack (exemplo DevOps)

```python
def send_slack_notification(connection_id: str, channel: str, text: str):
    url = f"https://api.maton.ai/v1/services/slack/proxy/chat.postMessage?connection_id={connection_id}"
    payload = {"channel": channel, "text": text}
    resp = requests.post(url, json=payload, headers={"Authorization": f"Bearer {MATON_KEY}"})
    return resp.json()
```

---

## Serviços suportados (exemplos)

| Categoria | Apps |
|-----------|------|
| **Produtividade** | Google Drive, Calendar, Notion, Trello, Asana |
| **Comunicação** | Slack, Discord, Microsoft Teams, Telegram |
| **CRM/Vendas** | HubSpot, Salesforce, Pipedrive |
| **Financeiro** | Stripe, PayPal, QuickBooks |
| **Marketing** | Mailchimp, Typeform, SendGrid |

---

## Uso por agente

| Agente | Caso de uso principal |
|--------|----------------------|
| **CEO** | Ler relatórios financeiros (Stripe), agendar reuniões (Calendar) |
| **PO** | Sincronizar backlog com Jira/Notion/Trello |
| **Developer** | Implementar webhooks e integrações de API solicitadas |
| **DevOps** | Enviar alertas para Slack/Discord, gerenciar usuários Google |
| **UX** | Extrair feedbacks de Typeform/HubSpot |

---

## Boas práticas

- Use o **Maton Proxy** para evitar lidar com tokens OAuth complexos e renovações (o Maton faz o refresh automaticamente).
- Sempre verifique se a `connection_id` está ativa antes de tentar operar.
- Documente novas integrações em `memory/warm/TOOLS.md`.
- Em caso de erro de autenticação, o DevOps deve ser acionado para re-autorizar o OAuth no dashboard do Maton.
