# Copyright (c) 2026 Diego Silva Morais <lukewaresoftwarehouse@gmail.com>
import pytest
from httpx import AsyncClient

@pytest.mark.asyncio
async def test_unauthenticated_access_to_sensitive_endpoints(client: AsyncClient):
    # Test endpoints that SHOULD NOT be public and should now return 401
    endpoints = [
        ("/agents", "GET"),
        ("/api/health/summary", "GET"),
        ("/api/governance/constitution/rules", "GET"),
        ("/api/memory/rag/search?query=test", "GET"),
    ]

    for path, method in endpoints:
        if method == "GET":
            response = await client.get(path)
        elif method == "POST":
            response = await client.post(path, json={})

        # After our fixes, these should return 401 Unauthorized
        print(f"Endpoint {method} {path} returned {response.status_code}")
        assert response.status_code == 401, f"Endpoint {path} should be secured!"
