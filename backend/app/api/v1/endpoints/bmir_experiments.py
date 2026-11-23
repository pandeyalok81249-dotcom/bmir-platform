from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_bmir_user, require_bmir_role
from app.core.database import get_db
from app.models.bmir import BMIRUser, Experiment, ResearchProject, AuditLog

router = APIRouter(prefix="/bmir/experiments", tags=["bmir-experiments"])


class ExperimentCreateUpdate(BaseModel):
    project_id: Optional[str] = None
    title: str
    domain: str
    objective: str
    hypothesis: str
    methodology: str
    materials_used: Optional[str] = None
    measurements: Optional[str] = None
    observations: Optional[str] = None
    results_summary: Optional[str] = None
    status: str = "Ongoing"  # Draft, Ongoing, Concluded, Replicated
    data_metrics: Optional[Dict[str, Any]] = None


@router.get("")
async def list_experiments(
    project_id: Optional[str] = Query(None),
    domain: Optional[str] = Query(None),
    status_filter: Optional[str] = Query(None, alias="status"),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Experiment).options(selectinload(Experiment.project), selectinload(Experiment.creator))
    if project_id:
        stmt = stmt.where(Experiment.project_id == project_id)
    if domain:
        stmt = stmt.where(func.lower(Experiment.domain) == domain.lower())
    if status_filter:
        stmt = stmt.where(func.lower(Experiment.status) == status_filter.lower())

    stmt = stmt.order_by(Experiment.updated_at.desc())
    result = await db.execute(stmt)
    experiments = result.scalars().all()

    return [
        {
            "id": exp.id,
            "project_id": exp.project_id,
            "project_title": exp.project.title if exp.project else None,
            "project_code": exp.project.project_code if exp.project else None,
            "creator_name": exp.creator.full_name if exp.creator else None,
            "title": exp.title,
            "domain": exp.domain,
            "objective": exp.objective,
            "hypothesis": exp.hypothesis,
            "status": exp.status,
            "version": exp.version,
            "results_summary": exp.results_summary,
            "data_metrics": exp.data_metrics,
            "created_at": exp.created_at.isoformat(),
            "updated_at": exp.updated_at.isoformat(),
        }
        for exp in experiments
    ]


@router.get("/{id}")
async def get_experiment_detail(id: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Experiment)
        .options(selectinload(Experiment.project), selectinload(Experiment.creator))
        .where(Experiment.id == id)
    )
    result = await db.execute(stmt)
    exp = result.scalar_one_or_none()
    if not exp:
        raise HTTPException(status_code=404, detail="Experiment record not found")

    return {
        "id": exp.id,
        "project_id": exp.project_id,
        "project_title": exp.project.title if exp.project else None,
        "project_code": exp.project.project_code if exp.project else None,
        "creator_name": exp.creator.full_name if exp.creator else None,
        "title": exp.title,
        "domain": exp.domain,
        "objective": exp.objective,
        "hypothesis": exp.hypothesis,
        "methodology": exp.methodology,
        "materials_used": exp.materials_used,
        "measurements": exp.measurements,
        "observations": exp.observations,
        "results_summary": exp.results_summary,
        "status": exp.status,
        "version": exp.version,
        "data_metrics": exp.data_metrics,
        "created_at": exp.created_at.isoformat(),
        "updated_at": exp.updated_at.isoformat(),
    }


@router.post("", dependencies=[Depends(require_bmir_role(["super_admin", "founder", "research_scientist", "research_engineer"]))])
async def create_experiment(
    payload: ExperimentCreateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: BMIRUser = Depends(get_current_bmir_user),
):
    exp = Experiment(
        created_by_id=current_user.id,
        **payload.model_dump(),
    )
    db.add(exp)
    await db.flush()

    log = AuditLog(
        user_id=current_user.id,
        action="CREATE_EXPERIMENT",
        resource_type="Experiment",
        resource_id=exp.id,
        details={"title": exp.title, "domain": exp.domain},
    )
    db.add(log)
    await db.commit()
    return {"id": exp.id, "title": exp.title, "version": exp.version, "message": "Experiment created successfully"}

