import pytest
from httpx import AsyncClient
from app.services.trajectory_simulator import CareerTrajectorySimulatorService
from app.ai.evaluation.dataset import BENCHMARK_RESUMES


def test_trajectory_simulator_service():
    service = CareerTrajectorySimulatorService()
    user_skills = ["Go", "Python", "SQL", "PostgreSQL", "Docker", "Kubernetes", "AWS", "Microservices"]
    user_exp = 7.0

    res = service.simulate_trajectories(
        candidate_id="cand_123",
        user_skills=user_skills,
        user_experience_years=user_exp,
        target_roles=["Senior Backend Engineer", "Technical Product Manager", "Junior Frontend Engineer"]
    )

    assert res.candidate_id == "cand_123"
    assert res.current_experience_years == 7.0
    assert len(res.simulations) == 3

    # Backend Engineer should be highest readiness
    backend_sim = next(s for s in res.simulations if "Backend" in s.target_role)
    assert backend_sim.overall_readiness_score >= 80.0
    assert backend_sim.transition_friction == "low"
    assert "immediate bridge" in backend_sim.estimated_ramp_up_time

    # Best path
    assert "Backend" in res.optimal_recommended_path
    assert "heuristic skill overlap" in res.disclaimer


@pytest.mark.asyncio
async def test_simulate_trajectory_endpoint(client: AsyncClient, auth_headers: dict):
    # Upload resume
    sample = BENCHMARK_RESUMES[0]
    files = {
        "file": ("alex_backend.txt", sample.resume_text.encode("utf-8"), "text/plain")
    }
    upload_resp = await client.post(
        "/api/v1/resumes/upload",
        files=files,
        data={"title": "Trajectory Candidate Resume"},
        headers=auth_headers
    )
    assert upload_resp.status_code == 200

    # Simulate trajectory
    payload = {
        "target_roles": ["Senior Backend Engineer", "Product Manager"]
    }
    sim_resp = await client.post("/api/v1/career-intelligence/simulate-trajectory", json=payload, headers=auth_headers)
    assert sim_resp.status_code == 200
    data = sim_resp.json()["data"]
    assert len(data["simulations"]) == 2
    assert data["optimal_recommended_path"] is not None
    assert "heuristic skill overlap" in data["disclaimer"]
