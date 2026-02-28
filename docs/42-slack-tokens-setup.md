# Slack: onde achar SLACK_BOT_TOKEN e SLACK_APP_TOKEN

Referência rápida para configurar o canal Slack do OpenClaw (Socket Mode). Usado no ClawDevs para que todos os agentes conversem no workspace [clawdevsai](https://clawdevsai.slack.com). Ver também: [37-deploy-fase0-telegram-ceo-ollama.md](37-deploy-fase0-telegram-ceo-ollama.md) (seção 3.1) e [config/openclaw/README.md](../config/openclaw/README.md).

**Modelo para conversa no Slack:** discussões entre agentes no Slack usam **Ollama (LLM local)**. Para apenas conversa (menor uso de VRAM): use um modelo pequeno — padrão na config local é **`ollama/qwen2.5:3b`**; alternativas: Phi-3 mini, Ministral-3:3b. Detalhes em [config/openclaw/README.md](../config/openclaw/README.md#modelo-menor-para-conversa-apenas-no-slack).

## Onde achar cada um

Tudo é configurado no **Slack API** do seu app:

1. Abra **[api.slack.com/apps](https://api.slack.com/apps)** e escolha o app (ou crie um para o workspace clawdevsai).
2. **Instale o app no workspace** (menu **Install App**), se ainda não instalou — o Bot Token só aparece depois disso.

**Atenção:** Na página **Basic Information**, a seção **"App Credentials"** (App ID, Client ID, Client Secret, Signing Secret) **não** contém os tokens do OpenClaw. Para Socket Mode você precisa dos dois tokens abaixo, que ficam em outras seções.

### Ordem recomendada (após criar o app)

1. **Settings → Socket Mode** — Ative **"Enable Socket Mode"** (toggle verde). A página explica que é preciso um **App Level Token** para estabelecer a conexão WebSocket.
2. **Settings → Basic Information** — Role a página até o fim. Aparece a seção **"App-Level Tokens"**. Clique em **Generate Token and Scopes**, scope **`connections:write`**, copie o token (`xapp-...`) → **SLACK_APP_TOKEN**.
3. **Settings → Install App** (ou **Features → OAuth & Permissions**) — **Install to Workspace** → autorize no ClawDevsAi → copie o **Bot User OAuth Token** (`xoxb-...`) → **SLACK_BOT_TOKEN**.

### SLACK_BOT_TOKEN (`xoxb-...`)

- Menu **Install App** ou **OAuth & Permissions**.
- Em **OAuth Tokens for Your Workspace** está o **Bot User OAuth Token** (só após instalar o app no workspace).
- Começa com `xoxb-`.
- Esse é o valor de **SLACK_BOT_TOKEN**.

### SLACK_APP_TOKEN (`xapp-...`)

- **Antes:** em **Socket Mode**, ative **Enable Socket Mode**.
- Depois: **Basic Information** → role até **App-Level Tokens** → **Generate Token and Scopes**.
- Crie um token com o scope **`connections:write`**.
- O token começa com `xapp-`.
- Esse é o valor de **SLACK_APP_TOKEN**.

---

## Diferença entre os dois

| | **SLACK_APP_TOKEN** (`xapp-...`) | **SLACK_BOT_TOKEN** (`xoxb-...`) |
|---|-----------------------------------|-----------------------------------|
| **Tipo** | App-Level Token | Bot User OAuth Token |
| **Onde** | Basic Information → App-Level Tokens (após ativar Socket Mode) | OAuth & Permissions (após instalar o app no workspace) |
| **Uso no Socket Mode** | Mantém a **conexão WebSocket** com o Slack (entrada de eventos em tempo real). | Usado para **chamar a API** (enviar mensagens, ler canais, etc.). |
| **Scopes** | Só precisa de `connections:write` para Socket Mode. | Vários scopes de bot (ex.: `chat:write`, `channels:read`, `users:read`, etc.) conforme o que o app faz. |

No **Socket Mode**, os dois são obrigatórios: o App Token é quem "liga" o canal (conexão persistente); o Bot Token é quem executa as ações (enviar/ler mensagens, etc.). Por isso a [doc do OpenClaw](https://docs.openclaw.ai/channels/slack) exige os dois quando você usa Socket Mode.

---

## Como criar o app no Slack (api.slack.com/apps)

Em **[Your Apps](https://api.slack.com/apps)** clique em **"Create an App"**. Você pode criar **"From a manifest"** (YAML abaixo) ou **"From scratch"** (configurar tudo na UI).

### Opção A: From a manifest (YAML)

Cole o manifest abaixo na aba **YAML**. Use indentação exata (2 espaços); se aparecer "We can't translate a manifest with errors", confira que não há espaços a mais/menos e que as chaves estão alinhadas.

```yaml
display_information:
  name: ClawdevsAI
  description: Bot OpenClaw para o workspace ClawDevs
features:
  bot_user:
    display_name: ClawdevsAI
    always_online: false
  app_home:
    messages_tab_enabled: true
    messages_tab_read_only_enabled: false
oauth_config:
  scopes:
    bot:
      - chat:write
      - channels:history
      - channels:read
      - im:history
      - users:read
      - app_mentions:read
      - reactions:read
      - reactions:write
      - files:read
      - files:write
settings:
  socket_mode_enabled: true
  event_subscriptions:
    bot_events:
      - app_mention
      - message.channels
      - message.im
      - reaction_added
      - reaction_removed
```

Avance (Next), escolha o workspace **ClawDevsAi** e crie o app. Depois: **Install App** (Bot Token) e **Basic Information → App-Level Tokens** (App Token com `connections:write`).

### Opção B: From scratch

1. **Create an App** → **From scratch** → nome (ex.: ClawdevsAI) e workspace **ClawDevsAi**.
2. No app criado: **Socket Mode** → Enable → **Basic Information → App-Level Tokens** → Generate com scope `connections:write` → copiar **SLACK_APP_TOKEN** (`xapp-...`).
3. **OAuth & Permissions** → **Install to Workspace** (se ainda não instalou) → copiar **Bot User OAuth Token** → **SLACK_BOT_TOKEN** (`xoxb-...`).
4. **Event Subscriptions** (ou Subscribe to bot events): ativar por exemplo `app_mention`, `message.im`, `message.channels`, conforme [OpenClaw — Slack](https://docs.openclaw.ai/channels/slack).

### Depois de criar o app (tela "Review summary & create your app")

Na última etapa (Step 3 of 3) você vê o resumo: nome do app (ex.: ClawdevsAI), aba **OAuth** com os Bot Scopes (chat:write, channels:history, etc.). Clique em **Create** para finalizar.

Em seguida, siga a [Ordem recomendada](#ordem-recomendada-após-criar-o-app) acima: **Socket Mode** → **Basic Information** (App-Level Tokens) → **Install App**. Coloque os dois tokens no `.env` ou no Secret do Kubernetes conforme a seção [Uso no projeto](#uso-no-projeto) abaixo.

---

## Uso no projeto

- Coloque os valores no **`.env`** na raiz do repositório (nunca commitar):
  - `SLACK_APP_TOKEN=xapp-...`
  - `SLACK_BOT_TOKEN=xoxb-...`
  - Opcional: `SLACK_DIRECTOR_USER_ID=U01234ABCD` (ID do Diretor no Slack para allowlist em DMs; ver abaixo onde achar).
- Ou use o **Secret** no Kubernetes (`openclaw-telegram` com chaves `SLACK_APP_TOKEN`, `SLACK_BOT_TOKEN`, `SLACK_DIRECTOR_USER_ID`) quando o OpenClaw rodar no cluster.

### Onde achar SLACK_DIRECTOR_USER_ID

Esse valor **não** fica em api.slack.com/apps (Basic Information, App Credentials ou App-Level Tokens). É o **ID do usuário Slack** da pessoa que é o Diretor/CEO no workspace (formato `U01234ABCD`). Use no `.env`: `SLACK_DIRECTOR_USER_ID=U...`.

**Qual ID usar:** o da pessoa que é o Diretor/CEO na sua organização. Em geral é o **Primary Workspace Owner** (dono do workspace). No workspace ClawDevsAi pode usar o do **clawdevsai** (dono) como Diretor; os outros membros aparecem como "Invited Member".

#### Opção 1: Pela administração do workspace

1. Acesse **[clawdevsai.slack.com/admin](https://clawdevsai.slack.com/admin)** (ou no Slack: **Admin Tools** → **Manage members**).
2. Em **People** → **Members**, a tabela lista todos os membros com a coluna **Member ID**.
3. Identifique o Diretor (ex.: Primary Workspace Owner) e copie o **Member ID** da linha (ex.: `UGAHL10QK7D`).

#### Opção 2: Pelo perfil no Slack (app ou web)

1. Clique no **nome ou na foto** do Diretor (em um canal ou na lista de membros).
2. No perfil que abrir, clique nos **três pontinhos (⋯)** ou em **More**.
3. Escolha **Copy member ID** (ou "Copiar ID do membro").

Alternativa: no link do perfil do usuário (ex.: `.../user/U01234ABCD`), o trecho que começa com `U` é o user ID.
