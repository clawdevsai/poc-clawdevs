"""
Tests for session_sync service - real code execution.
"""

import pytest
import json
from pathlib import Path
from datetime import datetime
from unittest.mock import patch, MagicMock, AsyncMock
from sqlmodel import select


class TestSyncSessions:
    """Test sync_sessions function with real code execution."""

    @pytest.mark.asyncio
    async def test_sync_sessions_creates_sessions(self):
        """Test that sync_sessions creates new sessions."""
        from app.services.session_sync import sync_sessions
        from sqlmodel import select
        from app.models import Session
        
        # Mock database session
        mock_db_session = AsyncMock()
        mock_result = AsyncMock()
        mock_result.first.return_value = None  # No existing session
        mock_db_session.exec = AsyncMock(return_value=mock_result)
        
        # Mock file system
        mock_session_data = {
            "session-1": {
                "sessionId": "sess-123",
                "updatedAt": 1712200000000,
                "deliveryContext": {
                    "channel": "telegram",
                    "to": "123456789"
                },
                "totalTokens": 1000
            }
        }
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.open') as mock_open:
                mock_file = MagicMock()
                mock_file.__enter__.return_value.read.return_value = json.dumps(mock_session_data)
                mock_open.return_value = mock_file
                
                with patch('app.services.session_sync._count_messages_in_session_file', return_value=5):
                    await sync_sessions(mock_db_session)
                    
                    # Verify session was created
                    mock_db_session.add.assert_called()
                    mock_db_session.commit.assert_awaited()

    @pytest.mark.asyncio
    async def test_sync_sessions_updates_existing(self):
        """Test that sync_sessions updates existing sessions."""
        from app.services.session_sync import sync_sessions
        
        mock_db_session = AsyncMock()
        
        # Mock existing session
        existing_session = MagicMock()
        existing_session.openclaw_session_id = "sess-123"
        
        mock_result = AsyncMock()
        mock_result.first.return_value = existing_session
        mock_db_session.exec = AsyncMock(return_value=mock_result)
        
        mock_session_data = {
            "session-1": {
                "sessionId": "sess-123",
                "updatedAt": 1712200000000,
                "deliveryContext": {
                    "channel": "telegram",
                    "to": "123456789"
                },
                "totalTokens": 2000  # Updated token count
            }
        }
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.open') as mock_open:
                mock_file = MagicMock()
                mock_file.__enter__.return_value.read.return_value = json.dumps(mock_session_data)
                mock_open.return_value = mock_file
                
                await sync_sessions(mock_db_session)
                
                # Verify session was updated
                assert existing_session.token_count == 2000

    @pytest.mark.asyncio
    async def test_sync_sessions_handles_missing_file(self):
        """Test that sync_sessions handles missing files gracefully."""
        from app.services.session_sync import sync_sessions
        
        mock_db_session = AsyncMock()
        
        with patch('pathlib.Path.exists', return_value=False):
            await sync_sessions(mock_db_session)
            
            # Should not add or commit
            mock_db_session.add.assert_not_called()
            mock_db_session.commit.assert_not_called()

    @pytest.mark.asyncio
    async def test_sync_sessions_handles_invalid_json(self):
        """Test that sync_sessions handles invalid JSON gracefully."""
        from app.services.session_sync import sync_sessions
        
        mock_db_session = AsyncMock()
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.open') as mock_open:
                mock_file = MagicMock()
                mock_file.__enter__.return_value.read.return_value = "invalid json"
                mock_open.return_value = mock_file
                
                await sync_sessions(mock_db_session)
                
                # Should handle gracefully without error
                mock_db_session.add.assert_not_called()

    @pytest.mark.asyncio
    async def test_sync_sessions_handles_empty_data(self):
        """Test that sync_sessions handles empty data gracefully."""
        from app.services.session_sync import sync_sessions
        
        mock_db_session = AsyncMock()
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.open') as mock_open:
                mock_file = MagicMock()
                mock_file.__enter__.return_value.read.return_value = "{}"
                mock_open.return_value = mock_file
                
                await sync_sessions(mock_db_session)
                
                # Should not add any sessions
                mock_db_session.add.assert_not_called()


class TestParseTimestamp:
    """Test _parse_timestamp function."""

    def test_parse_timestamp_valid_ms(self):
        """Test parsing valid timestamp in milliseconds."""
        from app.services.session_sync import _parse_timestamp
        
        ts = 1712200000000  # milliseconds
        dt = _parse_timestamp(ts)
        
        assert dt is not None
        assert isinstance(dt, datetime)

    def test_parse_timestamp_valid_seconds(self):
        """Test parsing valid timestamp in seconds."""
        from app.services.session_sync import _parse_timestamp
        
        ts = 1712200000  # seconds
        dt = _parse_timestamp(ts)
        
        assert dt is not None

    def test_parse_timestamp_none(self):
        """Test parsing None timestamp."""
        from app.services.session_sync import _parse_timestamp
        
        dt = _parse_timestamp(None)
        
        assert dt is None

    def test_parse_timestamp_string_iso(self):
        """Test parsing ISO format string."""
        from app.services.session_sync import _parse_timestamp
        
        dt = _parse_timestamp("2024-04-05T10:00:00Z")
        
        assert dt is not None

    def test_parse_timestamp_invalid(self):
        """Test parsing invalid timestamp."""
        from app.services.session_sync import _parse_timestamp
        
        dt = _parse_timestamp("invalid")
        
        assert dt is None

    def test_parse_timestamp_empty_string(self):
        """Test parsing empty string."""
        from app.services.session_sync import _parse_timestamp
        
        dt = _parse_timestamp("")
        
        assert dt is None


class TestCountMessagesInSessionFile:
    """Test _count_messages_in_session_file function."""

    def test_count_messages_empty_file(self):
        """Test counting messages in empty file."""
        from app.services.session_sync import _count_messages_in_session_file
        
        with patch('pathlib.Path.exists', return_value=False):
            count = _count_messages_in_session_file(Path("/fake/path.jsonl"))
        
        assert count == 0

    def test_count_messages_valid_file(self):
        """Test counting messages in valid file."""
        from app.services.session_sync import _count_messages_in_session_file
        
        mock_data = """{"role": "user", "content": "Hello"}
{"role": "assistant", "content": "Hi there"}
{"role": "system", "content": "System message"}
"""
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open') as mock_open:
                mock_file = MagicMock()
                mock_file.__enter__.return_value.readlines.return_value = mock_data.strip().split('\n')
                mock_open.return_value = mock_file
                
                count = _count_messages_in_session_file(Path("/fake/path.jsonl"))
                
                # Should count only user and assistant messages
                assert count == 2

    def test_count_messages_invalid_json(self):
        """Test counting messages with invalid JSON."""
        from app.services.session_sync import _count_messages_in_session_file
        
        mock_data = """{"role": "user", "content": "Hello"}
invalid json line
{"role": "assistant", "content": "Hi"}
"""
        
        with patch('pathlib.Path.exists', return_value=True):
            with patch('builtins.open') as mock_open:
                mock_file = MagicMock()
                mock_file.__enter__.return_value.readlines.return_value = mock_data.strip().split('\n')
                mock_open.return_value = mock_file
                
                count = _count_messages_in_session_file(Path("/fake/path.jsonl"))
                
                # Should count only valid messages
                assert count == 2
