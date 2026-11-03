from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from pydantic import BaseModel
from app.schemas.analysis import ResumeAnalysisResult
from app.schemas.interview import InterviewAnswerEvaluation


class AIProviderResponse(BaseModel):
    provider: str
    model: str
    content: Any
    input_tokens: int = 0
    output_tokens: int = 0
    latency_ms: int = 0
    estimated_cost_usd: float = 0.0


class BaseAIProvider(ABC):
    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @abstractmethod
    async def analyze_resume(
        self,
        resume_text: str,
        target_role: Optional[str] = None,
        career_stage: Optional[str] = None,
    ) -> AIProviderResponse:
        pass

    @abstractmethod
    async def extract_job_requirements(
        self, job_text: str
    ) -> AIProviderResponse:
        pass

    @abstractmethod
    async def improve_bullet(
        self,
        bullet_text: str,
        target_role: Optional[str] = None,
    ) -> AIProviderResponse:
        pass

    @abstractmethod
    async def evaluate_interview_answer(
        self,
        question: str,
        answer: str,
        role: str,
    ) -> AIProviderResponse:
        pass

