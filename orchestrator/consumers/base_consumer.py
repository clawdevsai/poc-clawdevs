"""
ClawDevs — Consumer Base (Redis Streams)
Classe base para todos os agentes consumirem eventos do Redis Streams.
Implementa semântica idempotente: ACK apenas após conclusão em disco.
Implementa Consumer Groups e slot único de revisão (pipeline explícito).

Referências:
  docs/issues/005-redis-streams-estado-global.md
  docs/issues/007-consumer-groups-fila-prioridade.md
  docs/03-arquitetura.md (Stream de eventos, Semântica idempotente)
"""

import os
import time
import logging
import json
import signal
import sys
from abc import ABC, abstractmethod
from typing import Optional

logger = logging.getLogger("clawdevs.consumer")


def _get_redis():
    import redis as redis_lib

    return redis_lib.Redis(
        host=os.getenv("REDIS_HOST", "redis-service"),
        port=int(os.getenv("REDIS_PORT", "6379")),
        db=int(os.getenv("REDIS_DB", "0")),
        decode_responses=True,
    )


class BaseConsumer(ABC):
    """Classe base para agentes consumidores de Redis Streams.

    Implementa:
    - Consumer Groups (XREADGROUP) para distribuição de eventos
    - Semântica idempotente: ACK apenas após conclusão em disco
    - Reentrega de eventos não confirmados (XAUTOCLAIM)
    - Graceful shutdown
    - Heartbeat para detecção de agente preso
    """

    def __init__(
        self,
        stream_name: Optional[str] = None,
        consumer_group: Optional[str] = None,
        consumer_name: Optional[str] = None,
    ):
        self.r = _get_redis()
        self.stream_name = stream_name or os.getenv(
            "REDIS_STREAM_INPUT", "task:backlog"
        )
        self.consumer_group = consumer_group or os.getenv(
            "REDIS_CONSUMER_GROUP", f"cg-{self.AGENT_NAME.lower()}"
        )
        self.consumer_name = consumer_name or os.getenv(
            "POD_NAME", f"{self.AGENT_NAME.lower()}-0"
        )
        self.output_stream = os.getenv("REDIS_STREAM_OUTPUT", "")
        self._running = True
        self._ensure_group()
        self._register_signal_handlers()

    AGENT_NAME = "BaseAgent"
    BLOCK_MS = 5000  # Aguardar 5s por eventos

    def _ensure_group(self):
        """Cria o consumer group se não existir."""
        try:
            self.r.xgroup_create(
                self.stream_name,
                self.consumer_group,
                id="$",
                mkstream=True,
            )
            logger.info(
                "Consumer group '%s' criado no stream '%s'.",
                self.consumer_group,
                self.stream_name,
            )
        except Exception as e:
            if "BUSYGROUP" in str(e):
                logger.debug("Consumer group '%s' já existe.", self.consumer_group)
            else:
                logger.error("Erro ao criar consumer group: %s", e)

    def _register_signal_handlers(self):
        signal.signal(signal.SIGTERM, self._graceful_shutdown)
        signal.signal(signal.SIGINT, self._graceful_shutdown)

    def _graceful_shutdown(self, *_):
        logger.info("[%s] Sinal de shutdown recebido. Finalizando...", self.AGENT_NAME)
        self._running = False
        sys.exit(0)

    def _reclaim_pending(self, min_idle_ms: int = 60000):
        """Reclama mensagens pendentes (não ACK'adas) por mais de min_idle_ms.
        Garante que mensagens não confirmadas sejam reprocessadas.
        """
        try:
            result = self.r.xautoclaim(
                self.stream_name,
                self.consumer_group,
                self.consumer_name,
                min_idle_ms,
                "0-0",
                count=5,
            )
            messages = (
                result[1]
                if isinstance(result, (list, tuple)) and len(result) > 1
                else []
            )
            if messages:
                logger.info(
                    "[%s] Reclamando %d mensagens pendentes.",
                    self.AGENT_NAME,
                    len(messages),
                )
                return messages
        except Exception as e:
            logger.debug("XAUTOCLAIM não disponível ou erro: %s", e)
        return []

    def run(self):
        """Loop principal: consome eventos e processa com semântica idempotente."""
        logger.info(
            "[%s] Iniciado. Escutando stream '%s' no grupo '%s'.",
            self.AGENT_NAME,
            self.stream_name,
            self.consumer_group,
        )

        while self._running:
            # 1. Verificar se há mensagens pendentes não ACK'adas (de reinicializações anteriores)
            pending = self._reclaim_pending()
            messages = pending or []

            # 2. Ler novas mensagens se não há pendentes
            if not messages:
                try:
                    result = self.r.xreadgroup(
                        self.consumer_group,
                        self.consumer_name,
                        {self.stream_name: ">"},
                        count=1,
                        block=self.BLOCK_MS,
                    )
                    if result:
                        messages = result[0][
                            1
                        ]  # [(stream_name, [(msg_id, data), ...])]
                except Exception as e:
                    logger.error("[%s] Erro ao ler stream: %s", self.AGENT_NAME, e)
                    time.sleep(5)
                    continue

            if not messages:
                continue

            for msg_id, data in messages:
                logger.info("[%s] Processando evento: %s", self.AGENT_NAME, msg_id)
                try:
                    # Processar evento
                    self.process(msg_id, data)
                    # ACK apenas APÓS conclusão bem-sucedida em disco
                    # (Semântica idempotente: Issue 005)
                    self.r.xack(self.stream_name, self.consumer_group, msg_id)
                    logger.info(
                        "[%s] Evento %s confirmado (ACK).", self.AGENT_NAME, msg_id
                    )
                except Exception as exc:
                    logger.error(
                        "[%s] Erro no processamento do evento %s: %s. "
                        "Mensagem NÃO confirmada — será reentregue.",
                        self.AGENT_NAME,
                        msg_id,
                        exc,
                    )
                    # Não envia ACK → mensagem permanece pendente e é reentregue

    @abstractmethod
    def process(self, msg_id: str, data: dict) -> None:
        """Processa um evento do stream. Implementar em cada agente.
        ATENÇÃO: Envio de ACK é automático após retorno sem exceção.
        Se houver falha, levante uma exceção para NÃO confirmar o ACK.
        """
        raise NotImplementedError

    def publish(self, stream: str, data: dict) -> str:
        """Publica evento em outro stream."""
        msg_id = self.r.xadd(stream, data)
        logger.debug(
            "[%s] Evento publicado em '%s': %s", self.AGENT_NAME, stream, msg_id
        )
        return msg_id

    def get_state(self, key: str) -> Optional[str]:
        """Lê estado do 'blackboard' global (Redis chaves)."""
        return self.r.get(key)

    def set_state(
        self, key: str, value: str, ttl_seconds: Optional[int] = None
    ) -> None:
        """Grava estado no blackboard. TTL automático para working buffer."""
        if ttl_seconds:
            self.r.setex(key, ttl_seconds, value)
        else:
            self.r.set(key, value)

    def set_state_json(
        self, key: str, data: dict, ttl_seconds: Optional[int] = 86400
    ) -> None:
        """Grava estado JSON com TTL padrão de 24h (working buffer)."""
        self.set_state(key, json.dumps(data), ttl_seconds=ttl_seconds)

    def get_state_json(self, key: str) -> Optional[dict]:
        """Lê estado JSON do blackboard."""
        value = self.get_state(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return None
        return None
