#!/usr/bin/env python3
"""
Heartbeat do CEO/orquestrador para contingência cluster acéfalo (124).
Atualiza ceo:last_strategy_ts no Redis somente quando o health check externo passar
(ex.: conectividade com API nuvem). Rodar no mesmo ambiente que o CEO/PO (gateway).
Quando a internet cair, este script deixa de atualizar o key; o monitor local detecta timeout.
Ref: docs/06-operacoes.md, docs/issues/124-contingencia-cluster-acefalo.md
"""
import os
import sys
import time
import urllib.request

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
from acefalo_redis import get_redis, touch_heartbeat


# URL para testar conectividade (sem consumir tokens). Ex.: HEAD request a API ou endpoint de saúde.
HEALTH_CHECK_URL = os.getenv("ACEFALO_HEALTH_CHECK_URL", "https://www.google.com/generate_204")
INTERVAL_SEC = int(os.getenv("ACEFALO_HEARTBEAT_INTERVAL_SEC", "60"))
TIMEOUT_SEC = int(os.getenv("ACEFALO_HEALTH_CHECK_TIMEOUT_SEC", "10"))


def check_connectivity() -> bool:
    """Retorna True se a URL responder (conectividade OK)."""
    try:
        req = urllib.request.Request(HEALTH_CHECK_URL, method="HEAD")
        urllib.request.urlopen(req, timeout=TIMEOUT_SEC)
        return True
    except Exception:
        return False


def main():
    r = get_redis()
    print(f"[Heartbeat] URL={HEALTH_CHECK_URL} interval={INTERVAL_SEC}s")
    while True:
        if check_connectivity():
            touch_heartbeat(r=r)
            print(f"[Heartbeat] OK @ {time.strftime('%Y-%m-%d %H:%M:%S')}")
        else:
            print(f"[Heartbeat] No connectivity, skipping update")
        time.sleep(INTERVAL_SEC)


if __name__ == "__main__":
    main()
    sys.exit(0)
