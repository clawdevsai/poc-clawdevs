#!/usr/bin/env python3
"""
Validação determinística de reputação de domínio (Fase 2 — 024).
Antes de liberar egress para um domínio (mesmo na whitelist), consultar API de reputação
(ex.: VirusTotal); rejeitar se domínio recém-registrado ou má reputação.
Ref: docs/05-seguranca-e-etica.md, docs/issues/024-skills-terceiros-checklist-egress.md
"""
import os
import sys

# Opcional: API key para VirusTotal ou outro provedor
VIRUSTOTAL_API_KEY = os.environ.get("VIRUSTOTAL_API_KEY", "")
# Se não houver API key, comportamento: block (conservador) ou allow (apenas log)
NO_API_BEHAVIOR = os.environ.get("CHECK_DOMAIN_NO_API", "block").lower()


def check_reputation(domain: str) -> tuple[bool, str]:
    """
    Retorna (allow, reason). True = permitir egress para o domínio.
    Sem API key: conforme NO_API_BEHAVIOR (block = rejeitar, allow = permitir com aviso).
    """
    domain = (domain or "").strip().lower()
    if not domain or ".." in domain or " " in domain:
        return False, "invalid_domain"
    if not VIRUSTOTAL_API_KEY:
        if NO_API_BEHAVIOR == "allow":
            return True, "no_api_allow"
        return False, "no_api_block"
    # Placeholder: integração VirusTotal (GET /domains/{id} ou similar)
    # try: response = requests.get(f"https://www.virustotal.com/api/v3/domains/{domain}", headers={"x-apikey": VIRUSTOTAL_API_KEY})
    # Por enquanto retorna allow se tiver API key (implementar chamada real quando necessário)
    return True, "ok"


def main() -> int:
    """CLI: check_domain_reputation.py <domain>. Exit 0 = allow, 1 = block."""
    if len(sys.argv) < 2:
        print("Uso: check_domain_reputation.py <domínio>", file=sys.stderr)
        return 2
    domain = sys.argv[1]
    allow, reason = check_reputation(domain)
    if not allow:
        print(f"BLOCK\t{domain}\t{reason}", file=sys.stderr)
        return 1
    print(f"ALLOW\t{domain}\t{reason}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
