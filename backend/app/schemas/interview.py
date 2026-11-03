from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class InterviewQuestion(BaseModel):
    id: str
    category: str  # technical, behavioral, experience_deep_dive, situational
    question: str
    context_from_resume: Optional[str] = None
    evaluation_criteria: List[str] = []


class InterviewGenerateRequest(BaseModel):
    resume_version_id: Optional[str] = None
    target_role: str = Field(..., min_length=2, max_length=150)
    focus_areas: Optional[List[str]] = None


class InterviewAnswerEvaluateRequest(BaseModel):
    question_id: str
    question_text: str
    user_answer: str = Field(..., min_length=10)


class InterviewAnswerEvaluation(BaseModel):
    question_id: str
    clarity_score: float  # 0 to 10
    star_method_adherence: str  # Strong, Moderate, Weak
    strengths: List[str] = []
    improvement_areas: List[str] = []
    improved_answer_sample: str


class InterviewSessionResponse(BaseModel):
    id: str
    user_id: str
    target_role: str
    session_data: Dict[str, Any]
    evaluation: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
