from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.analysis import ResumeAnalysis
from app.models.resume import Resume, ResumeVersion
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.resume import ResumeVersionResponse
from app.schemas.resume_evolution import (
    ResumeEvolutionDiffResponse,
    VersionRestoreResponse,
)
from app.services.resume_evolution import ResumeEvolutionService

router = APIRouter(prefix="/resumes", tags=["Resume Evolution"])


@router.get("/{resume_id}/versions", response_model=APIResponse[List[ResumeVersionResponse]])
async def list_resume_versions(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify ownership
    r_res = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == current_user.id)
    )
    resume = r_res.scalars().first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")

    v_res = await db.execute(
        select(ResumeVersion)
        .where(ResumeVersion.resume_id == resume_id)
        .order_by(desc(ResumeVersion.version_number))
    )
    versions = v_res.scalars().all()
    return APIResponse(
        success=True,
        data=[ResumeVersionResponse.model_validate(v) for v in versions],
    )


@router.get("/{resume_id}/evolution/diff", response_model=APIResponse[ResumeEvolutionDiffResponse])
async def compare_resume_versions(
    resume_id: str,
    base_version_id: str = Query(..., description="ID of baseline resume version"),
    compare_version_id: str = Query(..., description="ID of comparison resume version"),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # 1. Ownership validation
    r_res = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == current_user.id)
    )
    resume = r_res.scalars().first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")

    # 2. Fetch versions
    v1_res = await db.execute(
        select(ResumeVersion).where(
            ResumeVersion.id == base_version_id, ResumeVersion.resume_id == resume_id
        )
    )
    v1 = v1_res.scalars().first()
    if not v1:
        raise HTTPException(status_code=404, detail="Base resume version not found.")

    v2_res = await db.execute(
        select(ResumeVersion).where(
            ResumeVersion.id == compare_version_id, ResumeVersion.resume_id == resume_id
        )
    )
    v2 = v2_res.scalars().first()
    if not v2:
        raise HTTPException(status_code=404, detail="Comparison resume version not found.")

    # 3. Fetch associated analyses if available
    a1_res = await db.execute(
        select(ResumeAnalysis)
        .where(ResumeAnalysis.resume_version_id == v1.id)
        .order_by(desc(ResumeAnalysis.created_at))
    )
    v1_analysis = a1_res.scalars().first()

    a2_res = await db.execute(
        select(ResumeAnalysis)
        .where(ResumeAnalysis.resume_version_id == v2.id)
        .order_by(desc(ResumeAnalysis.created_at))
    )
    v2_analysis = a2_res.scalars().first()

    diff_report = ResumeEvolutionService.compare_versions(
        resume_id=resume_id,
        v1=v1,
        v2=v2,
        v1_analysis=v1_analysis,
        v2_analysis=v2_analysis,
    )

    return APIResponse(
        success=True,
        message="Resume version evolution calculated.",
        data=diff_report,
    )


@router.post("/{resume_id}/versions/{version_id}/restore", response_model=APIResponse[VersionRestoreResponse])
async def restore_resume_version(
    resume_id: str,
    version_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Ownership validation
    r_res = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == current_user.id)
    )
    resume = r_res.scalars().first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")

    try:
        result = await ResumeEvolutionService.restore_version(
            resume=resume,
            version_id_to_restore=version_id,
            db=db,
        )
        return APIResponse(
            success=True,
            message=result.message,
            data=result,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

