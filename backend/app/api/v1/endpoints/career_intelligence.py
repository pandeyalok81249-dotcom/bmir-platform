from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.profile import UserProfile
from app.models.resume import Resume, ResumeVersion
from app.models.user import User
from app.schemas.career_intelligence import FullCareerIntelligenceReport
from app.schemas.common import APIResponse
from app.schemas.trajectory_simulator import (
    TrajectorySimulatorRequest,
    TrajectorySimulatorResponse,
)
from app.services.career_intelligence import CareerIntelligenceEngine
from app.services.evidence_graph import EvidenceGraphService
from app.services.trajectory_simulator import CareerTrajectorySimulatorService

router = APIRouter(prefix="/career-intelligence", tags=["Career Intelligence"])
_trajectory_service = CareerTrajectorySimulatorService()
_evidence_service = EvidenceGraphService()


@router.get("/report", response_model=APIResponse[FullCareerIntelligenceReport])
async def get_career_intelligence_report(
    target_role: Optional[str] = Query(None, description="Optional target role override"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    report = await CareerIntelligenceEngine.generate_report(
        user_id=current_user.id,
        db=db,
        target_role_override=target_role,
    )
    return APIResponse(
        success=True,
        message="Contextual career intelligence synthesized successfully.",
        data=report,
    )


@router.post("/analyze", response_model=APIResponse[FullCareerIntelligenceReport])
async def analyze_career_profile(
    target_role: Optional[str] = Query(None, description="Optional target role override"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    report = await CareerIntelligenceEngine.generate_report(
        user_id=current_user.id,
        db=db,
        target_role_override=target_role,
    )
    return APIResponse(
        success=True,
        message="Career intelligence analysis completed.",
        data=report,
    )


@router.post("/simulate-trajectory", response_model=APIResponse[TrajectorySimulatorResponse])
async def simulate_career_trajectory(
    request: TrajectorySimulatorRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Retrieve user resume text and skills
    resume = None
    if request.resume_id:
        resume = await db.get(Resume, request.resume_id)
        if not resume or resume.user_id != current_user.id:
            raise HTTPException(status_code=404, detail="Resume not found")
    else:
        # Get latest resume for user
        r_res = await db.execute(
            select(Resume)
            .where(Resume.user_id == current_user.id)
            .order_by(desc(Resume.created_at))
        )
        resume = r_res.scalars().first()

    skills: List[str] = []
    exp_years: float = 3.0

    if resume:
        text = resume.extracted_text or ""
        skills = _evidence_service._extract_skills_from_text(text)
    
    # Check user profile
    prof_res = await db.execute(select(UserProfile).where(UserProfile.user_id == current_user.id))
    profile = prof_res.scalars().first()
    if profile:
        if profile.years_of_experience:
            exp_years = float(profile.years_of_experience)
        if profile.skills:
            for s in profile.skills:
                if s not in skills:
                    skills.append(s)

    sim_response = _trajectory_service.simulate_trajectories(
        candidate_id=current_user.id,
        user_skills=skills,
        user_experience_years=exp_years,
        target_roles=request.target_roles,
    )
    return APIResponse(data=sim_response)

