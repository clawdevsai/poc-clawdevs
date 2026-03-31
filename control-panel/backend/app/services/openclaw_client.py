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

import httpx
import os
import logging
from typing import Any, Optional, AsyncGenerator, Dict
from app.core.config import get_settings

settings = get_settings()
logger = logging.getLogger(__name__)


class NemoClawClient:
    def __init__(self):
        configured_url = (
            getattr(settings, "nemoclaw_gateway_url", "").strip()
            or settings.openclaw_gateway_url.strip()
        )
        configured_token = (
            getattr(settings, "nemoclaw_gateway_token", "").strip()
            or settings.openclaw_gateway_token.strip()
        )
        self.base_url = configured_url.rstrip("/")
        token = configured_token
        self.headers = {"Authorization": f"Bearer {token}"}
        self.fallback_enabled = (
            os.getenv("NEMOCLAW_FALLBACK_ENABLED", "true").strip().lower() != "false"
        )

    def _runtime_candidates(self) -> list[str]:
        configured = [self.base_url]
        env_candidates = [
            os.getenv("NEMOCLAW_GATEWAY_URL", "").strip(),
            os.getenv("PANEL_NEMOCLAW_GATEWAY_URL", "").strip(),
            os.getenv("OPENCLAW_GATEWAY_URL", "").strip(),
            os.getenv("PANEL_OPENCLAW_GATEWAY_URL", "").strip(),
            "http://nemoclaw:18789",
            "http://openclaw:18789",
            "http://clawdevs-nemoclaw:18789",
            "http://clawdevs-openclaw:18789",
        ]
        dedup: list[str] = []
        for item in [*configured, *env_candidates]:
            value = item.rstrip("/")
            if value and value not in dedup:
                dedup.append(value)
        return dedup

    async def health(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.get(f"{self.base_url}/healthz", headers=self.headers)
                return r.status_code == 200
        except Exception:
            return False

    async def get_sessions(self, limit: int = 50) -> list:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get(
                    f"{self.base_url}/v1/sessions",
                    headers=self.headers,
                    params={"limit": limit},
                )
                if r.status_code != 200:
                    return []
                payload: Any = r.json()
                if isinstance(payload, list):
                    return payload
                if isinstance(payload, dict):
                    items = payload.get("items", [])
                    return items if isinstance(items, list) else []
                return []
        except Exception:
            return []

    async def get_session(self, session_id: str) -> Optional[dict]:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.get(
                    f"{self.base_url}/v1/sessions/{session_id}",
                    headers=self.headers,
                )
                if r.status_code != 200:
                    return None
                payload: Any = r.json()
                return payload if isinstance(payload, dict) else None
        except Exception:
            return None

    async def get_approvals(self, status: str = "pending") -> list:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(
                f"{self.base_url}/v1/approvals",
                headers=self.headers,
                params={"status": status},
            )
            if r.status_code != 200:
                return []
            data: Any = r.json()
            if isinstance(data, list):
                return data
            if isinstance(data, dict):
                items = data.get("items", [])
                return items if isinstance(items, list) else []
            return []

    async def decide_approval(
        self, approval_id: str, decision: str, justification: str = ""
    ) -> Optional[dict]:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                r = await client.post(
                    f"{self.base_url}/v1/approvals/{approval_id}/decide",
                    headers=self.headers,
                    json={"decision": decision, "justification": justification},
                )
                if r.status_code not in (200, 201):
                    return None
                payload: Any = r.json()
                return payload if isinstance(payload, dict) else None
        except Exception:
            return None

    async def stream_chat(
        self, agent_slug: str, message: str, session_key: str | None = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream chat completions from the gateway.
        Yields dict events: {"event": "delta"|"done"|"error", "data": str}
        """
        resolved_session_key = (session_key or "").strip() or f"agent:{agent_slug}:main"
        # NemoClaw runs OpenClaw inside the sandbox; the gateway contract still expects
        # `openclaw` or `openclaw/<agentId>` as model identifiers.
        model_prefix = os.getenv("NEMOCLAW_MODEL_PREFIX", "openclaw")
        payload = {
            "model": f"{model_prefix}/{agent_slug}",
            "messages": [{"role": "user", "content": message}],
            "stream": True,
        }
        headers = {
            **self.headers,
            "Content-Type": "application/json",
            "x-openclaw-session-key": resolved_session_key,
        }
        candidates = self._runtime_candidates()
        try:
            for idx, candidate in enumerate(candidates):
                try:
                    async with httpx.AsyncClient(timeout=None) as client:
                        async with client.stream(
                            "POST",
                            f"{candidate}/v1/chat/completions",
                            headers=headers,
                            json=payload,
                        ) as r:
                            if r.status_code != 200:
                                text = await r.aread()
                                detail = text.decode("utf-8", errors="ignore") or "upstream error"
                                if not self.fallback_enabled or idx == len(candidates) - 1:
                                    yield {"event": "error", "data": detail}
                                    return
                                logger.warning(
                                    "nemoclaw_stream_fallback status=%s candidate=%s",
                                    r.status_code,
                                    candidate,
                                )
                                continue

                            logger.info("nemoclaw_stream_provider candidate=%s", candidate)
                            async for line in r.aiter_lines():
                                if not line or not line.startswith("data:"):
                                    continue
                                data = line[5:].strip()
                                if data == "[DONE]":
                                    yield {"event": "done"}
                                    return
                                yield {"event": "delta", "data": data}
                except Exception:  # noqa: BLE001
                    if not self.fallback_enabled or idx == len(candidates) - 1:
                        raise
                    logger.warning("nemoclaw_stream_network_fallback candidate=%s", candidate)
        except Exception as exc:  # noqa: BLE001
            yield {"event": "error", "data": str(exc)}

    async def run_agent_turn(
        self, agent_slug: str, message: str, session_key: str | None = None
    ) -> str:
        """Run a non-streaming turn and return plain text output."""
        resolved_session_key = (session_key or "").strip() or f"agent:{agent_slug}:main"
        model_prefix = os.getenv("NEMOCLAW_MODEL_PREFIX", "openclaw")
        payload = {
            "model": f"{model_prefix}/{agent_slug}",
            "messages": [{"role": "user", "content": message}],
            "stream": False,
        }
        headers = {
            **self.headers,
            "Content-Type": "application/json",
            "x-openclaw-session-key": resolved_session_key,
        }
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.base_url}/v1/chat/completions",
                headers=headers,
                json=payload,
            )
            response.raise_for_status()
            body: Any = response.json()
            return _extract_openclaw_text(body)


def _extract_openclaw_text(body: Any) -> str:
    if isinstance(body, dict):
        if isinstance(body.get("output_text"), str):
            return body["output_text"]
        choices = body.get("choices")
        if isinstance(choices, list) and choices:
            first = choices[0]
            if isinstance(first, dict):
                message = first.get("message")
                if isinstance(message, dict):
                    content = message.get("content")
                    return _normalize_content(content)
                text = first.get("text")
                if isinstance(text, str):
                    return text
    return str(body)


def _normalize_content(content: Any) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts: list[str] = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
                continue
            if isinstance(item, dict):
                text = item.get("text")
                if isinstance(text, str):
                    parts.append(text)
        return "\n".join(parts)
    return str(content)


# Backward compatibility aliases while migrating callers progressively.
OpenClawClient = NemoClawClient
openclaw_client = NemoClawClient()
nemoclaw_client = openclaw_client
