import uuid
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from pydantic import BaseModel, EmailStr
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_bmir_user, require_bmir_role
from app.core.database import get_db
from app.models.bmir import BMIRUser, CollaborationEnquiry, AuditLog

router = APIRouter(prefix="/bmir/collaboration", tags=["bmir-collaboration"])


class CollaborationSubmission(BaseModel):
    full_name: str
    email: EmailStr
    phone: Optional[str] = None
    organization: str
    organization_type: str  # University, Research Lab, Corporate R&D, Investor, Incubator, Independent Researcher
    pathway: str  # Research Collaboration, Prototype Development, Technical Review, Licensing, Funding
    project_interest: Optional[str] = None
    message: str
    proposal_summary: Optional[str] = None


class StatusReviewUpdate(BaseModel):
    status: str  # Pending, Under Review, Approved, Declined
    internal_notes: Optional[str] = None


@router.post("/enquiry")
async def submit_collaboration_enquiry(payload: CollaborationSubmission, db: AsyncSession = Depends(get_db)):
    # Generate unique enquiry number
    count_res = await db.execute(select(func.count(CollaborationEnquiry.id)))
    count = count_res.scalar() or 0
    enq_number = f"BMIR-ENQ-2026-{(count + 1):04d}"

    enq = CollaborationEnquiry(
        enquiry_number=enq_number,
        full_name=payload.full_name,
        email=payload.email,
        phone=payload.phone,
        organization=payload.organization,
        organization_type=payload.organization_type,
        pathway=payload.pathway,
        project_interest=payload.project_interest,
        message=payload.message,
        proposal_summary=payload.proposal_summary,
        status="Pending",
    )
    db.add(enq)
    await db.commit()

    return {
        "enquiry_number": enq.enquiry_number,
        "status": "Pending",
        "message": "Collaboration enquiry submitted successfully. BMIR research coordination committee will review your submission.",
    }


@router.get("/enquiries", dependencies=[Depends(require_bmir_role(["super_admin", "founder", "research_admin"]))])
async def list_collaboration_enquiries(
    status_filter: Optional[str] = Query(None, alias="status"),
    pathway: Optional[str] = Query(None),
    db: AsyncSession = Depends(get_db),
):
    stmt = select(CollaborationEnquiry)
    if status_filter:
        stmt = stmt.where(func.lower(CollaborationEnquiry.status) == status_filter.lower())
    if pathway:
        stmt = stmt.where(func.lower(CollaborationEnquiry.pathway) == pathway.lower())

    stmt = stmt.order_by(CollaborationEnquiry.created_at.desc())
    result = await db.execute(stmt)
    enquiries = result.scalars().all()

    return [
        {
            "id": e.id,
            "enquiry_number": e.enquiry_number,
            "full_name": e.full_name,
            "email": e.email,
            "phone": e.phone,
            "organization": e.organization,
            "organization_type": e.organization_type,
            "pathway": e.pathway,
            "project_interest": e.project_interest,
            "message": e.message,
            "proposal_summary": e.proposal_summary,
            "status": e.status,
            "internal_notes": e.internal_notes,
            "created_at": e.created_at.isoformat(),
        }
        for e in enquiries
    ]


@router.put("/enquiries/{id}/status", dependencies=[Depends(require_bmir_role(["super_admin", "founder", "research_admin"]))])
async def update_enquiry_status(
    id: str,
    payload: StatusReviewUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: BMIRUser = Depends(get_current_bmir_user),
):
    result = await db.execute(select(CollaborationEnquiry).where(CollaborationEnquiry.id == id))
    enq = result.scalar_one_or_none()
    if not enq:
        raise HTTPException(status_code=404, detail="Enquiry not found")

    allowed_statuses = ["Pending", "Under Review", "Approved", "Declined"]
    if payload.status not in allowed_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Allowed: {allowed_statuses}")

    enq.status = payload.status
    if payload.internal_notes:
        enq.internal_notes = payload.internal_notes

    log = AuditLog(
        user_id=current_user.id,
        action="UPDATE_ENQUIRY_STATUS",
        resource_type="CollaborationEnquiry",
        resource_id=enq.id,
        details={"status": enq.status, "enquiry_number": enq.enquiry_number},
    )
    db.add(log)
    await db.commit()

    return {
        "id": enq.id,
        "enquiry_number": enq.enquiry_number,
        "status": enq.status,
        "message": f"Status updated to {enq.status}",
    }

