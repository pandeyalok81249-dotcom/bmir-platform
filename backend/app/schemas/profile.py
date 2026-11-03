from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class EducationItem(BaseModel):
    institution: str
    degree: str
    field_of_study: Optional[str] = None
    start_year: Optional[int] = None
    end_year: Optional[int] = None
    gpa: Optional[str] = None


class ProfileUpdate(BaseModel):
    full_name: Optional[str] = Field(None, min_length=2, max_length=150)
    career_stage: Optional[str] = None  # student, entry, mid, senior, switcher
    current_role: Optional[str] = None
    target_role: Optional[str] = None
    experience_years: Optional[float] = None
    education: Optional[List[EducationItem]] = None
    preferred_location: Optional[str] = None
    career_goals: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


class ProfileResponse(BaseModel):
    id: str
    user_id: str
    full_name: str
    career_stage: Optional[str] = None
    current_role: Optional[str] = None
    target_role: Optional[str] = None
    experience_years: float = 0.0
    education: List[Dict[str, Any]] = []
    preferred_location: Optional[str] = None
    career_goals: Optional[str] = None
    preferences: Dict[str, Any] = {}
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
