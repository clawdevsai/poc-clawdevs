import pytest

from app.models import Task
from app.services import parallelism_gate


class DummySettings:
    ORCH_PARALLELISM_ENABLED = False
    ORCH_PARALLELISM_FORCE = False
    ORCH_PARALLELISM_COST_THRESHOLD = 2.0
    ORCH_PARALLELISM_LATENCY_THRESHOLD_SECONDS = 600
    ORCH_PARALLELISM_LOOKBACK_TASKS = 25
    ORCH_PARALLELISM_ADAPTIVE_ENABLED = True
    ORCH_PARALLELISM_ADAPTIVE_MIN_SAMPLES = 1
    ORCH_PARALLELISM_COST_MULTIPLIER = 1.2
    ORCH_PARALLELISM_LATENCY_MULTIPLIER = 1.2
    openclaw_data_path = "/tmp"


@pytest.mark.asyncio
async def test_parallelism_gate_disabled(db_session, monkeypatch):
    async def fake_settings():
        return DummySettings

    monkeypatch.setattr(parallelism_gate, "get_settings", lambda: DummySettings)
    allowed, reason = await parallelism_gate.evaluate_parallelism_gate(db_session, 1)
    assert allowed is False
    assert reason == "disabled"


@pytest.mark.asyncio
async def test_parallelism_gate_force(db_session, monkeypatch):
    class ForceSettings(DummySettings):
        ORCH_PARALLELISM_ENABLED = False
        ORCH_PARALLELISM_FORCE = True

    monkeypatch.setattr(parallelism_gate, "get_settings", lambda: ForceSettings)
    allowed, reason = await parallelism_gate.evaluate_parallelism_gate(db_session, 2)
    assert allowed is True
    assert reason == "force_enabled"


@pytest.mark.asyncio
async def test_parallelism_gate_thresholds_met(db_session, monkeypatch):
    class EnabledSettings(DummySettings):
        ORCH_PARALLELISM_ENABLED = True
        ORCH_PARALLELISM_FORCE = False

    monkeypatch.setattr(parallelism_gate, "get_settings", lambda: EnabledSettings)
    allowed, reason = await parallelism_gate.evaluate_parallelism_gate(db_session, 1)
    assert allowed is True
    assert reason in {"sequential_allowed", "thresholds_met"}


@pytest.mark.asyncio
async def test_adaptive_thresholds_persist(db_session, monkeypatch, tmp_path):
    class AdaptiveSettings(DummySettings):
        ORCH_PARALLELISM_ENABLED = True
        ORCH_PARALLELISM_FORCE = False
        ORCH_PARALLELISM_ADAPTIVE_ENABLED = True
        ORCH_PARALLELISM_ADAPTIVE_MIN_SAMPLES = 1
        openclaw_data_path = str(tmp_path)

    monkeypatch.setattr(parallelism_gate, "get_settings", lambda: AdaptiveSettings)

    task = Task(title="t1", status="done", actual_cost=5.0)
    db_session.add(task)
    await db_session.commit()

    allowed, reason = await parallelism_gate.evaluate_parallelism_gate(db_session, 2)
    assert reason in {"thresholds_met", "thresholds_exceeded", "sequential_allowed"}

    thresholds_file = tmp_path / "parallelism_thresholds.json"
    assert thresholds_file.exists()
