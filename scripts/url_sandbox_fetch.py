#!/usr/bin/env python3
"""
Sandbox para fetch de URL desconhecida (Fase 2 — 020 evolução).
Roda com timeout; grava resultado em arquivo; opcionalmente publica resumo no stream digest.
Uso: em Job com rede restrita (só essa URL ou whitelist). Variáveis: URL_SANDBOX_TARGET, OUTPUT_PATH, REDIS_*.
Ref: docs/issues/020-zero-trust-fluxo-classificacao.md (sandbox URL/API)
"""
from __future__ import annotations

import os
import sys
import urllib.request

URL = os.environ.get("URL_SANDBOX_TARGET", "")
OUTPUT_PATH = os.environ.get("URL_SANDBOX_OUTPUT", "/tmp/url_sandbox_output.html")
TIMEOUT_SEC = int(os.environ.get("URL_SANDBOX_TIMEOUT", "30"))
MAX_BYTES = int(os.environ.get("URL_SANDBOX_MAX_BYTES", "1048576"))  # 1 MiB
PUBLISH_DIGEST = os.environ.get("URL_SANDBOX_PUBLISH_DIGEST", "1") == "1"
REDIS_HOST = os.environ.get("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
STREAM_DIGEST = os.environ.get("STREAM_DIGEST", "digest:daily")


def fetch(url: str) -> tuple[bool, bytes, str]:
    """Retorna (ok, content, error_msg)."""
    if not url.startswith(("http://", "https://")):
        return False, b"", "invalid_scheme"
    req = urllib.request.Request(url, headers={"User-Agent": "ClawDevs-URL-Sandbox/1.0"})
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT_SEC) as r:
            data = r.read(MAX_BYTES + 1)
            if len(data) > MAX_BYTES:
                data = data[:MAX_BYTES]
            return True, data, ""
    except Exception as e:
        return False, b"", str(e)


def publish_digest(url: str, ok: bool, size: int, error: str) -> None:
    try:
        import redis
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, decode_responses=True)
        r.xadd(
            STREAM_DIGEST,
            {
                "type": "url_sandbox",
                "url": url[:500],
                "ok": "1" if ok else "0",
                "size": str(size),
                "error": (error or "")[:200],
            },
            maxlen=1000,
        )
    except Exception:
        pass


def main() -> int:
    url = URL.strip()
    if not url or url == "__URL_SANDBOX_TARGET__":
        print("URL_SANDBOX_TARGET não definido; nada a fazer (exit 0).", file=sys.stderr)
        return 0  # sucesso: Job aplicado sem URL não deve falhar
    ok, content, err = fetch(url)
    os.makedirs(os.path.dirname(OUTPUT_PATH) or ".", exist_ok=True)
    with open(OUTPUT_PATH, "wb") as f:
        f.write(content)
    if PUBLISH_DIGEST:
        publish_digest(url, ok, len(content), err)
    if not ok:
        print(f"Fetch falhou: {err}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
