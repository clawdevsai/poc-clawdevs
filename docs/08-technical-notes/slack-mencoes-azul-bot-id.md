# Por que @PO não fica azul no Slack (e como corrigir)

No Slack, quando o **CEO** (ou outro agente) escreve apenas **@PO** no texto, a mensagem é enviada como **texto simples**. O Slack **não** converte isso em menção: não fica azul e o app do PO **não** recebe o evento `app_mention`.

Para a menção ficar **azul** e **notificar** o outro app, a mensagem precisa usar o **formato do Slack**: `<@BOT_USER_ID>`.

---

## Resumo em 3 passos (para menção funcionar entre bots)

1. **Pegar o Bot User ID** de cada app no Slack: [api.slack.com/apps](https://api.slack.com/apps) → App → **OAuth & Permissions** ou **Install App** → anotar o **Bot User ID** (ex.: `U0ABC1234`).
2. **Substituir nos ConfigMaps** os placeholders pela menção real: onde está `<@ID_DO_BOT_PO>` usar `<@U0ABC1234>` (o ID do bot do PO). Fazer isso em todos os workspace configmaps que têm a tabela (CEO, PO, Architect, Developer).
3. **Aplicar e reiniciar**: `kubectl apply -f k8s/management-team/openclaw/workspace-*-configmap.yaml -n ai-agents` e `kubectl rollout restart deployment/openclaw -n ai-agents`.

Depois disso, quando o CEO (ou qualquer agente) escrever `<@U0ABC1234>` na mensagem, o Slack exibirá a menção em azul e o bot do PO será notificado.

---

## Formato correto

| Errado (só texto) | Certo (menção real) |
|-------------------|----------------------|
| `@PO`             | `<@U01234ABCD>`      |
| `@CEO`            | `<@U05678EFGH>`      |

Onde `U01234ABCD` é o **Bot User ID** do app no Slack (cada app tem um ID único).

---

## Onde achar o Bot User ID de cada app

1. Abra **[api.slack.com/apps](https://api.slack.com/apps)** e escolha o app (ex.: app do PO).
2. Vá em **OAuth & Permissions** (ou **Install App**).
3. Na seção **Bot User** (ou ao instalar no workspace), o **User ID** do bot aparece (formato `U0XXXXXX` ou similar).
4. Alternativa: no Slack, clique com o botão direito no nome do bot no canal → **Copy link** → o link contém o ID (ex.: `.../team/T123/user/U0XXXXXX`).

Anote o ID de cada app (CEO, PO, Architect, CyberSec, Developer, DevOps, QA, UX, DBA).

---

## O que fazer no ClawDevs

Cada agente precisa **saber o ID do bot** dos outros para montar a menção. Duas formas:

### Opção A: Colocar os IDs no ConfigMap do CEO (e dos outros agentes)

1. Obtenha o **Bot User ID** de cada app em [api.slack.com/apps](https://api.slack.com/apps) → App → **OAuth & Permissions** ou **Install App** → **Bot User** (ID no formato `U0XXXXXX`).
2. Edite `k8s/management-team/openclaw/workspace-ceo-configmap.yaml`: na seção **Apelidos no Slack**, substitua os placeholders pelo ID real. Ex.: onde está `<@ID_DO_BOT_PO>` coloque `<@U01234ABCD>` (o ID real do bot do PO).
3. Aplique e reinicie o OpenClaw:
   ```bash
   kubectl apply -f k8s/management-team/openclaw/workspace-ceo-configmap.yaml -n ai-agents
   kubectl rollout restart deployment/openclaw -n ai-agents
   ```
4. O CEO passará a “ver” na tabela o formato correto (ex.: `<@U01234ABCD>` para o PO) e usará isso na mensagem — a menção ficará azul e o PO será notificado.

Repita para os outros agentes que precisam mencionar (PO, Architect, etc.): edite o workspace ou soul correspondente com a mesma tabela preenchida com os IDs reais.

### Opção B: ConfigMap com mapeamento (se o gateway suportar)

Se o OpenClaw (ou um script no cluster) tiver suporte a substituir `@PO` por `<@ID>` **antes** de enviar a mensagem ao Slack, basta configurar um mapeamento `po → U0XXXXXX`. Hoje isso não existe no projeto; seria uma extensão do gateway ou do adapter Slack.

---

## Por que o UX “conseguiu”

O app **UX** pode ter conseguido menção azul por um destes motivos:

1. O modelo do UX gerou por acaso o formato `<@U0XXXXXX>` (se em algum contexto recebeu o ID do PO).
2. O usuário ou outro bot já tinha mencionado o PO na thread e o Slack exibiu o link.
3. Diferença de como cada app envia a mensagem (ex.: um via API com blocos, outro como texto puro).

A solução consistente é **todos os agentes** usarem o formato `<@BOT_USER_ID>` quando quiserem mencionar outro agente no Slack.

---

## Resumo

- **Problema:** `@PO` em texto puro não vira menção no Slack.
- **Solução:** Usar `<@BOT_USER_ID>` (ID real do bot do PO no Slack).
- **Ação:** Obter o Bot User ID de cada app em api.slack.com e colocar na tabela de menções no AGENTS.md (ou equivalente) de cada agente, no formato `<@U0XXXXXX>`.

Referência Slack: [Sending messages](https://api.slack.com/messaging/sending) — menções usam `<@USER_ID>`.
