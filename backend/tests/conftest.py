import os
import asyncio
from typing import AsyncGenerator
import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.core import database as core_db
from app.services import resume_analyzer as service_analyzer
from app.ai.base import AIProviderResponse, BaseAIProvider
from app.ai.factory import AIFactory
from app.core.database import Base, get_db
from app.models.user import User
from app.models.resume import Resume, ResumeVersion
from app.models.analysis import ResumeAnalysis
from app.models.job import JobMatch
from app.models.interview import InterviewSession
from app.models.application import Application
from app.models.profile import UserProfile
from app.models.roadmap import CareerRoadmap
from app.models.collaboration import (
    CollaborationWorkspace,
    WorkspaceMember,
    WorkspaceResume,
    WorkspaceInvitation,
    ResumeComment,
    ResumeSuggestion,
    CollaborationEvent,
    ResumeRevision,
)
from app.models.subscription import UserSubscription, UserUsageQuota
from app.main import app
from app.schemas.analysis import ResumeAnalysisResult
from tests.test_ai_providers import MOCK_ANALYSIS_JSON

TEST_DB_FILE = "./test_suite.db"
TEST_DATABASE_URL = f"sqlite+aiosqlite:///{TEST_DB_FILE}"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    future=True,
)
test_async_session = async_sessionmaker(
    test_engine, class_=AsyncSession, expire_on_commit=False
)

core_db.async_session_maker = test_async_session
service_analyzer.async_session_maker = test_async_session


class MockDeterministicAIProvider(BaseAIProvider):
    @property
    def provider_name(self) -> str:
        return "mocked-test-ai"

    async def analyze_resume(
        self,
        resume_text: str,
        target_role: str = None,
        career_stage: str = None,
    ) -> AIProviderResponse:
        return AIProviderResponse(
            provider="mocked-test-ai",
            model="mocked-gpt4",
            content=ResumeAnalysisResult.model_validate(MOCK_ANALYSIS_JSON),
            input_tokens=200,
            output_tokens=400,
            latency_ms=10,
            estimated_cost_usd=0.001,
        )

    async def extract_job_requirements(self, job_text: str) -> AIProviderResponse:
        return AIProviderResponse(
            provider="mocked-test-ai",
            model="mocked-gpt4",
            content={"role_title": "Software Engineer", "required_skills": ["Python", "FastAPI"], "years_required": 3},
        )

    async def improve_bullet(
        self, bullet_text: str, target_role: str = None
    ) -> AIProviderResponse:
        return AIProviderResponse(
            provider="mocked-test-ai",
            model="mocked-gpt4",
            content={
                "original": bullet_text,
                "improved": "Architected high-throughput REST API using FastAPI handling 20,000 req/min.",
                "action_verb_used": "Architected",
                "rationale": "Transformed passive phrasing into quantified engineering action.",
                "missing_metric_prompt": None,
            },
        )

    async def evaluate_interview_answer(
        self, question: str, answer: str, target_role: str = None
    ) -> AIProviderResponse:
        return AIProviderResponse(
            provider="mocked-test-ai",
            model="mocked-gpt4",
            content={"score": 85, "strengths": ["Clear structure"], "improvements": []},
        )


@pytest.fixture(autouse=True)
def mock_ai_factory_for_tests(monkeypatch):
    """
    Ensures background jobs in automated tests use deterministic mock AI
    responses without making outbound external requests or hitting rate limits.
    """
    mock_provider = MockDeterministicAIProvider()
    monkeypatch.setattr(AIFactory, "get_provider", lambda preferred=None: mock_provider)


@pytest_asyncio.fixture(scope="function", autouse=True)
async def db_schema_lifecycle():
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Seed BMIR baseline in test suite
    from app.db_init_and_seed import init_and_seed
    import app.core.database as cdb
    old_engine = cdb.engine
    old_maker = cdb.async_session_maker
    cdb.engine = test_engine
    cdb.async_session_maker = test_async_session
    try:
        await init_and_seed()
    finally:
        cdb.engine = old_engine
        cdb.async_session_maker = old_maker

    yield

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client() -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db():
        async with test_async_session() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def auth_headers(client: AsyncClient) -> dict:
    # Register test user
    payload = {
        "email": "candidate@example.com",
        "password": "SecurePassword123!",
        "full_name": "Alex Candidate",
    }
    resp = await client.post("/api/v1/auth/register", json=payload)
    assert resp.status_code == 200
    token = resp.json()["data"]["tokens"]["access_token"]
    return {"Authorization": f"Bearer {token}"}
