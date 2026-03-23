#!/usr/bin/env bash
set -euo pipefail

BASE="${PANEL_URL:-http://localhost:31881}"
FRONTEND="${PANEL_FRONTEND_URL:-http://localhost:31880}"
ADMIN="${PANEL_ADMIN_USERNAME:-admin}"
PASS="${PANEL_ADMIN_PASSWORD:-changeme}"

echo "=== ClawDevs Panel Smoke Test ==="
echo "Backend:  $BASE"
echo "Frontend: $FRONTEND"
echo ""

fail() { echo "FAIL: $1"; exit 1; }
ok()   { echo "OK:   $1"; }

# 1. Health check
echo "--- Health ---"
STATUS=$(curl -sf "$BASE/healthz" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('status',''))" 2>/dev/null || echo "")
[ "$STATUS" = "ok" ] && ok "GET /healthz" || fail "GET /healthz returned: $STATUS"

# 2. Login
echo "--- Auth ---"
TOKEN=$(curl -sf -X POST "$BASE/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"username\":\"$ADMIN\",\"password\":\"$PASS\"}" \
  | python3 -c "import sys,json; print(json.load(sys.stdin)['access_token'])" 2>/dev/null || echo "")
[ -n "$TOKEN" ] && ok "POST /auth/login → token" || fail "Login failed"

AUTH="Authorization: Bearer $TOKEN"

# 3. /me
ME=$(curl -sf "$BASE/auth/me" -H "$AUTH" | python3 -c "import sys,json; print(json.load(sys.stdin)['username'])" 2>/dev/null || echo "")
[ "$ME" = "$ADMIN" ] && ok "GET /auth/me → $ME" || fail "/auth/me returned: $ME"

# 4. Agents
AGENTS=$(curl -sf "$BASE/agents" -H "$AUTH" | python3 -c "import sys,json; print(json.load(sys.stdin)['total'])" 2>/dev/null || echo "0")
[ "$AGENTS" -ge 1 ] && ok "GET /agents → $AGENTS agents" || fail "No agents found"

# 5. Approvals
APPROVALS=$(curl -sf "$BASE/approvals" -H "$AUTH" | python3 -c "import sys,json; print(json.load(sys.stdin)['total'])" 2>/dev/null || echo "ERR")
[ "$APPROVALS" != "ERR" ] && ok "GET /approvals → $APPROVALS total" || fail "GET /approvals failed"

# 6. Frontend
echo "--- Frontend ---"
HTTP_CODE=$(curl -sf -o /dev/null -w "%{http_code}" "$FRONTEND/" 2>/dev/null || echo "0")
[ "$HTTP_CODE" = "200" ] && ok "GET $FRONTEND/ → 200" || fail "Frontend returned HTTP $HTTP_CODE"

echo ""
echo "=== All checks passed ==="
