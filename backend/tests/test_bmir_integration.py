import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    res = client.get("/health")
    assert res.status_code == 200
    assert "BMIR" in res.json().get("service", "")


def test_public_innovations_endpoint():
    res = client.get("/api/v1/bmir/innovations")
    assert res.status_code == 200
    data = res.json()
    assert len(data) == 27
    assert data[0]["title"] == "KRISHI-BODH ONE"
    assert data[0]["project_code"] == "BMIR-AGR-001"


def test_innovations_filtering_and_search():
    # Filter by domain
    res = client.get("/api/v1/bmir/innovations?domain=Agriculture")
    assert res.status_code == 200
    agri_items = res.json()
    assert len(agri_items) > 0
    assert all(item["domain"] == "Agriculture" for item in agri_items)

    # Search keyword
    res = client.get("/api/v1/bmir/innovations?q=Hydrogen")
    assert res.status_code == 200
    assert len(res.json()) >= 2


def test_patents_records():
    res = client.get("/api/v1/bmir/patents")
    assert res.status_code == 200
    patents = res.json()
    assert len(patents) >= 10
    # Check published gazette records
    published = [p for p in patents if p["patent_type"] == "Published"]
    assert len(published) == 3
    app_numbers = [p["application_number"] for p in published]
    assert "202631048563" in app_numbers
    assert "202631058488" in app_numbers
    assert "202631065492" in app_numbers


def test_research_projects_endpoint():
    res = client.get("/api/v1/bmir/projects")
    assert res.status_code == 200
    projects = res.json()
    assert len(projects) == 4
    codes = [p["project_code"] for p in projects]
    assert "BMIR-PRJ-01" in codes
    assert "BMIR-PRJ-02" in codes


def test_auth_login_founder_and_admin():
    # Founder login
    res = client.post(
        "/api/v1/bmir/auth/login",
        json={"email": "binod.pandey@bmirresearch.in", "password": "Bmir@2026!Enterprise"},
    )
    assert res.status_code == 200
    data = res.json()
    assert data["user"]["role"] == "founder"
    assert "access_token" in data
    token = data["access_token"]

    # Check /auth/me with token
    res = client.get("/api/v1/bmir/auth/me", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    assert res.json()["full_name"] == "Binod Pandey"

    # Check dashboard stats
    res = client.get("/api/v1/bmir/dashboard/stats", headers={"Authorization": f"Bearer {token}"})
    assert res.status_code == 200
    stats = res.json()
    assert stats["metrics"]["total_innovations"] == 27
    assert stats["metrics"]["published_patents"] == 3


def test_collaboration_proposal_submission_and_admin_review():
    # Public submission
    proposal = {
        "full_name": "Prof. S. R. Raman",
        "email": "sr.raman@bihar-agri-univ.ac.in",
        "phone": "+91 94312 00000",
        "organization": "Bihar Agricultural University",
        "organization_type": "University",
        "pathway": "Research Collaboration",
        "project_interest": "Hybrid Maize Seed Production",
        "message": "We propose a collaborative multi-location field evaluation of high-protein maize yield across our Bhagalpur test plots.",
    }
    res = client.post("/api/v1/bmir/collaboration/enquiry", json=proposal)
    assert res.status_code == 200
    enq_number = res.json().get("enquiry_number")
    assert "BMIR-ENQ-" in enq_number

    # Admin review
    admin_login = client.post(
        "/api/v1/bmir/auth/login",
        json={"email": "admin@bmirresearch.in", "password": "Bmir@2026!Enterprise"},
    )
    admin_token = admin_login.json()["access_token"]

    res = client.get(
        "/api/v1/bmir/collaboration/enquiries",
        headers={"Authorization": f"Bearer {admin_token}"},
    )
    assert res.status_code == 200
    enquiries = res.json()
    matching = [e for e in enquiries if e["enquiry_number"] == enq_number]
    assert len(matching) == 1


def test_ai_reasoning_and_multi_model():
    founder_login = client.post(
        "/api/v1/bmir/auth/login",
        json={"email": "binod.pandey@bmirresearch.in", "password": "Bmir@2026!Enterprise"},
    )
    token = founder_login.json()["access_token"]

    # AI Chat
    res = client.post(
        "/api/v1/bmir/ai/chat",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "prompt": "Evaluate thermal insulation and air moisture extraction kinetics in maize drying.",
            "module": "assistant",
        },
    )
    assert res.status_code == 200
    assert "conversation_id" in res.json()
    assert len(res.json()["content"]) > 100

    # Multi-Model Comparison
    res = client.post(
        "/api/v1/bmir/ai/multi-model-compare",
        headers={"Authorization": f"Bearer {token}"},
        json={"query": "Burst pressure limits of 200 bar composite hydrogen container", "domain": "Renewable Energy"},
    )
    assert res.status_code == 200
    data = res.json()
    assert "individual_responses" in data
    assert "key_agreements" in data
    assert "key_disagreements" in data
    assert "missing_evidence" in data

    # 8-Step Innovation Discovery
    res = client.post(
        "/api/v1/bmir/ai/innovation-discovery",
        headers={"Authorization": f"Bearer {token}"},
        json={"problem_statement": "Post-harvest grain mold in humid monsoons", "target_sector": "Agriculture & Smart Farming"},
    )
    assert res.status_code == 200
    disc = res.json()
    assert "step_1_problem_analysis" in disc
    assert "step_6_innovation_directions" in disc
    assert len(disc["step_6_innovation_directions"]) >= 2

