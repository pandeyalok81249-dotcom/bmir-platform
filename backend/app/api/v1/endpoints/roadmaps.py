import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.roadmap import CareerRoadmap
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.roadmap import CareerRoadmapGenerateRequest, CareerRoadmapResponse

router = APIRouter(prefix="/roadmaps", tags=["Career Roadmap"])


class ProgressUpdateRequest(BaseModel):
    milestone_id: str
    completed: bool


@router.post("/generate", response_model=APIResponse[CareerRoadmapResponse])
async def generate_career_roadmap(
    req: CareerRoadmapGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    target = req.target_role.strip()
    milestones = [
        {
            "id": str(uuid.uuid4()),
            "title": f"Master Core Architecture & Engineering Patterns for {target}",
            "description": "Solidify deep domain foundations, design patterns, and asynchronous API design.",
            "target_skills": ["System Design", "Clean Architecture", "API Resilience"],
            "estimated_hours": 30,
            "practical_project": f"Build a distributed backend or performant mobile client embodying {target} requirements.",
            "completed": False,
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Evidence-Based Production Optimization",
            "description": "Implement telemetry, performance benchmarks, and end-to-end integration testing.",
            "target_skills": ["Telemetry", "Docker / CI/CD", "Automated Testing"],
            "estimated_hours": 25,
            "practical_project": "Set up automated GitHub Actions workflow with linting and unit test coverage checks.",
            "completed": False,
        },
        {
            "id": str(uuid.uuid4()),
            "title": "Resume Portfolio Alignment & STAR Impact Storytelling",
            "description": "Incorporate verified quantified achievements and technical artifacts into career narrative.",
            "target_skills": ["STAR Storytelling", "Technical Communication", "Portfolio Delivery"],
            "estimated_hours": 15,
            "practical_project": "Publish working live demos with architectural walkthroughs.",
            "completed": False,
        },
    ]

    roadmap = CareerRoadmap(
        user_id=current_user.id,
        target_role=target,
        roadmap_data={"milestones": milestones},
        progress=0.0,
    )
    db.add(roadmap)
    await db.commit()
    await db.refresh(roadmap)

    return APIResponse(
        success=True,
        message="Personalized career roadmap generated.",
        data=CareerRoadmapResponse.model_validate(roadmap),
    )


@router.get("", response_model=APIResponse[Optional[CareerRoadmapResponse]])
async def get_latest_roadmap(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CareerRoadmap)
        .where(CareerRoadmap.user_id == current_user.id)
        .order_by(desc(CareerRoadmap.created_at))
    )
    roadmap = result.scalars().first()
    if not roadmap:
        return APIResponse(success=True, data=None)

    return APIResponse(success=True, data=CareerRoadmapResponse.model_validate(roadmap))


@router.patch("/{roadmap_id}/progress", response_model=APIResponse[CareerRoadmapResponse])
async def update_roadmap_progress(
    roadmap_id: str,
    progress_in: ProgressUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CareerRoadmap).where(
            CareerRoadmap.id == roadmap_id,
            CareerRoadmap.user_id == current_user.id,
        )
    )
    roadmap = result.scalars().first()
    if not roadmap:
        raise HTTPException(status_code=404, detail="Roadmap not found.")

    roadmap_data = dict(roadmap.roadmap_data or {})
    milestones = roadmap_data.get("milestones", [])
    completed_count = 0

    for m in milestones:
        if m.get("id") == progress_in.milestone_id:
            m["completed"] = progress_in.completed
        if m.get("completed"):
            completed_count += 1

    total = len(milestones) if milestones else 1
    roadmap.progress = round((completed_count / total) * 100, 1)
    roadmap.roadmap_data = roadmap_data

    await db.commit()
    await db.refresh(roadmap)

    return APIResponse(
        success=True,
        message="Roadmap progress updated.",
        data=CareerRoadmapResponse.model_validate(roadmap),
    )

