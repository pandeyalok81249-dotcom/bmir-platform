import pytest
from httpx import AsyncClient
from tests.test_resumes import SAMPLE_RESUME_TEXT


@pytest.mark.asyncio
async def test_tenant_isolation_and_unauthorized_access(client: AsyncClient):
    # 1. Unauthenticated request to protected endpoint should return 401
    unauth_resp = await client.get("/api/v1/resumes")
    assert unauth_resp.status_code == 401

    # 2. Register User A
    user_a = await client.post(
        "/api/v1/auth/register",
        json={"email": "usera@example.com", "password": "Password123!", "full_name": "User A"},
    )
    token_a = user_a.json()["data"]["tokens"]["access_token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # 3. Register User B
    user_b = await client.post(
        "/api/v1/auth/register",
        json={"email": "userb@example.com", "password": "Password123!", "full_name": "User B"},
    )
    token_b = user_b.json()["data"]["tokens"]["access_token"]
    headers_b = {"Authorization": f"Bearer {token_b}"}

    # 4. User A uploads a resume
    files = {"file": ("usera_resume.txt", SAMPLE_RESUME_TEXT.encode("utf-8"), "text/plain")}
    up_resp = await client.post(
        "/api/v1/resumes/upload", headers=headers_a, files=files, data={"title": "Private Resume A"}
    )
    assert up_resp.status_code == 200
    resume_a_id = up_resp.json()["data"]["id"]

    # 5. User B attempts to access User A's resume -> Must return 404
    b_access = await client.get(f"/api/v1/resumes/{resume_a_id}", headers=headers_b)
    assert b_access.status_code == 404

    # 6. User B attempts to delete User A's resume -> Must return 404
    b_delete = await client.delete(f"/api/v1/resumes/{resume_a_id}", headers=headers_b)
    assert b_delete.status_code == 404

    # 7. User A can access their own resume
    a_access = await client.get(f"/api/v1/resumes/{resume_a_id}", headers=headers_a)
    assert a_access.status_code == 200

