#!/usr/bin/env python3
"""
Geração de microADR (truncamento-finops). Architect gera microADR ao aprovar PR; nunca sumarizado; anexar ao Warm Store.
Ref: docs/07-configuracao-e-prompts.md (2.3), docs/agents-devs/microADR-template.json
Uso: python microadr_generate.py --issue 42 --branch main --title "feat: 2FA" --decision "Aprovado: 2FA com TOTP"
      ou importar: from microadr_generate import generate_and_store_microadr
"""
import json
import os
import sys
from datetime import datetime

KEY_PREFIX = os.environ.get("KEY_PREFIX_PROJECT", "project:v1")
MICROADR_KEY_PREFIX = f"{KEY_PREFIX}:microadr"
REDIS_HOST = os.environ.get("REDIS_HOST", "127.0.0.1")
REDIS_PORT = int(os.environ.get("REDIS_PORT", "6379"))
REDIS_PASSWORD = os.environ.get("REDIS_PASSWORD") or None


def generate_microadr(issue_id: str, branch: str, title: str, decision: str, related_pr: str = None) -> dict:
    """Gera estrutura microADR (JSON estrito)."""
    return {
        "title": title or f"Issue {issue_id}",
        "date": datetime.utcnow().strftime("%Y-%m-%d"),
        "context": f"Issue {issue_id}, branch {branch}. Code review aprovado.",
        "decision": decision,
        "consequences": "Registro para memória de longo prazo; nunca sumarizar.",
        "audit_deviation": {
            "justification": "Aprovação após code review (Architect).",
            "metric_or_reference": "Critérios de aceite e cobertura verificados.",
        },
        "author_agent": "architect",
        "related_pr": related_pr,
        "related_issue": issue_id,
    }


def store_microadr_redis(r, issue_id: str, microadr: dict) -> str:
    """Armazena microADR no Redis (lista por issue; Warm Store pode consumir depois)."""
    key = f"{MICROADR_KEY_PREFIX}:{issue_id}"
    r.rpush(key, json.dumps(microadr, ensure_ascii=False))
    r.expire(key, 86400 * 90)  # 90 dias
    return key


def generate_and_store_microadr(issue_id: str, branch: str, title: str, decision: str, related_pr: str = None):
    """Gera microADR e armazena no Redis. Retorna (microadr_dict, key) ou (None, None) em erro."""
    try:
        import redis
        r = redis.Redis(host=REDIS_HOST, port=REDIS_PORT, password=REDIS_PASSWORD, decode_responses=True)
    except ImportError:
        return None, None
    microadr = generate_microadr(issue_id, branch, title, decision, related_pr)
    key = store_microadr_redis(r, issue_id, microadr)
    return microadr, key


def main() -> None:
    import argparse
    ap = argparse.ArgumentParser(description="Gerar e armazenar microADR (truncamento-finops)")
    ap.add_argument("--issue", required=True, help="ID da issue")
    ap.add_argument("--branch", default="", help="Branch do PR")
    ap.add_argument("--title", default="", help="Título do PR/issue")
    ap.add_argument("--decision", default="Aprovado no code review.", help="Decisão registrada")
    ap.add_argument("--pr", default="", help="ID ou URL do PR")
    args = ap.parse_args()
    microadr, key = generate_and_store_microadr(
        args.issue, args.branch, args.title, args.decision, args.pr or None
    )
    if key:
        print(json.dumps(microadr, ensure_ascii=False, indent=2))
        print(f"Stored at Redis key: {key}", file=sys.stderr)
    else:
        print("Failed to store microADR.", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
