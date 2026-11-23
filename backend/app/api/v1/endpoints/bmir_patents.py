from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_current_bmir_user, get_optional_bmir_user, require_bmir_role
from app.core.database import get_db
from app.models.bmir import BMIRUser, PatentRecord, AuditLog

router = APIRouter(prefix="/bmir/patents", tags=["bmir-patents"])


class PatentRecordCreateUpdate(BaseModel):
    title: str
    application_number: str
    provisional_application_number: Optional[str] = None
    filing_date: Optional[str] = None
    provisional_filing_date: Optional[str] = None
    publication_date: Optional[str] = None
    journal_issue: Optional[str] = None
    journal_page: Optional[str] = None
    jurisdiction: str = "Indian Patent Office (IPO / Kolkata)"
    lead_inventor: str = "Binod Pandey"
    co_inventors: Optional[str] = None
    applicants: str = "Binod Pandey"
    patent_type: str = "Provisional"  # Idea, Provisional, Complete, Published, Granted, Abandoned
    legal_status: str = "Application Filed"
    verification_notes: Optional[str] = None
    claims_summary: Optional[str] = None
    innovation_id: Optional[str] = None
    is_confidential: bool = False


@router.get("")
async def list_patent_records(
    patent_type: Optional[str] = Query(None, description="Filter by patent type (Provisional, Complete, Published, Granted)"),
    legal_status: Optional[str] = Query(None, description="Filter by legal status"),
    q: Optional[str] = Query(None, description="Search keyword in title or application number"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[BMIRUser] = Depends(get_optional_bmir_user),
):
    stmt = select(PatentRecord).options(selectinload(PatentRecord.innovation))

    # Confidentiality check
    if not current_user or current_user.role in ["viewer", "external_collaborator"]:
        stmt = stmt.where(PatentRecord.is_confidential == False)

    if patent_type:
        stmt = stmt.where(func.lower(PatentRecord.patent_type) == patent_type.lower())

    if legal_status:
        stmt = stmt.where(PatentRecord.legal_status.ilike(f"%{legal_status}%"))

    if q:
        search_pattern = f"%{q.lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(PatentRecord.title).like(search_pattern),
                func.lower(PatentRecord.application_number).like(search_pattern),
                func.lower(PatentRecord.lead_inventor).like(search_pattern),
            )
        )

    stmt = stmt.order_by(PatentRecord.created_at.desc())
    result = await db.execute(stmt)
    records = result.scalars().all()

    return [
        {
            "id": p.id,
            "title": p.title,
            "application_number": p.application_number,
            "provisional_application_number": p.provisional_application_number,
            "filing_date": p.filing_date,
            "provisional_filing_date": p.provisional_filing_date,
            "publication_date": p.publication_date,
            "journal_issue": p.journal_issue,
            "journal_page": p.journal_page,
            "jurisdiction": p.jurisdiction,
            "lead_inventor": p.lead_inventor,
            "co_inventors": p.co_inventors,
            "applicants": p.applicants,
            "patent_type": p.patent_type,
            "legal_status": p.legal_status,
            "verification_notes": p.verification_notes,
            "claims_summary": p.claims_summary,
            "is_confidential": p.is_confidential,
            "innovation_code": p.innovation.project_code if p.innovation else None,
            "innovation_id": p.innovation_id,
        }
        for p in records
    ]


@router.get("/{id}")
async def get_patent_record(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[BMIRUser] = Depends(get_optional_bmir_user),
):
    stmt = (
        select(PatentRecord)
        .options(selectinload(PatentRecord.innovation))
        .where(or_(PatentRecord.id == id, PatentRecord.application_number == id))
    )
    result = await db.execute(stmt)
    p = result.scalar_one_or_none()

    if not p:
        raise HTTPException(status_code=404, detail="Patent record not found")

    if p.is_confidential and (not current_user or current_user.role in ["viewer", "external_collaborator"]):
        raise HTTPException(status_code=403, detail="Confidential patent record access restricted")

    return {
        "id": p.id,
        "title": p.title,
        "application_number": p.application_number,
        "provisional_application_number": p.provisional_application_number,
        "filing_date": p.filing_date,
        "provisional_filing_date": p.provisional_filing_date,
        "publication_date": p.publication_date,
        "journal_issue": p.journal_issue,
        "journal_page": p.journal_page,
        "jurisdiction": p.jurisdiction,
        "lead_inventor": p.lead_inventor,
        "co_inventors": p.co_inventors,
        "applicants": p.applicants,
        "patent_type": p.patent_type,
        "legal_status": p.legal_status,
        "verification_notes": p.verification_notes,
        "claims_summary": p.claims_summary,
        "is_confidential": p.is_confidential,
        "innovation": {
            "id": p.innovation.id,
            "title": p.innovation.title,
            "code": p.innovation.project_code,
            "domain": p.innovation.domain,
        }
        if p.innovation
        else None,
    }


@router.post("", dependencies=[Depends(require_bmir_role(["super_admin", "founder", "research_admin"]))])
async def create_patent_record(
    payload: PatentRecordCreateUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: BMIRUser = Depends(get_current_bmir_user),
):
    prec = PatentRecord(**payload.model_dump())
    db.add(prec)
    await db.flush()

    log = AuditLog(
        user_id=current_user.id,
        action="CREATE_PATENT_RECORD",
        resource_type="PatentRecord",
        resource_id=prec.id,
        details={"app_no": prec.application_number, "title": prec.title},
    )
    db.add(log)
    await db.commit()
    return {"id": prec.id, "application_number": prec.application_number, "message": "Patent record created successfully"}

