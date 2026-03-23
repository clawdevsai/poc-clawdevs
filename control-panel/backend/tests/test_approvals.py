import pytest
from uuid import uuid4
from app.models import Approval


@pytest.mark.asyncio
async def test_list_approvals(client, auth_headers, db_session):
    approval = Approval(
        action_type="file_write",
        status="pending",
        openclaw_approval_id=str(uuid4()),
    )
    db_session.add(approval)
    await db_session.commit()

    response = await client.get("/approvals", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert "items" in data
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_get_approval_stats(client, auth_headers, db_session):
    db_session.add(Approval(action_type="file_write", status="pending"))
    db_session.add(Approval(action_type="exec", status="approved"))
    db_session.add(Approval(action_type="exec", status="rejected"))
    await db_session.commit()

    response = await client.get("/approvals/stats", headers=auth_headers)
    assert response.status_code == 200
    data = response.json()
    assert data["pending"] >= 1
    assert data["approved"] >= 1
    assert data["rejected"] >= 1


@pytest.mark.asyncio
async def test_get_approval_by_id(client, auth_headers, db_session):
    approval = Approval(action_type="file_write", status="pending")
    db_session.add(approval)
    await db_session.commit()
    await db_session.refresh(approval)

    response = await client.get(f"/approvals/{approval.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["action_type"] == "file_write"


@pytest.mark.asyncio
async def test_decide_approval_no_gateway(client, auth_headers, db_session):
    # approval with no openclaw_approval_id — skips gateway call
    approval = Approval(action_type="file_write", status="pending")
    db_session.add(approval)
    await db_session.commit()
    await db_session.refresh(approval)

    response = await client.post(
        f"/approvals/{approval.id}/decide",
        headers=auth_headers,
        json={"decision": "approved", "justification": "Looks good"},
    )
    assert response.status_code == 200
    assert response.json()["status"] == "approved"
    assert response.json()["justification"] == "Looks good"


@pytest.mark.asyncio
async def test_decide_approval_already_decided(client, auth_headers, db_session):
    approval = Approval(action_type="file_write", status="approved")
    db_session.add(approval)
    await db_session.commit()
    await db_session.refresh(approval)

    response = await client.post(
        f"/approvals/{approval.id}/decide",
        headers=auth_headers,
        json={"decision": "rejected", "justification": "Changed mind"},
    )
    assert response.status_code == 409


@pytest.mark.asyncio
async def test_approvals_requires_auth(client):
    response = await client.get("/approvals")
    assert response.status_code == 403
