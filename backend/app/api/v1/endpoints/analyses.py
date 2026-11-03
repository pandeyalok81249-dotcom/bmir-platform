import asyncio
from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.redis import JobQueueManager
from app.models.analysis import ResumeAnalysis
from app.models.profile import UserProfile
from app.models.resume import Resume
from app.models.user import User
from app.schemas.analysis import ResumeAnalysisResponse
from app.schemas.common import APIResponse
from app.services.resume_analyzer import ResumeAnalyzerService

router = APIRouter(prefix="/analyses", tags=["Analyses"])


@router.get("/{analysis_id}", response_model=APIResponse[ResumeAnalysisResponse])
async def get_analysis(
    analysis_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ResumeAnalysis)
        .join(Resume, ResumeAnalysis.resume_id == Resume.id)
        .where(ResumeAnalysis.id == analysis_id, Resume.user_id == current_user.id)
    )
    analysis = result.scalars().first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis report not found.")

    return APIResponse(success=True, data=ResumeAnalysisResponse.model_validate(analysis))


@router.get("/{analysis_id}/status", response_model=APIResponse[Dict[str, Any]])
async def get_analysis_status(
    analysis_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify ownership
    result = await db.execute(
        select(ResumeAnalysis)
        .join(Resume, ResumeAnalysis.resume_id == Resume.id)
        .where(ResumeAnalysis.id == analysis_id, Resume.user_id == current_user.id)
    )
    analysis = result.scalars().first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    # Check real job queue status
    queue_state = await JobQueueManager.get_job_status(analysis_id)
    if queue_state:
        return APIResponse(
            success=True,
            data={
                "analysis_id": analysis_id,
                "status": queue_state.get("status", analysis.status),
                "stage_description": queue_state.get("stage_description", "Processing analysis..."),
                "overall_score": analysis.overall_score,
                "result": queue_state.get("result") or analysis.result_json,
                "error": queue_state.get("error") or analysis.error_details,
            },
        )

    return APIResponse(
        success=True,
        data={
            "analysis_id": analysis_id,
            "status": analysis.status,
            "stage_description": "Completed" if analysis.status == "completed" else "Processing...",
            "overall_score": analysis.overall_score,
            "result": analysis.result_json,
            "error": analysis.error_details,
        },
    )


@router.post("/{analysis_id}/retry", response_model=APIResponse[Dict[str, Any]])
async def retry_analysis(
    analysis_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ResumeAnalysis)
        .join(Resume, ResumeAnalysis.resume_id == Resume.id)
        .where(ResumeAnalysis.id == analysis_id, Resume.user_id == current_user.id)
    )
    analysis = result.scalars().first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    p_res = await db.execute(select(UserProfile).where(UserProfile.user_id == current_user.id))
    profile = p_res.scalars().first()

    analysis.status = "queued"
    analysis.error_details = None
    await db.commit()

    await JobQueueManager.set_job_status(
        job_id=analysis_id,
        status="queued",
        stage_description="Retrying analysis job...",
    )

    task = asyncio.create_task(
        ResumeAnalyzerService.process_analysis_job(
            analysis_id=analysis.id,
            resume_id=analysis.resume_id,
            user_id=current_user.id,
            target_role=profile.target_role if profile else None,
            career_stage=profile.career_stage if profile else None,
        )
    )
    JobQueueManager.register_async_task(analysis.id, task)

    return APIResponse(
        success=True,
        message="Analysis re-queued successfully.",
        data={"analysis_id": analysis.id, "status": "queued"},
    )


@router.post("/{analysis_id}/cancel", response_model=APIResponse[Dict[str, Any]])
async def cancel_analysis(
    analysis_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ResumeAnalysis)
        .join(Resume, ResumeAnalysis.resume_id == Resume.id)
        .where(ResumeAnalysis.id == analysis_id, Resume.user_id == current_user.id)
    )
    analysis = result.scalars().first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found.")

    cancelled = await JobQueueManager.cancel_job(analysis_id)
    if cancelled:
        analysis.status = "failed"
        analysis.error_details = "Cancelled by user."
        await db.commit()

    return APIResponse(
        success=True,
        message="Analysis cancellation processed." if cancelled else "Task already finished or not active.",
        data={"analysis_id": analysis_id, "cancelled": cancelled},
    )


@router.get("/resume/{resume_id}", response_model=APIResponse[List[ResumeAnalysisResponse]])
async def get_analyses_for_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    r_check = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == current_user.id)
    )
    if not r_check.scalars().first():
        raise HTTPException(status_code=404, detail="Resume not found.")

    result = await db.execute(
        select(ResumeAnalysis)
        .where(ResumeAnalysis.resume_id == resume_id)
        .order_by(desc(ResumeAnalysis.created_at))
    )
    analyses = result.scalars().all()
    return APIResponse(
        success=True,
        data=[ResumeAnalysisResponse.model_validate(a) for a in analyses],
    )
