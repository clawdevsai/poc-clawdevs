# Copyright (c) 2026 Diego Silva Morais <lukewaresoftwarehouse@gmail.com>
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_unauthenticated_access_to_sensitive_endpoints(client: AsyncClient):
    """Verify that sensitive endpoints return 401 when unauthenticated."""

    endpoints = [
        ("/agents", "GET"),
        ("/api/health/summary", "GET"),
        ("/api/governance/constitution/rules", "GET"),
        ("/api/memory/rag/search?query=test", "GET"),
    ]

    for url, method in endpoints:
        if method == "GET":
            response = await client.get(url)
        elif method == "POST":
            response = await client.post(url, json={})

        assert response.status_code == 401, f"Endpoint {url} should be protected but returned {response.status_code}"
