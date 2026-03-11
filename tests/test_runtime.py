from app.runtime import (
    AgentResult,
    EventEnvelope,
    ExecutionPolicy,
    PreparedRun,
    RunContext,
    ToolRegistry,
    build_session_sender,
    build_runtime_tool_registry,
    extract_issue_id,
    increment_attempt,
    load_runtime_stack_config,
    log_event,
    payload_to_dict,
    process_stream_message,
    should_stop_task,
    validate_runtime_stack,
)
from app.agents.base import AgentSettings, BaseRoleAgent
from app.agents.architect_agent import ArchitectDraftAgent
from app.agents.developer_agent import DeveloperAgent
from app.agents.devops_agent import DevOpsAgent
import io
from contextlib import redirect_stdout
import os


class FakeRedis:
    def __init__(self):
        self.acks = []
        self.store = {}
        self.deleted = []
        self.added = []
        self.incr_counts = {}

    def xack(self, stream_name, group_name, message_id):
        self.acks.append((stream_name, group_name, message_id))
        return 1

    def get(self, key):
        return self.store.get(key)

    def set(self, key, value, nx=False, ex=None):
        if nx and key in self.store:
            return False
        self.store[key] = value
        return True

    def delete(self, key):
        self.deleted.append(key)
        self.store.pop(key, None)
        return 1

    def xadd(self, stream_name, payload):
        self.added.append((stream_name, payload))
        return "1-0"

    def incr(self, key):
        current = self.incr_counts.get(key, 0) + 1
        self.incr_counts[key] = current
        self.store[key] = str(current)
        return current

    def expire(self, key, ttl_sec):
        return True


class FakeAgent:
    role_name = "PO"
    stream_name = "cmd:strategy"
    consumer_group = "clawdevs"
    consumer_name = "po-test"
    session_key = "agent:po:test"
    policy = ExecutionPolicy(block_ms=10, timeout_sec=0)

    def prepare(self, redis_client, ctx):
        return PreparedRun()

    def build_instruction(self, redis_client, ctx):
        return f"directive={ctx.event.get('directive', '')}"

    def on_success(self, redis_client, ctx, send_output):
        return AgentResult(
            status="forwarded",
            status_code="forwarded",
            event_name="fake.forwarded",
            summary=f"acked {ctx.message_id}",
        )

    def on_error(self, redis_client, ctx, error):
        raise AssertionError(f"unexpected error: {error}")


class BrokenPrepareAgent(FakeAgent):
    def prepare(self, redis_client, ctx):
        return "invalid"


class MinimalRoleAgent(BaseRoleAgent):
    def __init__(self):
        self.settings = AgentSettings(
            role_name="Minimal",
            stream_name="stream:minimal",
            consumer_group="clawdevs",
            consumer_name="minimal-1",
            session_key="agent:minimal:main",
            policy=ExecutionPolicy(block_ms=10, timeout_sec=0),
        )

    def build_instruction(self, redis_client, ctx):
        return "noop"


def test_extract_issue_id_prefers_known_keys():
    assert extract_issue_id({"issue_id": "42"}) == "42"
    assert extract_issue_id({"issue": "41"}) == "41"
    assert extract_issue_id({"task_id": "40"}) == "40"
    assert extract_issue_id({"foo": "bar"}) is None


def test_run_context_generates_identifiers():
    ctx = RunContext.from_message(
        stream_name="cmd:strategy",
        message_id="1-0",
        event={"directive": "priorizar login"},
        policy=ExecutionPolicy(),
    )
    assert ctx.run_id
    assert ctx.trace_id
    assert ctx.event_type == "unknown"
    assert ctx.issue_id is None
    assert ctx.attempt == 1
    assert ctx.budget_started_at > 0
    assert ctx.envelope.run_id == ctx.run_id


def test_event_envelope_flattens_payload_with_metadata():
    envelope = EventEnvelope.from_payload(
        {"type": "task_ready", "issue_id": "42", "priority": 1, "attempt": 2}
    )

    payload = envelope.to_payload()

    assert payload["type"] == "task_ready"
    assert payload["issue_id"] == "42"
    assert payload["attempt"] == "2"
    assert payload["priority"] == "1"
    assert payload["run_id"]
    assert payload["trace_id"]
    assert payload["budget_started_at"]


def test_event_envelope_increments_attempt_without_resetting_budget():
    envelope = EventEnvelope.from_payload({"type": "task_ready", "issue_id": "42", "attempt": 2})

    payload = envelope.next_attempt_payload(priority=3)

    assert payload["issue_id"] == "42"
    assert payload["attempt"] == "3"
    assert payload["priority"] == "3"
    assert payload["run_id"] == envelope.run_id
    assert payload["trace_id"] == envelope.trace_id
    assert payload["budget_started_at"] == str(envelope.budget_started_at)


def test_payload_to_dict_decodes_stream_payloads():
    assert payload_to_dict({"directive": b"Priorizar 2FA"}) == {"directive": "Priorizar 2FA"}
    assert payload_to_dict([b"issue_id", b"42", b"directive", b"Ship"]) == {
        "issue_id": "42",
        "directive": "Ship",
    }


def test_process_stream_message_acks_when_sender_succeeds():
    redis_client = FakeRedis()
    agent = FakeAgent()

    def sender(session_key, message, timeout_sec):
        assert session_key == "agent:po:test"
        assert message == "directive=Priorizar 2FA"
        assert timeout_sec == 0
        return True, {"queued": True}

    result = process_stream_message(
        redis_client,
        agent,
        sender,
        "cmd:strategy",
        "1-0",
        {"directive": "Priorizar 2FA"},
    )

    assert result.status == "forwarded"
    assert result.status_code == "forwarded"
    assert result.event_name == "fake.forwarded"
    assert redis_client.acks == [("cmd:strategy", "clawdevs", "1-0")]


def test_process_stream_message_rejects_invalid_prepare_contract():
    redis_client = FakeRedis()
    agent = BrokenPrepareAgent()

    def sender(session_key, message, timeout_sec):
        raise AssertionError("sender should not be called")

    try:
        process_stream_message(
            redis_client,
            agent,
            sender,
            "cmd:strategy",
            "1-0",
            {"directive": "Priorizar 2FA"},
        )
    except TypeError as error:
        assert "prepare()" in str(error)
    else:
        raise AssertionError("TypeError esperado para prepare() invalido")


def test_process_stream_message_acks_when_attempt_budget_is_exceeded():
    redis_client = FakeRedis()
    agent = FakeAgent()
    agent.policy = ExecutionPolicy(block_ms=10, timeout_sec=0, max_attempts=2)

    def sender(session_key, message, timeout_sec):
        raise AssertionError("sender should not be called")

    result = process_stream_message(
        redis_client,
        agent,
        sender,
        "cmd:strategy",
        "1-1",
        {"directive": "Priorizar 2FA", "attempt": "3"},
    )

    assert result.status == "budget_exceeded"
    assert result.status_code == "budget_max_attempts"
    assert result.event_name == "runtime.budget_max_attempts"
    assert result.metadata["reason"] == "max_attempts"
    assert redis_client.acks == [("cmd:strategy", "clawdevs", "1-1")]


def test_process_stream_message_acks_when_runtime_budget_is_exceeded():
    redis_client = FakeRedis()
    agent = FakeAgent()
    agent.policy = ExecutionPolicy(block_ms=10, timeout_sec=0, max_attempts=3, max_runtime_sec=1)

    def sender(session_key, message, timeout_sec):
        raise AssertionError("sender should not be called")

    result = process_stream_message(
        redis_client,
        agent,
        sender,
        "cmd:strategy",
        "1-2",
        {"directive": "Priorizar 2FA", "budget_started_at": "1"},
    )

    assert result.status == "budget_exceeded"
    assert result.status_code == "budget_max_runtime"
    assert result.event_name == "runtime.budget_max_runtime"
    assert result.metadata["reason"] == "max_runtime_sec"
    assert redis_client.acks == [("cmd:strategy", "clawdevs", "1-2")]


def test_base_role_agent_default_success_metadata():
    redis_client = FakeRedis()
    agent = MinimalRoleAgent()

    result = process_stream_message(
        redis_client,
        agent,
        lambda session_key, message, timeout_sec: (True, {"queued": True}),
        "stream:minimal",
        "9-0",
        {},
    )

    assert result.status == "forwarded"
    assert result.status_code == "forwarded"
    assert result.event_name == "agent.forwarded"
    assert result.metadata["run_id"]
    assert redis_client.acks == [("stream:minimal", "clawdevs", "9-0")]


def test_tool_registry_dispatches_session_sender():
    registry = ToolRegistry()
    calls = []

    def fake_tool(session_key, message, timeout_sec):
        calls.append((session_key, message, timeout_sec))
        return True, {"queued": True}

    registry.register("openclaw.sessions.send", fake_tool)
    sender = build_session_sender(registry)

    ok, output = sender("agent:po:test", "ship it", 3)

    assert ok is True
    assert output == {"queued": True}
    assert calls == [("agent:po:test", "ship it", 3)]


def test_runtime_stack_defaults_to_openclaw_plus_ollama():
    previous = {key: os.environ.get(key) for key in ("OPENCLAW_REQUIRED", "MODEL_PROVIDER", "MODEL_MODE")}
    for key in previous:
        os.environ.pop(key, None)

    try:
        config = load_runtime_stack_config()
    finally:
        for key, value in previous.items():
            if value is not None:
                os.environ[key] = value

    assert config.openclaw_required is True
    assert config.model_provider == "ollama"
    assert config.model_mode == "cloud"
    assert config.stack_label == "openclaw+ollama"


def test_runtime_stack_validation_requires_openclaw_and_ollama_model():
    previous = {
        key: os.environ.get(key)
        for key in ("OPENCLAW_GATEWAY_WS", "MODEL_PROVIDER", "MODEL_MODE", "OLLAMA_BASE_URL", "OLLAMA_MODEL")
    }
    for key in previous:
        os.environ.pop(key, None)

    try:
        errors = validate_runtime_stack()
    finally:
        for key, value in previous.items():
            if value is not None:
                os.environ[key] = value

    assert any("OPENCLAW_GATEWAY_WS" in error for error in errors)
    assert any("OLLAMA_MODEL" in error for error in errors)


def test_runtime_tool_registry_validates_stack_before_build():
    previous = {
        key: os.environ.get(key)
        for key in ("OPENCLAW_GATEWAY_WS", "MODEL_PROVIDER", "MODEL_MODE", "OLLAMA_BASE_URL", "OLLAMA_MODEL")
    }
    for key in previous:
        os.environ.pop(key, None)

    try:
        try:
            build_runtime_tool_registry()
        except RuntimeError as error:
            assert "OPENCLAW_GATEWAY_WS" in str(error)
            assert "OLLAMA_MODEL" in str(error)
        else:
            raise AssertionError("RuntimeError esperado para stack invalida")
    finally:
        for key, value in previous.items():
            if value is not None:
                os.environ[key] = value


def test_log_event_writes_json_line():
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        log_event("runtime.test", run_id="r1", trace_id="t1")

    output = buffer.getvalue()

    assert '"event": "runtime.test"' in output
    assert '"run_id": "r1"' in output
    assert '"trace_id": "t1"' in output


def test_architect_agent_acks_without_sending_when_issue_missing():
    redis_client = FakeRedis()
    agent = ArchitectDraftAgent()

    def sender(session_key, message, timeout_sec):
        raise AssertionError("sender should not be called")

    result = process_stream_message(
        redis_client,
        agent,
        sender,
        "draft.2.issue",
        "2-0",
        {"title": "No issue id"},
    )

    assert result.status == "ignored"
    assert result.status_code == "ignored_missing_issue"
    assert result.event_name == "architect.ignored_missing_issue"
    assert redis_client.acks == [("draft.2.issue", "clawdevs", "2-0")]


def test_developer_agent_requeues_when_lock_is_busy():
    redis_client = FakeRedis()
    agent = DeveloperAgent()
    lock_key = f"{agent.stream_name}:noop"
    redis_client.store[f"project:v1:issue:42:dev_lock"] = "other-agent"

    def sender(session_key, message, timeout_sec):
        raise AssertionError("sender should not be called")

    result = process_stream_message(
        redis_client,
        agent,
        sender,
        "task:backlog",
        "3-0",
        {"issue_id": "42", "priority": "1"},
    )

    assert result.status == "requeued"
    assert result.status_code == "requeued_lock_busy"
    assert result.event_name == "developer.requeued_lock_busy"
    assert len(redis_client.added) == 1
    stream_name, payload = redis_client.added[0]
    assert stream_name == "task:backlog"
    assert payload["type"] == "unknown"
    assert payload["issue_id"] == "42"
    assert payload["attempt"] == "2"
    assert payload["priority"] == "1"
    assert payload["run_id"]
    assert payload["trace_id"]
    assert payload["budget_started_at"]
    assert redis_client.acks == [("task:backlog", "clawdevs", "3-0")]


def test_developer_agent_acks_when_finops_stops_task():
    redis_client = FakeRedis()
    agent = DeveloperAgent()
    agent.finops_cost_estimate = 10.0

    def sender(session_key, message, timeout_sec):
        raise AssertionError("sender should not be called")

    result = process_stream_message(
        redis_client,
        agent,
        sender,
        "task:backlog",
        "4-0",
        {"issue_id": "77", "priority": "1"},
    )

    assert result.status == "halted"
    assert result.status_code == "halted_finops"
    assert result.event_name == "developer.halted_finops"
    assert redis_client.store["project:v1:issue:77:state"] == "Backlog"
    assert "project:v1:issue:77:dev_lock" in redis_client.deleted
    assert redis_client.acks == [("task:backlog", "clawdevs", "4-0")]


def test_devops_agent_sends_post_merge_instruction():
    redis_client = FakeRedis()
    agent = DevOpsAgent()

    def sender(session_key, message, timeout_sec):
        assert session_key == "agent:devops:main"
        assert "issue_id: 88" in message
        assert "branch: main" in message
        return True, {"queued": True}

    result = process_stream_message(
        redis_client,
        agent,
        sender,
        "event:devops",
        "5-0",
        {"issue_id": "88", "branch": "main", "repo": "org/repo"},
    )

    assert result.status == "forwarded"
    assert result.status_code == "forwarded"
    assert result.event_name == "devops.forwarded"
    assert redis_client.acks == [("event:devops", "clawdevs", "5-0")]


def test_runtime_finops_counts_and_stops():
    redis_client = FakeRedis()
    assert increment_attempt(redis_client, "123") == 1
    assert increment_attempt(redis_client, "123") == 2
    stop, reason = should_stop_task("123", 2, 0.1)
    assert stop is False
    stop, reason = should_stop_task("123", 999, 0.1)
    assert stop is True
