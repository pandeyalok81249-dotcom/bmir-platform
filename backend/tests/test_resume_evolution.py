import hashlib
import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.core.database import async_session_maker
from app.models.resume import ResumeVersion
from tests.test_resumes import SAMPLE_RESUME_TEXT


@pytest.mark.asyncio
async def test_resume_evolution_diff_and_restore(client: AsyncClient, auth_headers: dict):
    # 1. Upload baseline resume (creates version 1)
    files = {"file": ("alex_evolution.txt", SAMPLE_RESUME_TEXT.encode("utf-8"), "text/plain")}
    up_resp = await client.post("/api/v1/resumes/upload", headers=auth_headers, files=files)
    assert up_resp.status_code == 200
    resume_data = up_resp.json()["data"]
    resume_id = resume_data["id"]
    v1_id = resume_data["versions"][0]["id"]

    # 2. Add an improved Version 2 with upgraded STAR metrics and a new section
    async with async_session_maker() as session:
        v2_content = {
            "summary": "Senior Software Engineer with 6+ years building scalable backend microservices.",
            "experience": (
                "Senior Backend Engineer | CloudScale Inc. | 2022 - Present\n"
                "- Architected high-throughput REST API using FastAPI and PostgreSQL handling 50,000 requests per minute.\n"
                "- Engineered automated CI/CD pipelines reducing deployment latencies by 45%.\n"
            ),
            "skills": "Python, FastAPI, Docker, PostgreSQL, Kubernetes, Redis, Flutter, Dart, GraphQL, AWS.",
            "projects": "OpenSource Microservices: Architected distributed event stream handling 100k events/sec.",
            "education": "Bachelor of Science in Computer Science | UC Berkeley",
        }
        v2_hash = hashlib.sha256(str(v2_content).encode("utf-8")).hexdigest()
        v2 = ResumeVersion(
            resume_id=resume_id,
            version_number=2,
            resume_content=v2_content,
            content_hash=v2_hash,
        )
        session.add(v2)
        await session.commit()
        await session.refresh(v2)
        v2_id = v2.id

    # 3. List Versions
    versions_resp = await client.get(f"/api/v1/resumes/{resume_id}/versions", headers=auth_headers)
    assert versions_resp.status_code == 200
    versions_list = versions_resp.json()["data"]
    assert len(versions_list) == 2
    assert versions_list[0]["version_number"] == 2
    assert versions_list[1]["version_number"] == 1

    # 4. Compute Evolution Diff
    diff_resp = await client.get(
        f"/api/v1/resumes/{resume_id}/evolution/diff?base_version_id={v1_id}&compare_version_id={v2_id}",
        headers=auth_headers,
    )
    assert diff_resp.status_code == 200
    diff_data = diff_resp.json()["data"]

    assert diff_data["base_version_number"] == 1
    assert diff_data["compare_version_number"] == 2
    assert len(diff_data["content_diffs"]) >= 3
    assert len(diff_data["improved_achievements"]) >= 1
    assert "improved_bullet" in diff_data["improved_achievements"][0]
    assert diff_data["score_comparison"]["methodologies_compatible"] is True

    # 5. Restore Version 1 as new Version 3
    restore_resp = await client.post(
        f"/api/v1/resumes/{resume_id}/versions/{v1_id}/restore",
        headers=auth_headers,
    )
    assert restore_resp.status_code == 200
    restore_data = restore_resp.json()["data"]
    assert restore_data["restored_from_version_number"] == 1
    assert restore_data["new_version_number"] == 3

    # 6. Verify 3 total versions now exist
    v_check = await client.get(f"/api/v1/resumes/{resume_id}/versions", headers=auth_headers)
    assert len(v_check.json()["data"]) == 3

