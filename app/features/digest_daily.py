#!/usr/bin/env python3
"""
Digest diário (Fase 3 — 036).
Lê eventos do stream digest:daily (últimas 24h ou desde última execução),
gera Markdown em docs/agents-devs/digest-YYYY-MM-DD.md.
Opcional: envia para Telegram se TELEGRAM_BOT_TOKEN e TELEGRAM_CHAT_ID estiverem definidos.
Alertas imediatos (degradação, segurança, $5/dia) não passam por aqui — são enviados no momento pelo gateway/orquestrador.
Ref: docs/06-operacoes.md, docs/issues/036-digest-diario-alertas.md
"""
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from orchestration import get_redis, STREAM_DIGEST, DEGRADATION_REPORT_DIR

DIGEST_OUTPUT_DIR = os.environ.get("DIGEST_OUTPUT_DIR", "docs/agents-devs")
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")


def read_stream_since(r, stream: str, start_id: str = "-", end_id: str = "+", count: int = 500):
    """Lê mensagens do stream no intervalo [start_id, end_id]."""
    try:
        # XRANGE stream start end COUNT n
        entries = r.xrange(stream, min=start_id, max=end_id, count=count)
        return entries
    except Exception:
        return []


def run(date: datetime | None = None, send_telegram: bool = False) -> Path | None:
    date = date or datetime.utcnow()
    date_str = date.strftime("%Y-%m-%d")
    r = get_redis()

    # Ler todo o stream (em produção pode usar last_id salvo para incremental)
    entries = r.xrange(STREAM_DIGEST, count=1000)
    if not entries:
        out_path = Path(DIGEST_OUTPUT_DIR) / f"digest-{date_str}.md"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        out_path.write_text(
            f"# Digest — {date_str}\n\nNenhum evento no período.\n",
            encoding="utf-8",
        )
        print(f"[digest] Escrito {out_path} (vazio)")
        return out_path

    # Filtrar por data (opcional: só eventos de hoje)
    lines = [f"# Digest — {date_str}", ""]
    for eid, fields in entries:
        if not isinstance(fields, dict):
            continue
        ev_type = fields.get("type", "event")
        lines.append(f"## {ev_type}")
        for k, v in fields.items():
            if k == "type":
                continue
            lines.append(f"- **{k}:** {v}")
        lines.append("")

    out_path = Path(DIGEST_OUTPUT_DIR) / f"digest-{date_str}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"[digest] Escrito {out_path}")

    if send_telegram and TELEGRAM_BOT_TOKEN and TELEGRAM_CHAT_ID:
        _send_telegram(out_path.read_text(encoding="utf-8")[:4000])
    return out_path


def _send_telegram(text: str) -> None:
    try:
        import urllib.request
        import urllib.parse
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        data = urllib.parse.urlencode({"chat_id": TELEGRAM_CHAT_ID, "text": text}).encode()
        req = urllib.request.Request(url, data=data, method="POST")
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                print("[digest] Enviado para Telegram.")
    except Exception as e:
        print(f"[digest] Falha ao enviar Telegram: {e}", file=sys.stderr)


def main() -> None:
    import argparse
    p = argparse.ArgumentParser(description="Gera digest diário a partir do stream digest:daily")
    p.add_argument("--date", type=str, help="Data YYYY-MM-DD (default: hoje)")
    p.add_argument("--telegram", action="store_true", help="Enviar digest para Telegram")
    args = p.parse_args()
    date = None
    if args.date:
        try:
            date = datetime.strptime(args.date, "%Y-%m-%d")
        except ValueError:
            print("--date deve ser YYYY-MM-DD", file=sys.stderr)
            sys.exit(1)
    run(date=date, send_telegram=args.telegram)


if __name__ == "__main__":
    main()
