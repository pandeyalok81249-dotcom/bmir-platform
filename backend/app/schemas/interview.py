from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class InterviewQuestion(BaseModel):
    id: str
    category: str  # technical, behavioral, experience_deep_dive, situational
    question: str
    context_from_resume: Optional[str] = None
    evaluation_criteria: List[str] = []
    difficulty: str = "medium"  # entry, medium, hard, staff


class InterviewGenerateRequest(BaseModel):
    resume_id: Optional[str] = None
    resume_version_id: Optional[str] = None
    target_role: str = Field(..., min_length=2, max_length=150)
    focus_areas: Optional[List[str]] = None
    question_count: int = Field(default=5, ge=1, le=10)


class InterviewAnswerEvaluateRequest(BaseModel):
    question_id: str
    question_text: str
    user_answer: str = Field(..., min_length=10)


class STARBreakdown(BaseModel):
    situation_score: float = Field(..., ge=0.0, le=10.0)
    situation_feedback: str
    task_score: float = Field(..., ge=0.0, le=10.0)
    task_feedback: str
    action_score: float = Field(..., ge=0.0, le=10.0)
    action_feedback: str
    result_score: float = Field(..., ge=0.0, le=10.0)
    result_feedback: str


class InterviewAnswerEvaluation(BaseModel):
    question_id: str
    clarity_score: float  # 0 to 10
    overall_score: float = Field(default=75.0, ge=0.0, le=100.0)
    star_method_adherence: str  # Strong, Moderate, Weak
    star_breakdown: Optional[STARBreakdown] = None
    strengths: List[str] = []
    improvement_areas: List[str] = []
    improved_answer_sample: str
    follow_up_recommendation: Optional[str] = None


class FollowUpQuestionRequest(BaseModel):
    question_id: str
    previous_question: str
    user_answer: str = Field(..., min_length=10)
    weakest_area: Optional[str] = None


class FollowUpQuestionResponse(BaseModel):
    follow_up_id: str
    parent_question_id: str
    question: str
    target_star_component: str
    rationale: str


class InterviewSessionSummary(BaseModel):
    session_id: str
    target_role: str
    total_questions_answered: int
    average_overall_score: float
    star_competency_scores: Dict[str, float]
    category_scores: Dict[str, float]
    top_strengths: List[str]
    priority_improvements: List[str]
    readiness_verdict: str


class InterviewSessionResponse(BaseModel):
    id: str
    user_id: str
    target_role: str
    session_data: Dict[str, Any]
    evaluation: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
