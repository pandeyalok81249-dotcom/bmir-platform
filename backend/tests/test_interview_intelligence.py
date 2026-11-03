import pytest
from httpx import AsyncClient

from app.schemas.interview import (
    FollowUpQuestionRequest,
    InterviewAnswerEvaluateRequest,
    InterviewGenerateRequest,
)
from app.services.interview_intelligence import InterviewIntelligenceEngine


@pytest.fixture
def interview_engine():
    return InterviewIntelligenceEngine()


def test_adaptive_questions_generation(interview_engine: InterviewIntelligenceEngine):
    resume_text = """
    Senior Software Engineer with 6 years experience building scalable backend services.
    Proficient in Python, FastAPI, Docker, Kubernetes, PostgreSQL, and Redis.
    Architected asynchronous event-driven microservices handling 25,000 req/min.
    """
    questions = interview_engine.generate_adaptive_questions(
        target_role="Staff Backend Engineer",
        resume_text=resume_text,
        focus_areas=["Distributed Systems", "Kubernetes"],
        count=5,
    )

    assert len(questions) == 5
    categories = {q.category for q in questions}
    assert "technical" in categories
    assert "behavioral" in categories
    assert "experience_deep_dive" in categories
    assert "situational" in categories

    for q in questions:
        assert q.id
        assert len(q.question) > 20
        assert len(q.evaluation_criteria) >= 2


def test_star_evaluation_strong_answer(interview_engine: InterviewIntelligenceEngine):
    strong_answer = """
    At my previous company, our payment processing microservice experienced high latency during Black Friday surges.
    My responsibility was to identify the operational bottleneck and re-architect the payment gateway integration.
    I investigated the execution traces, identified unindexed database locks, designed an asynchronous queue with Redis and Celery,
    and implemented optimistic locking with circuit breakers.
    As a result, we reduced p99 latency by 68% from 1800ms to 420ms and eliminated payment timeouts, delivering $2.4M in processed orders with zero dropped transactions.
    """
    eval_result = interview_engine.evaluate_star_answer(
        question="Tell me about a challenging technical bottleneck you resolved.",
        answer=strong_answer,
        category="technical",
        target_role="Senior Backend Engineer",
    )

    assert eval_result.star_method_adherence == "Strong"
    assert eval_result.overall_score >= 80.0
    assert eval_result.star_breakdown is not None
    assert eval_result.star_breakdown.result_score >= 8.0
    assert eval_result.star_breakdown.action_score >= 8.0
    assert len(eval_result.strengths) >= 2
    assert "Situation" in eval_result.improved_answer_sample


def test_star_evaluation_weak_answer(interview_engine: InterviewIntelligenceEngine):
    weak_answer = "We had some bugs in the code so we talked about it in a meeting and fixed the errors."
    eval_result = interview_engine.evaluate_star_answer(
        question="Describe a time you faced a production bug.",
        answer=weak_answer,
        category="behavioral",
        target_role="Backend Engineer",
    )

    assert eval_result.star_method_adherence in ["Moderate", "Weak"]
    assert eval_result.overall_score < 75.0
    assert eval_result.star_breakdown.result_score < 6.0
    assert len(eval_result.improvement_areas) >= 1
    assert eval_result.follow_up_recommendation is not None


def test_follow_up_question_generation(interview_engine: InterviewIntelligenceEngine):
    follow_up = interview_engine.generate_follow_up_question(
        question="Describe an architectural decision you made.",
        answer="I chose PostgreSQL instead of MongoDB.",
        weakest_area="result",
    )
    assert follow_up.follow_up_id
    assert "metric" in follow_up.question.lower() or "impact" in follow_up.question.lower()
    assert follow_up.target_star_component == "result"


def test_session_summary_calculation(interview_engine: InterviewIntelligenceEngine):
    answers = [
        {
            "question_id": "q1",
            "category": "technical",
            "evaluation": {
                "overall_score": 90.0,
                "star_breakdown": {"situation_score": 9.0, "task_score": 8.5, "action_score": 9.5, "result_score": 9.0},
                "strengths": ["Excellent technical clarity"],
                "improvement_areas": ["None"],
            },
        },
        {
            "question_id": "q2",
            "category": "behavioral",
            "evaluation": {
                "overall_score": 80.0,
                "star_breakdown": {"situation_score": 8.0, "task_score": 8.0, "action_score": 8.0, "result_score": 8.0},
                "strengths": ["Solid STAR alignment"],
                "improvement_areas": ["Quantify impact further"],
            },
        },
    ]
    summary = interview_engine.summarize_session(
        session_id="session-123",
        target_role="Senior Platform Engineer",
        answers=answers,
    )
    assert summary.session_id == "session-123"
    assert summary.total_questions_answered == 2
    assert summary.average_overall_score == 85.0
    assert "Ready for Senior & Staff Interview Loops" in summary.readiness_verdict
    assert summary.category_scores["technical"] == 90.0
    assert summary.category_scores["behavioral"] == 80.0


@pytest.mark.asyncio
async def test_interview_api_full_flow(client: AsyncClient, auth_headers: dict):
    # 1. Generate interview session
    gen_payload = {
        "target_role": "Lead Cloud Architect",
        "focus_areas": ["AWS", "Microservices", "Security"],
        "question_count": 4,
    }
    gen_resp = await client.post("/api/v1/interviews/generate", json=gen_payload, headers=auth_headers)
    assert gen_resp.status_code == 200
    gen_data = gen_resp.json()["data"]
    session_id = gen_data["id"]
    questions = gen_data["session_data"]["questions"]
    assert len(questions) == 4
    first_q = questions[0]

    # 2. Evaluate answer
    eval_payload = {
        "question_id": first_q["id"],
        "question_text": first_q["question"],
        "user_answer": (
            "When designing our multi-region payment gateway, I evaluated active-active replication tradeoffs. "
            "My responsibility was ensuring zero data loss and sub-200ms latency. "
            "I implemented DynamoDB global tables with token bucket rate limiting and AWS KMS envelope encryption. "
            "As a result, we achieved 99.999% availability with zero downtime across 4 failover drills."
        ),
    }
    eval_resp = await client.post(f"/api/v1/interviews/{session_id}/evaluate", json=eval_payload, headers=auth_headers)
    assert eval_resp.status_code == 200
    eval_data = eval_resp.json()["data"]
    assert eval_data["overall_score"] >= 75.0
    assert eval_data["star_method_adherence"] in ["Strong", "Moderate"]
    assert eval_data["star_breakdown"] is not None

    # 3. Generate follow-up
    fu_payload = {
        "question_id": first_q["id"],
        "previous_question": first_q["question"],
        "user_answer": eval_payload["user_answer"],
        "weakest_area": "action",
    }
    fu_resp = await client.post(f"/api/v1/interviews/{session_id}/follow-up", json=fu_payload, headers=auth_headers)
    assert fu_resp.status_code == 200
    fu_data = fu_resp.json()["data"]
    assert fu_data["parent_question_id"] == first_q["id"]
    assert len(fu_data["question"]) > 10

    # 4. Get summary
    sum_resp = await client.get(f"/api/v1/interviews/{session_id}/summary", headers=auth_headers)
    assert sum_resp.status_code == 200
    sum_data = sum_resp.json()["data"]
    assert sum_data["session_id"] == session_id
    assert sum_data["total_questions_answered"] == 1
    assert sum_data["average_overall_score"] >= 75.0

    # 5. Get history
    hist_resp = await client.get("/api/v1/interviews/history", headers=auth_headers)
    assert hist_resp.status_code == 200
    hist_data = hist_resp.json()["data"]
    assert len(hist_data) >= 1
    assert any(s["id"] == session_id for s in hist_data)
