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
from typing import Optional
from app.core.config import get_settings

settings = get_settings()


class OpenClawClient:
    def __init__(self):
        self.base_url = settings.openclaw_gateway_url.rstrip("/")
        token = (settings.openclaw_gateway_token or "").strip()
        self.headers = {"Authorization": f"Bearer {token}"} if token else {}

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
                return r.json().get(
                    "items", r.json() if isinstance(r.json(), list) else []
                )
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
                return r.json()
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
            data = r.json()
            return data.get("items", data if isinstance(data, list) else [])

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
                return r.json()
        except Exception:
            return None


openclaw_client = OpenClawClient()
