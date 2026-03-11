from app.runtime import (
    AgentResult,
    EventEnvelope,
    ExecutionPolicy,
    OpenClawSessionConfig,
    PreparedRun,
    RunContext,
    ToolRegistry,
    TOOL_PUBLISH_BACKLOG,
    TOOL_PUBLISH_CODE_READY,
    TOOL_PUBLISH_DEPLOY_EVENT,
    TOOL_PUBLISH_DRAFT_REJECTED,
    build_session_sender,
    build_runtime_tool_registry,
    extract_issue_id,
    get_role_openclaw_config,
    increment_attempt,
    resolve_openclaw_session_config,
    load_runtime_stack_config,
    log_event,
    inspect_openclaw_output,
    normalize_openclaw_output,
    payload_to_dict,
    process_stream_message,
    publish_backlog,
    publish_code_ready,
    publish_deploy_event,
    publish_draft_rejected,
    build_runtime_session_sender,
    render_openclaw_message,
    should_stop_task,
    validate_runtime_stack,
)
from app.runtime.check_stack import main as check_stack_main
from app.agents.base import AgentSettings, BaseRoleAgent
from app.agents.architect_agent import ArchitectDraftAgent
from app.agents.developer_agent import DeveloperAgent
from app.agents.devops_agent import DevOpsAgent
import io
from contextlib import redirect_stdout
import os
from app.shared.issue_state import STATE_DEPLOYED, STATE_READY, STATE_REFINAMENTO


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

    def smembers(self, key):
        return set()

    def sadd(self, key, value):
        return 1

    def hset(self, key, mapping):
        self.store[key] = mapping
        return True

    def hgetall(self, key):
        return self.store.get(key, {})


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
        assert "OpenClaw role profile: po" in message
        assert "[rule:core]" in message
        assert "[skill:github_issue_flow]" in message
        assert "directive=Priorizar 2FA" in message
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

    def fake_tool(session_key, message, timeout_sec, session_config=None):
        calls.append((session_key, message, timeout_sec, session_config))
        return True, {"queued": True}

    registry.register("openclaw.sessions.send", fake_tool, allowed_roles=("PO",))
    session_config = OpenClawSessionConfig(
        session_key="agent:po:test",
        provider="ollama",
        mode="cloud",
        model="qwen2.5-coder:32b",
        base_url="https://ollama.example",
    )
    sender = build_session_sender(registry, role_name="PO", session_config=session_config)

    ok, output = sender("agent:po:test", "ship it", 3)

    assert ok is True
    assert output == {"queued": True}
    assert calls == [("agent:po:test", "ship it", 3, session_config)]
    assert sender.allowed_tools == ("openclaw.sessions.send",)
    assert sender.session_config == session_config


def test_tool_registry_blocks_role_without_permission():
    registry = ToolRegistry()
    registry.register(
        "openclaw.sessions.send",
        lambda session_key, message, timeout_sec, session_config=None: (True, {"queued": True}),
        allowed_roles=("Developer",),
    )
    sender = build_session_sender(registry, role_name="PO")

    try:
        sender("agent:po:test", "ship it", 3)
    except PermissionError as error:
        assert "role sem permissao" in str(error)
    else:
        raise AssertionError("PermissionError esperado para role sem acesso")


def test_publish_backlog_sets_ready_and_emits_task_backlog():
    redis_client = FakeRedis()

    ok, output = publish_backlog(
        redis_client=redis_client,
        issue_id="42",
        title="Login",
        summary="Ship login",
        priority="1",
    )

    assert ok is True
    assert output["stream"] == "task:backlog"
    assert redis_client.store["project:v1:issue:42:state"] == STATE_READY
    assert redis_client.added[-1] == (
        "task:backlog",
        {"issue_id": "42", "title": "Login", "summary": "Ship login", "priority": "1"},
    )


def test_publish_draft_rejected_sets_refinamento():
    redis_client = FakeRedis()

    ok, output = publish_draft_rejected(
        redis_client=redis_client,
        issue_id="51",
        reason="missing acceptance criteria",
        title="Feature X",
    )

    assert ok is True
    assert output["state"] == STATE_REFINAMENTO
    assert redis_client.store["project:v1:issue:51:state"] == STATE_REFINAMENTO
    assert redis_client.added[-1] == (
        "draft_rejected",
        {"issue_id": "51", "reason": "missing acceptance criteria", "title": "Feature X"},
    )


def test_publish_code_ready_emits_code_ready_stream():
    redis_client = FakeRedis()

    ok, output = publish_code_ready(
        redis_client=redis_client,
        issue_id="88",
        branch="feat/login",
        repo="org/repo",
    )

    assert ok is True
    assert output["stream"] == "code:ready"
    assert redis_client.added[-1] == (
        "code:ready",
        {"issue_id": "88", "branch": "feat/login", "repo": "org/repo"},
    )


def test_publish_deploy_event_sets_deployed_and_emits_feature_complete():
    redis_client = FakeRedis()

    ok, output = publish_deploy_event(
        redis_client=redis_client,
        issue_id="90",
        branch="main",
        repo="org/repo",
        pr="123",
    )

    assert ok is True
    assert output["state"] == STATE_DEPLOYED
    assert redis_client.store["project:v1:issue:90:state"] == STATE_DEPLOYED
    assert redis_client.added[0] == (
        "event:devops",
        {"issue_id": "90", "branch": "main", "repo": "org/repo", "pr": "123"},
    )
    assert redis_client.added[1][0] == "orchestrator:events"
    assert redis_client.added[1][1]["type"] == "feature_complete"


def test_runtime_tool_registry_registers_role_tools():
    previous = {
        key: os.environ.get(key)
        for key in ("OPENCLAW_GATEWAY_WS", "MODEL_PROVIDER", "MODEL_MODE", "OLLAMA_BASE_URL", "OLLAMA_MODEL")
    }
    os.environ["OPENCLAW_GATEWAY_WS"] = "ws://127.0.0.1:18789"
    os.environ["MODEL_PROVIDER"] = "ollama"
    os.environ["MODEL_MODE"] = "cloud"
    os.environ["OLLAMA_BASE_URL"] = "https://ollama.example"
    os.environ["OLLAMA_MODEL"] = "qwen2.5-coder:32b"

    try:
        registry = build_runtime_tool_registry()
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    assert TOOL_PUBLISH_BACKLOG in registry._tools
    assert TOOL_PUBLISH_DRAFT_REJECTED in registry._tools
    assert TOOL_PUBLISH_CODE_READY in registry._tools
    assert TOOL_PUBLISH_DEPLOY_EVENT in registry._tools
    assert registry.default_session_config.model_provider == "ollama"


def test_resolve_openclaw_session_config_uses_stack_settings():
    stack = load_runtime_stack_config()
    session = resolve_openclaw_session_config(
        "agent:developer:main",
        stack,
    )

    assert session.session_key == "agent:developer:main"
    assert session.provider == stack.model_provider
    assert session.mode == stack.model_mode
    assert session.model == stack.ollama_model
    assert session.base_url == stack.ollama_base_url


def test_build_runtime_session_sender_resolves_ollama_session():
    registry = ToolRegistry()
    calls = []

    def fake_tool(session_key, message, timeout_sec, session_config=None):
        calls.append((session_key, message, timeout_sec, session_config))
        return True, {"queued": True}

    registry.register("openclaw.sessions.send", fake_tool, allowed_roles=("Developer",))
    registry.default_session_config = load_runtime_stack_config()
    sender = build_runtime_session_sender(
        registry,
        role_name="Developer",
        session_key="agent:developer:main",
    )

    ok, output = sender("agent:developer:main", "implementar", 5)

    assert ok is True
    assert output == {"queued": True}
    assert calls[0][0] == "agent:developer:main"
    assert calls[0][3] is not None
    assert calls[0][3].provider == "ollama"


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
        else:
            raise AssertionError("RuntimeError esperado para stack invalida")
    finally:
        for key, value in previous.items():
            if value is not None:
                os.environ[key] = value


def test_check_stack_returns_success_for_valid_openclaw_ollama_stack():
    previous = {
        key: os.environ.get(key)
        for key in ("OPENCLAW_GATEWAY_WS", "MODEL_PROVIDER", "MODEL_MODE", "OLLAMA_BASE_URL", "OLLAMA_MODEL")
    }
    os.environ["OPENCLAW_GATEWAY_WS"] = "ws://127.0.0.1:18789"
    os.environ["MODEL_PROVIDER"] = "ollama"
    os.environ["MODEL_MODE"] = "cloud"
    os.environ["OLLAMA_BASE_URL"] = "https://ollama.example"
    os.environ["OLLAMA_MODEL"] = "qwen2.5-coder:32b"

    try:
        buffer = io.StringIO()
        with redirect_stdout(buffer):
            exit_code = check_stack_main()
    finally:
        for key, value in previous.items():
            if value is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = value

    output = buffer.getvalue()
    assert exit_code == 0
    assert '"ok": true' in output
    assert '"stack": "openclaw+ollama"' in output


def test_log_event_writes_json_line():
    buffer = io.StringIO()
    with redirect_stdout(buffer):
        log_event("runtime.test", run_id="r1", trace_id="t1")

    output = buffer.getvalue()

    assert '"event": "runtime.test"' in output
    assert '"run_id": "r1"' in output
    assert '"trace_id": "t1"' in output


def test_openclaw_role_assets_are_bound_for_developer():
    config = get_role_openclaw_config("Developer")

    assert config is not None
    assert config.profile == "developer"
    assert "code_delivery" in config.skills
    assert "change_safety" in config.rules
    assert config.output_schema == "developer"


def test_render_openclaw_message_includes_profile_rules_and_skills():
    message = render_openclaw_message(
        "Developer",
        "Implementar issue 42",
        allowed_tools=("openclaw.sessions.send", "redis.publish_code_ready"),
    )

    assert "OpenClaw role profile: developer" in message
    assert "[rule:core]" in message
    assert "[rule:change_safety]" in message
    assert "[skill:code_delivery]" in message
    assert "[skill:test_execution]" in message
    assert "Allowed runtime tools:" in message
    assert "- redis.publish_code_ready" in message
    assert "[output_schema:developer]" in message
    assert "Expected output schema for Developer." in message
    assert "Task instruction:" in message
    assert "Implementar issue 42" in message


def test_normalize_openclaw_output_parses_raw_json():
    normalized = normalize_openclaw_output({"raw": '{"status":"implemented","summary":"ok"}'})

    assert normalized["status"] == "implemented"
    assert normalized["summary"] == "ok"


def test_inspect_openclaw_output_validates_schema_fields():
    inspection = inspect_openclaw_output(
        "Developer",
        {
            "status": "implemented",
            "summary": "done",
            "files_changed": ["app/x.py"],
            "verification": ["pytest"],
            "next_action": "code:ready",
        },
    )

    assert inspection["schema"] == "developer"
    assert inspection["valid"] is True
    assert inspection["missing_fields"] == ()


def test_inspect_openclaw_output_flags_missing_fields():
    inspection = inspect_openclaw_output(
        "Developer",
        {"status": "implemented", "summary": "done"},
    )

    assert inspection["schema"] == "developer"
    assert inspection["valid"] is False
    assert "files_changed" in inspection["missing_fields"]


def test_process_stream_message_marks_invalid_openclaw_output():
    redis_client = FakeRedis()
    agent = FakeAgent()
    agent.policy = ExecutionPolicy(block_ms=10, timeout_sec=5)

    def sender(session_key, message, timeout_sec):
        return True, {"status": "implemented", "summary": "done"}

    result = process_stream_message(
        redis_client,
        agent,
        sender,
        "cmd:strategy",
        "7-0",
        {"directive": "Priorizar 2FA"},
    )

    assert result.status == "invalid_output"
    assert result.status_code == "openclaw_invalid_output"
    assert result.event_name == "runtime.openclaw_invalid_output"
    assert result.metadata["output_valid"] is False


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
