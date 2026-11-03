from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class ResumeCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)


class ResumeVersionResponse(BaseModel):
    id: str
    resume_id: str
    version_number: int
    resume_content: Dict[str, Any]
    content_hash: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeResponse(BaseModel):
    id: str
    user_id: str
    title: str
    original_filename: str
    file_type: str
    file_size_bytes: int
    processing_status: str
    latest_score: Optional[float] = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ResumeDetailResponse(ResumeResponse):
    extracted_text: Optional[str] = None
    versions: List[ResumeVersionResponse] = []
