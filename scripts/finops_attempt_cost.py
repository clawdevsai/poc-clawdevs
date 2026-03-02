#!/usr/bin/env python3
"""
Persistência acoplada ao FinOps (truncamento-finops). Contador de tentativas × custo no pre-flight.
No pre-flight, custo estimado × número da tentativa (penalidade progressiva); ao atingir gatilho,
orquestrador interrompe a tarefa, devolve ao backlog do PO e libera travas (GPU).
Ref: docs/06-operacoes.md, docs/13-habilidades-proativas.md, docs/issues/041-truncamento-contexto-finops.md
Uso: FINOPS_MAX_ATTEMPTS=5 python finops_attempt_cost.py --issue 42 [--attempt 3] [--cost-estimate 0.02]
      Retorna exit 0 se pode continuar, 1 se deve interromper (devolver ao PO).
"""
import argparse
import os
import sys

REDIS_HOST = os.environ.get("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD") or None
KEY_PREFIX = os.environ.get("KEY_PREFIX_PROJECT", "project:v1")
FINOPS_MAX_ATTEMPTS = int(os.environ.get("FINOPS_MAX_ATTEMPTS", "5"))
FINOPS_DAILY_CAP = float(os.environ.get("FINOPS_DAILY_CAP", "5.0"))


def get_attempt_count(r, issue_id: str) -> int:
    """Lê contador de tentativas da issue no Redis."""
    key = f"{KEY_PREFIX}:issue:{issue_id}:attempt_count"
    try:
        return int(r.get(key) or 0)
    except Exception:
        return 0


def increment_attempt(r, issue_id: str) -> int:
    """Incrementa contador de tentativas; retorna novo valor."""
    key = f"{KEY_PREFIX}:issue:{issue_id}:attempt_count"
    n = r.incr(key)
    r.expire(key, 86400 * 2)  # 2 dias
    return n


def should_stop_task(issue_id: str, attempt: int, cost_estimate: float) -> tuple[bool, str]:
    """
    Retorna (True, motivo) se a tarefa deve ser interrompida (devolver ao PO, liberar GPU).
    Penalidade progressiva: custo_efetivo = cost_estimate * attempt.
    """
    if attempt >= FINOPS_MAX_ATTEMPTS:
        return True, f"Tentativas ({attempt}) >= máximo ({FINOPS_MAX_ATTEMPTS}); devolver ao PO."
    effective_cost = cost_estimate * attempt
    if effective_cost >= FINOPS_DAILY_CAP:
        return True, f"Custo efetivo estimado ({effective_cost:.2f}) >= teto diário ({FINOPS_DAILY_CAP}); devolver ao PO."
    return False, ""


def main() -> None:
    ap = argparse.ArgumentParser(description="FinOps: verificar se deve interromper tarefa (truncamento-finops)")
    ap.add_argument("--issue", required=True, help="ID da issue")
    ap.add_argument("--attempt", type=int, default=None, help="Número da tentativa (default: lê do Redis)")
    ap.add_argument("--cost-estimate", type=float, default=0.01, help="Custo estimado por tentativa (USD)")
    ap.add_argument("--increment", action="store_true", help="Incrementar contador no Redis antes de verificar")
    args = ap.parse_args()
    try:
        import redis
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True)
    except ImportError:
        print("redis não instalado.", file=sys.stderr)
        sys.exit(0)
    if args.increment:
        attempt = increment_attempt(r, args.issue)
    else:
        attempt = args.attempt if args.attempt is not None else get_attempt_count(r, args.issue)
    stop, reason = should_stop_task(args.issue, attempt, args.cost_estimate)
    if stop:
        print(f"INTERROMPER: {reason}", file=sys.stderr)
        sys.exit(1)
    print(f"OK: attempt={attempt}", file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()
