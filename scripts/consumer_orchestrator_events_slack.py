#!/usr/bin/env python3
"""
Consumidor do stream orchestrator:events — envia cada evento ao Slack (Fase 3).
Executar como processo contínuo (Deployment no cluster) ou em foreground.
Requer: REDIS_*, ORCHESTRATOR_SLACK_* (ou SLACK_* no cluster via Secret orchestrator-slack).
Ref: docs/06-operacoes.md, STREAM_ORCHESTRATOR_EVENTS.
"""
import os
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orchestration_phase3 import get_redis, STREAM_ORCHESTRATOR_EVENTS
from slack_notify import send_slack
try:
    from arbitrage_cloud import run as run_arbitrage_cloud
except ImportError:
    def run_arbitrage_cloud(r, issue_id: str) -> bool:
        return False

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
                    if send_slack(text, env_prefix="ORCHESTRATOR_"):
                        r.xack(STREAM_ORCHESTRATOR_EVENTS, CONSUMER_GROUP, msg_id)
                    # 5º strike (032): tentar arbitragem na nuvem
                    if msg.get("type") == "issue_back_to_po" and msg.get("reason") == "fifth_strike":
                        iid = msg.get("issue_id", "").strip()
                        if iid:
                            try:
                                if run_arbitrage_cloud(r, iid):
                                    send_slack(f"*ClawDevs — Arbitragem nuvem*\nIssue `{iid}`: solução gravada em Redis (`cloud_arbitrage_solution`).", env_prefix="ORCHESTRATOR_")
                            except Exception:
                                pass
                    # Se send_slack falhou, não faz XACK (reprocessar depois)
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"[consumer_orchestrator_events_slack] Erro: {e}", file=sys.stderr)
            time.sleep(5)


def main():
    has_slack = (
        os.environ.get("ORCHESTRATOR_SLACK_WEBHOOK_URL")
        or os.environ.get("ORCHESTRATOR_SLACK_BOT_TOKEN")
        or os.environ.get("SLACK_WEBHOOK_URL")
        or os.environ.get("SLACK_BOT_TOKEN")
    )
    while not has_slack:
        print("[consumer_orchestrator_events_slack] Aguardando ORCHESTRATOR_SLACK_* ou SLACK_* (Secret orchestrator-slack no cluster).", file=sys.stderr)
        time.sleep(30)
        has_slack = (
            os.environ.get("ORCHESTRATOR_SLACK_WEBHOOK_URL")
            or os.environ.get("ORCHESTRATOR_SLACK_BOT_TOKEN")
            or os.environ.get("SLACK_WEBHOOK_URL")
            or os.environ.get("SLACK_BOT_TOKEN")
        )
    print(f"[consumer_orchestrator_events_slack] Iniciando (stream={STREAM_ORCHESTRATOR_EVENTS} group={CONSUMER_GROUP}).")
    run_loop()


if __name__ == "__main__":
    main()
