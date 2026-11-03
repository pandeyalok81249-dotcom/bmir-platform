import pytest
from httpx import AsyncClient
from tests.test_resumes import SAMPLE_RESUME_TEXT


@pytest.mark.asyncio
async def test_job_match_and_analytics(client: AsyncClient, auth_headers: dict):
    # 1. Upload Resume
    files = {"file": ("resume.txt", SAMPLE_RESUME_TEXT.encode("utf-8"), "text/plain")}
    up_resp = await client.post("/api/v1/resumes/upload", headers=auth_headers, files=files)
    assert up_resp.status_code == 200
    version_id = up_resp.json()["data"]["versions"][0]["id"]

    # 2. Create Job Description
    job_payload = {
        "job_title": "Lead Backend & Mobile Architect",
        "company": "TechGlobal Solutions",
        "raw_text": (
            "We are looking for a Senior Architect proficient in Python, FastAPI, Flutter, Docker, "
            "Kubernetes, and Redis. Required: 5+ years building distributed backends. "
            "Preferred: Experience with GraphQL and AWS."
        ),
    }
    job_resp = await client.post(
        "/api/v1/job-matches/descriptions", headers=auth_headers, json=job_payload
    )
    assert job_resp.status_code == 200
    job_id = job_resp.json()["data"]["id"]

    # 3. Perform Resume-to-Job Match
    match_payload = {
        "resume_version_id": version_id,
        "job_description_id": job_id,
    }
    match_resp = await client.post(
        "/api/v1/job-matches/match", headers=auth_headers, json=match_payload
    )
    assert match_resp.status_code == 200
    match_data = match_resp.json()["data"]
    assert match_data["match_score"] > 60
    assert len(match_data["match_result"]["matched_skills"]) > 0

    # 4. Verify Dashboard Analytics has genuine data
    import asyncio
    dash_data = None
    for _ in range(25):
        dash_resp = await client.get("/api/v1/analytics/dashboard", headers=auth_headers)
        assert dash_resp.status_code == 200
        dash_data = dash_resp.json()["data"]
        if dash_data["resume_overview"].get("latest_score") is not None:
            break
        await asyncio.sleep(0.05)

    assert dash_data is not None
    assert dash_data["resume_overview"]["total_resumes"] >= 1
    assert dash_data["resume_overview"]["latest_score"] is not None

    # 5. Verify Skill Gap Analytics
    gap_resp = await client.get("/api/v1/analytics/skill-gaps", headers=auth_headers)
    assert gap_resp.status_code == 200
    gap_data = gap_resp.json()["data"]
    assert gap_data["has_match_data"] is True
    assert len(gap_data["verified_skills"]) > 0

