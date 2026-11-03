import asyncio
import pytest
from httpx import AsyncClient
from tests.test_resumes import SAMPLE_RESUME_TEXT


@pytest.mark.asyncio
async def test_background_job_lifecycle(client: AsyncClient, auth_headers: dict):
    # 1. Upload resume (enqueues background analysis)
    files = {"file": ("test_resume.txt", SAMPLE_RESUME_TEXT.encode("utf-8"), "text/plain")}
    up_resp = await client.post("/api/v1/resumes/upload", headers=auth_headers, files=files)
    assert up_resp.status_code == 200
    resume_id = up_resp.json()["data"]["id"]

    # 2. Get list of analyses for this resume
    list_resp = await client.get(f"/api/v1/analyses/resume/{resume_id}", headers=auth_headers)
    assert list_resp.status_code == 200
    analyses = list_resp.json()["data"]
    assert len(analyses) >= 1
    analysis_id = analyses[0]["id"]

    # Allow the async worker task a brief cycle to process
    await asyncio.sleep(0.5)

    # 3. Poll real job status
    status_resp = await client.get(f"/api/v1/analyses/{analysis_id}/status", headers=auth_headers)
    assert status_resp.status_code == 200
    status_data = status_resp.json()["data"]
    assert status_data["analysis_id"] == analysis_id
    assert status_data["status"] in ["queued", "processing", "completed"]
    assert "stage_description" in status_data

    # 4. Trigger Retry
    retry_resp = await client.post(f"/api/v1/analyses/{analysis_id}/retry", headers=auth_headers)
    assert retry_resp.status_code == 200
    assert retry_resp.json()["data"]["status"] == "queued"

    # 5. Cancel Job
    cancel_resp = await client.post(f"/api/v1/analyses/{analysis_id}/cancel", headers=auth_headers)
    assert cancel_resp.status_code == 200

