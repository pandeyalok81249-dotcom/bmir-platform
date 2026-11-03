from datetime import date, datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ApplicationCreate(BaseModel):
    company: str = Field(..., min_length=1, max_length=200)
    position: str = Field(..., min_length=1, max_length=200)
    job_description_id: Optional[str] = None
    resume_version_id: Optional[str] = None
    status: str = "saved"  # saved, applied, screening, interview, offer, rejected, withdrawn
    application_date: Optional[date] = None
    interview_dates: List[Dict[str, Any]] = []
    notes: Optional[str] = None
    follow_up_date: Optional[date] = None


class ApplicationUpdate(BaseModel):
    company: Optional[str] = None
    position: Optional[str] = None
    status: Optional[str] = None
    application_date: Optional[date] = None
    interview_dates: Optional[List[Dict[str, Any]]] = None
    notes: Optional[str] = None
    follow_up_date: Optional[date] = None


class ApplicationResponse(BaseModel):
    id: str
    user_id: str
    job_description_id: Optional[str] = None
    resume_version_id: Optional[str] = None
    company: str
    position: str
    status: str
    application_date: Optional[date] = None
    interview_dates: List[Dict[str, Any]] = []
    notes: Optional[str] = None
    follow_up_date: Optional[date] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
