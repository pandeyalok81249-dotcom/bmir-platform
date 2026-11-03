import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.services.evidence_graph import EvidenceGraphService
from app.ai.evaluation.dataset import BENCHMARK_RESUMES


def test_evidence_graph_service_construction():
    service = EvidenceGraphService()
    sample = BENCHMARK_RESUMES[0]  # Alex Chen (Senior Backend)

    graph = service.build_graph(
        resume_id="res_test_001",
        resume_text=sample.resume_text,
        target_role=sample.target_role,
        job_requirements=["Go", "PostgreSQL", "Apache Kafka", "Kubernetes", "Rust"]
    )

    assert graph.resume_id == "res_test_001"
    assert graph.target_role == sample.target_role
    assert len(graph.nodes) > 10
    assert len(graph.edges) > 5

    # Check node types
    node_types = {n.node_type for n in graph.nodes}
    assert "skill" in node_types
    assert "experience_bullet" in node_types
    assert "job_requirement" in node_types

    # Check edge strengths
    strengths = {e.strength for e in graph.edges}
    assert "strong_evidence" in strengths

    # Verify summary
    summary = graph.summary
    assert summary.total_skills > 0
    assert summary.strong_evidence_count > 0
    assert summary.overall_evidence_score > 50.0
    assert len(summary.critical_findings) > 0


@pytest.mark.asyncio
async def test_evidence_graph_endpoint(client: AsyncClient, auth_headers: dict):
    # 1. Upload a resume
    sample = BENCHMARK_RESUMES[0]
    files = {
        "file": ("alex_backend.txt", sample.resume_text.encode("utf-8"), "text/plain")
    }
    data = {"title": "Evidence Graph Test Resume"}

    create_resp = await client.post(
        "/api/v1/resumes/upload",
        files=files,
        data=data,
        headers=auth_headers
    )
    assert create_resp.status_code == 200
    resume_id = create_resp.json()["data"]["id"]

    # 2. Get evidence graph
    graph_resp = await client.get(f"/api/v1/resumes/{resume_id}/evidence-graph", headers=auth_headers)
    assert graph_resp.status_code == 200
    graph_data = graph_resp.json()["data"]
    assert graph_data["resume_id"] == resume_id
    assert len(graph_data["nodes"]) > 0
    assert graph_data["summary"]["total_skills"] > 0
    assert "Evidence categorization reflects automated parsing" in graph_data["disclaimer"]
