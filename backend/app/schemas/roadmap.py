from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class MilestoneItem(BaseModel):
    id: str
    title: str
    description: str
    target_skills: List[str]
    estimated_hours: int
    practical_project: Optional[str] = None
    completed: bool = False


class CareerRoadmapGenerateRequest(BaseModel):
    target_role: str = Field(..., min_length=2, max_length=150)
    current_resume_id: Optional[str] = None


class CareerRoadmapResponse(BaseModel):
    id: str
    user_id: str
    target_role: str
    roadmap_data: Dict[str, Any]
    progress: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
