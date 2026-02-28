#!/usr/bin/env python3
"""
Adapter HTTP para publicação em Redis Streams (Fase 1 — 018).
Fase 2: token bucket para cmd:strategy, check_egress para whitelist + reputação.
Ref: docs/38-redis-streams-estado-global.md, docs/44-fase2-seguranca-automacao.md
"""
import os
import sys

# Permitir importar scripts no mesmo volume (/config no pod)
_CONFIG = os.environ.get("CONFIG_DIR", os.path.dirname(os.path.abspath(__file__)))
if _CONFIG not in sys.path:
    sys.path.insert(0, _CONFIG)

REDIS_HOST = os.environ.get("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD") or None
PHASE2_TOKEN_BUCKET_ENABLED = os.environ.get("PHASE2_TOKEN_BUCKET_ENABLED", "1") == "1"
PHASE2_DOMAIN_REPUTATION_ENABLED = os.environ.get("PHASE2_DOMAIN_REPUTATION_ENABLED", "1") == "1"

try:
    import redis
except ImportError:
    print("Instale redis: pip install redis", file=sys.stderr)
    sys.exit(1)

try:
    from flask import Flask, request, jsonify
except ImportError:
    print("Instale flask: pip install flask", file=sys.stderr)
    sys.exit(1)

# Fase 2 — token bucket (opcional se script não estiver montado)
try:
    from gateway_token_bucket import (
        check_token_bucket,
        record_strategy_event,
        should_degrade_ceo_to_local,
    )
except ImportError:
    check_token_bucket = record_strategy_event = should_degrade_ceo_to_local = None

# Fase 2 — reputação de domínio (opcional)
try:
    from check_domain_reputation import check_reputation as _check_reputation
except ImportError:
    _check_reputation = None

app = Flask(__name__)
r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True,
)


def _allowed_domains_set():
    raw = os.environ.get("ALLOWED_DOMAINS", "")
    out = set()
    for line in raw.replace(",", "\n").splitlines():
        d = line.strip().lower()
        if d and not d.startswith("#"):
            out.add(d)
    return out


@app.route("/health", methods=["GET"])
def health():
    try:
        r.ping()
        return jsonify({"status": "ok", "redis": "connected"}), 200
    except Exception as e:
        return jsonify({"status": "error", "redis": str(e)}), 503


@app.route("/publish", methods=["POST"])
def publish():
    """
    POST JSON: { "stream": "cmd:strategy" | "task:backlog" | ..., "data": { ... } }
    Para cmd:strategy: aplica token bucket (Fase 2) se PHASE2_TOKEN_BUCKET_ENABLED=1.
    """
    try:
        body = request.get_json(force=True, silent=True) or {}
    except Exception:
        return jsonify({"error": "Invalid JSON"}), 400
    stream = body.get("stream") or (request.form and request.form.get("stream"))
    data = body.get("data")
    if isinstance(data, list):
        data = {k: v for k, v in zip(data[::2], data[1::2])} if len(data) % 2 == 0 else {}
    if not stream:
        return jsonify({"error": "Missing 'stream'"}), 400
    if not data or not isinstance(data, dict):
        return jsonify({"error": "Missing or invalid 'data' (object)"}), 400

    # Fase 2 — token bucket para cmd:strategy
    if stream == "cmd:strategy" and PHASE2_TOKEN_BUCKET_ENABLED and check_token_bucket is not None:
        if not check_token_bucket(r):
            return (
                jsonify({
                    "error": "token_bucket_limit",
                    "message": "Limite de eventos de estratégia por hora excedido.",
                }),
                429,
            )

    flat = {k: str(v) for k, v in data.items()}
    try:
        msg_id = r.xadd(stream, flat)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    # Fase 2 — registrar evento após publicar em cmd:strategy
    if stream == "cmd:strategy" and PHASE2_TOKEN_BUCKET_ENABLED and record_strategy_event is not None:
        try:
            record_strategy_event(r)
        except Exception:
            pass

    resp = {"ok": True, "stream": stream, "id": msg_id}
    if stream == "cmd:strategy" and should_degrade_ceo_to_local is not None:
        try:
            resp["degrade_ceo"] = should_degrade_ceo_to_local(r)
        except Exception:
            resp["degrade_ceo"] = False
    return jsonify(resp), 200


@app.route("/check_egress", methods=["GET"])
def check_egress():
    """
    Fase 2 — Zero Trust egress. GET ?domain=example.com
    Verifica whitelist (ALLOWED_DOMAINS) e opcionalmente reputação (check_domain_reputation).
    Retorna 200 { "allow": true } ou 403 { "allow": false, "reason": "..." }.
    """
    domain = (request.args.get("domain") or "").strip().lower()
    if not domain:
        return jsonify({"error": "Missing 'domain' query"}), 400
    if ".." in domain or " " in domain:
        return jsonify({"allow": False, "reason": "invalid_domain"}), 403

    allowed = _allowed_domains_set()
    if not allowed:
        return jsonify({"allow": False, "reason": "no_whitelist_configured"}), 503

    if domain not in allowed:
        return jsonify({"allow": False, "reason": "domain_not_in_whitelist"}), 403

    if PHASE2_DOMAIN_REPUTATION_ENABLED and _check_reputation is not None:
        allow, reason = _check_reputation(domain)
        if not allow:
            return jsonify({"allow": False, "reason": reason}), 403
        return jsonify({"allow": True, "reason": reason}), 200

    return jsonify({"allow": True, "reason": "whitelist"}), 200


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
