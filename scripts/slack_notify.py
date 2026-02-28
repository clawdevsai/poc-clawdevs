#!/usr/bin/env python3
"""
Envio de mensagens para Slack (Fase 3 — alertas e consumidores).
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
) -> bool:
    """
    Envia mensagem ao Slack. Usa webhook se SLACK_WEBHOOK_URL estiver definido;
    senão usa SLACK_BOT_TOKEN + SLACK_ALERTS_CHANNEL_ID (ou channel passado).
    Retorna True se enviou com sucesso.
    """
    webhook_url = webhook_url or os.environ.get("SLACK_WEBHOOK_URL", "").strip()
    bot_token = bot_token or os.environ.get("SLACK_BOT_TOKEN", "").strip()
    channel = channel or os.environ.get("SLACK_ALERTS_CHANNEL_ID") or os.environ.get("SLACK_ALL_CLAWDEVSAI_CHANNEL_ID", "").strip()

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
    ok = send_slack(text)
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
