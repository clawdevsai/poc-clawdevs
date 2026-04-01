# Copyright (c) 2026 Diego Silva Morais <lukewaresoftwarehouse@gmail.com>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""
Circuit Breaker implementation for agent resilience.

Prevents cascading failures by opening the circuit when failure threshold is exceeded.
States: closed (normal), open (failing), half-open (testing recovery).
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, UTC
from enum import Enum
from typing import Callable, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    success_threshold: int = 2
    timeout_seconds: float = 60.0
    half_open_max_calls: int = 3


@dataclass
class CircuitBreakerMetrics:
    total_calls: int = 0
    successful_calls: int = 0
    failed_calls: int = 0
    last_failure_at: datetime | None = None
    last_success_at: datetime | None = None
    state_changed_at: datetime | None = None


class CircuitBreakerOpen(Exception):
    """Raised when circuit breaker is open and call is rejected."""

    def __init__(self, circuit_name: str, retry_after: float):
        self.circuit_name = circuit_name
        self.retry_after = retry_after
        super().__init__(
            f"Circuit '{circuit_name}' is open. Retry after {retry_after:.1f}s"
        )


class CircuitBreaker:
    def __init__(
        self,
        name: str,
        config: CircuitBreakerConfig | None = None,
    ):
        self.name = name
        self.config = config or CircuitBreakerConfig()
        self.state = CircuitState.CLOSED
        self._failure_count = 0
        self._success_count = 0
        self._half_open_calls = 0
        self.metrics = CircuitBreakerMetrics()
        self._lock = asyncio.Lock()

    async def call(
        self,
        func: Callable[..., T],
        *args,
        fallback: T | None = None,
        **kwargs,
    ) -> T:
        """Execute function with circuit breaker protection."""
        async with self._lock:
            if self.state == CircuitState.OPEN:
                if await self._should_attempt_reset():
                    await self._transition_to_half_open()
                else:
                    raise CircuitBreakerOpen(
                        self.name, self.config.timeout_seconds
                    )

            if self.state == CircuitState.HALF_OPEN:
                if self._half_open_calls >= self.config.half_open_max_calls:
                    raise CircuitBreakerOpen(
                        self.name, self.config.timeout_seconds
                    )
                self._half_open_calls += 1

        self.metrics.total_calls += 1

        try:
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)
            await self._on_success()
            return result
        except Exception as exc:
            await self._on_failure()
            if fallback is not None:
                logger.warning(
                    f"Circuit '{self.name}' fallback triggered: {exc}"
                )
                return fallback
            raise

    async def _on_success(self) -> None:
        """Handle successful call."""
        async with self._lock:
            self.metrics.successful_calls += 1
            self.metrics.last_success_at = datetime.now(UTC).replace(
                tzinfo=None
            )

            if self.state == CircuitState.HALF_OPEN:
                self._success_count += 1
                if self._success_count >= self.config.success_threshold:
                    await self._transition_to_closed()
            else:
                self._failure_count = 0

    async def _on_failure(self) -> None:
        """Handle failed call."""
        async with self._lock:
            self.metrics.failed_calls += 1
            self.metrics.last_failure_at = datetime.now(UTC).replace(
                tzinfo=None
            )
            self._failure_count += 1
            self._success_count = 0

            if self.state == CircuitState.HALF_OPEN:
                await self._transition_to_open()
            elif self._failure_count >= self.config.failure_threshold:
                await self._transition_to_open()

    async def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.metrics.state_changed_at is None:
            return True
        elapsed = (
            datetime.now(UTC).replace(tzinfo=None)
            - self.metrics.state_changed_at
        ).total_seconds()
        return elapsed >= self.config.timeout_seconds

    async def _transition_to_open(self) -> None:
        """Transition to OPEN state."""
        logger.warning(f"Circuit '{self.name}' opened after failures")
        self.state = CircuitState.OPEN
        self.metrics.state_changed_at = datetime.now(UTC).replace(tzinfo=None)

    async def _transition_to_half_open(self) -> None:
        """Transition to HALF_OPEN state."""
        logger.info(f"Circuit '{self.name}' attempting recovery (half-open)")
        self.state = CircuitState.HALF_OPEN
        self._half_open_calls = 0
        self._success_count = 0
        self.metrics.state_changed_at = datetime.now(UTC).replace(tzinfo=None)

    async def _transition_to_closed(self) -> None:
        """Transition to CLOSED state."""
        logger.info(f"Circuit '{self.name}' recovered (closed)")
        self.state = CircuitState.CLOSED
        self._failure_count = 0
        self._half_open_calls = 0
        self.metrics.state_changed_at = datetime.now(UTC).replace(tzinfo=None)

    def get_status(self) -> dict:
        """Get circuit breaker status."""
        return {
            "name": self.name,
            "state": self.state.value,
            "failure_count": self._failure_count,
            "success_count": self._success_count,
            "total_calls": self.metrics.total_calls,
            "successful_calls": self.metrics.successful_calls,
            "failed_calls": self.metrics.failed_calls,
            "last_failure_at": (
                self.metrics.last_failure_at.isoformat()
                if self.metrics.last_failure_at
                else None
            ),
            "last_success_at": (
                self.metrics.last_success_at.isoformat()
                if self.metrics.last_success_at
                else None
            ),
        }

    async def reset(self) -> None:
        """Manually reset the circuit breaker."""
        async with self._lock:
            await self._transition_to_closed()
            self._failure_count = 0
            self._success_count = 0
            self._half_open_calls = 0
            logger.info(f"Circuit '{self.name}' manually reset")


class CircuitBreakerRegistry:
    """Registry for managing multiple circuit breakers."""

    def __init__(self):
        self._breakers: dict[str, CircuitBreaker] = {}
        self._lock = asyncio.Lock()

    async def get_or_create(
        self,
        name: str,
        config: CircuitBreakerConfig | None = None,
    ) -> CircuitBreaker:
        """Get existing or create new circuit breaker."""
        async with self._lock:
            if name not in self._breakers:
                self._breakers[name] = CircuitBreaker(name, config)
            return self._breakers[name]

    async def get(self, name: str) -> CircuitBreaker | None:
        """Get circuit breaker by name."""
        return self._breakers.get(name)

    async def get_all_status(self) -> list[dict]:
        """Get status of all circuit breakers."""
        return [cb.get_status() for cb in self._breakers.values()]

    async def reset_all(self) -> None:
        """Reset all circuit breakers."""
        for cb in self._breakers.values():
            await cb.reset()


circuit_breaker_registry = CircuitBreakerRegistry()
