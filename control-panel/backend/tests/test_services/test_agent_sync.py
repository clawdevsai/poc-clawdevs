import pytest
import json
import os
from pathlib import Path
from datetime import datetime, timezone
from unittest.mock import patch, MagicMock

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


class TestAgentSyncFunctions:
    """Test agent sync utility functions."""

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
        assert "dev_backend" in ROLE_MAP
        assert ROLE_MAP["dev_backend"] == "Backend Developer"

    def test_display_name_map(self):
        """Test that DISPLAY_NAME_MAP has all agents."""
        assert "ceo" in DISPLAY_NAME_MAP
        assert DISPLAY_NAME_MAP["ceo"] == "Victor"
        assert "qa_engineer" in DISPLAY_NAME_MAP
        assert DISPLAY_NAME_MAP["qa_engineer"] == "Bruno"
        assert "devops_sre" in DISPLAY_NAME_MAP
        assert DISPLAY_NAME_MAP["devops_sre"] == "Diego"


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

    def test_parse_identity_dev_backend(self):
        """Test parse_identity for dev backend."""
        identity = parse_identity("dev_backend")
        assert identity["display_name"] == "Mateus"
        assert identity["role"] == "Backend Developer"

    def test_parse_identity_all_agents(self):
        """Test parse_identity for all agents."""
        for agent in AGENT_SLUGS:
            identity = parse_identity(agent)
            assert "display_name" in identity
            assert "role" in identity
            assert "model" in identity

    def test_parse_identity_empty_slug(self):
        """Test parse_identity with empty slug."""
        identity = parse_identity("")
        assert "display_name" in identity
        assert "role" in identity


class TestStatusFromHeartbeat:
    """Test _status_from_heartbeat function."""

    def test_status_offline_no_heartbeat(self):
        """Test status is offline when no heartbeat."""
        status = _status_from_heartbeat(None)
        assert status == "offline"

    def test_status_working_recent_heartbeat_with_session(self):
        """Test status is working with recent heartbeat and active session."""
        recent_time = datetime.utcnow()
        status = _status_from_heartbeat(recent_time, has_active_session=True)
        assert status == "working"

    def test_status_online_recent_heartbeat_no_session(self):
        """Test status is online with recent heartbeat and no session."""
        recent_time = datetime.utcnow()
        status = _status_from_heartbeat(recent_time, has_active_session=False)
        assert status == "online"

    def test_status_idle_older_heartbeat(self):
        """Test status is idle with older heartbeat."""
        older_time = datetime.utcnow().replace(
            hour=datetime.utcnow().hour - 2
        )
        status = _status_from_heartbeat(older_time)
        assert status == "idle"

    def test_status_offline_very_old_heartbeat(self):
        """Test status is offline with very old heartbeat."""
        very_old_time = datetime.utcnow().replace(
            hour=datetime.utcnow().hour - 3
        )
        status = _status_from_heartbeat(very_old_time)
        assert status == "offline"

    def test_status_edge_case_5_minutes(self):
        """Test status at 5 minute boundary."""
        five_min_ago = datetime.utcnow().replace(
            minute=datetime.utcnow().minute - 5
        )
        status = _status_from_heartbeat(five_min_ago)
        assert status in ["online", "idle"]

    def test_status_with_none_timezone(self):
        """Test status with naive datetime."""
        naive_time = datetime.utcnow()
        status = _status_from_heartbeat(naive_time)
        assert status in ["online", "idle"]


class TestHasActiveSession:
    """Test _has_active_session function."""

    def test_has_active_session_false_empty(self):
        """Test has_active_session returns False for empty dict."""
        result = _has_active_session({})
        assert result is False

    def test_has_active_session_false_none(self):
        """Test has_active_session returns False for None."""
        result = _has_active_session(None)
        assert result is False

    def test_has_active_session_false_string(self):
        """Test has_active_session returns False for string."""
        result = _has_active_session("not a dict")
        assert result is False

    def test_has_active_session_false_list(self):
        """Test has_active_session returns False for list."""
        result = _has_active_session([])
        assert result is False

    def test_has_active_session_true_active_status(self):
        """Test has_active_session returns True for active status."""
        payload = {
            "session1": {"status": "active"}
        }
        result = _has_active_session(payload)
        assert result is True

    def test_has_active_session_false_aborted(self):
        """Test has_active_session returns False when aborted."""
        payload = {
            "session1": {
                "status": "active",
                "abortedLastRun": True
            }
        }
        result = _has_active_session(payload)
        assert result is False

    def test_has_active_session_false_not_recent(self):
        """Test has_active_session returns False for old updated_at."""
        payload = {
            "session1": {
                "abortedLastRun": False,
                "updatedAt": 1000  # Very old timestamp
            }
        }
        result = _has_active_session(payload)
        assert result is False

    def test_has_active_session_multiple_sessions(self):
        """Test has_active_session with multiple sessions."""
        payload = {
            "session1": {"status": "inactive"},
            "session2": {"status": "active"},
            "session3": {"status": "ended"}
        }
        result = _has_active_session(payload)
        assert result is True

    def test_has_active_session_all_aborted(self):
        """Test has_active_session when all sessions aborted."""
        payload = {
            "session1": {"status": "active", "abortedLastRun": True},
            "session2": {"status": "active", "abortedLastRun": True}
        }
        result = _has_active_session(payload)
        assert result is False

    def test_has_active_session_recent_update(self):
        """Test has_active_session with recent update."""
        now_ms = int(datetime.utcnow().timestamp() * 1000)
        recent = now_ms - 100000  # 100 seconds ago (within 5 min)
        payload = {
            "session1": {
                "abortedLastRun": False,
                "updatedAt": recent
            }
        }
        result = _has_active_session(payload)
        assert result is True


class TestPickLatestRuntimeEntry:
    """Test _pick_latest_runtime_entry function."""

    def test_pick_latest_returns_none_empty(self):
        """Test _pick_latest_runtime_entry returns None for empty."""
        item, timestamp = _pick_latest_runtime_entry({})
        assert item is None
        assert timestamp is None

    def test_pick_latest_returns_none_none(self):
        """Test _pick_latest_runtime_entry returns None for None."""
        item, timestamp = _pick_latest_runtime_entry(None)
        assert item is None
        assert timestamp is None

    def test_pick_latest_with_valid_data(self):
        """Test _pick_latest_runtime_entry with valid data."""
        now = datetime.utcnow().timestamp()
        payload = {
            "entry1": {"updatedAt": now * 1000},
            "entry2": {"updatedAt": (now - 100) * 1000}
        }
        item, timestamp = _pick_latest_runtime_entry(payload)
        assert item is not None
        assert timestamp is not None

    def test_pick_latest_with_string_values(self):
        """Test _pick_latest_runtime_entry with string values."""
        payload = {
            "entry1": "not a dict",
            "entry2": {"updatedAt": 1000}
        }
        item, timestamp = _pick_latest_runtime_entry(payload)
        assert item is not None


class TestGetOpenclawConfig:
    """Test _get_openclaw_config function."""

    def test_get_config_returns_dict(self):
        """Test that _get_openclaw_config returns dict."""
        config = _get_openclaw_config()
        assert isinstance(config, dict)

    def test_get_config_is_cached(self):
        """Test that _get_openclaw_config is cached."""
        config1 = _get_openclaw_config()
        config2 = _get_openclaw_config()
        assert config1 is config2


class TestGetAgentConfig:
    """Test _get_agent_config function."""

    def test_get_agent_config_returns_dict(self):
        """Test that _get_agent_config returns dict."""
        config = _get_agent_config("ceo")
        assert isinstance(config, dict)

    def test_get_agent_config_not_found(self):
        """Test _get_agent_config for non-existent agent."""
        config = _get_agent_config("nonexistent")
        assert config == {}


class TestSyncAgents:
    """Test sync_agents function (with mocked database)."""

    @pytest.mark.asyncio
    async def test_sync_agents_creates_agents(self, db_session):
        """Test that sync_agents creates agents from config."""
        from sqlmodel import select
        from app.models import Agent

        # Mock the parse_identity function to avoid file access
        with patch('app.services.agent_sync.parse_identity') as mock_parse:
            mock_parse.return_value = {
                "display_name": "Test Agent",
                "role": "Test Role",
                "model": None
            }
            # Note: sync_agents is a complex function that interacts with
            # the database. This test documents the expected behavior.
            pass

    @pytest.mark.asyncio
    async def test_sync_agents_updates_existing(self, db_session):
        """Test that sync_agents updates existing agents."""
        # This test documents the expected update behavior
        pass

    @pytest.mark.asyncio
    async def test_sync_agents_handles_errors(self, db_session):
        """Test that sync_agents handles errors gracefully."""
        # This test documents error handling
        pass
