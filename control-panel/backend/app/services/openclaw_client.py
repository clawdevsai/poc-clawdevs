import httpx
from app.core.config import get_settings

settings = get_settings()


class OpenClawClient:
    def __init__(self):
        self.base_url = settings.openclaw_gateway_url
        self.headers = {"Authorization": f"Bearer {settings.openclaw_gateway_token}"}

    async def get_approvals(self, status: str = "pending") -> list:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{self.base_url}/v1/approvals",
                headers=self.headers,
                params={"status": status},
                timeout=10.0,
            )
            r.raise_for_status()
            return r.json().get("items", [])

    async def decide_approval(self, approval_id: str, decision: str, justification: str = "") -> dict:
        async with httpx.AsyncClient() as client:
            r = await client.post(
                f"{self.base_url}/v1/approvals/{approval_id}/decide",
                headers=self.headers,
                json={"decision": decision, "justification": justification},
                timeout=10.0,
            )
            r.raise_for_status()
            return r.json()

    async def get_sessions(self) -> list:
        async with httpx.AsyncClient() as client:
            r = await client.get(
                f"{self.base_url}/v1/sessions",
                headers=self.headers,
                timeout=10.0,
            )
            r.raise_for_status()
            return r.json().get("items", [])

    async def health(self) -> bool:
        try:
            async with httpx.AsyncClient() as client:
                r = await client.get(f"{self.base_url}/healthz", timeout=5.0)
                return r.status_code == 200
        except Exception:
            return False


openclaw = OpenClawClient()
