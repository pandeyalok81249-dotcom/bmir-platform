import pytest
from httpx import AsyncClient, ASGITransport

from app.main import app
from app.services.market_intelligence import JobMarketIntelligenceService


def test_service_role_market_overview():
    service = JobMarketIntelligenceService()
    overview = service.get_role_market_overview("Senior Backend Engineer")

    assert overview.role_title == "Senior Backend Engineer"
    assert overview.demand_index > 0
    assert overview.provenance.sample_size >= 10000
    assert "O*NET" in overview.provenance.source_name
    assert "historical observational aggregate" in overview.provenance.disclaimer.lower() or "observational aggregate" in overview.provenance.disclaimer.lower()
    assert len(overview.top_demanded_skills) >= 5
    assert "0-2 yrs (Junior)" in overview.experience_distribution

    # Verify skill metrics
    python_skill = next((s for s in overview.top_demanded_skills if s.skill_name == "Python"), None)
    assert python_skill is not None
    assert 0.0 <= python_skill.frequency_percentage <= 100.0
    assert python_skill.importance_tier == "critical"


def test_service_compare_locations():
    service = JobMarketIntelligenceService()
    locations = service.compare_locations("Machine Learning Engineer")

    assert len(locations) >= 3
    sf = next((l for l in locations if "San Francisco" in l.location), None)
    assert sf is not None
    assert sf.relative_job_volume_index > 80.0
    assert sf.remote_eligible_percentage > 0.0
    assert sf.provenance.geographic_scope == sf.location


def test_service_analyze_market_fit():
    service = JobMarketIntelligenceService()
    
    # Profile with high overlap
    res_high = service.analyze_market_fit(
        target_role="Senior Backend Engineer",
        user_skills=["Python", "SQL", "PostgreSQL", "Docker", "AWS", "Kubernetes", "Redis", "Microservices", "Go"],
        user_experience_years=5.5
    )
    assert res_high.market_match_score >= 80.0
    assert "Python" in res_high.matching_skills
    assert "PostgreSQL" in res_high.matching_skills
    assert "Exceeds typical market median experience" in res_high.experience_fit_verdict

    # Profile with gaps
    res_low = service.analyze_market_fit(
        target_role="Senior Backend Engineer",
        user_skills=["HTML", "CSS"],
        user_experience_years=1.0
    )
    assert res_low.market_match_score < 40.0
    assert len(res_low.missing_critical_skills) > 0
    assert "Below typical market experience threshold" in res_low.experience_fit_verdict
    assert len(res_low.actionable_recommendations) > 0


@pytest.mark.asyncio
async def test_market_intelligence_endpoints(auth_headers: dict):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Role trends
        resp = await client.get("/api/v1/market-intelligence/role-trends?role=Machine+Learning+Engineer", headers=auth_headers)
        assert resp.status_code == 200
        data = resp.json()["data"]
        assert data["demand_index"] > 80.0
        assert data["provenance"]["sample_size"] > 5000

        # 2. Location comparison
        resp_loc = await client.get("/api/v1/market-intelligence/location-comparison?role=Machine+Learning+Engineer", headers=auth_headers)
        assert resp_loc.status_code == 200
        locs = resp_loc.json()["data"]
        assert len(locs) >= 3

        # 3. Gap analysis
        gap_payload = {
            "target_role": "Machine Learning Engineer",
            "user_skills": ["Python", "PyTorch", "SQL"],
            "user_experience_years": 3.5
        }
        resp_gap = await client.post("/api/v1/market-intelligence/gap-analysis", json=gap_payload, headers=auth_headers)
        assert resp_gap.status_code == 200
        gap_data = resp_gap.json()["data"]
        assert gap_data["market_match_score"] > 0
        assert "Python" in gap_data["matching_skills"]
        assert gap_data["provenance"]["source_name"] is not None
