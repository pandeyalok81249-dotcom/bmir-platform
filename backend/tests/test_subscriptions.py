import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_subscription_tiers_metadata(client: AsyncClient):
    resp = await client.get("/api/v1/subscriptions/tiers")
    assert resp.status_code == 200
    data = resp.json()["data"]
    assert len(data) >= 3
    tiers = {t["tier"]: t for t in data}
    assert "free" in tiers
    assert "pro" in tiers
    assert "professional" in tiers

    assert tiers["free"]["max_resumes_per_month"] == 3
    assert tiers["pro"]["max_resumes_per_month"] == 25
    assert tiers["professional"]["max_resumes_per_month"] == 999999
    assert "evidence_graph" in tiers["pro"]["included_features"]
    assert "collaboration_workspaces" in tiers["professional"]["included_features"]


@pytest.mark.asyncio
async def test_user_default_subscription_and_usage(client: AsyncClient, auth_headers: dict):
    # 1. Fetch current subscription
    sub_resp = await client.get("/api/v1/subscriptions/me", headers=auth_headers)
    assert sub_resp.status_code == 200
    sub_data = sub_resp.json()["data"]
    assert sub_data["tier"] == "free"
    assert sub_data["status"] == "active"
    assert sub_data["cancel_at_period_end"] is False

    # 2. Fetch usage quota
    usage_resp = await client.get("/api/v1/subscriptions/usage", headers=auth_headers)
    assert usage_resp.status_code == 200
    usage_data = usage_resp.json()["data"]
    assert usage_data["tier"] == "free"
    assert usage_data["resumes_uploaded"] == 0
    assert usage_data["max_resumes"] == 3
    assert usage_data["max_ai_analyses"] == 5

    # 3. Check feature access on free tier
    check_resp = await client.get("/api/v1/subscriptions/check/basic_analysis", headers=auth_headers)
    assert check_resp.status_code == 200
    assert check_resp.json()["data"]["allowed"] is True

    # 4. Check locked feature on free tier
    lock_resp = await client.get("/api/v1/subscriptions/check/evidence_graph", headers=auth_headers)
    assert lock_resp.status_code == 200
    lock_data = lock_resp.json()["data"]
    assert lock_data["allowed"] is False
    assert lock_data["required_tier"] == "pro"


@pytest.mark.asyncio
async def test_subscription_upgrade_and_cancellation(client: AsyncClient, auth_headers: dict):
    # 1. Upgrade to Pro
    upgrade_payload = {"target_tier": "pro", "payment_method_id": "pm_card_visa"}
    up_resp = await client.post("/api/v1/subscriptions/upgrade", json=upgrade_payload, headers=auth_headers)
    assert up_resp.status_code == 200
    up_data = up_resp.json()["data"]
    assert up_data["tier"] == "pro"
    assert up_data["status"] == "active"

    # 2. Verify unlocked feature
    check_resp = await client.get("/api/v1/subscriptions/check/evidence_graph", headers=auth_headers)
    assert check_resp.status_code == 200
    assert check_resp.json()["data"]["allowed"] is True

    # 3. Verify expanded usage limits
    usage_resp = await client.get("/api/v1/subscriptions/usage", headers=auth_headers)
    assert usage_resp.status_code == 200
    usage_data = usage_resp.json()["data"]
    assert usage_data["tier"] == "pro"
    assert usage_data["max_resumes"] == 25
    assert usage_data["max_ai_analyses"] == 100

    # 4. Cancel subscription (cancel at period end)
    cancel_resp = await client.post("/api/v1/subscriptions/cancel", headers=auth_headers)
    assert cancel_resp.status_code == 200
    assert cancel_resp.json()["data"]["cancel_at_period_end"] is True
