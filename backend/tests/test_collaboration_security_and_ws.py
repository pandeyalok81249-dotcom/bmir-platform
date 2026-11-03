import json
import pytest
from httpx import AsyncClient

from app.api.v1.endpoints.collaboration_ws import collaboration_websocket_endpoint
from app.core.collaboration_manager import collaboration_ws_manager
from tests.test_resumes import SAMPLE_RESUME_TEXT


class MockWebSocket:
    def __init__(self, incoming_messages=None):
        self.accepted = False
        self.closed = False
        self.close_code = None
        self.sent_messages = []
        self._incoming = incoming_messages or []

    async def accept(self):
        self.accepted = True

    async def close(self, code=1000):
        self.closed = True
        self.close_code = code

    async def send_json(self, data):
        self.sent_messages.append(data)

    async def receive_text(self):
        if self._incoming:
            return self._incoming.pop(0)
        from fastapi import WebSocketDisconnect
        raise WebSocketDisconnect()


@pytest.mark.asyncio
async def test_cross_tenant_security_isolation(client: AsyncClient, auth_headers: dict):
    # 1. User A (auth_headers) uploads Resume A
    files = {"file": ("user_a_resume.txt", SAMPLE_RESUME_TEXT.encode("utf-8"), "text/plain")}
    up_resp = await client.post("/api/v1/resumes/upload", headers=auth_headers, files=files)
    assert up_resp.status_code == 200
    resume_a_id = up_resp.json()["data"]["id"]

    # 2. Register User B
    user_b_payload = {
        "email": "user_b_unauthorized@example.com",
        "password": "SecurePassword123!",
        "full_name": "Bob Intruder",
    }
    b_reg = await client.post("/api/v1/auth/register", json=user_b_payload)
    assert b_reg.status_code == 200
    token_b = b_reg.json()["data"]["tokens"]["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 3. User B attempts to access Resume A directly -> Must return 404
    b_access = await client.get(f"/api/v1/resumes/{resume_a_id}", headers=headers_b)
    assert b_access.status_code == 404

    # 4. User B attempts to view or post comments on Resume A -> Must return 404
    b_comment = await client.post(
        f"/api/v1/collaboration/resumes/{resume_a_id}/comments",
        headers=headers_b,
        json={"comment_text": "Unauthorized comment probe"},
    )
    assert b_comment.status_code == 404

    # 5. User A creates Workspace and shares Resume A
    ws_resp = await client.post(
        "/api/v1/collaboration/workspaces",
        headers=auth_headers,
        json={"name": "Secure Shared Review"},
    )
    ws_id = ws_resp.json()["data"]["id"]

    await client.post(
        f"/api/v1/collaboration/workspaces/{ws_id}/resumes/{resume_a_id}",
        headers=auth_headers,
    )

    # 6. User A invites User B as Reviewer
    inv_resp = await client.post(
        f"/api/v1/collaboration/workspaces/{ws_id}/invitations",
        headers=auth_headers,
        json={"invitee_email": "user_b_unauthorized@example.com", "role": "reviewer"},
    )
    token = inv_resp.json()["data"]["token"]

    # User B accepts invitation
    await client.post(f"/api/v1/collaboration/invitations/{token}/accept", headers=headers_b)

    # 7. User B NOW has authorized access to post comments on Resume A
    auth_comment = await client.post(
        f"/api/v1/collaboration/resumes/{resume_a_id}/comments",
        headers=headers_b,
        json={"comment_text": "Authorized review comment from Bob."},
    )
    assert auth_comment.status_code == 200
    assert auth_comment.json()["data"]["comment_text"] == "Authorized review comment from Bob."


@pytest.mark.asyncio
async def test_websocket_authorization_and_events(client: AsyncClient, auth_headers: dict):
    # 1. Upload Resume
    files = {"file": ("ws_resume.txt", SAMPLE_RESUME_TEXT.encode("utf-8"), "text/plain")}
    up_resp = await client.post("/api/v1/resumes/upload", headers=auth_headers, files=files)
    assert up_resp.status_code == 200
    resume_id = up_resp.json()["data"]["id"]

    token = auth_headers["Authorization"].replace("Bearer ", "")

    # 2. Test Invalid Token rejection
    bad_ws = MockWebSocket()
    await collaboration_websocket_endpoint(
        websocket=bad_ws,
        resume_id=resume_id,
        token="invalid.token.here",
    )
    assert bad_ws.closed is True
    assert bad_ws.close_code == 1008
    assert bad_ws.accepted is False

    # 3. Test Valid Token connection & heartbeat
    incoming = [
        json.dumps({"type": "ping"}),
        json.dumps({"type": "cursor_focus", "section": "experience", "selected_text": "FastAPI"}),
    ]
    good_ws = MockWebSocket(incoming_messages=incoming)
    await collaboration_websocket_endpoint(
        websocket=good_ws,
        resume_id=resume_id,
        token=token,
    )
    assert good_ws.accepted is True
    assert len(good_ws.sent_messages) >= 3

    # First message: Collaborator joined broadcast
    assert good_ws.sent_messages[0]["type"] == "collaborator_joined"

    # Second message: Active Collaborators list
    assert good_ws.sent_messages[1]["type"] == "active_collaborators"

    # Third message: Pong Heartbeat response
    assert good_ws.sent_messages[2]["type"] == "pong"
    assert "timestamp" in good_ws.sent_messages[2]
