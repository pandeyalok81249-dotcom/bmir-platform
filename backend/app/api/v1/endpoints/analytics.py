from typing import Any, Dict, List
from fastapi import APIRouter, Depends
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.analysis import ResumeAnalysis
from app.models.application import Application
from app.models.job import JobDescription, JobMatch
from app.models.profile import UserProfile
from app.models.resume import Resume
from app.models.user import User
from app.schemas.common import APIResponse

router = APIRouter(prefix="/analytics", tags=["Analytics"])


@router.get("/dashboard", response_model=APIResponse[Dict[str, Any]])
async def get_dashboard_analytics(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # User Profile
    p_res = await db.execute(select(UserProfile).where(UserProfile.user_id == current_user.id))
    profile = p_res.scalars().first()

    # Total Resumes
    r_count_res = await db.execute(
        select(func.count(Resume.id)).where(Resume.user_id == current_user.id)
    )
    total_resumes = r_count_res.scalar() or 0

    # Latest Resume
    latest_r_res = await db.execute(
        select(Resume)
        .where(Resume.user_id == current_user.id)
        .order_by(desc(Resume.created_at))
    )
    latest_resume = latest_r_res.scalars().first()

    # Latest Analysis
    latest_score = None
    latest_analysis_date = None
    recent_strengths = []
    recent_improvements = []
    if latest_resume:
        a_res = await db.execute(
            select(ResumeAnalysis)
            .where(ResumeAnalysis.resume_id == latest_resume.id)
            .order_by(desc(ResumeAnalysis.created_at))
        )
        latest_analysis = a_res.scalars().first()
        if latest_analysis:
            latest_score = latest_analysis.overall_score
            latest_analysis_date = latest_analysis.created_at.isoformat()
            if latest_analysis.result_json:
                recent_strengths = latest_analysis.result_json.get("key_strengths", [])[:3]
                recent_improvements = latest_analysis.result_json.get("priority_improvements", [])[:3]

    # Application Status Counts
    app_res = await db.execute(
        select(Application.status, func.count(Application.id))
        .where(Application.user_id == current_user.id)
        .group_by(Application.status)
    )
    app_counts = {status: count for status, count in app_res.all()}

    # Recent Activity Events
    activity_events = []
    if latest_resume:
        activity_events.append({
            "type": "resume_upload",
            "title": f"Uploaded '{latest_resume.title}'",
            "timestamp": latest_resume.created_at.isoformat(),
        })
    if latest_analysis_date:
        activity_events.append({
            "type": "resume_analyzed",
            "title": f"Intelligence audit completed (Score: {latest_score}/100)",
            "timestamp": latest_analysis_date,
        })

    data = {
        "user": {
            "full_name": profile.full_name if profile else "Professional",
            "career_stage": profile.career_stage if profile else "Unspecified",
            "target_role": profile.target_role if profile else "Not Set",
        },
        "resume_overview": {
            "total_resumes": total_resumes,
            "latest_resume_title": latest_resume.title if latest_resume else None,
            "latest_score": latest_score,
            "last_analysis_date": latest_analysis_date,
        },
        "application_pipeline": app_counts,
        "recent_activity": activity_events,
        "career_insights": {
            "strengths": recent_strengths,
            "priority_improvements": recent_improvements,
        },
    }

    return APIResponse(success=True, data=data)


@router.get("/skill-gaps", response_model=APIResponse[Dict[str, Any]])
async def get_skill_gaps(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Fetch user's latest job match
    m_res = await db.execute(
        select(JobMatch)
        .join(JobDescription, JobMatch.job_description_id == JobDescription.id)
        .where(JobDescription.user_id == current_user.id)
        .order_by(desc(JobMatch.created_at))
    )
    latest_match = m_res.scalars().first()

    verified_skills = []
    missing_skills = []
    unverified_skills = []

    if latest_match and latest_match.match_result:
        for item in latest_match.match_result.get("matched_skills", []):
            st = item.get("status")
            name = item.get("skill_name")
            if st == "verified_demonstrated":
                verified_skills.append(name)
            elif st == "mentioned_only":
                unverified_skills.append(name)
            elif st == "missing":
                missing_skills.append(name)

    return APIResponse(
        success=True,
        data={
            "verified_skills": verified_skills,
            "unverified_skills": unverified_skills,
            "missing_skills": missing_skills,
            "has_match_data": bool(latest_match),
        },
    )

