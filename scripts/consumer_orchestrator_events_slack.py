#!/usr/bin/env python3
"""
Consumidor do stream orchestrator:events — envia cada evento ao Slack (Fase 3).
Executar como processo contínuo (Deployment no cluster) ou em foreground.
Requer: REDIS_*, SLACK_WEBHOOK_URL ou SLACK_BOT_TOKEN + SLACK_ALERTS_CHANNEL_ID.
Ref: docs/06-operacoes.md, STREAM_ORCHESTRATOR_EVENTS.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orchestration_phase3 import get_redis, STREAM_ORCHESTRATOR_EVENTS
from slack_notify import send_slack

CONSUMER_GROUP = os.environ.get("ORCHESTRATOR_EVENTS_SLACK_GROUP", "slack")
CONSUMER_NAME = os.environ.get("ORCHESTRATOR_EVENTS_SLACK_CONSUMER", "slack-consumer")
BLOCK_MS = int(os.environ.get("ORCHESTRATOR_EVENTS_BLOCK_MS", "5000"))


def _format_message(msg: dict) -> str:
    """Formata payload do evento para texto Slack (legível)."""
    t = msg.get("type", "event")
    parts = [f"*ClawDevs — {t}*"]
    for k, v in msg.items():
        if k == "type" or not v:
            continue
        parts.append(f"• {k}: `{v}`")
    return "\n".join(parts)


def _ensure_group(r):
    try:
        r.xgroup_create(STREAM_ORCHESTRATOR_EVENTS, CONSUMER_GROUP, id="0", mkstream=True)
    except Exception:
        pass  # group already exists or stream exists without group


def run_loop():
    r = get_redis()
    _ensure_group(r)
    last_id = ">"
    while True:
        try:
            streams = r.xreadgroup(
                CONSUMER_GROUP,
                CONSUMER_NAME,
                {STREAM_ORCHESTRATOR_EVENTS: last_id},
                count=10,
                block=BLOCK_MS,
            )
            if not streams:
                continue
            for stream_name, messages in streams:
                for msg_id, raw in messages:
                    msg = raw if isinstance(raw, dict) else dict(zip((raw or [])[::2], (raw or [])[1::2]))
                    text = _format_message(msg)
                    if send_slack(text):
                        r.xack(STREAM_ORCHESTRATOR_EVENTS, CONSUMER_GROUP, msg_id)
                    else:
                        # não avança last_id para reprocessar depois
                        pass
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"[consumer_orchestrator_events_slack] Erro: {e}", file=sys.stderr)
            time.sleep(5)


def main():
    if not (os.environ.get("SLACK_WEBHOOK_URL") or os.environ.get("SLACK_BOT_TOKEN")):
        print("[consumer_orchestrator_events_slack] SLACK_WEBHOOK_URL ou SLACK_BOT_TOKEN necessário.", file=sys.stderr)
        sys.exit(1)
    print(f"[consumer_orchestrator_events_slack] Iniciando (stream={STREAM_ORCHESTRATOR_EVENTS} group={CONSUMER_GROUP}).")
    run_loop()


if __name__ == "__main__":
    main()
