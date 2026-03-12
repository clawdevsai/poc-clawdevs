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
    TOOL_PUBLISH_PR_REVIEW,
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
from app.agents.architect_review_agent import ArchitectReviewAgent
from app.agents.po_agent import POAgent
from app.agents.developer_agent import DeveloperAgent
from app.agents.devops_agent import DevOpsAgent
from app.agents.dba_agent import DBAAgent
from app.agents.cybersec_agent import CyberSecAgent
from app.agents.qa_agent import QAAgent
from app.core.github_reviews import publish_consensus_comment, publish_role_review_comment
from app.core.github_prs import check_pr_merged_status
from app.core.github_issues import ensure_github_issue_for_runtime_issue
from app.core.review_consensus import finalize_round_if_ready, record_review_decision
from app.interfaces.github_webhook import (
    collect_metrics,
    is_reset_authorized,
    process_pull_request_event,
    reset_metrics,
    verify_signature,
)
from app.runtime.stream_worker import _claim_pending_messages
import io
from contextlib import redirect_stdout
import os
from unittest.mock import patch
from app.shared.issue_state import STATE_DEPLOYED, STATE_IN_REVIEW, STATE_READY, STATE_REFINAMENTO


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


def test_claim_pending_messages_normalizes_xautoclaim_output():
    class FakeRedisAutoClaim:
        def xautoclaim(self, _stream, _group, _consumer, _idle, start_id, count):
            assert start_id == "0-0"
            assert count == 10
            return ("1-0", [(b"1-1", {b"issue_id": b"DIR-1"})], [])

    agent = FakeAgent()
    next_start, messages = _claim_pending_messages(
        FakeRedisAutoClaim(),
        agent,
        start_id="0-0",
        min_idle_ms=30000,
        count=10,
    )

    assert next_start == "1-0"
    assert messages == [("1-1", {b"issue_id": b"DIR-1"})]


def test_claim_pending_messages_handles_missing_xautoclaim():
    class FakeRedisNoAutoClaim:
        pass

    agent = FakeAgent()
    next_start, messages = _claim_pending_messages(
        FakeRedisNoAutoClaim(),
        agent,
        start_id="0-0",
        min_idle_ms=30000,
        count=10,
    )

    assert next_start == "0-0"
    assert messages == []


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


def test_publish_code_ready_emits_pr_review_with_round_control():
    redis_client = FakeRedis()

    ok, output = publish_code_ready(
        redis_client=redis_client,
        issue_id="88",
        branch="feat/login",
        repo="org/repo",
        pr="123",
    )

    assert ok is True
    assert output["stream"] == "pr:review"
    assert output["round"] == "1"
    assert output["state"] == STATE_IN_REVIEW
    assert redis_client.store["project:v1:issue:88:state"] == STATE_IN_REVIEW
    assert redis_client.store["project:v1:issue:88:pr_review_round"] == "1"
    assert redis_client.store["project:v1:issue:88:pr_number"] == "123"
    assert redis_client.store["project:v1:issue:88:repo"] == "org/repo"
    assert redis_client.added[0] == (
        "code:ready",
        {"issue_id": "88", "branch": "feat/login", "repo": "org/repo", "pr": "123", "round": "1"},
    )
    assert redis_client.added[1] == (
        "pr:review",
        {"issue_id": "88", "branch": "feat/login", "repo": "org/repo", "pr": "123", "round": "1"},
    )


def test_publish_code_ready_escalates_after_round_limit():
    redis_client = FakeRedis()

    for _ in range(6):
        ok, output = publish_code_ready(
            redis_client=redis_client,
            issue_id="99",
            branch="feat/limits",
            repo="org/repo",
            pr="999",
        )

    assert ok is True
    assert output["status"] == "escalated"
    assert output["round"] == "6"
    assert redis_client.store["project:v1:issue:99:pr_review_round"] == "6"
    assert redis_client.added[-1][0] == "orchestrator:events"
    assert redis_client.added[-1][1]["type"] == "architect_final_decision_required"


def test_publish_deploy_event_sets_deployed_and_emits_feature_complete():
    redis_client = FakeRedis()
    redis_client.store["project:v1:issue:90:active_developer"] = "developer-1"
    redis_client.store["project:v1:developer:developer-1:active_issue"] = "90"

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
    assert redis_client.store["project:v1:issue:90:pr_merged"] == "1"
    assert "project:v1:issue:90:pr_review_round" in redis_client.deleted
    assert "project:v1:developer:developer-1:active_issue" in redis_client.deleted
    assert "project:v1:issue:90:active_developer" in redis_client.deleted
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
    assert TOOL_PUBLISH_PR_REVIEW in registry._tools
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


def test_openclaw_role_assets_are_bound_for_new_review_roles():
    dba = get_role_openclaw_config("DBA")
    cybersec = get_role_openclaw_config("CyberSec")
    architect_review = get_role_openclaw_config("Architect-review")

    assert dba is not None
    assert dba.profile == "dba"
    assert dba.output_schema == "dba"
    assert cybersec is not None
    assert cybersec.profile == "cybersec"
    assert cybersec.output_schema == "cybersec"
    assert architect_review is not None
    assert architect_review.profile == "architect_review"
    assert architect_review.output_schema == "architect_review"


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


def test_architect_agent_routes_approved_issue_to_backlog():
    redis_client = FakeRedis()
    agent = ArchitectDraftAgent()
    agent.settings.policy = ExecutionPolicy(block_ms=10, timeout_sec=5)

    def sender(session_key, message, timeout_sec):
        return True, {
            "status": "approved",
            "summary": "aprovado",
            "decision": "ok",
            "next_action": "task:backlog",
        }

    result = process_stream_message(
        redis_client,
        agent,
        sender,
        "draft.2.issue",
        "2-1",
        {"issue_id": "DIR-100", "title": "API CRUD user", "summary": "criar endpoints", "priority": "1"},
    )

    assert result.status == "forwarded"
    assert result.status_code == "architect_approved_to_backlog"
    assert result.event_name == "architect.approved_to_backlog"
    assert redis_client.store["project:v1:issue:DIR-100:state"] == "Ready"
    assert redis_client.added[-1][0] == "task:backlog"
    assert redis_client.added[-1][1]["issue_id"] == "DIR-100"
    assert redis_client.acks == [("draft.2.issue", "clawdevs", "2-1")]


def test_architect_agent_routes_rejected_issue_to_draft_rejected():
    redis_client = FakeRedis()
    agent = ArchitectDraftAgent()
    agent.settings.policy = ExecutionPolicy(block_ms=10, timeout_sec=5)

    def sender(session_key, message, timeout_sec):
        return True, {
            "status": "rejected",
            "summary": "reprovado",
            "decision": "faltam criterios",
            "next_action": "draft_rejected",
        }

    result = process_stream_message(
        redis_client,
        agent,
        sender,
        "draft.2.issue",
        "2-2",
        {"issue_id": "DIR-101", "title": "API CRUD user", "summary": "criar endpoints", "priority": "1"},
    )

    assert result.status == "forwarded"
    assert result.status_code == "architect_rejected_to_refinamento"
    assert result.event_name == "architect.rejected_to_refinamento"
    assert redis_client.store["project:v1:issue:DIR-101:state"] == "Refinamento"
    assert redis_client.added[-1][0] == "draft_rejected"
    assert redis_client.added[-1][1]["issue_id"] == "DIR-101"
    assert redis_client.acks == [("draft.2.issue", "clawdevs", "2-2")]


def test_po_agent_publishes_draft_and_marks_github_sync():
    redis_client = FakeRedis()
    agent = POAgent()

    with patch(
        "app.agents.po_agent.ensure_github_issue_for_runtime_issue",
        return_value={"status": "synced", "number": "77", "url": "https://github.com/org/repo/issues/77"},
    ) as mocked_sync:
        result = process_stream_message(
            redis_client,
            agent,
            lambda session_key, message, timeout_sec: (
                True,
                {
                    "status": "planned",
                    "summary": "ok",
                    "next_action": "draft.2.issue",
                    "issues": [
                        {"title": "Criar endpoint POST /users", "priority": "1", "acceptance": "retornar 201"}
                    ],
                },
            ),
            "cmd:strategy",
            "9-9",
            {"issue_id": "DIR-200", "repo": "clawdevsai/user-api"},
        )

    assert result.status == "forwarded"
    assert result.status_code == "po_published_draft_issue"
    assert result.metadata["published_count"] == 1
    assert result.metadata["github_synced"] == 1
    assert redis_client.store["project:v1:issue:DIR-200-1:state"] == "Refinamento"
    assert redis_client.added[-1][0] == "draft.2.issue"
    assert redis_client.added[-1][1]["issue_id"] == "DIR-200-1"
    mocked_sync.assert_called_once()


def test_qa_agent_consumes_pr_review_stream_by_default():
    previous_qa_review = os.environ.get("QA_REVIEW_STREAM")
    previous_pr_review = os.environ.get("STREAM_PR_REVIEW")
    os.environ.pop("QA_REVIEW_STREAM", None)
    os.environ.pop("STREAM_PR_REVIEW", None)
    try:
        agent = QAAgent()
    finally:
        if previous_qa_review is None:
            os.environ.pop("QA_REVIEW_STREAM", None)
        else:
            os.environ["QA_REVIEW_STREAM"] = previous_qa_review
        if previous_pr_review is None:
            os.environ.pop("STREAM_PR_REVIEW", None)
        else:
            os.environ["STREAM_PR_REVIEW"] = previous_pr_review
    assert agent.stream_name == "pr:review"


def test_dba_and_cybersec_agents_consume_pr_review_stream():
    dba = DBAAgent()
    cybersec = CyberSecAgent()
    assert dba.stream_name == "pr:review"
    assert cybersec.stream_name == "pr:review"


def test_architect_review_ignores_non_escalation_events():
    redis_client = FakeRedis()
    agent = ArchitectReviewAgent()

    def sender(session_key, message, timeout_sec):
        raise AssertionError("sender should not be called")

    result = process_stream_message(
        redis_client,
        agent,
        sender,
        "orchestrator:events",
        "2-2",
        {"type": "feature_complete", "issue_id": "11"},
    )

    assert result.status == "ignored"
    assert result.status_code == "ignored_non_final_decision_event"
    assert result.event_name == "architect_review.ignored_non_final_decision_event"
    assert redis_client.acks == [("orchestrator:events", "clawdevs-architect-review", "2-2")]


def test_architect_review_processes_escalation_event():
    redis_client = FakeRedis()
    agent = ArchitectReviewAgent()

    def sender(session_key, message, timeout_sec):
        assert session_key == "agent:architect_review:main"
        assert "issue_id: 12" in message
        assert "round: 6" in message
        return True, {"queued": True}

    result = process_stream_message(
        redis_client,
        agent,
        sender,
        "orchestrator:events",
        "2-3",
        {"type": "architect_final_decision_required", "issue_id": "12", "round": "6", "max_rounds": "5"},
    )

    assert result.status == "forwarded"
    assert result.status_code == "forwarded"
    assert result.event_name == "architect_review.forwarded"
    assert redis_client.acks == [("orchestrator:events", "clawdevs-architect-review", "2-3")]


def test_developer_agent_requeues_when_lock_is_busy():
    redis_client = FakeRedis()
    agent = DeveloperAgent()
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


def test_developer_agent_blocks_new_issue_until_previous_merge():
    redis_client = FakeRedis()
    agent = DeveloperAgent()
    developer_id = os.getenv("POD_NAME", os.getenv("HOSTNAME", "developer"))
    redis_client.store[f"project:v1:developer:{developer_id}:active_issue"] = "41"
    redis_client.store["project:v1:issue:41:pr_merged"] = "0"

    def sender(session_key, message, timeout_sec):
        raise AssertionError("sender should not be called")

    result = process_stream_message(
        redis_client,
        agent,
        sender,
        "task:backlog",
        "3-1",
        {"issue_id": "42", "priority": "1"},
    )

    assert result.status == "blocked"
    assert result.status_code == "blocked_waiting_merge"
    assert result.event_name == "developer.blocked_waiting_merge"
    assert len(redis_client.added) == 1
    stream_name, payload = redis_client.added[0]
    assert stream_name == "task:backlog"
    assert payload["issue_id"] == "42"
    assert payload["attempt"] == "2"
    assert redis_client.acks == [("task:backlog", "clawdevs", "3-1")]


def test_developer_agent_allows_next_issue_when_previous_merge_confirmed_by_github():
    redis_client = FakeRedis()
    agent = DeveloperAgent()
    developer_id = os.getenv("POD_NAME", os.getenv("HOSTNAME", "developer"))
    redis_client.store[f"project:v1:developer:{developer_id}:active_issue"] = "41"
    redis_client.store["project:v1:issue:41:pr_merged"] = "0"
    redis_client.store["project:v1:issue:41:pr_number"] = "441"
    redis_client.store["project:v1:issue:41:repo"] = "org/repo"

    with patch("app.agents.developer_agent.check_pr_merged_status", return_value=True):
        result = process_stream_message(
            redis_client,
            agent,
            lambda session_key, message, timeout_sec: (True, {"queued": True}),
            "task:backlog",
            "3-2",
            {"issue_id": "42", "priority": "1"},
        )

    assert result.status == "forwarded"
    assert result.status_code == "forwarded"
    assert redis_client.store["project:v1:issue:41:pr_merged"] == "1"
    assert redis_client.store[f"project:v1:developer:{developer_id}:active_issue"] == "42"
    assert redis_client.acks == [("task:backlog", "clawdevs", "3-2")]


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


def test_review_consensus_pending_until_all_roles_submit():
    redis_client = FakeRedis()
    record_review_decision(
        redis_client,
        issue_id="501",
        review_round="1",
        role="QA",
        send_output={"status": "approved", "summary": "qa ok"},
        repo="",
        pr="",
    )

    status = finalize_round_if_ready(
        redis_client,
        issue_id="501",
        review_round="1",
        branch="feat/x",
        repo="org/repo",
        pr="501",
    )

    assert status == "pending"
    assert redis_client.added == []


def test_review_consensus_approved_publishes_event_devops_once():
    redis_client = FakeRedis()
    for role in ("QA", "DBA", "CyberSec"):
        record_review_decision(
            redis_client,
            issue_id="502",
            review_round="2",
            role=role,
            send_output={"status": "approved", "summary": f"{role} ok"},
            repo="",
            pr="",
        )

    status = finalize_round_if_ready(
        redis_client,
        issue_id="502",
        review_round="2",
        branch="feat/y",
        repo="org/repo",
        pr="502",
    )
    assert status == "approved"
    assert redis_client.added[0][0] == "event:devops"
    assert redis_client.added[0][1]["issue_id"] == "502"
    assert redis_client.added[1][0] == "orchestrator:events"
    assert redis_client.added[1][1]["type"] == "review_consensus_approved"

    second = finalize_round_if_ready(
        redis_client,
        issue_id="502",
        review_round="2",
        branch="feat/y",
        repo="org/repo",
        pr="502",
    )
    assert second == "already_finalized"
    assert len(redis_client.added) == 2


def test_review_consensus_blocked_returns_issue_to_backlog():
    redis_client = FakeRedis()
    record_review_decision(
        redis_client,
        issue_id="503",
        review_round="3",
        role="QA",
        send_output={"status": "approved", "summary": "qa ok"},
        repo="",
        pr="",
    )
    record_review_decision(
        redis_client,
        issue_id="503",
        review_round="3",
        role="DBA",
        send_output={"status": "blocked", "summary": "missing index"},
        repo="",
        pr="",
    )
    record_review_decision(
        redis_client,
        issue_id="503",
        review_round="3",
        role="CyberSec",
        send_output={"status": "approved", "summary": "sec ok"},
        repo="",
        pr="",
    )

    status = finalize_round_if_ready(
        redis_client,
        issue_id="503",
        review_round="3",
        branch="feat/z",
        repo="org/repo",
        pr="503",
    )
    assert status == "blocked"
    assert redis_client.store["project:v1:issue:503:state"] == "Backlog"
    assert redis_client.added[0][0] == "task:backlog"
    assert redis_client.added[0][1]["reason"] == "review_blocked"
    assert redis_client.added[1][0] == "orchestrator:events"
    assert redis_client.added[1][1]["type"] == "review_consensus_blocked"


def test_publish_role_review_comment_is_idempotent_when_not_configured():
    redis_client = FakeRedis()
    first = publish_role_review_comment(
        redis_client,
        issue_id="601",
        review_round="1",
        role="QA",
        decision="approved",
        summary="ok",
        repo="",
        pr="601",
    )
    second = publish_role_review_comment(
        redis_client,
        issue_id="601",
        review_round="1",
        role="QA",
        decision="approved",
        summary="ok",
        repo="",
        pr="601",
    )
    assert first == "skipped_not_configured"
    assert second == "skipped_not_configured"


def test_publish_consensus_comment_uses_request_fn_and_sets_posted_state():
    redis_client = FakeRedis()
    calls = []

    def fake_request(url, headers, body):
        calls.append((url, headers, body))

    previous_token = os.environ.get("GITHUB_TOKEN")
    os.environ["GITHUB_TOKEN"] = "token-x"
    try:
        result = publish_consensus_comment(
            redis_client,
            issue_id="602",
            review_round="2",
            repo="org/repo",
            pr="77",
            outcome="approved",
            decisions_by_role={
                "QA": {"decision": "approved", "summary": "qa ok"},
                "DBA": {"decision": "approved", "summary": "dba ok"},
                "CyberSec": {"decision": "approved", "summary": "sec ok"},
            },
            request_fn=fake_request,
        )
        assert result == "posted"
        assert len(calls) == 1
        assert calls[0][0].endswith("/repos/org/repo/issues/77/comments")
    finally:
        if previous_token is None:
            os.environ.pop("GITHUB_TOKEN", None)
        else:
            os.environ["GITHUB_TOKEN"] = previous_token


def test_check_pr_merged_status_uses_request_fn_and_cache():
    redis_client = FakeRedis()
    calls = []

    def fake_request(url, headers):
        calls.append((url, headers))
        return {"merged": True}

    previous_token = os.environ.get("GITHUB_TOKEN")
    os.environ["GITHUB_TOKEN"] = "token-x"
    try:
        first = check_pr_merged_status(
            redis_client,
            issue_id="701",
            repo="org/repo",
            pr="91",
            request_fn=fake_request,
        )
        second = check_pr_merged_status(
            redis_client,
            issue_id="701",
            repo="org/repo",
            pr="91",
            request_fn=fake_request,
        )
    finally:
        if previous_token is None:
            os.environ.pop("GITHUB_TOKEN", None)
        else:
            os.environ["GITHUB_TOKEN"] = previous_token

    assert first is True
    assert second is True
    assert len(calls) == 1
    assert redis_client.store["project:v1:issue:701:github_pr_merged_cache"] == "1"


def test_ensure_github_issue_for_runtime_issue_creates_and_persists_mapping():
    redis_client = FakeRedis()
    calls = []

    def fake_request(url, headers, payload):
        calls.append((url, headers, payload))
        return {"number": 88, "html_url": "https://github.com/org/repo/issues/88"}

    previous_token = os.environ.get("GITHUB_TOKEN")
    os.environ["GITHUB_TOKEN"] = "token-x"
    try:
        result = ensure_github_issue_for_runtime_issue(
            redis_client,
            issue_id="DIR-300",
            repo="org/repo",
            title="Criar endpoint",
            body="Detalhes de aceite",
            request_fn=fake_request,
        )
    finally:
        if previous_token is None:
            os.environ.pop("GITHUB_TOKEN", None)
        else:
            os.environ["GITHUB_TOKEN"] = previous_token

    assert result["status"] == "synced"
    assert redis_client.store["project:v1:issue:DIR-300:github_issue_number"] == "88"
    assert redis_client.store["project:v1:issue:DIR-300:github_issue_url"] == "https://github.com/org/repo/issues/88"
    assert redis_client.store["project:v1:issue:DIR-300:github_sync_status"] == "synced"
    assert redis_client.store["project:v1:issue:DIR-300:repo"] == "org/repo"
    assert len(calls) == 1


def test_ensure_github_issue_for_runtime_issue_is_idempotent_when_already_synced():
    redis_client = FakeRedis()
    redis_client.store["project:v1:issue:DIR-301:github_issue_number"] = "89"
    redis_client.store["project:v1:issue:DIR-301:github_issue_url"] = "https://github.com/org/repo/issues/89"

    result = ensure_github_issue_for_runtime_issue(
        redis_client,
        issue_id="DIR-301",
        repo="org/repo",
        title="Nao deve criar",
        body="",
        request_fn=lambda *_args, **_kwargs: {"number": 90},
    )

    assert result["status"] == "already_synced"
    assert result["number"] == "89"
    assert redis_client.store["project:v1:issue:DIR-301:github_sync_status"] == "already_synced"


def test_github_webhook_sets_in_review_on_pr_synchronize():
    redis_client = FakeRedis()
    redis_client.store["project:v1:repo:org__repo:pr:77:issue_id"] = "TG-77"

    result = process_pull_request_event(
        redis_client,
        {
            "action": "synchronize",
            "number": 77,
            "repository": {"full_name": "org/repo"},
            "pull_request": {"number": 77},
        },
    )

    assert result["status"] == "ok"
    assert result["transition"] == "in_review"
    assert redis_client.store["project:v1:issue:TG-77:state"] == "InReview"
    assert redis_client.store["project:v1:github:webhook:metric:in_review_total"] == "1"
    assert redis_client.added[-1][0] == "orchestrator:events"
    assert redis_client.added[-1][1]["type"] == "github_pr_in_review"


def test_github_webhook_marks_merged_and_emits_devops_event():
    redis_client = FakeRedis()
    redis_client.store["project:v1:repo:org__repo:pr:99:issue_id"] = "TG-99"
    redis_client.store["project:v1:issue:TG-99:active_developer"] = "developer-1"
    redis_client.store["project:v1:developer:developer-1:active_issue"] = "TG-99"

    result = process_pull_request_event(
        redis_client,
        {
            "action": "closed",
            "number": 99,
            "repository": {"full_name": "org/repo"},
            "pull_request": {
                "number": 99,
                "merged": True,
                "base": {"ref": "main"},
            },
        },
    )

    assert result["status"] == "ok"
    assert result["transition"] == "merged"
    assert redis_client.store["project:v1:issue:TG-99:pr_merged"] == "1"
    assert redis_client.store["project:v1:issue:TG-99:state"] == "Deployed"
    assert redis_client.store["project:v1:github:webhook:metric:merged_total"] == "1"
    assert "project:v1:developer:developer-1:active_issue" in redis_client.deleted
    assert "project:v1:issue:TG-99:active_developer" in redis_client.deleted
    assert redis_client.added[0][0] == "event:devops"
    assert redis_client.added[0][1]["reason"] == "github_webhook_pr_merged"
    assert redis_client.added[1][0] == "orchestrator:events"
    assert redis_client.added[1][1]["type"] == "github_pr_merged"


def test_github_webhook_signature_validation():
    body = b'{"action":"opened"}'
    secret = "abc123"
    import hmac
    import hashlib

    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    assert verify_signature(body, f"sha256={digest}", secret) is True
    assert verify_signature(body, "sha256=invalid", secret) is False


def test_github_webhook_collect_metrics_reads_defaults():
    redis_client = FakeRedis()
    metrics = collect_metrics(redis_client)
    assert metrics["received_total"] == ""
    assert metrics["processed_total"] == ""


def test_github_webhook_reset_metrics_clears_counters():
    redis_client = FakeRedis()
    redis_client.store["project:v1:github:webhook:metric:received_total"] = "10"
    redis_client.store["project:v1:github:webhook:metric:last_result"] = "ok"
    reset_metrics(redis_client)
    assert redis_client.store.get("project:v1:github:webhook:metric:received_total") is None
    assert redis_client.store.get("project:v1:github:webhook:metric:last_result") is None


def test_github_webhook_reset_authorization_requires_matching_token():
    assert is_reset_authorized("", "secret-x") is False
    assert is_reset_authorized("wrong", "secret-x") is False
    assert is_reset_authorized("secret-x", "secret-x") is True
