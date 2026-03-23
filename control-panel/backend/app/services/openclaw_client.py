import httpx
from typing import Optional
from app.core.config import get_settings

settings = get_settings()


class OpenClawClient:
    def __init__(self):
        self.base_url = settings.openclaw_gateway_url.rstrip("/")
        self.headers = {"Authorization": f"Bearer {settings.openclaw_gateway_token}"}

    async def health(self) -> bool:
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                r = await client.get(f"{self.base_url}/healthz", headers=self.headers)
                return r.status_code == 200
        except Exception:
            return False

    async def get_sessions(self, limit: int = 50) -> list:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(
                f"{self.base_url}/v1/sessions",
                headers=self.headers,
                params={"limit": limit},
            )
            if r.status_code != 200:
                return []
            return r.json().get("items", r.json() if isinstance(r.json(), list) else [])

    async def get_session(self, session_id: str) -> Optional[dict]:
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.get(
                f"{self.base_url}/v1/sessions/{session_id}",
                headers=self.headers,
            )
            if r.status_code != 200:
                return None
            return r.json()

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
        async with httpx.AsyncClient(timeout=10.0) as client:
            r = await client.post(
                f"{self.base_url}/v1/approvals/{approval_id}/decide",
                headers=self.headers,
                json={"decision": decision, "justification": justification},
            )
            if r.status_code not in (200, 201):
                return None
            return r.json()


openclaw_client = OpenClawClient()
