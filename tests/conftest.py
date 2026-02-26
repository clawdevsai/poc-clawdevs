import pytest
from unittest.mock import MagicMock


# Mocking redis before any imports that might use it
@pytest.fixture(autouse=True)
def mock_redis(monkeypatch):
    mock_lib = MagicMock()
    mock_instance = MagicMock()
    mock_lib.Redis.return_value = mock_instance
    monkeypatch.setattr("redis.Redis", MagicMock(return_value=mock_instance))
    return mock_instance


@pytest.fixture
def gateway_mock_redis():
    mock = MagicMock()
    # Mock pipeline
    pipeline = MagicMock()
    mock.pipeline.return_value = pipeline
    pipeline.execute.return_value = [0, 0]  # Default for token bucket
    return mock
