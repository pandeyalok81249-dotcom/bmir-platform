import re
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.factory import AIFactory
from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.job import JobDescription, JobMatch
from app.models.resume import Resume, ResumeVersion
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.job_match import (
    JobDescriptionCreate,
    JobDescriptionResponse,
    JobMatchRequest,
    JobMatchResponse,
    JobMatchResult,
)
from app.services.job_matcher import JobMatcherService

router = APIRouter(prefix="/job-matches", tags=["Job Match"])


@router.post("/descriptions", response_model=APIResponse[JobDescriptionResponse])
async def create_job_description(
    job_in: JobDescriptionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Extract requirements via AI or deterministic regex
    extracted = {}
    try:
        provider = AIFactory.get_provider()
        ai_resp = await provider.extract_job_requirements(job_in.raw_text)
        extracted = ai_resp.content
    except Exception:
        # Deterministic fallback extraction
        skills_found = []
        common_reqs = [
            "python", "javascript", "typescript", "flutter", "dart", "react", "docker",
            "kubernetes", "postgresql", "fastapi", "aws", "gcp", "git", "ci/cd", "redis",
            "rest api", "graphql", "agile", "leadership"
        ]
        lower_raw = job_in.raw_text.lower()
        for c in common_reqs:
            if re.search(r"\b" + re.escape(c) + r"\b", lower_raw):
                skills_found.append(c.capitalize())
        extracted = {
            "job_title": job_in.job_title,
            "required_skills": skills_found[:8],
            "preferred_skills": skills_found[8:],
            "min_experience_years": 2.0,
            "required_education": ["Bachelor's degree in Computer Science or equivalent practical experience"],
            "key_responsibilities": ["Design, test, and maintain robust production software."],
        }

    job_desc = JobDescription(
        user_id=current_user.id,
        company=job_in.company,
        job_title=job_in.job_title,
        raw_text=job_in.raw_text,
        extracted_requirements=extracted,
    )
    db.add(job_desc)
    await db.commit()
    await db.refresh(job_desc)

    return APIResponse(
        success=True,
        message="Job description parsed and saved.",
        data=JobDescriptionResponse.model_validate(job_desc),
    )


@router.get("/descriptions", response_model=APIResponse[List[JobDescriptionResponse]])
async def list_job_descriptions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(JobDescription)
        .where(JobDescription.user_id == current_user.id)
        .order_by(desc(JobDescription.created_at))
    )
    jobs = result.scalars().all()
    return APIResponse(
        success=True,
        data=[JobDescriptionResponse.model_validate(j) for j in jobs],
    )


@router.post("/match", response_model=APIResponse[JobMatchResponse])
async def match_resume_to_job(
    match_req: JobMatchRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Verify ResumeVersion belongs to current user
    v_res = await db.execute(
        select(ResumeVersion)
        .join(Resume, ResumeVersion.resume_id == Resume.id)
        .where(ResumeVersion.id == match_req.resume_version_id, Resume.user_id == current_user.id)
    )
    version = v_res.scalars().first()
    if not version:
        raise HTTPException(status_code=404, detail="Resume version not found.")

    # Verify JobDescription belongs to current user
    j_res = await db.execute(
        select(JobDescription).where(
            JobDescription.id == match_req.job_description_id,
            JobDescription.user_id == current_user.id,
        )
    )
    job = j_res.scalars().first()
    if not job:
        raise HTTPException(status_code=404, detail="Job description not found.")

    # Execute match
    match_result = JobMatcherService.match(
        resume_content=version.resume_content,
        job_reqs=job.extracted_requirements,
    )

    job_match = JobMatch(
        resume_version_id=version.id,
        job_description_id=job.id,
        match_score=match_result.overall_match_score,
        match_result=match_result.model_dump(),
        methodology_version="1.0",
    )
    db.add(job_match)
    await db.commit()
    await db.refresh(job_match)

    return APIResponse(
        success=True,
        message="Match evaluation complete.",
        data=JobMatchResponse(
            id=job_match.id,
            resume_version_id=job_match.resume_version_id,
            job_description_id=job_match.job_description_id,
            match_score=job_match.match_score,
            match_result=match_result,
            methodology_version=job_match.methodology_version,
            created_at=job_match.created_at,
        ),
    )


@router.get("/match/{match_id}", response_model=APIResponse[JobMatchResponse])
async def get_match_detail(
    match_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(JobMatch)
        .join(ResumeVersion, JobMatch.resume_version_id == ResumeVersion.id)
        .join(Resume, ResumeVersion.resume_id == Resume.id)
        .where(JobMatch.id == match_id, Resume.user_id == current_user.id)
    )
    match_record = result.scalars().first()
    if not match_record:
        raise HTTPException(status_code=404, detail="Job match record not found.")

    return APIResponse(
        success=True,
        data=JobMatchResponse(
            id=match_record.id,
            resume_version_id=match_record.resume_version_id,
            job_description_id=match_record.job_description_id,
            match_score=match_record.match_score,
            match_result=JobMatchResult.model_validate(match_record.match_result),
            methodology_version=match_record.methodology_version,
            created_at=match_record.created_at,
        ),
    )

