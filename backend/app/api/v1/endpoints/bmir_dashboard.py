from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends
from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_bmir_user
from app.core.database import get_db
from app.models.bmir import (
    BMIRUser,
    Innovation,
    PatentRecord,
    ResearchProject,
    Experiment,
    CollaborationEnquiry,
    KnowledgeDocument,
    AuditLog,
    BMIRNotification,
)

router = APIRouter(prefix="/bmir/dashboard", tags=["bmir-dashboard"])


@router.get("/stats")
async def get_dashboard_statistics(
    db: AsyncSession = Depends(get_db),
    current_user: BMIRUser = Depends(get_current_bmir_user),
):
    # Total innovations count
    inv_count = (await db.execute(select(func.count(Innovation.id)))).scalar() or 0

    # Patent records
    total_patents = (await db.execute(select(func.count(PatentRecord.id)))).scalar() or 0
    published_patents = (
        await db.execute(select(func.count(PatentRecord.id)).where(PatentRecord.patent_type == "Published"))
    ).scalar() or 0
    provisional_patents = (
        await db.execute(select(func.count(PatentRecord.id)).where(PatentRecord.patent_type == "Provisional"))
    ).scalar() or 0

    # Research projects
    active_projects = (
        await db.execute(select(func.count(ResearchProject.id)).where(ResearchProject.status == "Active"))
    ).scalar() or 0
    total_projects = (await db.execute(select(func.count(ResearchProject.id)))).scalar() or 0

    # Experiments
    total_experiments = (await db.execute(select(func.count(Experiment.id)))).scalar() or 0
    concluded_experiments = (
        await db.execute(select(func.count(Experiment.id)).where(Experiment.status == "Concluded"))
    ).scalar() or 0

    # Collaboration Enquiries
    total_enquiries = (await db.execute(select(func.count(CollaborationEnquiry.id)))).scalar() or 0
    pending_enquiries = (
        await db.execute(select(func.count(CollaborationEnquiry.id)).where(CollaborationEnquiry.status == "Pending"))
    ).scalar() or 0
    approved_enquiries = (
        await db.execute(select(func.count(CollaborationEnquiry.id)).where(CollaborationEnquiry.status == "Approved"))
    ).scalar() or 0

    # Knowledge Documents
    total_documents = (await db.execute(select(func.count(KnowledgeDocument.id)))).scalar() or 0

    # Domain breakdown
    domain_stmt = select(Innovation.domain, func.count(Innovation.id)).group_by(Innovation.domain)
    domain_rows = (await db.execute(domain_stmt)).all()
    domain_distribution = [{"domain": r[0], "count": r[1]} for r in domain_rows]

    # Stage breakdown
    stage_stmt = select(Innovation.development_stage, func.count(Innovation.id)).group_by(Innovation.development_stage)
    stage_rows = (await db.execute(stage_stmt)).all()
    stage_distribution = [{"stage": r[0], "count": r[1]} for r in stage_rows]

    # Recent Audit Activity
    audit_stmt = select(AuditLog).order_by(AuditLog.created_at.desc()).limit(8)
    audit_rows = (await db.execute(audit_stmt)).scalars().all()
    recent_activity = [
        {
            "id": a.id,
            "action": a.action,
            "resource_type": a.resource_type,
            "resource_id": a.resource_id,
            "details": a.details,
            "timestamp": a.created_at.isoformat(),
        }
        for a in audit_rows
    ]

    # Verification Breakdown for Innovations
    inv_verif_stmt = select(Innovation.verification_status, func.count(Innovation.id)).group_by(Innovation.verification_status)
    inv_verif_rows = (await db.execute(inv_verif_stmt)).all()
    inv_verification = {r[0]: r[1] for r in inv_verif_rows}

    # Verification Breakdown for Patents
    pat_verif_stmt = select(PatentRecord.verification_status, func.count(PatentRecord.id)).group_by(PatentRecord.verification_status)
    pat_verif_rows = (await db.execute(pat_verif_stmt)).all()
    pat_verification = {r[0]: r[1] for r in pat_verif_rows}

    # Verification Breakdown for Projects
    proj_verif_stmt = select(ResearchProject.verification_status, func.count(ResearchProject.id)).group_by(ResearchProject.verification_status)
    proj_verif_rows = (await db.execute(proj_verif_stmt)).all()
    proj_verification = {r[0]: r[1] for r in proj_verif_rows}

    # Recent Innovations
    recent_inv_stmt = select(Innovation).order_by(Innovation.created_at.desc()).limit(6)
    recent_invs = (await db.execute(recent_inv_stmt)).scalars().all()
    innovations_list = [
        {
            "id": inv.id,
            "project_code": inv.project_code,
            "title": inv.title,
            "domain": inv.domain,
            "development_stage": inv.development_stage,
            "prototype_status": inv.prototype_status,
            "verification_status": inv.verification_status,
            "patent_status": inv.patent_status,
        }
        for inv in recent_invs
    ]

    # Recent Patents
    recent_pat_stmt = select(PatentRecord).order_by(PatentRecord.created_at.desc()).limit(6)
    recent_pats = (await db.execute(recent_pat_stmt)).scalars().all()
    patents_list = [
        {
            "id": pat.id,
            "application_number": pat.application_number,
            "title": pat.title,
            "patent_type": pat.patent_type,
            "legal_status": pat.legal_status,
            "publication_date": pat.publication_date,
            "journal_issue": pat.journal_issue,
            "verification_status": pat.verification_status,
        }
        for pat in recent_pats
    ]

    # Active Projects List
    projects_stmt = select(ResearchProject).order_by(ResearchProject.created_at.desc()).limit(6)
    projects_res = (await db.execute(projects_stmt)).scalars().all()
    projects_list = [
        {
            "id": p.id,
            "project_code": p.project_code,
            "title": p.title,
            "domain": p.domain,
            "progress_pct": p.progress_pct,
            "status": p.status,
            "lead_researcher": p.lead_researcher,
            "verification_status": p.verification_status,
        }
        for p in projects_res
    ]

    return {
        "metrics": {
            "total_innovations": inv_count,
            "verified_innovations": inv_verification.get("Verified", 0),
            "pending_innovations": inv_verification.get("Pending verification", 0),
            "draft_innovations": inv_verification.get("Draft", 0),
            "total_patents": total_patents,
            "published_patents": published_patents,
            "provisional_patents": provisional_patents,
            "verified_patents": pat_verification.get("Verified", 0),
            "total_projects": total_projects,
            "active_projects": active_projects,
            "verified_projects": proj_verification.get("Verified", 0),
            "total_experiments": total_experiments,
            "concluded_experiments": concluded_experiments,
            "total_enquiries": total_enquiries,
            "pending_enquiries": pending_enquiries,
            "approved_enquiries": approved_enquiries,
            "total_documents": total_documents,
        },
        "verification_breakdown": {
            "innovations": inv_verification,
            "patents": pat_verification,
            "projects": proj_verification,
        },
        "recent_innovations": innovations_list,
        "recent_patents": patents_list,
        "active_projects": projects_list,
        "domain_distribution": domain_distribution,
        "stage_distribution": stage_distribution,
        "recent_activity": recent_activity,
        "user_profile": {
            "full_name": current_user.full_name,
            "role": current_user.role,
            "email": current_user.email,
            "organization": current_user.organization,
        },
    }


@router.get("/search")
async def global_platform_search(
    q: str = "",
    db: AsyncSession = Depends(get_db),
    current_user: BMIRUser = Depends(get_current_bmir_user),
):
    """Real multi-entity search across innovations, patents, projects, and documents."""
    query_str = f"%{q.strip()}%"
    results = []

    if not q.strip():
        return {"query": q, "total": 0, "results": []}

    # Search Innovations
    inv_stmt = select(Innovation).where(
        (Innovation.title.ilike(query_str)) |
        (Innovation.project_code.ilike(query_str)) |
        (Innovation.domain.ilike(query_str)) |
        (Innovation.summary.ilike(query_str))
    ).limit(8)
    inv_rows = (await db.execute(inv_stmt)).scalars().all()
    for inv in inv_rows:
        results.append({
            "type": "Innovation",
            "id": inv.id,
            "code": inv.project_code,
            "title": inv.title,
            "category": inv.domain,
            "status": inv.development_stage,
            "verification_status": inv.verification_status,
        })

    # Search Patents
    pat_stmt = select(PatentRecord).where(
        (PatentRecord.title.ilike(query_str)) |
        (PatentRecord.application_number.ilike(query_str))
    ).limit(8)
    pat_rows = (await db.execute(pat_stmt)).scalars().all()
    for pat in pat_rows:
        results.append({
            "type": "Patent Record",
            "id": pat.id,
            "code": pat.application_number,
            "title": pat.title,
            "category": pat.patent_type,
            "status": pat.legal_status,
            "verification_status": pat.verification_status,
        })

    # Search Projects
    proj_stmt = select(ResearchProject).where(
        (ResearchProject.title.ilike(query_str)) |
        (ResearchProject.project_code.ilike(query_str)) |
        (ResearchProject.domain.ilike(query_str))
    ).limit(8)
    proj_rows = (await db.execute(proj_stmt)).scalars().all()
    for prj in proj_rows:
        results.append({
            "type": "Research Project",
            "id": prj.id,
            "code": prj.project_code,
            "title": prj.title,
            "category": prj.domain,
            "status": prj.status,
            "verification_status": prj.verification_status,
        })

    # Search Knowledge Documents
    doc_stmt = select(KnowledgeDocument).where(
        (KnowledgeDocument.title.ilike(query_str)) |
        (KnowledgeDocument.domain.ilike(query_str)) |
        (KnowledgeDocument.keywords.ilike(query_str))
    ).limit(8)
    doc_rows = (await db.execute(doc_stmt)).scalars().all()
    for doc in doc_rows:
        results.append({
            "type": "Knowledge Document",
            "id": doc.id,
            "code": doc.doc_type,
            "title": doc.title,
            "category": doc.domain,
            "status": "Available",
            "verification_status": doc.verification_status,
        })

    return {"query": q, "total": len(results), "results": results}


@router.get("/notifications")
async def get_platform_notifications(
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    current_user: BMIRUser = Depends(get_current_bmir_user),
):
    """Retrieve real-time institutional notifications and pending review items."""
    notifications = []

    # 1. Query persistent notifications
    stmt = select(BMIRNotification).order_by(BMIRNotification.created_at.desc()).limit(20)
    if category and category != "all":
        stmt = stmt.where(BMIRNotification.category == category)
    db_notifs = (await db.execute(stmt)).scalars().all()

    for n in db_notifs:
        notifications.append({
            "id": n.id,
            "category": n.category,
            "title": n.title,
            "detail": n.content,
            "link_url": n.link_url,
            "timestamp": n.created_at.isoformat(),
            "unread": not n.is_read,
        })

    # If empty, add live collaboration enquiry items
    if not notifications:
        enq_stmt = select(CollaborationEnquiry).where(CollaborationEnquiry.status == "Pending").limit(4)
        pending_enqs = (await db.execute(enq_stmt)).scalars().all()
        for enq in pending_enqs:
            notifications.append({
                "id": f"enq-{enq.id}",
                "category": "collaboration",
                "title": f"New Proposal: {enq.full_name}",
                "detail": f"{enq.organization} requested {enq.pathway}",
                "link_url": "collaboration_mgmt",
                "timestamp": enq.created_at.isoformat(),
                "unread": True,
            })

    unread_count = len([n for n in notifications if n["unread"]])
    return {"notifications": notifications, "unread_count": unread_count}


@router.put("/notifications/{id}/read")
async def mark_notification_read(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: BMIRUser = Depends(get_current_bmir_user),
):
    notif = await db.get(BMIRNotification, id)
    if notif:
        notif.is_read = True
        await db.commit()
    return {"message": "Notification marked as read", "id": id}


@router.post("/notifications/mark-all-read")
async def mark_all_notifications_read(
    db: AsyncSession = Depends(get_db),
    current_user: BMIRUser = Depends(get_current_bmir_user),
):
    await db.execute(update(BMIRNotification).values(is_read=True))
    await db.commit()
    return {"message": "All notifications marked as read"}

