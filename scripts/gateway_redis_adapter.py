#!/usr/bin/env python3
"""
Adapter HTTP para publicação em Redis Streams (Fase 1 — 018).
O gateway OpenClaw (ou outro serviço) envia POST /publish com stream e payload;
o adapter faz XADD no Redis. Uso: publicação automática de cmd:strategy, task:backlog, draft.2.issue.
Ref: docs/38-redis-streams-estado-global.md, docs/41-fase1-agentes-soul-pods.md
"""
import os
import sys

REDIS_HOST = os.environ.get("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD") or None

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

app = Flask(__name__)
r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True,
)


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
    POST JSON: { "stream": "cmd:strategy" | "task:backlog" | "draft.2.issue" | ..., "data": { "key": "value", ... } }
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
    flat = {k: str(v) for k, v in data.items()}
    try:
        msg_id = r.xadd(stream, flat)
        return jsonify({"ok": True, "stream": stream, "id": msg_id}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port)
