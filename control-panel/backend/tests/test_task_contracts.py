from app.services.task_contracts import validate_contract


def test_validate_contract_ok():
    ok, data, errors = validate_contract(
        "plan",
        {
            "task_id": "t1",
            "task_title": "Title",
            "task_description": "Desc",
            "plan_steps": ["step"],
            "risk_notes": ["risk"],
        },
    )
    assert ok is True
    assert data is not None
    assert errors == []

    ok, data, errors = validate_contract(
        "execute",
        {
            "task_id": "t1",
            "plan_steps": ["step"],
            "actions": ["do"],
            "artifacts": ["file"],
            "evidence": ["log"],
            "errors": [],
        },
    )
    assert ok is True
    assert data is not None

    ok, data, errors = validate_contract(
        "self_review",
        {"task_id": "t1", "checks": ["c"], "issues": [], "decision": "pass"},
    )
    assert ok is True

    ok, data, errors = validate_contract(
        "peer_review",
        {
            "task_id": "t1",
            "reviewer": "ceo",
            "issues": [],
            "decision": "rework",
        },
    )
    assert ok is True

    ok, data, errors = validate_contract(
        "consolidate",
        {
            "task_id": "t1",
            "summary": "sum",
            "artifacts": ["file"],
            "evidence": ["log"],
            "next_steps": ["next"],
        },
    )
    assert ok is True


def test_validate_contract_rejects_missing_fields():
    ok, data, errors = validate_contract("plan", {"task_id": "t1"})
    assert ok is False
    assert data is None
    assert errors


def test_validate_contract_unknown():
    ok, data, errors = validate_contract("unknown", {"task_id": "t1"})
    assert ok is False
    assert data is None
    assert errors == ["unknown_contract"]
