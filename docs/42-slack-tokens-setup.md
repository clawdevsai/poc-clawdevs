# Slack: onde achar os tokens (OpenClaw — app próprio)

Referência rápida para configurar o canal Slack do **OpenClaw** (Socket Mode). No ClawDevs cada agente tem seu próprio app Slack: o OpenClaw usa **OPENCLAW_SLACK_*** no `.env`; o orquestrador usa **ORCHESTRATOR_SLACK_*** ou o Secret `orchestrator-slack`. Este doc cobre o app do OpenClaw (workspace [clawdevsai](https://clawdevsai.slack.com)). Ver também: [37-deploy-fase0-telegram-ceo-ollama.md](37-deploy-fase0-telegram-ceo-ollama.md) (seção 3.2) e [config/openclaw/README.md](../config/openclaw/README.md).

**Modelo para conversa no Slack:** discussões entre agentes no Slack usam **Ollama (LLM local)**. Para apenas conversa (menor uso de VRAM): use um modelo pequeno — padrão na config local é **`ollama/qwen2.5:3b`**; alternativas: Phi-3 mini, Ministral-3:3b. Detalhes em [config/openclaw/README.md](../config/openclaw/README.md#modelo-menor-para-conversa-apenas-no-slack).

## Onde achar cada um

Tudo é configurado no **Slack API** do seu app:

1. Abra **[api.slack.com/apps](https://api.slack.com/apps)** e escolha o app (ou crie um para o workspace clawdevsai).
2. **Instale o app no workspace** (menu **Install App**), se ainda não instalou — o Bot Token só aparece depois disso.

**Atenção:** Na página **Basic Information**, a seção **"App Credentials"** (App ID, Client ID, Client Secret, Signing Secret) **não** contém os tokens do OpenClaw. Para Socket Mode você precisa dos dois tokens abaixo, que ficam em outras seções.

### Ordem recomendada (após criar o app)

1. **Settings → Socket Mode** — Ative **"Enable Socket Mode"** (toggle verde). A página explica que é preciso um **App Level Token** para estabelecer a conexão WebSocket.
2. **Settings → Basic Information** — Role a página até o fim. Aparece a seção **"App-Level Tokens"**. Clique em **Generate Token and Scopes**, scope **`connections:write`**, copie o token (`xapp-...`) → **OPENCLAW_SLACK_APP_TOKEN** no `.env`.
3. **Settings → Install App** (ou **Features → OAuth & Permissions**) — **Install to Workspace** → autorize no ClawDevsAi → copie o **Bot User OAuth Token** (`xoxb-...`) → **OPENCLAW_SLACK_BOT_TOKEN** no `.env`.

### OPENCLAW_SLACK_BOT_TOKEN (`xoxb-...`)

- Menu **Install App** ou **OAuth & Permissions**.
- Em **OAuth Tokens for Your Workspace** está o **Bot User OAuth Token** (só após instalar o app no workspace).
- Começa com `xoxb-`.
- Esse é o valor de **OPENCLAW_SLACK_BOT_TOKEN** no `.env`.

### OPENCLAW_SLACK_APP_TOKEN (`xapp-...`)

- **Antes:** em **Socket Mode**, ative **Enable Socket Mode**.
- Depois: **Basic Information** → role até **App-Level Tokens** → **Generate Token and Scopes**.
- Crie um token com o scope **`connections:write`**.
- O token começa com `xapp-`.
- Esse é o valor de **OPENCLAW_SLACK_APP_TOKEN** no `.env`.

---

## Diferença entre os dois

| | **OPENCLAW_SLACK_APP_TOKEN** (`xapp-...`) | **OPENCLAW_SLACK_BOT_TOKEN** (`xoxb-...`) |
|---|-----------------------------------|-----------------------------------|
| **Tipo** | App-Level Token | Bot User OAuth Token |
| **Onde** | Basic Information → App-Level Tokens (após ativar Socket Mode) | OAuth & Permissions (após instalar o app no workspace) |
| **Uso no Socket Mode** | Mantém a **conexão WebSocket** com o Slack (entrada de eventos em tempo real). | Usado para **chamar a API** (enviar mensagens, ler canais, etc.). |
| **Scopes** | Só precisa de `connections:write` para Socket Mode. | Vários scopes de bot (ex.: `chat:write`, `channels:read`, `users:read`, etc.) conforme o que o app faz. |

No **Socket Mode**, os dois são obrigatórios: o App Token é quem "liga" o canal (conexão persistente); o Bot Token é quem executa as ações (enviar/ler mensagens, etc.). Por isso a [doc do OpenClaw](https://docs.openclaw.ai/channels/slack) exige os dois quando você usa Socket Mode.

---

## Um app Slack por agente

No ClawDevs **cada agente** (CEO, PO, Developer, DevOps, Architect, QA, CyberSec, UX, DBA) deve ter **seu próprio app** em [api.slack.com/apps](https://api.slack.com/apps) e suas próprias variáveis no `.env`:

- `CEO_SLACK_APP_TOKEN` / `CEO_SLACK_BOT_TOKEN`
- `PO_SLACK_APP_TOKEN` / `PO_SLACK_BOT_TOKEN`
- `DEVELOPER_SLACK_APP_TOKEN` / `DEVELOPER_SLACK_BOT_TOKEN`
- (e assim por diante para DEVOPS, ARCHITECT, QA, CYBERSEC, UX, DBA)

**Nunca reutilize o BOT token de um agente em outro.** Por exemplo: não use `CEO_SLACK_BOT_TOKEN` em `DEVELOPER_SLACK_BOT_TOKEN`. Se fizer isso, as respostas no Slack aparecerão como outro app (ex.: CEO) ou as menções serão tratadas pelo agente errado — cada um precisa conversar com você com sua própria personalidade (SOUL). O gateway OpenClaw usa um *account* por agente; cada account exige o par APP_TOKEN + BOT_TOKEN do **mesmo** app desse agente.

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
2. No app criado: **Socket Mode** → Enable → **Basic Information → App-Level Tokens** → Generate com scope `connections:write` → copiar **OPENCLAW_SLACK_APP_TOKEN** (`xapp-...`) no `.env`.
3. **OAuth & Permissions** → **Install to Workspace** (se ainda não instalou) → copiar **Bot User OAuth Token** → **OPENCLAW_SLACK_BOT_TOKEN** (`xoxb-...`) no `.env`.
4. **Event Subscriptions** (ou Subscribe to bot events): ativar por exemplo `app_mention`, `message.im`, `message.channels`, conforme [OpenClaw — Slack](https://docs.openclaw.ai/channels/slack).

### Depois de criar o app (tela "Review summary & create your app")

Na última etapa (Step 3 of 3) você vê o resumo: nome do app (ex.: ClawdevsAI), aba **OAuth** com os Bot Scopes (chat:write, channels:history, etc.). Clique em **Create** para finalizar.

Em seguida, siga a [Ordem recomendada](#ordem-recomendada-após-criar-o-app) acima: **Socket Mode** → **Basic Information** (App-Level Tokens) → **Install App**. Coloque os dois tokens no `.env` ou no Secret do Kubernetes conforme a seção [Uso no projeto](#uso-no-projeto) abaixo.

---

## Uso no projeto (OpenClaw)

- Coloque os valores no **`.env`** na raiz do repositório (nunca commitar), com prefixo **OPENCLAW_** (cada agente tem seu próprio app):
  - `OPENCLAW_SLACK_APP_TOKEN=xapp-...`
  - `OPENCLAW_SLACK_BOT_TOKEN=xoxb-...`
  - Opcional: `OPENCLAW_SLACK_DIRECTOR_USER_ID=U01234ABCD` (ID do Diretor no Slack para allowlist em DMs; ver abaixo onde achar).
- O script `./scripts/k8s-openclaw-secret-from-env.sh` lê OPENCLAW_SLACK_* (ou SLACK_* em fallback) e grava no **Secret** `openclaw-telegram` com chaves `SLACK_APP_TOKEN`, `SLACK_BOT_TOKEN`, `SLACK_DIRECTOR_USER_ID` para o gateway no cluster.

### Onde achar OPENCLAW_SLACK_DIRECTOR_USER_ID

Esse valor **não** fica em api.slack.com/apps (Basic Information, App Credentials ou App-Level Tokens). É o **ID do usuário Slack** da pessoa que é o Diretor/CEO no workspace (formato `U01234ABCD`). Use no `.env`: `OPENCLAW_SLACK_DIRECTOR_USER_ID=U...`.

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

---

## Pod em crash / `account_inactive` (CEO e PO não respondem)

Se o pod do OpenClaw no Minikube fica em **Error** (Back-off restarting) e os logs mostram:

```text
[slack] [default] starting provider
Unhandled promise rejection: Error: An API error occurred: account_inactive
```

a conexão Slack do **provider default** está com token inválido ou app inativo. O gateway usa primeiro o app **OpenClaw** (variáveis `OPENCLAW_SLACK_APP_TOKEN` e `OPENCLAW_SLACK_BOT_TOKEN`). Se esse app estiver desinstalado, revogado ou com token antigo, o Slack devolve `account_inactive` e o processo cai — por isso CEO e PO deixam de responder (o pod nem fica pronto).

**O que fazer:**

1. **Verificar o app OpenClaw no Slack**  
   Acesse [api.slack.com/apps](https://api.slack.com/apps) e abra o app usado como gateway (o que gerou os tokens em `OPENCLAW_SLACK_*`).

2. **Reinstalar o app no workspace**  
   Em **Install App** (ou **OAuth & Permissions**), use **Reinstall to Workspace** se o app tiver sido desinstalado ou os tokens revogados.

3. **Renovar os tokens**  
   - **App-Level Token:** Basic Information → App-Level Tokens → gerar novo com scope `connections:write` → atualizar **OPENCLAW_SLACK_APP_TOKEN** no `.env`.  
   - **Bot Token:** OAuth & Permissions → (Re)Install to Workspace → copiar **Bot User OAuth Token** → atualizar **OPENCLAW_SLACK_BOT_TOKEN** no `.env**.

4. **Atualizar o Secret e reiniciar o deployment**  
   ```bash
   ./scripts/k8s-openclaw-secret-from-env.sh
   kubectl rollout restart deployment/openclaw -n ai-agents
   ```

5. **Conferir se o pod sobe**  
   ```bash
   kubectl get pods -n ai-agents -l app=openclaw
   kubectl logs -n ai-agents deployment/openclaw --tail=50
   ```  
   Quando o **default** Slack conectar sem `account_inactive`, o pod fica **Running** e os agentes (CEO, PO, etc.) voltam a poder responder. Se você usa um app por agente (CEO_SLACK_*, PO_SLACK_*), confira também em api.slack.com que cada app está instalado e com tokens válidos no `.env`.

---

## Logs: `channel resolve failed` / `user resolve failed` (missing_scope)

Se nos logs do gateway aparecer `[slack] channel resolve failed; using config entries. Error: An API error occurred: missing_scope` (ou `user resolve failed`), o app **ClawdevsAI** (CEO) está sem scopes necessários. No **[api.slack.com/apps](https://api.slack.com/apps)** → app ClawdevsAI → **OAuth & Permissions** → **Scopes** (Bot Token Scopes), adicione:

- **`channels:read`** — para resolver nomes/IDs de canais
- **`users:read`** — para resolver nomes/IDs de usuários

Depois clique em **Reinstall to Workspace** para aplicar. O Socket Mode continua funcionando; esses scopes evitam os erros de resolução nos logs.
