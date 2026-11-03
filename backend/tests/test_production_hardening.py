import pytest
from httpx import AsyncClient
from app.core.rate_limit import SlidingWindowRateLimiter
from app.core.database import Base


@pytest.mark.asyncio
async def test_security_headers_present(client: AsyncClient):
    resp = await client.get("/health")
    assert resp.status_code == 200
    assert resp.headers.get("X-Content-Type-Options") == "nosniff"
    assert resp.headers.get("X-Frame-Options") == "DENY"
    assert resp.headers.get("X-XSS-Protection") == "1; mode=block"
    assert "Strict-Transport-Security" in resp.headers
    assert "Referrer-Policy" in resp.headers


@pytest.mark.asyncio
async def test_health_and_readiness_endpoints(client: AsyncClient):
    h_resp = await client.get("/health")
    assert h_resp.status_code == 200
    assert h_resp.json()["status"] == "healthy"

    r_resp = await client.get("/ready")
    assert r_resp.status_code == 200
    assert r_resp.json()["status"] == "ready"


def test_sliding_window_rate_limiter_logic():
    limiter = SlidingWindowRateLimiter(limit=3, window_seconds=10)
    client_id = "test_client_ip"

    # Call 1
    allowed, remaining, _ = limiter.is_allowed(client_id)
    assert allowed is True
    assert remaining == 2

    # Call 2
    allowed, remaining, _ = limiter.is_allowed(client_id)
    assert allowed is True
    assert remaining == 1

    # Call 3
    allowed, remaining, _ = limiter.is_allowed(client_id)
    assert allowed is True
    assert remaining == 0

    # Call 4: Exceeded!
    allowed, remaining, reset_in = limiter.is_allowed(client_id)
    assert allowed is False
    assert remaining == 0
    assert reset_in > 0


def test_composite_indexes_registered():
    indexes = {idx.name: idx for table in Base.metadata.tables.values() for idx in table.indexes}
    assert "ix_resumes_user_created" in indexes
    assert "ix_analyses_resume_created" in indexes
    assert "ix_job_matches_version_score" in indexes
    assert "ix_interviews_user_created" in indexes
    assert "ix_subscriptions_user_status" in indexes

