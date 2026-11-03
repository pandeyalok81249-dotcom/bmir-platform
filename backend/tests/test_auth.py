import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_register_and_login(client: AsyncClient):
    # 1. Register
    reg_payload = {
        "email": "testuser@example.com",
        "password": "StrongPassword999!",
        "full_name": "Test Engineer",
    }
    reg_resp = await client.post("/api/v1/auth/register", json=reg_payload)
    assert reg_resp.status_code == 200
    reg_data = reg_resp.json()
    assert reg_data["success"] is True
    assert reg_data["data"]["user"]["email"] == "testuser@example.com"
    assert "access_token" in reg_data["data"]["tokens"]

    # 2. Login with valid credentials
    login_payload = {
        "email": "testuser@example.com",
        "password": "StrongPassword999!",
    }
    login_resp = await client.post("/api/v1/auth/login", json=login_payload)
    assert login_resp.status_code == 200
    login_data = login_resp.json()
    assert login_data["success"] is True
    access_token = login_data["data"]["tokens"]["access_token"]
    refresh_token = login_data["data"]["tokens"]["refresh_token"]

    # 3. Refresh token rotation
    ref_resp = await client.post("/api/v1/auth/refresh", json={"refresh_token": refresh_token})
    assert ref_resp.status_code == 200
    ref_data = ref_resp.json()
    assert "access_token" in ref_data["data"]
    assert "refresh_token" in ref_data["data"]

    # 4. Login with invalid password fails
    bad_login = await client.post("/api/v1/auth/login", json={"email": "testuser@example.com", "password": "WrongPassword"})
    assert bad_login.status_code == 401

