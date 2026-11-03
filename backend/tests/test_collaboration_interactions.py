import pytest
from httpx import AsyncClient
from tests.test_resumes import SAMPLE_RESUME_TEXT


@pytest.mark.asyncio
async def test_comments_suggestions_and_concurrency(client: AsyncClient, auth_headers: dict):
    # 1. Upload Resume
    files = {"file": ("collab_resume.txt", SAMPLE_RESUME_TEXT.encode("utf-8"), "text/plain")}
    up_resp = await client.post("/api/v1/resumes/upload", headers=auth_headers, files=files)
    assert up_resp.status_code == 200
    resume_id = up_resp.json()["data"]["id"]

    # 2. Add Comment
    comment_payload = {
        "section": "experience",
        "selected_text": "Architected high-throughput REST API using FastAPI",
        "comment_text": "Consider adding the specific query latency or memory reduction metric here.",
    }
    c_resp = await client.post(
        f"/api/v1/collaboration/resumes/{resume_id}/comments",
        headers=auth_headers,
        json=comment_payload,
    )
    assert c_resp.status_code == 200
    comment_id = c_resp.json()["data"]["id"]
    assert c_resp.json()["data"]["status"] == "active"

    # 3. List and Resolve Comment
    c_list = await client.get(
        f"/api/v1/collaboration/resumes/{resume_id}/comments", headers=auth_headers
    )
    assert c_list.status_code == 200
    assert len(c_list.json()["data"]) >= 1

    resolve_resp = await client.patch(
        f"/api/v1/collaboration/comments/{comment_id}",
        headers=auth_headers,
        json={"status": "resolved"},
    )
    assert resolve_resp.status_code == 200
    assert resolve_resp.json()["data"]["status"] == "resolved"

    # 4. Propose Suggestion
    sug_payload = {
        "section": "experience",
        "original_text": "Worked on a python backend service for users.",
        "suggested_text": "Architected asynchronous REST microservices using FastAPI handling 20,000 req/min.",
        "rationale": "Incorporated quantifiable throughput and strong action verb.",
    }
    sug_resp = await client.post(
        f"/api/v1/collaboration/resumes/{resume_id}/suggestions",
        headers=auth_headers,
        json=sug_payload,
    )
    assert sug_resp.status_code == 200
    suggestion_id = sug_resp.json()["data"]["id"]
    assert sug_resp.json()["data"]["status"] == "pending"

    # 5. Accept Suggestion
    review_resp = await client.post(
        f"/api/v1/collaboration/suggestions/{suggestion_id}/review",
        headers=auth_headers,
        json={"action": "accept"},
    )
    assert review_resp.status_code == 200
    assert review_resp.json()["data"]["status"] == "accepted"

    # 6. Verify Revisions - Accepting suggestion automatically records revision 1
    rev_list = await client.get(
        f"/api/v1/collaboration/resumes/{resume_id}/revisions", headers=auth_headers
    )
    assert rev_list.status_code == 200
    revs = rev_list.json()["data"]
    assert len(revs) >= 1
    head_rev = revs[0]["revision_number"]

    # 7. Optimistic Concurrency Conflict Detection:
    # A collaborator tries to commit revision based on an outdated base revision
    stale_payload = {
        "base_revision_number": 0,  # Outdated base revision
        "patch_data": {"section": "summary", "text": "Stale edit"},
        "description": "Concurrent stale write",
    }
    conflict_resp = await client.post(
        f"/api/v1/collaboration/resumes/{resume_id}/revisions",
        headers=auth_headers,
        json=stale_payload,
    )
    assert conflict_resp.status_code == 409
    assert "Conflict detected" in conflict_resp.json()["error"]["message"]

    # 8. Valid Commit on Top of Current Head Revision
    valid_payload = {
        "base_revision_number": head_rev,
        "patch_data": {"section": "summary", "text": "Up-to-date collaborative rewrite"},
        "description": "Sequential valid revision",
    }
    valid_resp = await client.post(
        f"/api/v1/collaboration/resumes/{resume_id}/revisions",
        headers=auth_headers,
        json=valid_payload,
    )
    assert valid_resp.status_code == 200
    assert valid_resp.json()["data"]["revision_number"] == head_rev + 1
