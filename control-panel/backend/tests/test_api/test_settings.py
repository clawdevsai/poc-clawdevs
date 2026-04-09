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

"""Test suite for runtime settings API endpoints."""

import pytest
from httpx import AsyncClient
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

from app.models import RuntimeSettingAudit


class TestRuntimeSettings:
    """Test runtime settings endpoints."""

    @pytest.mark.asyncio
    async def test_get_runtime_settings(self, client: AsyncClient, auth_headers: dict):
        response = await client.get("/settings/runtime", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert "limits" in data
        assert "flags" in data
        assert "model_provider" in data
        assert "model_name" in data
        assert "agent_updates" in data
        assert "thresholds" in data

    @pytest.mark.asyncio
    async def test_update_runtime_settings_requires_confirm(
        self, client: AsyncClient, auth_headers: dict
    ):
        response = await client.put(
            "/settings/runtime",
            json={"model_name": "gpt-5.4"},
            headers=auth_headers,
        )
        assert response.status_code == 400

        response = await client.put(
            "/settings/runtime",
            json={"model_name": "gpt-5.4", "confirm_text": "CONFIRM"},
            headers=auth_headers,
        )
        assert response.status_code == 200

        response = await client.put(
            "/settings/runtime",
            json={"agent_updates": [{"agent_slug": "ceo", "enabled": False}]},
            headers=auth_headers,
        )
        assert response.status_code == 400

        response = await client.put(
            "/settings/runtime",
            json={
                "agent_updates": [{"agent_slug": "ceo", "enabled": False}],
                "confirm_text": "DISABLE",
            },
            headers=auth_headers,
        )
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_update_runtime_settings_audits_change(
        self,
        client: AsyncClient,
        auth_headers: dict,
        db_session: AsyncSession,
    ):
        response = await client.put(
            "/settings/runtime",
            json={
                "thresholds": {"db_pool_warning_pct": 70},
                "confirm_text": "CONFIRM",
            },
            headers=auth_headers,
        )
        assert response.status_code == 200

        audit_result = await db_session.exec(
            select(RuntimeSettingAudit).where(
                RuntimeSettingAudit.setting_key == "thresholds"
            )
        )
        audit = audit_result.first()
        assert audit is not None
        assert audit.new_value_json == {"db_pool_warning_pct": 70}
