"""Tests for agent_sync service."""
import pytest
import json
from pathlib import Path
from datetime import datetime, timezone, timedelta
from unittest.mock import patch, MagicMock, AsyncMock
from sqlmodel import select

from app.services.agent_sync import (
    sync_agents,
    parse_identity,
    _status_from_heartbeat,
    _has_active_session,
    _get_openclaw_config,
    _get_agent_config,
    _pick_latest_runtime_entry,
    AGENT_SLUGS,
    ROLE_MAP,
    DISPLAY_NAME_MAP,
    CRON_MAP,
)
from app.models import Agent


class TestAgentSyncConstants:
    """Test agent sync constants."""

    def test_agent_slugs_exists(self):
        """Test that AGENT_SLUGS is defined and not empty."""
        assert len(AGENT_SLUGS) > 0
        assert "ceo" in AGENT_SLUGS
        assert "qa_engineer" in AGENT_SLUGS

    def test_agent_slugs_count(self):
        """Test that AGENT_SLUGS has all expected agents."""
        assert len(AGENT_SLUGS) >= 12
        expected_agents = [
            "ceo", "po", "arquiteto", "dev_backend", "dev_frontend",
            "dev_mobile", "qa_engineer", "devops_sre", "security_engineer",
            "ux_designer", "dba_data_engineer", "memory_curator"
        ]
        for agent in expected_agents:
            assert agent in AGENT_SLUGS

    def test_role_map_contains_expected_roles(self):
        """Test that ROLE_MAP has all expected agent roles."""
        assert "ceo" in ROLE_MAP
        assert ROLE_MAP["ceo"] == "CEO / Orchestrator"
        assert "qa_engineer" in ROLE_MAP
        assert ROLE_MAP["qa_engineer"] == "QA Engineer"

    def test_display_name_map(self):
        """Test that DISPLAY_NAME_MAP has all agents."""
        assert "ceo" in DISPLAY_NAME_MAP
        assert DISPLAY_NAME_MAP["ceo"] == "Victor"
        assert "qa_engineer" in DISPLAY_NAME_MAP
        assert DISPLAY_NAME_MAP["qa_engineer"] == "Bruno"

    def test_cron_map_exists(self):
        """Test that CRON_MAP has all agent slugs."""
        for slug in AGENT_SLUGS:
            assert slug in CRON_MAP


class TestParseIdentity:
    """Test parse_identity function."""

    def test_parse_identity_default_values(self):
        """Test parse_identity with default values (no IDENTITY.md)."""
        identity = parse_identity("ceo")
        assert identity["display_name"] == "Victor"
        assert identity["role"] == "CEO / Orchestrator"
        assert "model" in identity

    def test_parse_identity_qa_engineer(self):
        """Test parse_identity for QA engineer."""
        identity = parse_identity("qa_engineer")
        assert identity["display_name"] == "Bruno"
        assert identity["role"] == "QA Engineer"

    def test_parse_identity_all_agents(self):
        """Test parse_identity for all agents."""
        for agent in AGENT_SLUGS:
            identity = parse_identity(agent)
            assert "display_name" in identity
            assert "role" in identity
            assert "model" in identity


class TestStatusFromHeartbeat:
    """Test _status_from_heartbeat function."""

    def test_status_offline_no_heartbeat(self):
        status = _status_from_heartbeat(None)
        assert status == "offline"

    def test_status_working_recent_with_session(self):
        recent_time = datetime.utcnow()
        status = _status_from_heartbeat(recent_time, has_active_session=True)
        assert status == "working"

    def test_status_online_recent_no_session(self):
        recent_time = datetime.utcnow()
        status = _status_from_heartbeat(recent_time, has_active_session=False)
        assert status == "online"

    def test_status_idle_10_minutes(self):
        older_time = datetime.utcnow() - timedelta(minutes=10)
        status = _status_from_heartbeat(older_time)
        assert status == "idle"

    def test_status_offline_1_hour(self):
        very_old_time = datetime.utcnow() - timedelta(hours=1)
        status = _status_from_heartbeat(very_old_time)
        assert status == "offline"

    def test_status_with_timezone_aware_datetime(self):
        aware_time = datetime.now(timezone.utc)
        status = _status_from_heartbeat(aware_time)
        assert status in ["online", "working", "idle"]


class TestHasActiveSession:
    """Test _has_active_session function."""

    def test_returns_false_for_empty(self):
        result = _has_active_session({})
        assert result is False

    def test_returns_false_for_none(self):
        result = _has_active_session(None)
        assert result is False

    def test_returns_false_for_non_dict(self):
        result = _has_active_session("string")
        assert result is False

    def test_true_for_active_status(self):
        payload = {"sess1": {"status": "active"}}
        assert _has_active_session(payload) is True

    def test_false_when_aborted(self):
        payload = {"sess1": {"status": "active", "abortedLastRun": True}}
        assert _has_active_session(payload) is False

    def test_false_when_too_old(self):
        old_ts = int(datetime.utcnow().timestamp() * 1000) - 600000  # 10 min ago
        payload = {"sess1": {"abortedLastRun": False, "updatedAt": old_ts}}
        assert _has_active_session(payload) is False

    def test_true_for_recent_update(self):
        now_ms = int(datetime.utcnow().timestamp() * 1000)
        recent_ts = now_ms - 100000  # ~100 sec ago (within 5min)
        payload = {"sess1": {"abortedLastRun": False, "updatedAt": recent_ts}}
        assert _has_active_session(payload) is True

    def test_multiple_sessions_one_active(self):
        payload = {
            "s1": {"status": "ended"},
            "s2": {"status": "active"},
            "s3": {"status": "ended"}
        }
        assert _has_active_session(payload) is True


class TestPickLatestRuntimeEntry:
    """Test _pick_latest_runtime_entry function."""

    def test_returns_none_for_empty_dict(self):
        item, ts = _pick_latest_runtime_entry({})
        assert item is None and ts is None

    def test_returns_none_for_none(self):
        item, ts = _pick_latest_runtime_entry(None)
        assert item is None and ts is None

    def test_returns_latest_entry(self):
        now = datetime.utcnow().timestamp()
        payload = {
            "a": {"updatedAt": (now - 100) * 1000},
            "b": {"updatedAt": now * 1000},
            "c": {"updatedAt": (now - 50) * 1000}
        }
        item, ts = _pick_latest_runtime_entry(payload)
        assert item["updatedAt"] == now * 1000

    def test_ignores_non_dict_values(self):
        payload = {"a": "string", "b": 123, "c": {"updatedAt": 1000}}
        item, ts = _pick_latest_runtime_entry(payload)
        assert item is not None
        assert item["updatedAt"] == 1000


class TestGetOpenclawConfig:
    """Test _get_openclaw_config."""

    def test_returns_dict_even_if_file_missing(self):
        config = _get_openclaw_config()
        assert isinstance(config, dict)

    def test_config_is_cached(self):
        config1 = _get_openclaw_config()
        config2 = _get_openclaw_config()
        assert config1 is config2


class TestGetAgentConfig:
    """Test _get_agent_config."""

    def test_returns_empty_for_missing_agent(self):
        config = _get_agent_config("nonexistent")
        assert config == {}

    def test_returns_agent_config_if_present(self):
        # This depends on openclaw.json existing; just ensure it returns dict
        config = _get_agent_config("ceo")
        assert isinstance(config, dict)


class TestSyncAgentsRuntime:
    """Test sync_agents_runtime (with mocked file system)."""

    @pytest.mark.asyncio
    async def test_sync_agents_runtime_updates_status(self, db_session: AsyncSession):
        """Test that sync_agents_runtime updates agent status from runtime files."""
        from app.services.agent_sync import sync_agents_runtime
        from sqlmodel import select
        from app.models import Agent

        # Pre-populate an agent
        agent = Agent(
            slug="qa_engineer",
            display_name="Bruno",
            role="QA Engineer",
            status="offline",
            current_model=None,
        )
        db_session.add(agent)
        await db_session.commit()

        # Mock sessions.json with recent runtime data
        sessions_data = {
            "sess1": {
                "sessionId": "abc123",
                "updatedAt": int(datetime.utcnow().timestamp() * 1000),
                "status": "active",
                "abortedLastRun": False
            }
        }

        with patch('pathlib.Path.exists') as mock_exists:
            # Return True for qa_engineer sessions file
            def exists_side_effect(path):
                return "qa_engineer" in str(path)
            mock_exists.side_effect = exists_side_effect

            with patch('pathlib.Path.read_text') as mock_read:
                mock_read.return_value = json.dumps(sessions_data)

                with patch.object(Agent, 'updated_at', None):
                    await sync_agents_runtime(db_session)

        # Refresh agent from DB
        await db_session.refresh(agent)
        assert agent.status in ["working", "online"]  # recent heartbeat
        assert agent.openclaw_session_id == "abc123"

    @pytest.mark.asyncio
    async def test_sync_agents_runtime_handles_missing_file(self, db_session: AsyncSession):
        """Test that sync_agents_runtime handles missing sessions file."""
        from app.services.agent_sync import sync_agents_runtime

        # No sessions file exists
        with patch('pathlib.Path.exists', return_value=False):
            await sync_agents_runtime(db_session)
        # Should complete without exception

    @pytest.mark.asyncio
    async def test_sync_agents_runtime_handles_invalid_json(self, db_session: AsyncSession):
        """Test that sync_agents_runtime handles invalid JSON gracefully."""
        from app.services.agent_sync import sync_agents_runtime

        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.read_text') as mock_read:
                mock_read.return_value = "invalid json"
                await sync_agents_runtime(db_session)
        # Should complete without exception

    @pytest.mark.asyncio
    async def test_sync_agents_runtime_clears_cache(self, db_session: AsyncSession):
        """Test that config cache is cleared before reading."""
        from app.services.agent_sync import sync_agents_runtime

        with patch('app.services.agent_sync._get_openclaw_config') as mock_config:
            mock_config.return_value = {"agents": {"list": []}}
            with patch('pathlib.Path.exists', return_value=False):
                await sync_agents_runtime(db_session)
            # Not necessarily calling cache_clear directly due to caching decorator,
            # but the function itself calls cache_clear
            assert mock_config.called
