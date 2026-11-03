import pytest
from httpx import AsyncClient
from tests.test_resumes import SAMPLE_RESUME_TEXT


@pytest.mark.asyncio
async def test_career_intelligence_engine(client: AsyncClient, auth_headers: dict):
    # 1. Upload baseline resume
    files = {"file": ("alex_career.txt", SAMPLE_RESUME_TEXT.encode("utf-8"), "text/plain")}
    up_resp = await client.post("/api/v1/resumes/upload", headers=auth_headers, files=files)
    assert up_resp.status_code == 200

    # 2. Query Career Intelligence Report
    report_resp = await client.get("/api/v1/career-intelligence/report", headers=auth_headers)
    assert report_resp.status_code == 200
    report = report_resp.json()["data"]

    # Verify all 10 Analytical Dimensions are present
    assert "progression" in report
    assert "skill_gaps" in report
    assert "role_suitability" in report
    assert "transition_analysis" in report
    assert "experience_relevance" in report
    assert "project_evidence" in report
    assert "readiness" in report
    assert "learning_priorities" in report
    assert "career_suggestions" in report
    assert "goal_tracking" in report

    # 1. Progression
    prog = report["progression"]
    assert len(prog["title_trajectory"]) >= 1
    assert prog["years_of_experience"] > 0
    assert len(prog["findings"]) >= 1
    assert prog["findings"][0]["inference_type"] in ["verified_fact", "ai_inference"]
    assert prog["findings"][0]["reasoning"] != ""

    # 2. Skill gaps
    gaps = report["skill_gaps"]
    assert len(gaps["verified_skills"]) > 0
    assert any(s in gaps["verified_skills"] for s in ["Python", "Fastapi", "Docker", "Flutter"])

    # 3. Role Suitability
    suit = report["role_suitability"]
    assert 0 <= suit["suitability_score"] <= 100
    assert len(suit["strengths"]) > 0

    # 4. Career Transition
    trans = report["transition_analysis"]
    assert 0 <= trans["transition_friction_score"] <= 100
    assert len(trans["transferable_skills"]) > 0

    # 5. Experience Relevance
    rel = report["experience_relevance"]
    assert 0 <= rel["overall_relevance_score"] <= 100
    assert rel["signal_to_noise_ratio"] > 0

    # 6. Readiness
    readiness = report["readiness"]
    assert 0 <= readiness["market_readiness_score"] <= 100

    # 7. Learning Priorities & Suggestions
    assert len(report["learning_priorities"]) >= 1
    assert len(report["career_suggestions"]) >= 1
    assert report["career_suggestions"][0]["alignment_score"] > 70
    assert len(report["career_suggestions"][0]["key_matching_evidence"]) > 0

    # 8. Trigger explicit target role analysis
    target_resp = await client.post(
        "/api/v1/career-intelligence/analyze?target_role=Principal+Distributed+Systems+Architect",
        headers=auth_headers,
    )
    assert target_resp.status_code == 200
    target_report = target_resp.json()["data"]
    assert target_report["role_suitability"]["target_role"] == "Principal Distributed Systems Architect"

