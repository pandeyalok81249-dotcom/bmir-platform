import pytest
from httpx import AsyncClient
from tests.test_resumes import SAMPLE_RESUME_TEXT


@pytest.mark.asyncio
async def test_collaboration_workspaces_and_invitations(client: AsyncClient, auth_headers: dict):
    # 1. Create Workspace
    ws_payload = {
        "name": "CloudScale Peer Review Group",
        "description": "Cross-reviewing distributed backend engineering resumes",
    }
    create_resp = await client.post(
        "/api/v1/collaboration/workspaces", headers=auth_headers, json=ws_payload
    )
    assert create_resp.status_code == 200
    ws_data = create_resp.json()["data"]
    workspace_id = ws_data["id"]
    assert ws_data["name"] == "CloudScale Peer Review Group"
    assert ws_data["user_role"] == "owner"

    # 2. Upload resume and share to workspace
    files = {"file": ("resume_collab.txt", SAMPLE_RESUME_TEXT.encode("utf-8"), "text/plain")}
    up_resp = await client.post("/api/v1/resumes/upload", headers=auth_headers, files=files)
    assert up_resp.status_code == 200
    resume_id = up_resp.json()["data"]["id"]

    share_resp = await client.post(
        f"/api/v1/collaboration/workspaces/{workspace_id}/resumes/{resume_id}",
        headers=auth_headers,
    )
    assert share_resp.status_code == 200

    # 3. Create Invitation
    inv_payload = {"invitee_email": "peer_reviewer@example.com", "role": "reviewer", "expiry_days": 5}
    inv_resp = await client.post(
        f"/api/v1/collaboration/workspaces/{workspace_id}/invitations",
        headers=auth_headers,
        json=inv_payload,
    )
    assert inv_resp.status_code == 200
    inv_data = inv_resp.json()["data"]
    token = inv_data["token"]
    assert inv_data["status"] == "pending"

    # 4. Register Second User (Peer Reviewer)
    peer_reg = {
        "email": "peer_reviewer@example.com",
        "password": "SecurePassword123!",
        "full_name": "Jordan Peer Reviewer",
    }
    peer_resp = await client.post("/api/v1/auth/register", json=peer_reg)
    assert peer_resp.status_code == 200
    peer_token = peer_resp.json()["data"]["tokens"]["access_token"]
    peer_headers = {"Authorization": f"Bearer {peer_token}"}

    # 5. Peer Reviewer accepts invitation
    accept_resp = await client.post(
        f"/api/v1/collaboration/invitations/{token}/accept", headers=peer_headers
    )
    assert accept_resp.status_code == 200

    # 6. Verify Workspace Details shows 2 members and 1 shared resume
    detail_resp = await client.get(
        f"/api/v1/collaboration/workspaces/{workspace_id}", headers=auth_headers
    )
    assert detail_resp.status_code == 200
    detail = detail_resp.json()["data"]
    assert detail["member_count"] == 2
    assert detail["resume_count"] == 1
    assert resume_id in detail["shared_resume_ids"]

    # 7. Update Peer Member role to editor
    peer_user_id = peer_resp.json()["data"]["user"]["id"]
    role_resp = await client.patch(
        f"/api/v1/collaboration/workspaces/{workspace_id}/members/{peer_user_id}",
        headers=auth_headers,
        json={"role": "editor"},
    )
    assert role_resp.status_code == 200
    assert role_resp.json()["data"]["role"] == "editor"

    # 8. Check activity events
    events_resp = await client.get(
        f"/api/v1/collaboration/workspaces/{workspace_id}/events", headers=auth_headers
    )
    assert events_resp.status_code == 200
    events = events_resp.json()["data"]
    assert len(events) >= 3

