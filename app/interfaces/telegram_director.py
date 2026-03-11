#!/usr/bin/env python3
"""Bridge Telegram -> cmd:strategy (diretor conversa com CEO via chat)."""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.parse
import urllib.request

from app.shared.redis_client import get_redis_with_retry

TELEGRAM_BOT_TOKEN = (os.getenv("TELEGRAM_BOT_TOKEN") or "").strip()
TELEGRAM_CHAT_ID = (os.getenv("TELEGRAM_CHAT_ID") or "").strip()
STREAM_CMD_STRATEGY = os.getenv("STREAM_CMD_STRATEGY", "cmd:strategy")
STATE_KEY_OFFSET = os.getenv("TELEGRAM_OFFSET_KEY", "telegram:director:last_update_id")
OLLAMA_BASE_URL = (os.getenv("OLLAMA_BASE_URL") or os.getenv("OLLAMA_HOST") or "http://ollama:11434").rstrip("/")
OLLAMA_MODEL = (
    os.getenv("OPENCLAW_MODEL_CEO_PRIMARY")
    or os.getenv("OPENCLAW_MODEL_CEO")
    or os.getenv("OLLAMA_MODEL")
    or "qwen3.5:397b-cloud"
).strip()


def _telegram_request(method: str, payload: dict) -> dict:
    base = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/{method}"
    data = urllib.parse.urlencode(payload).encode("utf-8")
    request = urllib.request.Request(base, data=data, method="POST")
    with urllib.request.urlopen(request, timeout=70) as response:
        raw = response.read().decode("utf-8")
    body = json.loads(raw)
    if not body.get("ok"):
        raise RuntimeError(f"telegram_{method}_error: {body}")
    return body


def send_message(chat_id: str, text: str) -> None:
    try:
        _telegram_request("sendMessage", {"chat_id": chat_id, "text": text})
    except Exception as error:
        print(f"[telegram] erro ao responder chat {chat_id}: {error}")


def ensure_polling_mode() -> None:
    """Force getUpdates mode (disable webhook) to prevent transport conflicts."""
    try:
        _telegram_request("deleteWebhook", {"drop_pending_updates": False})
    except Exception as error:
        print(f"[telegram] aviso: nao foi possivel limpar webhook: {error}")


def generate_ceo_reply(instruction: str) -> str | None:
    chat_payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "Você é o CEO técnico do ClawDevs AI. Responda em português, "
                    "de forma objetiva, com foco em estratégia de produto e execução."
                ),
            },
            {"role": "user", "content": instruction},
        ],
        "stream": False,
    }
    endpoints: list[tuple[str, dict]] = [
        ("/api/chat", chat_payload),
        ("/v1/chat/completions", chat_payload),
    ]
    last_error: Exception | None = None

    for endpoint, payload in endpoints:
        body = json.dumps(payload).encode("utf-8")
        request = urllib.request.Request(
            f"{OLLAMA_BASE_URL}{endpoint}",
            data=body,
            method="POST",
            headers={"Content-Type": "application/json"},
        )
        try:
            with urllib.request.urlopen(request, timeout=90) as response:
                raw = response.read().decode("utf-8")
            parsed = json.loads(raw)
            if endpoint == "/api/chat":
                message = parsed.get("message") or {}
                content = (message.get("content") or "").strip()
            else:
                choices = parsed.get("choices") or []
                message = (choices[0] or {}).get("message") if choices else {}
                content = (message or {}).get("content", "").strip()
            if content:
                return content
        except Exception as error:
            last_error = error
            continue

    print(f"[telegram] falha ao gerar resposta CEO via Ollama: {last_error}")
    return None


def get_updates(offset: int) -> list[dict]:
    body = _telegram_request(
        "getUpdates",
        {
            "offset": offset,
            "timeout": 30,
            "allowed_updates": json.dumps(["message"]),
        },
    )
    return body.get("result", [])


def normalize_issue_id(update_id: int) -> str:
    return f"TG-{update_id}"


def handle_message(redis_client, update: dict) -> None:
    message = update.get("message") or {}
    chat = message.get("chat") or {}
    chat_id = str(chat.get("id") or "")
    text = (message.get("text") or "").strip()
    update_id = int(update.get("update_id", 0))

    if not chat_id or not text:
        return

    if TELEGRAM_CHAT_ID and chat_id != TELEGRAM_CHAT_ID:
        send_message(chat_id, "Chat não autorizado para este bot.")
        return

    if text in {"/start", "/help"}:
        send_message(
            chat_id,
            "Envie uma diretriz estratégica em texto. "
            "Ela será publicada no fluxo CEO/PO.",
        )
        return

    issue_id = normalize_issue_id(update_id)
    payload = {
        "issue_id": issue_id,
        "directive": text,
        "source": "telegram",
        "event_name": "cmd.strategy.telegram",
        "chat_id": chat_id,
        "update_id": str(update_id),
    }
    redis_client.xadd(STREAM_CMD_STRATEGY, payload, maxlen=5000, approximate=True)
    ceo_reply = generate_ceo_reply(text)
    if ceo_reply:
        send_message(chat_id, f"CEO:\n{ceo_reply}\n\n(ref: {issue_id})")
    else:
        send_message(chat_id, f"Diretriz recebida e enfileirada ({issue_id}).")
    print(f"[telegram] publicado em {STREAM_CMD_STRATEGY}: {issue_id}")


def main() -> int:
    if not TELEGRAM_BOT_TOKEN:
        print("[telegram] TELEGRAM_BOT_TOKEN não definido. Bridge desabilitada.")
        while True:
            time.sleep(60)

    redis_client = get_redis_with_retry()
    ensure_polling_mode()
    last_update_id = int(redis_client.get(STATE_KEY_OFFSET) or 0)
    next_offset = last_update_id + 1 if last_update_id > 0 else 0

    print(
        f"[telegram] bridge ativa | stream={STREAM_CMD_STRATEGY} "
        f"| chat_filter={'on' if TELEGRAM_CHAT_ID else 'off'}"
    )

    while True:
        try:
            updates = get_updates(next_offset)
            for update in updates:
                update_id = int(update.get("update_id", 0))
                if update_id:
                    next_offset = update_id + 1
                    redis_client.set(STATE_KEY_OFFSET, str(update_id))
                handle_message(redis_client, update)
        except urllib.error.HTTPError as error:
            if error.code == 409:
                print(
                    "[telegram] conflito 409 no getUpdates: outro polling ativo "
                    "com o mesmo bot token."
                )
            else:
                print(f"[telegram] erro HTTP: {error}")
            time.sleep(5)
        except urllib.error.URLError as error:
            print(f"[telegram] erro de rede: {error}")
            time.sleep(5)
        except Exception as error:
            print(f"[telegram] erro no loop: {error}")
            time.sleep(5)


if __name__ == "__main__":
    raise SystemExit(main())
