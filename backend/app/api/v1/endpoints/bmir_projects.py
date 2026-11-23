from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_bmir_user, get_optional_bmir_user, require_bmir_role
from app.core.database import get_db
from app.models.bmir import BMIRUser, ResearchProject, Experiment, AuditLog

router = APIRouter(prefix="/bmir/projects", tags=["bmir-projects"])


class ProjectCreateUpdate(BaseModel):
    project_code: str
    title: str
    domain: str
    objective: str
    research_questions: Optional[str] = None
    methodology: str
    technical_requirements: Optional[str] = None
    progress_pct: int = 10
    status: str = "Active"
    lead_researcher: str = "Binod Pandey"
    team_members: Optional[str] = None
    expected_outcome: Optional[str] = None


@router.get("")
async def list_research_projects(
    domain: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    q: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(ResearchProject)
    if domain:
        stmt = stmt.where(func.lower(ResearchProject.domain) == domain.lower())
    if status_filter:
        stmt = stmt.where(func.lower(ResearchProject.status) == status_filter.lower())
    if q:
        search_pattern = f"%{q.lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(ResearchProject.title).like(search_pattern),
                func.lower(ResearchProject.project_code).like(search_pattern),
                func.lower(ResearchProject.objective).like(search_pattern),
            )
        )
    stmt = stmt.order_by(ResearchProject.created_at.desc())
    result = await db.execute(stmt)
    projects = result.scalars().all()

    return [
        {
            "id": p.id,
            "project_code": p.project_code,
            "title": p.title,
            "domain": p.domain,
            "objective": p.objective,
            "research_questions": p.research_questions,
            "methodology": p.methodology,
            "technical_requirements": p.technical_requirements,
            "progress_pct": p.progress_pct,
            "status": p.status,
            "lead_researcher": p.lead_researcher,
            "team_members": p.team_members,
            "created_at": p.created_at.isoformat(),
        }
        for p in projects
    ]


@router.get("/{id}")
async def get_research_project_detail(id: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(ResearchProject)
        .options(selectinload(ResearchProject.experiments))
        .where(or_(ResearchProject.id == id, ResearchProject.project_code == id))
    )
    result = await db.execute(stmt)
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Project not found")

    return {
        "id": p.id,
        "project_code": p.project_code,
        "title": p.title,
        "domain": p.domain,
        "objective": p.objective,
        "research_questions": p.research_questions,
        "methodology": p.methodology,
        "technical_requirements": p.technical_requirements,
        "progress_pct": p.progress_pct,
        "status": p.status,
        "lead_researcher": p.lead_researcher,
        "team_members": p.team_members,
        "expected_outcome": p.expected_outcome,
        "created_at": p.created_at.isoformat(),
        "experiments": [
            {
                "id": exp.id,
                "title": exp.title,
                "domain": exp.domain,
                "status": exp.status,
                "version": exp.version,
                "results_summary": exp.results_summary,
                "created_at": exp.created_at.isoformat(),
            }
            for exp in p.experiments
        ],
    }


@router.post("", dependencies=[Depends(require_bmir_role(["super_admin", "founder", "research_scientist", "research_engineer"]))])
async def create_research_project(
    payload: ProjectCreateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: BMIRUser = Depends(get_current_bmir_user),
):
    prj = ResearchProject(**payload.model_dump())
    db.add(prj)
    await db.flush()

    log = AuditLog(
        user_id=current_user.id,
        action="CREATE_RESEARCH_PROJECT",
        resource_type="ResearchProject",
        resource_id=prj.id,
        details={"code": prj.project_code, "title": prj.title},
    )
    db.add(log)
    await db.commit()
    return {"id": prj.id, "project_code": prj.project_code, "message": "Project created successfully"}

