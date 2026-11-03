from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class JobDescriptionCreate(BaseModel):
    job_title: str = Field(..., min_length=2, max_length=200)
    company: Optional[str] = Field(None, max_length=200)
    raw_text: str = Field(..., min_length=20)


class JobDescriptionResponse(BaseModel):
    id: str
    user_id: str
    company: Optional[str] = None
    job_title: str
    raw_text: str
    extracted_requirements: Dict[str, Any] = {}
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class JobMatchRequest(BaseModel):
    resume_version_id: str
    job_description_id: str


class SkillMatchDetail(BaseModel):
    skill_name: str
    is_required: bool
    status: str  # 'verified_demonstrated', 'mentioned_only', 'missing', 'unassessed'
    evidence_text: Optional[str] = None


class JobMatchResult(BaseModel):
    overall_match_score: float  # 0 to 100
    required_skills_match: float
    preferred_skills_match: float
    experience_alignment: str
    matched_skills: List[SkillMatchDetail] = []
    missing_critical_skills: List[str] = []
    recommended_positioning: List[str] = []


class JobMatchResponse(BaseModel):
    id: str
    resume_version_id: str
    job_description_id: str
    match_score: float
    match_result: JobMatchResult
    methodology_version: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
