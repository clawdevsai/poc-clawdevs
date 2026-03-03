#!/usr/bin/env python3
"""
Rotação/sincronização de tokens do Gateway (Fase 2 — 025 evolução).
Lê token/chat_id de uma "fonte" (env ou Secret openclaw-telegram-rotation-source)
e atualiza o Secret openclaw-telegram usado pelo deployment. Opcional: rollout restart.
Uso: em CronJob a cada 2–3 min; ou manual após atualizar a fonte.
Ref: docs/25-rotacao-tokens-service-account.md, docs/issues/025-rotacao-tokens-sandbox-roteador.md
"""
import base64
import os
import sys

NAMESPACE = os.environ.get("NAMESPACE", "ai-agents")
SECRET_NAME = os.environ.get("TELEGRAM_SECRET_NAME", "openclaw-telegram")
SOURCE_SECRET = os.environ.get("TELEGRAM_ROTATION_SOURCE_SECRET", "openclaw-telegram-rotation-source")
DEPLOYMENT_NAME = os.environ.get("OPENCLAW_DEPLOYMENT_NAME", "openclaw")
DO_RESTART = os.environ.get("ROTATION_RESTART_DEPLOYMENT", "1") == "1"


def get_source_from_env():
    token = os.environ.get("TELEGRAM_BOT_TOKEN_NEW") or os.environ.get("TELEGRAM_BOT_TOKEN")
    chat = os.environ.get("TELEGRAM_CHAT_ID_NEW") or os.environ.get("TELEGRAM_CHAT_ID")
    return (token or "").strip(), (chat or "").strip()


def main() -> int:
    try:
        from kubernetes import client, config
    except ImportError:
        print("Instale kubernetes: pip install kubernetes", file=sys.stderr)
        return 2

    config.load_incluster_config()
    v1 = client.CoreV1Api()

    # Fonte: env ou Secret SOURCE_SECRET
    token_new, chat_new = get_source_from_env()
    if not token_new:
        try:
            src = v1.read_namespaced_secret(SOURCE_SECRET, NAMESPACE)
            data = src.data or {}
            token_new = (base64.b64decode(data.get("TELEGRAM_BOT_TOKEN", b"")).decode(errors="replace")).strip()
            chat_new = (base64.b64decode(data.get("TELEGRAM_CHAT_ID", b"")).decode(errors="replace")).strip()
        except Exception as e:
            print(f"Fonte não disponível (env ou Secret {SOURCE_SECRET}): {e}", file=sys.stderr)
            return 0  # no-op, não falhar o CronJob

    if not token_new:
        return 0

    try:
        current = v1.read_namespaced_secret(SECRET_NAME, NAMESPACE)
        cur_data = current.data or {}
        cur_token = (base64.b64decode(cur_data.get("TELEGRAM_BOT_TOKEN", b"")).decode(errors="replace")).strip()
        cur_chat = (base64.b64decode(cur_data.get("TELEGRAM_CHAT_ID", b"")).decode(errors="replace")).strip()
    except Exception:
        cur_token = cur_chat = ""

    if cur_token == token_new and (not chat_new or cur_chat == chat_new):
        return 0

    body = client.V1Secret(
        data={
            "TELEGRAM_BOT_TOKEN": base64.b64encode(token_new.encode()).decode(),
            "TELEGRAM_CHAT_ID": base64.b64encode((chat_new or cur_chat).encode()).decode(),
        }
    )
    v1.patch_namespaced_secret(SECRET_NAME, NAMESPACE, body)
    print("Secret openclaw-telegram atualizado.", file=sys.stderr)

    if DO_RESTART:
        try:
            app = client.AppsV1Api()
            app.patch_namespaced_deployment(
                DEPLOYMENT_NAME,
                NAMESPACE,
                {"spec": {"template": {"metadata": {"annotations": {"kubectl.kubernetes.io/restartedAt": __import__("datetime").datetime.utcnow().isoformat() + "Z"}}}}},
            )
            print("Deployment openclaw rollout restart acionado.", file=sys.stderr)
        except Exception as e:
            print(f"Aviso: não foi possível reiniciar deployment: {e}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    sys.exit(main())
