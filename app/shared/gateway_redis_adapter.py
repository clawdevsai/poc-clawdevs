#!/usr/bin/env python3
"""
Adapter HTTP para publicação em Redis Streams (Fase 1 — 018).
Fase 2: token bucket para cmd:strategy, check_egress para whitelist + reputação.
Ref: docs/38-redis-streams-estado-global.md, docs/44-fase2-seguranca-automacao.md
"""
import json
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

# truncamento-finops — truncamento na borda antes de enfileirar
TRUNCATE_BORDER_ENABLED = os.environ.get("TRUNCATE_BORDER_ENABLED", "1") == "1"
TRUNCATE_BORDER_MAX_TOKENS = int(os.environ.get("TRUNCATE_BORDER_MAX_TOKENS", "4000"))
PREFLIGHT_SUMMARIZE_MIN = int(os.environ.get("PREFLIGHT_SUMMARIZE_MIN_INTERACTIONS", "3"))
MAX_TOKENS_CEO = int(os.environ.get("MAX_TOKENS_PER_REQUEST_CEO", "8192"))
MAX_TOKENS_PO = int(os.environ.get("MAX_TOKENS_PER_REQUEST_PO", "8192"))
MAX_TOKENS_CLOUD_DEFAULT = int(os.environ.get("MAX_TOKENS_PER_REQUEST_CLOUD_DEFAULT", "4096"))
try:
    from truncate_payload_border import truncate_payload, estimate_tokens as _estimate_tokens
except ImportError:
    truncate_payload = _estimate_tokens = None

# Pre-flight summarize (truncamento-finops): opcional no container
try:
    from preflight_summarize import count_interactions, summarize_via_ollama
    _preflight_available = True
except ImportError:
    _preflight_available = False


def _get_profile_json(profile_name: str) -> dict | None:
    """Lê perfil do agente (config-perfis) de env (ConfigMap agent-profiles). Retorna dict ou None."""
    key = f"profile_{profile_name}".lower()
    raw = os.environ.get(key) or os.environ.get(key.upper())
    if not raw or key == "profile__readme":
        return None
    try:
        return json.loads(raw)
    except (json.JSONDecodeError, TypeError):
        return None


def _truncate_value(val: str, max_tokens: int = None) -> str:
    if not val or truncate_payload is None or _estimate_tokens is None:
        return val
    limit = max_tokens if max_tokens is not None else TRUNCATE_BORDER_MAX_TOKENS
    if _estimate_tokens(val) <= limit:
        return val
    out, _ = truncate_payload(val, max_tokens=limit)
    return out


def _apply_preflight_and_max_tokens(data: dict, stream: str, preflight: bool, profile: str) -> dict:
    """truncamento-finops: pre-flight summarize (se >N interações) e max_tokens por perfil. Retorna data modificado."""
    out = dict(data)
    payload_key = None
    payload_val = None
    for k in ("payload", "body", "content"):
        if k in out and isinstance(out[k], str) and len(out[k]) > 200:
            payload_key = k
            payload_val = out[k]
            break
    if not payload_key:
        return out
    try:
        payload_obj = json.loads(payload_val)
    except (json.JSONDecodeError, TypeError):
        payload_obj = None
    if preflight and _preflight_available and payload_obj is not None:
        n = count_interactions(payload_obj)
        if n > PREFLIGHT_SUMMARIZE_MIN:
            summary = summarize_via_ollama(
                "\n".join(
                    str(m.get("content", m))[:2000]
                    for m in (payload_obj.get("messages") or payload_obj.get("history") or [payload_obj])
                    if isinstance(m, dict) or isinstance(m, str)
                )
            )
            if summary:
                payload_obj["messages"] = [{"role": "system", "content": f"[Resumo pré-nuvem — {n} interações]: {summary}"}]
                payload_obj["_preflight_summarized"] = True
                payload_val = json.dumps(payload_obj, ensure_ascii=False)
    if profile == "ceo":
        limit = MAX_TOKENS_CEO
    elif profile == "po":
        limit = MAX_TOKENS_PO
    else:
        limit = MAX_TOKENS_CLOUD_DEFAULT
    out[payload_key] = _truncate_value(payload_val, max_tokens=limit)
    return out


app = Flask(__name__)
r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True,
)

# Memoria (SharedMemory): chave do documento estratégico (CEO grava, PO lê)
KEY_PREFIX_PROJECT = os.environ.get("KEY_PREFIX_PROJECT", "project:v1")
STRATEGY_DOC_KEY = os.environ.get("STRATEGY_DOC_KEY", f"{KEY_PREFIX_PROJECT}:strategy_doc")
STRATEGY_DOC_TTL_SEC = int(os.environ.get("STRATEGY_DOC_TTL_SEC", "0"))  # 0 = sem TTL


def _allowed_domains_set():
    raw = os.environ.get("ALLOWED_DOMAINS", "")
    out = set()
    for line in raw.replace(",", "\n").splitlines():
        d = line.strip().lower()
        if d and not d.startswith("#"):
            out.add(d)
    return out


@app.route("/write-strategy", methods=["POST"])
def write_strategy():
    """
    CEO grava documento estratégico na Memoria (SharedMemory).
    POST JSON: { "body": "conteúdo do documento" } ou form body=...
    Opcional: "project_id" para chave project:v1:strategy:{id}. TTL via STRATEGY_DOC_TTL_SEC (0 = sem TTL).
    """
    try:
        body = request.get_json(force=True, silent=True) or {}
    except Exception:
        body = {}
    if not body and request.form:
        body = dict(request.form)
    doc_body = body.get("body") or (request.form and request.form.get("body"))
    if isinstance(doc_body, list):
        doc_body = doc_body[0] if doc_body else ""
    if not doc_body:
        return jsonify({"error": "Missing 'body' (document content)"}), 400
    doc_body = str(doc_body)
    project_id = (body.get("project_id") or "").strip()
    key = f"{KEY_PREFIX_PROJECT}:strategy:{project_id}" if project_id else STRATEGY_DOC_KEY
    try:
        if STRATEGY_DOC_TTL_SEC and STRATEGY_DOC_TTL_SEC > 0:
            r.setex(key, STRATEGY_DOC_TTL_SEC, doc_body)
        else:
            r.set(key, doc_body)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    return jsonify({"ok": True, "key": key}), 200


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

    # truncamento-finops — truncamento na borda: valores grandes truncados antes de enfileirar
    flat = {}
    for k, v in data.items():
        s = str(v)
        if len(s) > 500:
            s = _truncate_value(s)
        flat[k] = s
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


@app.route("/publish-to-cloud", methods=["POST"])
def publish_to_cloud():
    """
    truncamento-finops: Publicar payload destinado à nuvem com pre-flight summarize e max tokens.
    POST JSON: { "stream": "...", "data": { ... }, "preflight": true, "profile": "ceo"|"po"|"default" }.
    Aplica pre-flight summarize se data.payload/data.body tiver >PREFLIGHT_SUMMARIZE_MIN_INTERACTIONS
    interações; aplica MAX_TOKENS_PER_REQUEST_* ao payload; depois publica no Redis (mesmo fluxo que /publish).
    """
    try:
        body = request.get_json(force=True, silent=True) or {}
    except Exception:
        return jsonify({"error": "Invalid JSON"}), 400
    stream = body.get("stream")
    data = body.get("data")
    if isinstance(data, list):
        data = {k: v for k, v in zip(data[::2], data[1::2])} if len(data) % 2 == 0 else {}
    if not stream or not data or not isinstance(data, dict):
        return jsonify({"error": "Missing 'stream' or 'data'"}), 400
    preflight = body.get("preflight", True)
    profile = (body.get("profile") or "default").lower()
    if profile not in ("ceo", "po", "default"):
        profile = "default"
    data = _apply_preflight_and_max_tokens(data, stream, preflight, profile)
    # Reutilizar lógica de publish (token bucket, truncamento, xadd)
    if stream == "cmd:strategy" and PHASE2_TOKEN_BUCKET_ENABLED and check_token_bucket is not None:
        if not check_token_bucket(r):
            return (
                jsonify({"error": "token_bucket_limit", "message": "Limite de eventos de estratégia por hora excedido."}),
                429,
            )
    flat = {}
    for k, v in data.items():
        s = str(v)
        if len(s) > 500:
            s = _truncate_value(s)
        flat[k] = s
    try:
        msg_id = r.xadd(stream, flat)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    if stream == "cmd:strategy" and PHASE2_TOKEN_BUCKET_ENABLED and record_strategy_event is not None:
        try:
            record_strategy_event(r)
        except Exception:
            pass
    resp = {"ok": True, "stream": stream, "id": msg_id, "preflight_applied": preflight, "profile": profile}
    profile_suggestion = _get_profile_json(profile)
    if profile_suggestion:
        resp["profile_suggestion"] = profile_suggestion
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
