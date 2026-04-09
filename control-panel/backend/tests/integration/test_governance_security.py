import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_governance_endpoints_require_auth(client: AsyncClient):
    """Verify that governance endpoints return 401 when no token is provided."""
    endpoints = [
        "/api/governance/constitution/rules",
        "/api/governance/cost/team-spending",
        "/api/governance/multi-repo/rules",
    ]

    for endpoint in endpoints:
        response = await client.get(endpoint)
        # It should return 401 because get_current_user dependency (via HTTPBearer) will fail first
        assert response.status_code == 401
        assert response.json()["detail"] in ["Not authenticated", "Could not validate credentials"]
