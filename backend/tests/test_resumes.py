import pytest
from httpx import AsyncClient

SAMPLE_RESUME_TEXT = """
Alex Candidate
alex@example.com | (555) 019-2834 | San Francisco, CA

Professional Summary
Senior Software Engineer with 6+ years of experience building scalable backend microservices and mobile applications.

Technical Skills
Python, Dart, Flutter, FastAPI, PostgreSQL, Docker, Redis, Kubernetes, Git, CI/CD, REST API.

Work Experience
Senior Backend Engineer | CloudScale Inc. | 2022 - Present
- Architected high-throughput REST API using FastAPI and PostgreSQL handling 20,000 requests per minute.
- Containerized microservices using Docker and orchestrated automated deployments with Kubernetes.
- Migrated relational data layers, improving database query latencies across primary transaction paths.

Software Engineer | MobileFlow Labs | 2019 - 2022
- Developed cross-platform client using Flutter and Dart with clean architecture and reactive state management.
- Integrated third-party OAuth2 authentication and offline sync mechanisms with local SQLite persistence.

Education
Bachelor of Science in Computer Science | University of California, Berkeley | 2015 - 2019
"""


@pytest.mark.asyncio
async def test_resume_upload_and_analysis(client: AsyncClient, auth_headers: dict):
    # 1. Upload Resume as TXT
    files = {
        "file": ("alex_resume.txt", SAMPLE_RESUME_TEXT.encode("utf-8"), "text/plain")
    }
    data = {"title": "Alex Candidate Resume v1"}

    upload_resp = await client.post(
        "/api/v1/resumes/upload", headers=auth_headers, files=files, data=data
    )
    assert upload_resp.status_code == 200
    res_data = upload_resp.json()
    assert res_data["success"] is True
    resume = res_data["data"]
    resume_id = resume["id"]
    assert resume["title"] == "Alex Candidate Resume v1"
    assert resume["processing_status"] == "parsed"

    # Allow async worker task to complete audit
    import asyncio
    detail_data = None
    for _ in range(25):
        detail_resp = await client.get(f"/api/v1/resumes/{resume_id}", headers=auth_headers)
        assert detail_resp.status_code == 200
        detail_data = detail_resp.json()["data"]
        if detail_data.get("latest_score") is not None:
            break
        await asyncio.sleep(0.05)

    # 2. Verify Resume Details
    assert detail_data is not None
    assert len(detail_data["versions"]) >= 1
    assert detail_data["latest_score"] is not None
    assert detail_data["latest_score"] > 50

    # 3. List Resumes
    list_resp = await client.get("/api/v1/resumes", headers=auth_headers)
    assert list_resp.status_code == 200
    assert len(list_resp.json()["data"]) >= 1

    # 4. Trigger Re-analysis with explicit target role
    reanalysis_resp = await client.post(
        f"/api/v1/resumes/{resume_id}/analyze?target_role=Senior+Staff+Engineer",
        headers=auth_headers,
    )
    assert reanalysis_resp.status_code == 200
    analysis_job = reanalysis_resp.json()["data"]
    assert analysis_job["status"] == "queued"
    analysis_id = analysis_job["analysis_id"]

    # Allow worker task to process
    await asyncio.sleep(0.5)
    report_resp = await client.get(f"/api/v1/analyses/{analysis_id}", headers=auth_headers)
    assert report_resp.status_code == 200
    report_data = report_resp.json()["data"]
    assert report_data["status"] == "completed"
    assert report_data["result_json"] is not None
    assert len(report_data["result_json"]["skills_extracted"]) > 5

    # 5. Delete Resume
    del_resp = await client.delete(f"/api/v1/resumes/{resume_id}", headers=auth_headers)
    assert del_resp.status_code == 200

