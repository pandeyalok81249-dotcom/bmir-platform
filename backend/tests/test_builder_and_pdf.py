import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_bullet_improvement_and_pdf_export(client: AsyncClient, auth_headers: dict):
    # 1. Improve Bullet
    bullet_req = {
        "bullet_text": "Worked on a python backend service for users.",
        "target_role": "Senior Backend Engineer",
    }
    improve_resp = await client.post(
        "/api/v1/resume-builder/improve-bullet", headers=auth_headers, json=bullet_req
    )
    assert improve_resp.status_code == 200
    improved_data = improve_resp.json()["data"]
    assert "improved" in improved_data
    assert "action_verb_used" in improved_data

    # 2. Export Resume PDF
    pdf_req = {
        "resume_content": {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "summary": "Experienced Software Engineer with a passion for high-reliability systems.",
            "skills": ["Python", "FastAPI", "PostgreSQL", "Docker", "Flutter"],
            "experience": [
                {
                    "title": "Senior Engineer",
                    "company": "Tech Corp",
                    "dates": "2021 - Present",
                    "bullets": [
                        "Architected low-latency microservices with FastAPI.",
                        "Optimized relational database queries reducing latency.",
                    ],
                }
            ],
            "education": [
                {"degree": "B.S. in Computer Science", "institution": "Stanford University"}
            ],
        },
        "template_name": "professional",
    }
    pdf_resp = await client.post(
        "/api/v1/resume-builder/export-pdf", headers=auth_headers, json=pdf_req
    )
    assert pdf_resp.status_code == 200
    assert pdf_resp.headers["content-type"] == "application/pdf"
    assert len(pdf_resp.content) > 1000  # Valid PDF binary generated

