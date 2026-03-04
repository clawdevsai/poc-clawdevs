#!/usr/bin/env python3
"""
Monitor de contingência cluster acéfalo (124).
Loop: verifica ceo:last_strategy_ts; se inativo por ACEFALO_TIMEOUT_MIN, dispara contingência
(branch efêmera, snapshot fila, pausa). Em seguida: health check a cada 5 min; após 3 ciclos OK,
executa retomada (checkout limpo, clear pausa). Notificação ao Diretor é assíncrona (log ou Telegram).
Ref: docs/06-operacoes.md, docs/issues/124-contingencia-cluster-acefalo.md
"""
import os
import sys
import time

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
if SCRIPT_DIR not in sys.path:
    sys.path.insert(0, SCRIPT_DIR)
from acefalo_redis import get_redis, get_last_strategy_ts, is_consumption_paused
from acefalo_contingency import run_contingency
from acefalo_retomada import run_retomada


ACEFALO_TIMEOUT_MIN = float(os.getenv("ACEFALO_TIMEOUT_MIN", "5"))
CHECK_INTERVAL_SEC = int(os.getenv("ACEFALO_MONITOR_CHECK_SEC", "60"))
HEALTH_CHECK_INTERVAL_SEC = int(os.getenv("ACEFALO_HEALTH_CHECK_INTERVAL_SEC", "300"))  # 5 min
STABLE_CYCLES = int(os.getenv("ACEFALO_STABLE_CYCLES", "3"))


def health_check_ok():
    """Testa conectividade (mesmo critério do heartbeat writer)."""
    try:
        import urllib.request
        url = os.getenv("ACEFALO_HEALTH_CHECK_URL", "https://www.google.com/generate_204")
        req = urllib.request.Request(url, method="HEAD")
        urllib.request.urlopen(req, timeout=10)
        return True
    except Exception:
        return False


def main():
    r = get_redis()
    print(f"[Acefalo] Monitor: timeout={ACEFALO_TIMEOUT_MIN} min, health_interval={HEALTH_CHECK_INTERVAL_SEC}s, stable_cycles={STABLE_CYCLES}")

    while True:
        if is_consumption_paused(r=r):
            # Modo pausa: health check a cada 5 min; 3 ciclos OK → retomada
            ok_count = 0
            while ok_count < STABLE_CYCLES:
                time.sleep(HEALTH_CHECK_INTERVAL_SEC)
                if health_check_ok():
                    ok_count += 1
                    print(f"[Acefalo] Health check OK ({ok_count}/{STABLE_CYCLES})")
                else:
                    ok_count = 0
                    print("[Acefalo] Health check falhou, reset contador")
            print("[Acefalo] Conectividade estável; executando retomada automática.")
            res = run_retomada(r=r)
            print(f"[Acefalo] Retomada: {res}")
            # TODO: notificação assíncrona ao Diretor (Telegram/digest)
        else:
            # Modo normal: verificar se heartbeat expirou
            last_ts = get_last_strategy_ts(r=r)
            now = time.time()
            if last_ts is not None:
                idle_sec = now - last_ts
                if idle_sec >= ACEFALO_TIMEOUT_MIN * 60:
                    print(f"[Acefalo] Timeout: sem heartbeat há {idle_sec:.0f}s. Disparando contingência.")
                    res = run_contingency(r=r)
                    print(f"[Acefalo] Contingência: {res}")
                    # TODO: notificação assíncrona ao Diretor
            else:
                # Nunca recebeu heartbeat: não disparar ainda (boot recente)
                pass
        time.sleep(CHECK_INTERVAL_SEC)


if __name__ == "__main__":
    main()
    sys.exit(0)
