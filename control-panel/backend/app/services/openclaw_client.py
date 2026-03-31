from __future__ import annotations

from typing import Any, AsyncGenerator, Optional

import httpx

from app.core.config import get_settings


class NemoClawClient:
    def __init__(self, *, timeout_seconds: float = 30.0):
        self._settings = get_settings()
        self._timeout = timeout_seconds

    def _base_url(self) -> str:
        url = (self._settings.nemoclaw_gateway_url or self._settings.openclaw_gateway_url).rstrip(
            "/"
        )
        return url

    def _headers(self) -> dict[str, str]:
        token = (self._settings.nemoclaw_gateway_token or self._settings.openclaw_gateway_token or "").strip()
        if not token:
            return {}
        return {"Authorization": f"Bearer {token}"}

    async def health(self) -> bool:
        url = f"{self._base_url()}/healthz"
        try:
            async with httpx.AsyncClient(timeout=self._timeout) as client:
                resp = await client.get(url, headers=self._headers())
            return 200 <= resp.status_code < 400
        except Exception:
            return False

    async def run_agent_turn(
        self,
        agent_slug: str,
        message: str,
        *,
        session_key: Optional[str] = None,
    ) -> str:
        url = f"{self._base_url()}/v1/chat/completions"
        payload: dict[str, Any] = {
            "model": f"panel/{agent_slug}",
            "stream": False,
            "messages": [{"role": "user", "content": message}],
        }
        if session_key:
            payload["metadata"] = {"session_key": session_key}
        async with httpx.AsyncClient(timeout=self._timeout) as client:
            resp = await client.post(url, json=payload, headers=self._headers())
            resp.raise_for_status()
            data = resp.json()
        if isinstance(data, dict):
            output_text = data.get("output_text")
            if isinstance(output_text, str):
                return output_text
            choices = data.get("choices")
            if isinstance(choices, list) and choices:
                msg = choices[0].get("message") if isinstance(choices[0], dict) else None
                if isinstance(msg, dict):
                    content = msg.get("content")
                    if isinstance(content, str):
                        return content
        return ""

    async def stream_chat(
        self, *, agent_slug: str, message: str, session_key: str
    ) -> AsyncGenerator[dict[str, Any], None]:
        try:
            text = await self.run_agent_turn(
                agent_slug=agent_slug, message=message, session_key=session_key
            )
            if text:
                yield {"event": "delta", "data": text}
            yield {"event": "done", "data": None}
        except Exception as e:
            yield {"event": "error", "data": str(e)}

    async def decide_approval(self, approval_id: str, decision: str, justification: str) -> None:
        return None

    async def get_sessions(self, *, limit: int = 1000) -> list[dict[str, Any]]:
        return []

    async def get_session(self, session_id: str) -> dict[str, Any]:
        return {}


nemoclaw_client = NemoClawClient()

__all__ = ["NemoClawClient", "nemoclaw_client"]
