"""
ClawDevs — Orchestrator Gateway
Controla o fluxo de eventos entre agentes via Redis Streams.
Implementa:
  - Token Bucket para eventos de estratégia do CEO (max 5/hora)
  - Degradação por eficiência (razão CEO/PO)
  - Pipeline de truncamento de contexto na borda
  - Roteamento CEO/PO (nuvem vs local)
  - Monitoramento de cluster acéfalo

Referências:
  docs/issues/126-token-bucket-degradacao-eficiencia.md
  docs/issues/129-ceo-vfm-fitness-no-raciocinio.md
  docs/03-arquitetura.md (Estágio de borda)
  docs/07-configuracao-e-prompts.md (FinOps Gateway)
"""

import os
import time
import logging
import threading
from typing import Optional
from dataclasses import dataclass, field
from orchestrator.gateway.balancer import DynamicBalancer

logger = logging.getLogger("clawdevs.gateway")


def _get_redis():
    import redis as redis_lib

    return redis_lib.Redis(
        host=os.getenv("REDIS_HOST", "redis-service"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        db=int(os.getenv("REDIS_DB", "0")),
        decode_responses=True,
    )


# ─── Token Bucket (Issue 126) ────────────────────────────────────────────────


class TokenBucket:
    """Controla a taxa de eventos de estratégia do CEO.
    Máx. 5 eventos de estratégia por hora por padrão.
    Implementado no Redis para persistência entre reinicializações.
    """

    def __init__(
        self,
        r,
        key: str = "token_bucket:ceo_strategy",
        limit: int = 5,
        window_seconds: int = 3600,
    ):
        self.r = r
        self.key = key
        self.limit = int(os.getenv("TOKEN_BUCKET_STRATEGY_LIMIT", str(limit)))
        self.window = int(os.getenv("TOKEN_BUCKET_WINDOW_SECONDS", str(window_seconds)))

    def allow(self) -> bool:
        """Retorna True se o evento de estratégia pode prosseguir; False se interceptar."""
        pipe = self.r.pipeline()
        now = int(time.time())
        window_start = now - self.window

        # Usar Sorted Set com timestamp como score
        pipe.zremrangebyscore(self.key, "-inf", window_start)
        pipe.zcard(self.key)
        pipe.zadd(self.key, {str(now): now})
        pipe.expire(self.key, self.window + 60)
        results = pipe.execute()

        count_before = results[1]
        if count_before >= self.limit:
            # Remove o evento que acabou de adicionar (foi rejeitado)
            self.r.zrem(self.key, str(now))
            logger.warning(
                "TOKEN BUCKET: Evento de estratégia bloqueado. "
                "Contagem na janela: %d/%d (janela: %ds)",
                count_before,
                self.limit,
                self.window,
            )
            return False

        logger.debug(
            "Token bucket: %d/%d eventos na janela.", count_before + 1, self.limit
        )
        return True


# ─── Degradação por Eficiência (Issue 126) ───────────────────────────────────


class EfficiencyDegradation:
    """Monitora razão ideias CEO vs tarefas aprovadas pelo PO.
    Se razão abaixo do limiar, bloqueia nuvem para CEO e força CPU (Phi-3).
    """

    RATIO_KEY = "efficiency:ceo_ideas_total"
    APPROVED_KEY = "efficiency:po_approved_total"
    DEGRADED_KEY = "efficiency:ceo_degraded"

    def __init__(self, r, min_ratio: float = 0.3):
        self.r = r
        self.min_ratio = float(os.getenv("CEO_EFFICIENCY_MIN_RATIO", str(min_ratio)))

    def record_ceo_idea(self) -> None:
        self.r.incr(self.RATIO_KEY)

    def record_po_approved(self) -> None:
        self.r.incr(self.APPROVED_KEY)

    def is_degraded(self) -> bool:
        total = int(self.r.get(self.RATIO_KEY) or 0)
        approved = int(self.r.get(self.APPROVED_KEY) or 0)
        if total < 10:
            return False  # Poucos dados — não degradar ainda
        ratio = approved / total
        degraded = ratio < self.min_ratio
        if degraded:
            self.r.set(self.DEGRADED_KEY, "1", ex=3600)
            logger.warning(
                "DEGRADAÇÃO: CEO em modo local. Razão aprovação: %.2f (mínimo: %.2f)",
                ratio,
                self.min_ratio,
            )
        return degraded

    def get_model_for_ceo(self) -> str:
        """Retorna modelo correto para CEO com base na eficiência."""
        if self.is_degraded():
            return "phi3:mini"  # Forçar local em CPU
        return os.getenv("CEO_CLOUD_MODEL", "gemini-1.5-pro")


# ─── Truncamento de contexto na borda (Issues 041, 003-arquitetura) ──────────


class ContextTruncator:
    """Aplica truncamento de tokens na borda antes de enviar ao provedor.
    Garante que nenhum agente receba carga que estoure a VRAM ou a cota de API.
    """

    def __init__(self, max_tokens: int = 4000):
        self.max_tokens = int(os.getenv("GATEWAY_MAX_TOKENS", str(max_tokens)))

    def estimate_tokens(self, text: str) -> int:
        """Estimativa simples: 1 token ≈ 4 caracteres."""
        return len(text) // 4

    def truncate(self, payload: str, keep_header_chars: int = 500) -> tuple[str, bool]:
        """Trunca payload se exceder max_tokens. Mantém cabeçalho + causa raiz.
        Retorna (payload_truncado, foi_truncado).
        """
        estimated = self.estimate_tokens(payload)
        if estimated <= self.max_tokens:
            return payload, False

        # Manter cabeçalho (contexto inicial) e truncar meio
        max_chars = int(self.max_tokens * 4)
        tail_len = max_chars - keep_header_chars
        header = payload[:keep_header_chars]
        tail = payload[-tail_len:] if tail_len > 0 else ""
        truncated = f"{header}\n\n[... CONTEÚDO TRUNCADO — contexto reduzido para limite de {self.max_tokens} tokens ...]\n\n{tail}"
        logger.info(
            "Payload truncado: %d → %d tokens estimados.",
            estimated,
            self.estimate_tokens(truncated),
        )
        return truncated, True

    def protect_acceptance_criteria(self, payload: str) -> tuple[str, str]:
        """Separa critérios de aceite do payload principal.
        Critérios marcados com <!-- CRITERIOS_ACEITE --> nunca são truncados.
        Issue 041: validação reversa do PO.
        """
        import re

        pattern = r"<!-- CRITERIOS_ACEITE -->(.*?)<!-- /CRITERIOS_ACEITE -->"
        criteria_blocks = re.findall(pattern, payload, re.DOTALL)
        criteria = "\n".join(criteria_blocks)
        # Remove blocos de critérios do payload principal (para truncamento)
        clean_payload = re.sub(
            pattern, "[CRITERIOS_PROTEGIDOS]", payload, flags=re.DOTALL
        )
        return clean_payload, criteria


# ─── VFM Score CEO (Issue 129) ───────────────────────────────────────────────


@dataclass
class VFMScore:
    """Value-for-Money score gerado pelo CEO antes de enviar evento de estratégia.
    Formato do artefato VFM_CEO_score.json.
    """

    event_id: str
    estimated_tokens_cost: int
    estimated_hours_saved: float
    estimated_dollar_cost: float
    benefit_score: float
    net_score: float
    threshold: float = 0.0
    approved: bool = field(init=False)

    def __post_init__(self):
        self.approved = self.net_score >= self.threshold

    def to_dict(self) -> dict:
        return {
            "event_id": self.event_id,
            "estimated_tokens_cost": self.estimated_tokens_cost,
            "estimated_hours_saved": self.estimated_hours_saved,
            "estimated_dollar_cost": self.estimated_dollar_cost,
            "benefit_score": self.benefit_score,
            "net_score": self.net_score,
            "threshold": self.threshold,
            "approved": self.approved,
        }

    @classmethod
    def from_json(cls, data: dict) -> "VFMScore":
        return cls(
            event_id=data["event_id"],
            estimated_tokens_cost=data["estimated_tokens_cost"],
            estimated_hours_saved=data["estimated_hours_saved"],
            estimated_dollar_cost=data["estimated_dollar_cost"],
            benefit_score=data["benefit_score"],
            net_score=data["net_score"],
            threshold=data.get("threshold", 0.0),
        )


# ─── Orçamento de Degradação (Issue 017) ────────────────────────────────────


class DegradationBudget:
    """Monitora eventos de 5º strike e aprovações por omissão cosmética.
    Se > 10-15% das tarefas do sprint caírem nessa rota → loop de consenso → freio de mão.
    """

    FIFTH_STRIKE_KEY = "degradation:fifth_strike_count"
    COSMETIC_APPROVAL_KEY = "degradation:cosmetic_approval_count"
    SPRINT_TOTAL_KEY = "degradation:sprint_total"
    BRAKE_KEY = "degradation:emergency_brake_active"

    def __init__(self, r, threshold_pct: float = 0.12):
        self.r = r
        self.threshold = float(
            os.getenv("DEGRADATION_THRESHOLD_PCT", str(threshold_pct))
        )

    def record_fifth_strike(self):
        self.r.incr(self.FIFTH_STRIKE_KEY)
        self._check_budget()

    def record_cosmetic_approval(self):
        self.r.incr(self.COSMETIC_APPROVAL_KEY)
        self._check_budget()

    def record_task_completed(self):
        self.r.incr(self.SPRINT_TOTAL_KEY)

    def _check_budget(self):
        total = int(self.r.get(self.SPRINT_TOTAL_KEY) or 0)
        if total < 10:
            return
        escapes = int(self.r.get(self.FIFTH_STRIKE_KEY) or 0)
        escapes += int(self.r.get(self.COSMETIC_APPROVAL_KEY) or 0)
        ratio = escapes / total
        if ratio >= self.threshold:
            self._trigger_consensus_loop(ratio)

    def _trigger_consensus_loop(self, ratio: float):
        """Aciona loop de consenso pré-freio de mão (QA + Architect)."""
        logger.critical(
            "ORÇAMENTO DE DEGRADAÇÃO: %.1f%% das tarefas em rota de fuga (limite: %.1f%%). "
            "Acionando loop de consenso (QA + Architect).",
            ratio * 100,
            self.threshold * 100,
        )
        # Publica evento para QA e Architect iniciarem loop de consenso
        r = self.r
        r.xadd(
            "degradation:consensus_trigger",
            {
                "ratio": str(ratio),
                "timestamp": str(int(time.time())),
                "action": "consensus_loop",
            },
        )

    def trigger_emergency_brake(self):
        """Freio de mão: pausa a esteira. Acionado pelo DevOps se loop de consenso falhar."""
        self.r.set(self.BRAKE_KEY, "1")
        logger.critical(
            "FREIO DE MÃO ativado. Esteira pausada. Aguardando comando explícito de desbloqueio."
        )

    def is_brake_active(self) -> bool:
        return bool(self.r.get(self.BRAKE_KEY))


# ─── Heartbeat / Cluster Acéfalo (Issues 124) ────────────────────────────────


class HeadblessClusterWatchdog:
    """Monitora heartbeat do CEO no Redis.
    Se nenhum comando estratégico do CEO em > 5 min → contingência cluster acéfalo.
    """

    CEO_HEARTBEAT_KEY = "heartbeat:ceo_last_command"
    TIMEOUT_KEY = "heartbeat:ceo_timeout_seconds"
    RECOVERY_ACTIVE_KEY = "heartbeat:recovery_active"

    def __init__(self, r, timeout_seconds: int = 300):
        self.r = r
        self.timeout = int(
            os.getenv("HEARTBEAT_CEO_TIMEOUT_SECONDS", str(timeout_seconds))
        )
        self._running = False
        self._thread: Optional[threading.Thread] = None
        self.consecutive_stable = 0

    def record_ceo_command(self):
        """Chamado sempre que o CEO envia um comando estratégico."""
        self.r.set(self.CEO_HEARTBEAT_KEY, str(int(time.time())), ex=self.timeout * 2)

    def start(self):
        self._running = True
        thread = threading.Thread(target=self._watch_loop, daemon=True)
        self._thread = thread
        thread.start()
        logger.info(
            "Watchdog cluster acéfalo iniciado (timeout CEO: %ds).", self.timeout
        )

    def stop(self):
        self._running = False

    def _watch_loop(self):
        while self._running:
            time.sleep(60)  # Verificar a cada 1 min
            last_cmd = self.r.get(self.CEO_HEARTBEAT_KEY)
            if last_cmd is None:
                elapsed = self.timeout + 1
            else:
                elapsed = int(time.time()) - int(last_cmd)

            if elapsed > self.timeout:
                if not self.r.get(self.RECOVERY_ACTIVE_KEY):
                    logger.warning(
                        "Cluster acéfalo detectado: %ds sem comando CEO (limite: %ds). "
                        "Acionando contingência local.",
                        elapsed,
                        self.timeout,
                    )
                    self._trigger_headless_failsafe()
            else:
                # Verificar se está em recuperação e conectividade voltou
                if self.r.get(self.RECOVERY_ACTIVE_KEY):
                    self.consecutive_stable += 1
                    logger.info(
                        "Conectividade estável: %d/3 ciclos. CEO ativo há %ds.",
                        self.consecutive_stable,
                        elapsed,
                    )
                    if self.consecutive_stable >= 3:
                        self._trigger_auto_resume()
                        self.consecutive_stable = 0
                else:
                    self.consecutive_stable = 0

    def _trigger_headless_failsafe(self):
        """Aciona protocolo de contingência: commit em branch efêmera + pausa GPU."""
        import datetime

        timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
        branch_name = f"recovery-failsafe-{timestamp}"
        self.r.set(self.RECOVERY_ACTIVE_KEY, "1")
        self.r.xadd(
            "devops:emergency",
            {
                "action": "headless_failsafe",
                "branch": branch_name,
                "timestamp": str(int(time.time())),
                "reason": "ceo_timeout",
            },
        )
        logger.critical(
            "Contingência cluster acéfalo: branch efêmera '%s' solicitada.", branch_name
        )

    def _trigger_auto_resume(self):
        """Retomada automática após 3 ciclos estáveis (sem comando humano)."""
        self.r.delete(self.RECOVERY_ACTIVE_KEY)
        self.r.xadd(
            "devops:emergency",
            {
                "action": "auto_resume",
                "timestamp": str(int(time.time())),
                "reason": "connectivity_restored_3_cycles",
            },
        )
        logger.info(
            "Retomada automática acionada (3 ciclos estáveis). Nenhuma intervenção humana necessária."
        )


# ─── Gateway principal ───────────────────────────────────────────────────────


class Gateway:
    """Gateway central do ClawDevs.
    Controla todos os eventos antes de chegarem aos agentes.
    """

    def __init__(self):
        self.r = _get_redis()
        self.token_bucket = TokenBucket(self.r)
        self.efficiency = EfficiencyDegradation(self.r)
        self.truncator = ContextTruncator()
        self.degradation_budget = DegradationBudget(self.r)
        self.watchdog = HeadblessClusterWatchdog(self.r)
        self.balancer = DynamicBalancer(self.r)

    def start(self):
        self.watchdog.start()
        logger.info("Gateway ClawDevs iniciado.")

    def process_strategy_event(self, event: dict) -> Optional[dict]:
        """Processa evento de estratégia do CEO.
        Verifica VFM Score, Token Bucket e Degradação por Eficiência.
        """
        event_id = event.get("event_id", "unknown")

        # 1. Verificar VFM Score (deve vir no payload pelo CEO)
        vfm_data = event.get("vfm_score")
        if vfm_data:
            vfm = VFMScore.from_json(vfm_data)
            if not vfm.approved:
                logger.info(
                    "VFM Score negativo (%.2f < %.2f): evento %s descartado antes do Gateway.",
                    vfm.net_score,
                    vfm.threshold,
                    event_id,
                )
                return None

        # 2. Token Bucket
        if not self.token_bucket.allow():
            self.r.xadd(
                "ceo:rejected",
                {
                    "event_id": event_id,
                    "reason": "token_bucket_exceeded",
                    "timestamp": str(int(time.time())),
                },
            )
            return None

        # 3. Registrar no modelo de eficiência
        self.efficiency.record_ceo_idea()
        self.watchdog.record_ceo_command()

        # 4. Truncamento de contexto
        payload = event.get("payload", "")
        if payload:
            clean_payload, criteria = self.truncator.protect_acceptance_criteria(
                payload
            )
            truncated_payload, was_truncated = self.truncator.truncate(clean_payload)
            event["payload"] = truncated_payload
            if criteria:
                event["acceptance_criteria"] = criteria  # Payload duplo (não truncado)
            if was_truncated:
                event["context_truncated"] = True

        # 5. Roteamento Inteligente (Nuvem vs GPU vs CPU)
        agent_role = event.get("agent_role", "CEO")
        priority = event.get("priority", 1)
        tier = self.balancer.decide_placement(agent_role, priority)
        event["tier"] = tier
        event["model"] = self.balancer.get_model_for_tier(tier, agent_role)

        logger.info(
            "Evento %s roteado para TIER=%s MODEL=%s", event_id, tier, event["model"]
        )

        return event

    def process_po_approval(self, task_id: str):
        """Registra aprovação do PO (tarefas aprovadas para desenvolvimento)."""
        self.efficiency.record_po_approved()
        self.degradation_budget.record_task_completed()

    def process_fifth_strike(self, task_id: str, reason: str):
        """Registra 5º strike de uma tarefa."""
        self.degradation_budget.record_fifth_strike()
        logger.warning("5º Strike registrado: tarefa %s. Razão: %s", task_id, reason)

    def is_brake_active(self) -> bool:
        return self.degradation_budget.is_brake_active()


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    gw = Gateway()
    gw.start()
    logger.info("Gateway rodando. Pressione Ctrl+C para parar.")
    try:
        while True:
            time.sleep(10)
    except KeyboardInterrupt:
        gw.watchdog.stop()
        logger.info("Gateway encerrado.")
