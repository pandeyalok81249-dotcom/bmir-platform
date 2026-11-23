from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_bmir_user, get_optional_bmir_user, require_bmir_role
from app.core.database import get_db
from app.models.bmir import BMIRUser, Innovation, PatentRecord, FeasibilityEvaluation, InnovationRoadmap, AuditLog

router = APIRouter(prefix="/bmir/innovations", tags=["bmir-innovations"])


class InnovationCreateUpdate(BaseModel):
    project_code: str
    title: str
    title_hi: Optional[str] = None
    domain: str
    summary: str
    summary_hi: Optional[str] = None
    problem_statement: str
    problem_statement_hi: Optional[str] = None
    proposed_solution: str
    proposed_solution_hi: Optional[str] = None
    technical_description: Optional[str] = None
    technical_description_hi: Optional[str] = None
    development_stage: str = "Concept"
    prototype_status: str = "Unverified Concept"
    validation_required: Optional[str] = None
    validation_required_hi: Optional[str] = None
    collaboration_sought: Optional[str] = None
    collaboration_sought_hi: Optional[str] = None
    patent_application_no: Optional[str] = None
    patent_status: str = "Not filed / unverified"
    co_inventors: Optional[str] = None
    is_published: bool = True
    is_confidential: bool = False


@router.get("")
async def list_innovations(
    q: Optional[str] = Query(None, description="Search keyword in title, summary, or problem"),
    domain: Optional[str] = Query(None, description="Filter by research domain"),
    stage: Optional[str] = Query(None, description="Filter by development stage"),
    patent_status: Optional[str] = Query(None, description="Filter by patent status"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[BMIRUser] = Depends(get_optional_bmir_user),
):
    stmt = select(Innovation)

    # If unauthenticated or regular viewer, only show non-confidential published innovations
    if not current_user or current_user.role in ["viewer", "external_collaborator"]:
        stmt = stmt.where(Innovation.is_confidential == False, Innovation.is_published == True)

    if domain:
        stmt = stmt.where(func.lower(Innovation.domain) == domain.lower())

    if stage:
        stmt = stmt.where(func.lower(Innovation.development_stage) == stage.lower())

    if patent_status:
        stmt = stmt.where(Innovation.patent_status.ilike(f"%{patent_status}%"))

    if q:
        search_pattern = f"%{q.lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(Innovation.title).like(search_pattern),
                func.lower(Innovation.summary).like(search_pattern),
                func.lower(Innovation.problem_statement).like(search_pattern),
                func.lower(Innovation.project_code).like(search_pattern),
                func.lower(Innovation.domain).like(search_pattern),
            )
        )

    stmt = stmt.order_by(Innovation.project_code.asc())
    result = await db.execute(stmt)
    items = result.scalars().all()

    return [
        {
            "id": inv.id,
            "project_code": inv.project_code,
            "title": inv.title,
            "title_hi": inv.title_hi,
            "domain": inv.domain,
            "summary": inv.summary,
            "summary_hi": inv.summary_hi,
            "problem_statement": inv.problem_statement,
            "problem_statement_hi": inv.problem_statement_hi,
            "proposed_solution": inv.proposed_solution,
            "proposed_solution_hi": inv.proposed_solution_hi,
            "development_stage": inv.development_stage,
            "prototype_status": inv.prototype_status,
            "validation_required": inv.validation_required,
            "validation_required_hi": inv.validation_required_hi,
            "collaboration_sought": inv.collaboration_sought,
            "collaboration_sought_hi": inv.collaboration_sought_hi,
            "patent_application_no": inv.patent_application_no,
            "patent_status": inv.patent_status,
            "co_inventors": inv.co_inventors,
            "is_published": inv.is_published,
            "verification_status": inv.verification_status,
            "created_at": inv.created_at.isoformat(),
        }
        for inv in items
    ]


@router.get("/domains/list")
async def get_domains_summary(db: AsyncSession = Depends(get_db)):
    stmt = (
        select(Innovation.domain, func.count(Innovation.id))
        .where(Innovation.is_published == True)
        .group_by(Innovation.domain)
    )
    result = await db.execute(stmt)
    rows = result.all()
    return [{"domain": r[0], "count": r[1]} for r in rows]


@router.get("/{id}")
async def get_innovation_detail(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[BMIRUser] = Depends(get_optional_bmir_user),
):
    stmt = (
        select(Innovation)
        .options(
            selectinload(Innovation.patent_records),
            selectinload(Innovation.feasibility_evaluations),
            selectinload(Innovation.roadmaps),
        )
        .where(or_(Innovation.id == id, Innovation.project_code == id))
    )
    result = await db.execute(stmt)
    inv = result.scalar_one_or_none()

    if not inv:
        raise HTTPException(status_code=404, detail="Innovation not found")

    if inv.is_confidential and (not current_user or current_user.role in ["viewer", "external_collaborator"]):
        raise HTTPException(status_code=403, detail="Access to confidential innovation restricted")

    return {
        "id": inv.id,
        "project_code": inv.project_code,
        "title": inv.title,
        "title_hi": inv.title_hi,
        "domain": inv.domain,
        "summary": inv.summary,
        "summary_hi": inv.summary_hi,
        "problem_statement": inv.problem_statement,
        "problem_statement_hi": inv.problem_statement_hi,
        "proposed_solution": inv.proposed_solution,
        "proposed_solution_hi": inv.proposed_solution_hi,
        "technical_description": inv.technical_description,
        "technical_description_hi": inv.technical_description_hi,
        "development_stage": inv.development_stage,
        "prototype_status": inv.prototype_status,
        "validation_required": inv.validation_required,
        "validation_required_hi": inv.validation_required_hi,
        "collaboration_sought": inv.collaboration_sought,
        "collaboration_sought_hi": inv.collaboration_sought_hi,
        "patent_application_no": inv.patent_application_no,
        "patent_status": inv.patent_status,
        "co_inventors": inv.co_inventors,
        "is_published": inv.is_published,
        "is_confidential": inv.is_confidential,
        "verification_status": inv.verification_status,
        "patent_records": [
            {
                "id": p.id,
                "title": p.title,
                "application_number": p.application_number,
                "provisional_application_number": p.provisional_application_number,
                "filing_date": p.filing_date,
                "publication_date": p.publication_date,
                "journal_issue": p.journal_issue,
                "journal_page": p.journal_page,
                "patent_type": p.patent_type,
                "legal_status": p.legal_status,
                "verification_notes": p.verification_notes,
            }
            for p in inv.patent_records
        ],
        "feasibility_evaluations": [
            {
                "id": f.id,
                "title": f.title,
                "overall_score": f.overall_score,
                "scientific_feasibility": f.scientific_feasibility,
                "engineering_feasibility": f.engineering_feasibility,
                "material_availability": f.material_availability,
                "manufacturing_readiness": f.manufacturing_readiness,
                "energy_efficiency": f.energy_efficiency,
                "economic_viability": f.economic_viability,
                "environmental_impact": f.environmental_impact,
                "safety_compliance": f.safety_compliance,
                "confidence_level": f.confidence_level,
                "limitations_and_risks": f.limitations_and_risks,
            }
            for f in inv.feasibility_evaluations
        ],
        "roadmaps": [
            {
                "id": r.id,
                "title": r.title,
                "phases": r.phases_json,
                "estimated_timeline_months": r.estimated_timeline_months,
                "status": r.status,
            }
            for r in inv.roadmaps
        ],
    }


@router.post("", dependencies=[Depends(require_bmir_role(["super_admin", "founder", "research_admin", "research_scientist"]))])
async def create_innovation(
    payload: InnovationCreateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: BMIRUser = Depends(get_current_bmir_user),
):
    inv = Innovation(**payload.model_dump())
    db.add(inv)
    await db.flush()

    log = AuditLog(
        user_id=current_user.id,
        action="CREATE_INNOVATION",
        resource_type="Innovation",
        resource_id=inv.id,
        details={"code": inv.project_code, "title": inv.title},
    )
    db.add(log)
    await db.commit()
    return {"id": inv.id, "project_code": inv.project_code, "message": "Innovation created successfully"}


@router.put("/{id}", dependencies=[Depends(require_bmir_role(["super_admin", "founder", "research_admin"]))])
async def update_innovation(
    id: str,
    payload: InnovationCreateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: BMIRUser = Depends(get_current_bmir_user),
):
    result = await db.execute(select(Innovation).where(Innovation.id == id))
    inv = result.scalar_one_or_none()
    if not inv:
        raise HTTPException(status_code=404, detail="Innovation not found")

    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(inv, key, value)

    log = AuditLog(
        user_id=current_user.id,
        action="UPDATE_INNOVATION",
        resource_type="Innovation",
        resource_id=inv.id,
        details={"title": inv.title},
    )
    db.add(log)
    await db.commit()
    return {"message": "Innovation updated successfully", "id": inv.id}


class InnovationVerificationUpdate(BaseModel):
    verification_status: str


@router.put("/{id}/verification", dependencies=[Depends(require_bmir_role(["super_admin", "founder", "research_admin"]))])
async def update_innovation_verification(
    id: str,
    req: InnovationVerificationUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: BMIRUser = Depends(get_current_bmir_user),
):
    inv = await db.get(Innovation, id)
    if not inv:
        raise HTTPException(status_code=404, detail="Innovation not found")

    allowed = ["Verified", "Pending verification", "Draft", "Unpublished", "Archived"]
    if req.verification_status not in allowed:
        raise HTTPException(status_code=400, detail=f"Invalid verification status. Allowed: {allowed}")

    inv.verification_status = req.verification_status
    log = AuditLog(
        user_id=current_user.id,
        action="UPDATE_VERIFICATION_STATUS",
        resource_type="Innovation",
        resource_id=inv.id,
        details={"status": req.verification_status},
    )
    db.add(log)
    await db.commit()
    return {"message": "Verification status updated", "id": inv.id, "verification_status": inv.verification_status}

