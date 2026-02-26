# API Gateway — Integração com APIs externas

Os agentes do enxame podem **conectar a mais de 100 APIs de terceiros** (Google Workspace, Microsoft 365, Notion, Slack, Airtable, HubSpot, Stripe, etc.) por meio de um **gateway com OAuth gerenciado** (Maton). O gateway atua como proxy: o agente envia requisições para o gateway com a chave Maton; o gateway injeta o token OAuth do serviço alvo e repassa a chamada à API nativa. Cada serviço exige **autorização OAuth explícita do usuário** (fluxo de conexão no Maton); a chave `MATON_API_KEY` **não** concede acesso a terceiros por si só.

**Quando usar:** Quando o Diretor ou o time precisar integrar o projeto com serviços externos (Slack, Google Sheets, Notion, CRM, e-mail, pagamentos, etc.) e uma conexão OAuth já tiver sido autorizada no Maton.

**Segurança:** Alinhado à **postura Zero Trust** ([05-seguranca-e-etica.md](05-seguranca-e-etica.md)): não criar ou usar conexões sem aprovação; não expor `MATON_API_KEY` em código, logs ou respostas; validar URLs e payloads conforme [14-seguranca-runtime-agentes.md](14-seguranca-runtime-agentes.md).

---

## Visão geral

| Aspecto | Descrição |
|--------|-----------|
| **Provedor** | [Maton](https://maton.ai) — gateway e gestão de conexões OAuth. |
| **Base URL das APIs** | `https://gateway.maton.ai/{app}/{native-api-path}` |
| **Gestão de conexões** | `https://ctrl.maton.ai` (listar, criar, obter, excluir conexões). |
| **Autenticação** | Header `Authorization: Bearer $MATON_API_KEY`. |
| **Variável de ambiente** | `MATON_API_KEY` — obrigatória para uso do gateway. |

**Regra importante:** O path da URL **deve** começar com o nome do app da conexão (ex.: `/google-mail/...`, `/slack/...`). Esse prefixo define qual conexão OAuth o gateway usa.

---

## Autenticação

Todas as requisições ao gateway exigem o header:

```
Authorization: Bearer $MATON_API_KEY
```

A chave é usada apenas para autenticar no Maton. O acesso a cada serviço (Gmail, Slack, etc.) depende de **conexões OAuth** criadas e autorizadas pelo usuário no Maton; o gateway injeta o token correspondente na chamada à API nativa.

---

## Gestão de conexões (ctrl.maton.ai)

- **Listar:** `GET https://ctrl.maton.ai/connections?app={app}&status=ACTIVE`
- **Criar:** `POST https://ctrl.maton.ai/connections` — body `{"app": "slack"}`; a resposta traz uma URL para o usuário completar OAuth no browser.
- **Obter:** `GET https://ctrl.maton.ai/connections/{connection_id}`
- **Excluir:** `DELETE https://ctrl.maton.ai/connections/{connection_id}`

Se houver múltiplas conexões para o mesmo app, usar o header `Maton-Connection: {connection_id}` na requisição ao gateway; caso contrário, o gateway usa a conexão ativa padrão (mais antiga).

---

## Serviços suportados (resumo)

O gateway faz proxy para as APIs nativas dos serviços abaixo. O **app name** é o segmento usado em `https://gateway.maton.ai/{app}/...`.

| Categoria | Exemplos de app name |
|-----------|----------------------|
| **Google** | `google-mail`, `google-calendar`, `google-drive`, `google-sheets`, `google-docs`, `google-ads`, `google-analytics-admin`, `google-analytics-data`, `google-bigquery`, `google-contacts`, `google-forms`, `google-meet`, `google-merchant`, `google-play`, `google-search-console`, `google-slides`, `google-tasks`, `google-classroom`, `google-workspace-admin`, `youtube` |
| **Microsoft** | `microsoft-excel`, `microsoft-teams`, `microsoft-to-do`, `outlook`, `one-drive` |
| **Produtividade / Colab** | `notion`, `slack`, `confluence`, `jira`, `asana`, `monday`, `linear`, `clickup`, `trello`, `basecamp`, `coda`, `airtable` |
| **CRM / Vendas** | `hubspot`, `salesforce`, `pipedrive`, `attio`, `zoho-crm`, `zoho-bigin`, `apollo` |
| **E-mail / Marketing** | `mailchimp`, `brevo`, `klaviyo`, `sendgrid`, `mailgun`, `getresponse`, `mailerlite`, `constant-contact`, `active-campaign`, `instantly`, `lemlist`, `manychat` |
| **Pagamentos / Commerce** | `stripe`, `squareup`, `chargebee`, `gumroad`, `woocommerce`, `quickbooks`, `xero`, `zoho-books`, `zoho-inventory` |
| **Agendamento / Eventos** | `calendly`, `cal-com`, `acuity-scheduling`, `eventbrite`, `zoho-bookings` |
| **Comunicação** | `twilio`, `telegram`, `whatsapp-business`, `quo` |
| **Armazenamento / Arquivos** | `dropbox`, `dropbox-business`, `box`, `pdf-co`, `signnow` |
| **Outros** | `github`, `firebase`, `netlify`, `wordpress`, `typeform`, `tally`, `jotform`, `cognito-forms`, `elevenlabs`, `vimeo`, `sentry`, `posthog`, `clockify`, `toggl-track`, `todoist`, `ticktick`, `motion`, `fireflies`, `fathom`, `granola`, `clickfunnels`, `systeme`, `keap`, `kit`, `clio`, `jobber`, `companycam`, `callrail`, `snapchat`, e dezenas de outros |

Para paths e payloads exatos, consultar a documentação oficial de cada API; o gateway repassa path, query params, body e headers (exceto Host e Authorization) para a API nativa. Métodos suportados: GET, POST, PUT, PATCH, DELETE.

---

## Exemplos de uso

### Slack — enviar mensagem

```bash
# POST https://gateway.maton.ai/slack/api/chat.postMessage
# Body: {"channel": "C0123456", "text": "Hello!"}
curl -s -X POST "https://gateway.maton.ai/slack/api/chat.postMessage" \
  -H "Authorization: Bearer $MATON_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"channel":"C0123456","text":"Hello!"}'
```

### HubSpot — criar contato

```bash
# POST https://gateway.maton.ai/hubspot/crm/v3/objects/contacts
curl -s -X POST "https://gateway.maton.ai/hubspot/crm/v3/objects/contacts" \
  -H "Authorization: Bearer $MATON_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"properties":{"email":"john@example.com","firstname":"John","lastname":"Doe"}}'
```

### Google Sheets — ler valores

```bash
# GET https://gateway.maton.ai/google-sheets/v4/spreadsheets/{id}/values/{range}
curl -s "https://gateway.maton.ai/google-sheets/v4/spreadsheets/SPREADSHEET_ID/values/Sheet1!A1:B2" \
  -H "Authorization: Bearer $MATON_API_KEY"
```

### Listar conexões ativas

```bash
curl -s "https://ctrl.maton.ai/connections?status=ACTIVE" \
  -H "Authorization: Bearer $MATON_API_KEY"
```

---

## Quem usa no enxame

| Agente | Uso típico |
|--------|------------|
| **CEO** | Pesquisa e integração com fontes externas (quando aprovado). |
| **PO** | Sincronizar backlog com Jira, Linear, Asana, Notion; notificações em Slack. |
| **Developer** | Implementar integrações (Slack, Notion, Google Sheets, Stripe, etc.) usando o gateway após aprovação. |
| **DevOps** | Configurar variável `MATON_API_KEY` no ambiente; não expor em repositórios. |
| **CyberSec** | Validar que uso do gateway segue Zero Trust; auditar que nenhuma chave vaza em código ou logs. |

Nenhum agente deve **criar** novas conexões OAuth ou **expor** a chave Maton sem aprovação do Diretor.

---

## Erros comuns e limites

- **400:** Falta conexão ativa para o app solicitado — criar conexão em ctrl.maton.ai e completar OAuth.
- **401:** Chave Maton inválida ou ausente — verificar `MATON_API_KEY`.
- **429:** Limite de taxa (10 req/s por conta); limites da API de destino também se aplicam.
- **4xx/5xx** repassados da API de destino: tratar conforme documentação do serviço.

Token OAuth expirado pode gerar 500; criar nova conexão e, se necessário, remover a antiga.

---

## Obter a API Key

1. Criar conta ou entrar em [maton.ai](https://maton.ai).
2. Em [maton.ai/settings](https://maton.ai/settings), copiar a API Key.
3. Definir no ambiente: `export MATON_API_KEY="sua_chave"` (ou no secrets do cluster, nunca em código).

Este documento consolida a habilidade **API Gateway** para o time de agentes; a instalação da skill no OpenClaw (quando disponível no ecossistema) segue o fluxo de [19-descoberta-instalacao-skills.md](19-descoberta-instalacao-skills.md) e o checklist de [05-seguranca-e-etica.md](05-seguranca-e-etica.md).
