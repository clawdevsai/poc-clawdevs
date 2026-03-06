#!/usr/bin/env python3
"""
Envio de mensagens para Slack (alertas e consumidores).
Suporta: Incoming Webhook (SLACK_WEBHOOK_URL) ou API chat.postMessage (SLACK_BOT_TOKEN + canal).
Uso: slack_notify.py "Texto da mensagem"   ou   python -c "from slack_notify import send_slack; send_slack('...')"
Ref: docs/06-operacoes.md (alertas imediatos), docs/42-slack-tokens-setup.md
"""
import json
import os
import sys
import urllib.error
import urllib.request


def send_slack(
    text: str,
    *,
    webhook_url: str | None = None,
    bot_token: str | None = None,
    channel: str | None = None,
    env_prefix: str | None = None,
) -> bool:
    """
    Envia mensagem ao Slack. Usa webhook se SLACK_WEBHOOK_URL estiver definido;
    senão usa SLACK_BOT_TOKEN + SLACK_ALERTS_CHANNEL_ID (ou channel passado).
    Se env_prefix for passado (ex.: "ORCHESTRATOR_"), lê {prefix}SLACK_WEBHOOK_URL etc.
    Retorna True se enviou com sucesso.
    """
    p = (env_prefix or "").strip()
    webhook_key = f"{p}SLACK_WEBHOOK_URL" if p else "SLACK_WEBHOOK_URL"
    bot_key = f"{p}SLACK_BOT_TOKEN" if p else "SLACK_BOT_TOKEN"
    channel_key = f"{p}SLACK_ALERTS_CHANNEL_ID" if p else "SLACK_ALERTS_CHANNEL_ID"
    channel_fallback_key = f"{p}SLACK_ALL_CLAWDEVSAI_CHANNEL_ID" if p else "SLACK_ALL_CLAWDEVSAI_CHANNEL_ID"
    webhook_url = webhook_url or os.environ.get(webhook_key, "").strip()
    bot_token = bot_token or os.environ.get(bot_key, "").strip()
    channel = channel or os.environ.get(channel_key, "").strip() or os.environ.get(channel_fallback_key, "").strip()
    # Quando só o app CEO está configurado, CEO_* pode herdar de OPENCLAW_SLACK_* (mesmo app)
    if p == "CEO_" and (not bot_token or not channel):
        bot_token = bot_token or os.environ.get("OPENCLAW_SLACK_BOT_TOKEN", "").strip()
        channel = channel or os.environ.get("OPENCLAW_SLACK_ALL_CLAWDEVSAI_CHANNEL_ID", "").strip()

    if webhook_url:
        return _send_webhook(webhook_url, text)
    if bot_token and channel:
        return _send_api(bot_token, channel, text)
    return False


def _send_webhook(url: str, text: str) -> bool:
    try:
        body = json.dumps({"text": text}).encode("utf-8")
        req = urllib.request.Request(url, data=body, method="POST", headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status == 200
    except Exception:
        return False


def _send_api(bot_token: str, channel: str, text: str) -> bool:
    try:
        body = json.dumps({"channel": channel, "text": text}).encode("utf-8")
        req = urllib.request.Request(
            "https://slack.com/api/chat.postMessage",
            data=body,
            method="POST",
            headers={
                "Content-Type": "application/json; charset=utf-8",
                "Authorization": f"Bearer {bot_token}",
            },
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return data.get("ok") is True
    except Exception:
        return False


def main() -> None:
    if len(sys.argv) < 2:
        print("Uso: slack_notify.py <mensagem>", file=sys.stderr)
        sys.exit(1)
    text = " ".join(sys.argv[1:])
    prefix = os.environ.get("SLACK_ENV_PREFIX", "").strip() or None
    ok = send_slack(text, env_prefix=prefix)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
