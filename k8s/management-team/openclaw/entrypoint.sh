#!/bin/sh
# Entrypoint OpenClaw Gateway — injeta tokens de Telegram e Slack na config.
# Telegram: só CEO; Slack: multi-account (1 app por agente, socket mode).
# Ref: https://docs.openclaw.ai/channels/slack (Quick setup + Token model)
set -e
CONFIG_SRC="/config/openclaw.json"
CONFIG_RUN="/tmp/openclaw.json"

# --- Telegram ---
# Replaces __TELEGRAM_CHAT_ID__ placeholder with actual ID or makes it an empty list
if [ -n "$TELEGRAM_CHAT_ID" ]; then
  sed "s/__TELEGRAM_CHAT_ID__/$TELEGRAM_CHAT_ID/g" "$CONFIG_SRC" > "$CONFIG_RUN"
else
  sed 's/"__TELEGRAM_CHAT_ID__"/""/g' "$CONFIG_SRC" | \
  sed 's/"allowFrom": \[""\]/"allowFrom": []/' | \
  sed 's/"dmPolicy": "allowlist"/"dmPolicy": "pairing"/' > "$CONFIG_RUN"
fi

# Pre-replace non-quoted placeholders to ensure valid JSON for Node.js parsing
sed -i "s/__SLACK_ENABLED__/false/g" "$CONFIG_RUN"

# --- Inject Secrets ---
AUTH_TOKEN="${OPENCLAW_AUTH_TOKEN:-default-auth-token}"
API_KEY="${OLLAMA_API_KEY:-default-ollama-key}"
sed -i "s/__OPENCLAW_AUTH_TOKEN__/$AUTH_TOKEN/g" "$CONFIG_RUN"
sed -i "s/__OLLAMA_API_KEY__/$API_KEY/g" "$CONFIG_RUN"

# --- Slack: habilitar e injetar accounts via Node.js ---
# O formato segue a doc: channels.slack.accounts.<id> = { mode, appToken, botToken }
# dmPolicy/groupPolicy/channels ficam no nível channels.slack (herdados por todos os accounts).
if command -v node >/dev/null 2>&1; then
  CONFIG_RUN="$CONFIG_RUN" node -e "
    const fs = require('fs');
    const path = process.env.CONFIG_RUN || '/tmp/openclaw.json';
    let raw = fs.readFileSync(path, 'utf8');
    let config;
    try {
      config = JSON.parse(raw);
    } catch (e) {
      console.error('Failed to parse config:', raw);
      throw e;
    }
    if (!config.channels || !config.channels.slack) process.exit(0);

    const agents = [
      ['ceo','CEO'],['po','PO'],['devops','DEVOPS'],['architect','ARCHITECT'],['developer','DEVELOPER'],
      ['qa','QA'],['cybersec','CYBERSEC'],['ux','UX'],['dba','DBA']
    ];

    // Build accounts per agent (docs format: mode + appToken + botToken per account)
    const accounts = {};
    for (const [id, prefix] of agents) {
      const app = process.env[prefix + '_SLACK_APP_TOKEN'];
      const bot = process.env[prefix + '_SLACK_BOT_TOKEN'];
      if (app && bot) {
        accounts[id] = { mode: 'socket', appToken: app, botToken: bot, dmPolicy: 'open', allowFrom: ['*'] };
      }
    }

    // Fallback: if no per-agent tokens, try default SLACK_APP_TOKEN/SLACK_BOT_TOKEN
    if (Object.keys(accounts).length === 0) {
      const app = process.env.SLACK_APP_TOKEN;
      const bot = process.env.SLACK_BOT_TOKEN;
      if (app && bot) {
        // Single-app mode: tokens at top level (docs quick setup format)
        config.channels.slack.appToken = app;
        config.channels.slack.botToken = bot;
        config.channels.slack.enabled = true;
      }
    } else {
      config.channels.slack.accounts = accounts;
      config.channels.slack.enabled = true;
    }

    // Channel ID placeholder
    const chanId = process.env.SLACK_ALL_CLAWDEVSAI_CHANNEL_ID || 'C0AHSCLSQKC';
    const channels = config.channels.slack.channels || {};
    if (channels['__SLACK_ALL_CLAWDEVSAI_CHANNEL_ID__'] !== undefined) {
      delete channels['__SLACK_ALL_CLAWDEVSAI_CHANNEL_ID__'];
      channels[chanId] = {};
    }
    config.channels.slack.channels = channels;

    // Remove placeholder accounts entry
    if (config.channels.slack.accounts && config.channels.slack.accounts['__SLACK_ACCOUNTS_JSON__']) {
      delete config.channels.slack.accounts['__SLACK_ACCOUNTS_JSON__'];
    }

    // If no Slack tokens at all, keep disabled
    if (!config.channels.slack.appToken && (!config.channels.slack.accounts || Object.keys(config.channels.slack.accounts).length === 0)) {
      config.channels.slack.enabled = false;
    }

    fs.writeFileSync(path, JSON.stringify(config, null, 2));
  "
fi

# Cleanup remaining placeholders (in case Node.js wasn't available)
sed -i 's/__SLACK_ENABLED__/false/g' "$CONFIG_RUN"
CHAN_ID="${SLACK_ALL_CLAWDEVSAI_CHANNEL_ID:-C0AHSCLSQKC}"
sed -i "s/__SLACK_ALL_CLAWDEVSAI_CHANNEL_ID__/$CHAN_ID/g" "$CONFIG_RUN"
sed -i '/"__SLACK_ACCOUNTS_JSON__"/d' "$CONFIG_RUN"

export OPENCLAW_CONFIG_PATH="$CONFIG_RUN"
exec openclaw gateway --allow-unconfigured --port 18789 --bind lan
