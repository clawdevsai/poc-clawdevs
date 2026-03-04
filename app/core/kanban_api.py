
#!/usr/bin/env python3
"""
Kanban API — Backend REST para o dashboard Kanban do ClawDevs.
Lê/grava estado das issues no Redis existente (issue_state.py).
Server-Sent Events (SSE) para atualizações em tempo real via kanban:events stream.

Endpoints:
  GET  /api/board              — Board completo (issues agrupadas por estado)
  GET  /api/issues/<id>        — Detalhes de uma issue
  POST /api/issues             — Criar nova issue
  PATCH /api/issues/<id>/state — Mover issue (transição de estado)
  GET  /api/events             — SSE stream de mudanças em tempo real
  GET  /health                 — Health check

Ref: docs/agents-devs/state-machine-issues.md, docs/38-redis-streams-estado-global.md
"""
import json
import os
import sys
import time
import uuid

_CONFIG = os.environ.get("CONFIG_DIR", os.path.dirname(os.path.abspath(__file__)))
if _CONFIG not in sys.path:
    sys.path.insert(0, _CONFIG)

import kanban_db

REDIS_HOST = os.environ.get("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD") or None
PORT = int(os.environ.get("KANBAN_API_PORT", "5001"))

KEY_PREFIX = os.environ.get("KEY_PREFIX_PROJECT", "project:v1")
STREAM_KANBAN_EVENTS = os.environ.get("STREAM_KANBAN_EVENTS", "kanban:events")

# Índice de issues conhecidas pelo Kanban
KANBAN_INDEX_KEY = f"{KEY_PREFIX}:kanban:index"  # Redis SET com issue_ids

try:
    import redis
except ImportError:
    print("Instale redis: pip install redis", file=sys.stderr)
    sys.exit(1)

try:
    from flask import Flask, Response, jsonify, request
    from flask_cors import CORS
except ImportError:
    print("Instale: pip install flask flask-cors", file=sys.stderr)
    sys.exit(1)

# Reutilizar módulos existentes
try:
    from issue_state import (
        VALID_STATES,
        get_issue_state,
        set_issue_state,
    )
except ImportError:
    # Fallback se não estiver no path
    VALID_STATES = {
        "New", "Shortlisted", "Interviewed",
    }

    def get_issue_state(r, issue_id):
        key = f"{KEY_PREFIX}:issue:{issue_id}:state"
        return r.get(key)

    def set_issue_state(r, issue_id, state, ttl_sec=None):
        if state not in VALID_STATES:
            return False
        key = f"{KEY_PREFIX}:issue:{issue_id}:state"
        if ttl_sec:
            r.setex(key, ttl_sec, state)
        else:
            r.set(key, state)
        return True

try:
    from kanban_event_publisher import publish_kanban_event, publish_kanban_issue_created
except ImportError:
    def publish_kanban_event(r, issue_id, old_state, new_state, agent="api", extra=None):
        try:
            payload = {"issue_id": str(issue_id), "from_state": str(old_state or ""),
                       "to_state": str(new_state), "agent": str(agent),
                       "ts": str(int(time.time() * 1000))}
            if extra:
                payload.update({k: str(v) for k, v in extra.items()})
            return r.xadd(STREAM_KANBAN_EVENTS, payload, maxlen=1000, approximate=True)
        except Exception:
            return None

    def publish_kanban_issue_created(r, issue_id, title, agent="director"):
        return publish_kanban_event(r, issue_id, "", "Backlog", agent,
                                    extra={"action": "created", "title": title})


# ── Ordered columns for the Kanban board ─────────────────────────────────────
COLUMNS_ORDER = [
    "New", "Shortlisted", "Interviewed",
]

app = Flask(__name__)
CORS(app)

r = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    password=REDIS_PASSWORD,
    decode_responses=True,
)

# Initialize SQLite
kanban_db.init_db()


# ── Helpers ───────────────────────────────────────────────────────────────────

def _issue_key(issue_id: str) -> str:
    return f"{KEY_PREFIX}:issue:{issue_id}"


def _get_issue_data(issue_id: str) -> dict | None:
    """Lê dados da issue do HASH Redis."""
    key = _issue_key(issue_id)
    data = r.hgetall(key)
    if not data:
        return None
    data["id"] = issue_id
    data["state"] = get_issue_state(r, issue_id) or "New"
    return data


def _list_all_issues() -> list[dict]:
    """Lista todas as issues do SQLite (persistente)."""
    return kanban_db.get_all_issues()


# ── Board ─────────────────────────────────────────────────────────────────────

@app.route("/api/board", methods=["GET"])
def get_board():
    """Retorna o board completo: colunas com issues."""
    issues = _list_all_issues()
    columns = {col: [] for col in COLUMNS_ORDER}
    for issue in issues:
        state = issue.get("state", "New")
        if state in columns:
            columns[state].append(issue)
        else:
            columns["New"].append(issue)
    return jsonify({
        "columns": COLUMNS_ORDER,
        "board": columns,
        "total": len(issues),
    })


# ── Issues CRUD ───────────────────────────────────────────────────────────────

@app.route("/api/issues/<issue_id>", methods=["GET"])
def get_issue(issue_id):
    """Detalhes de uma issue."""
    issue = _get_issue_data(issue_id)
    if not issue:
        return jsonify({"error": "Issue not found"}), 404
    return jsonify(issue)


@app.route("/api/issues", methods=["POST"])
def create_issue():
    """
    Cria nova issue.
    POST JSON: { "title": "...", "summary": "...", "agent": "director" }
    """
    try:
        body = request.get_json(force=True, silent=True) or {}
    except Exception:
        return jsonify({"error": "Invalid JSON"}), 400

    title = (body.get("title") or "").strip()
    if not title:
        return jsonify({"error": "Missing 'title'"}), 400

    summary = (body.get("summary") or "").strip()
    agent = (body.get("agent") or "director").strip()
    priority = (body.get("priority") or "medium").strip()

    issue_id = body.get("id") or str(uuid.uuid4())[:8]
    key = _issue_key(issue_id)

    # Gravar dados da issue como HASH
    r.hset(key, mapping={
        "title": title,
        "summary": summary,
        "priority": priority,
        "created_by": agent,
        "created_at": str(int(time.time() * 1000)),
    })

    # Definir estado inicial
    state = (body.get("state") or "New").strip()
    if state not in VALID_STATES:
        state = "New"
    
    set_issue_state(r, issue_id, state)

    # Adicionar ao índice do Kanban
    r.sadd(KANBAN_INDEX_KEY, issue_id)

    # Persistir no SQLite
    issue_type = (body.get("type") or "task").strip().lower()
    kanban_db.save_issue(issue_id, issue_type, title, summary, state, priority, agent)

    # Publicar evento
    publish_kanban_issue_created(r, issue_id, title, agent)

    # Auto-registrar atividade de criação
    kanban_db.add_activity(agent, f"Created {issue_type}: {title}")

    return jsonify({
        "ok": True,
        "id": issue_id,
        "state": state,
        "type": issue_type
    }), 201


@app.route("/api/issues/<issue_id>/state", methods=["PATCH"])
def update_issue_state(issue_id):
    """
    Mover issue para novo estado.
    PATCH JSON: { "state": "InProgress", "agent": "developer" }
    """
    try:
        body = request.get_json(force=True, silent=True) or {}
    except Exception:
        return jsonify({"error": "Invalid JSON"}), 400

    new_state = (body.get("state") or "").strip()
    agent = (body.get("agent") or "api").strip()

    if new_state not in VALID_STATES:
        return jsonify({
            "error": f"Invalid state '{new_state}'",
            "valid_states": sorted(VALID_STATES),
        }), 400

    # Verificar se a issue existe
    if not r.exists(_issue_key(issue_id)):
        return jsonify({"error": "Issue not found"}), 404

    old_state = get_issue_state(r, issue_id) or "Backlog"
    set_issue_state(r, issue_id, new_state)

    # Garantir que está no índice
    r.sadd(KANBAN_INDEX_KEY, issue_id)

    # Atualizar no SQLite
    kanban_db.update_issue_state(issue_id, new_state)

    # Publicar evento
    publish_kanban_event(r, issue_id, old_state, new_state, agent)

    # Registrar atividade
    kanban_db.add_activity(agent, f"Moved issue {issue_id} to {new_state}")

    return jsonify({
        "ok": True,
        "id": issue_id,
        "from": old_state,
        "to": new_state,
    })


@app.route("/api/issues/<issue_id>", methods=["DELETE"])
def delete_issue(issue_id):
    """Remove issue do Kanban index (Redis)."""
    r.srem(KANBAN_INDEX_KEY, issue_id)
    return jsonify({"ok": True, "id": issue_id})


@app.route("/api/activities", methods=["GET"])
def get_activities():
    """Retorna log de atividades recentes dos agentes."""
    limit = request.args.get("limit", 50, type=int)
    items = kanban_db.get_recent_activities(limit)
    return jsonify(items)


@app.route("/api/activities", methods=["POST"])
def post_activity():
    """Agentes usam este endpoint para dizer o que estão fazendo."""
    body = request.get_json(force=True, silent=True) or {}
    agent = (body.get("agent") or "unknown").strip()
    message = (body.get("message") or "").strip()
    if not message:
        return jsonify({"error": "Missing 'message'"}), 400
    
    kanban_db.add_activity(agent, message)
    return jsonify({"ok": True}), 201


# ── Server-Sent Events ───────────────────────────────────────────────────────

@app.route("/api/events", methods=["GET"])
def sse_events():
    """
    SSE endpoint — consome kanban:events Redis Stream em tempo real.
    O frontend se conecta a este endpoint para receber atualizações push.
    """
    def generate():
        last_id = "$"  # Apenas novas mensagens
        while True:
            try:
                results = r.xread(
                    {STREAM_KANBAN_EVENTS: last_id},
                    count=10,
                    block=5000,  # 5s block
                )
                if results:
                    for stream_name, messages in results:
                        for msg_id, data in messages:
                            last_id = msg_id
                            event_data = json.dumps(data, ensure_ascii=False)
                            yield f"id: {msg_id}\nevent: kanban\ndata: {event_data}\n\n"
                else:
                    # Heartbeat para manter conexão viva
                    yield f": heartbeat {int(time.time())}\n\n"
            except redis.ConnectionError:
                yield f"event: error\ndata: {{\"error\": \"redis_disconnected\"}}\n\n"
                time.sleep(2)
            except GeneratorExit:
                return
            except Exception as e:
                yield f"event: error\ndata: {{\"error\": \"{str(e)}\"}}\n\n"
                time.sleep(1)

    return Response(
        generate(),
        mimetype="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
            "Access-Control-Allow-Origin": "*",
        },
    )


# ── Sync: descobrir issues existentes no Redis ───────────────────────────────

@app.route("/api/sync", methods=["POST"])
def sync_existing_issues():
    """
    Escaneia Redis buscando todas as chaves project:v1:issue:*:state e
    adiciona as issues ao índice do Kanban. Útil para importar issues
    que já existiam antes do Kanban.
    """
    pattern = f"{KEY_PREFIX}:issue:*:state"
    count = 0
    for key in r.scan_iter(match=pattern, count=100):
        # key = project:v1:issue:42:state → issue_id = 42
        parts = key.replace(f"{KEY_PREFIX}:issue:", "").rsplit(":state", 1)
        if parts and parts[0]:
            issue_id = parts[0]
            r.sadd(KANBAN_INDEX_KEY, issue_id)
            count += 1
    return jsonify({"ok": True, "synced": count})


# ── Health ────────────────────────────────────────────────────────────────────

@app.route("/health", methods=["GET"])
def health():
    try:
        r.ping()
        return jsonify({"status": "ok", "service": "kanban-api", "redis": "connected"})
    except Exception as e:
        return jsonify({"status": "error", "redis": str(e)}), 503


# ── Main ──────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=PORT, threaded=True)
