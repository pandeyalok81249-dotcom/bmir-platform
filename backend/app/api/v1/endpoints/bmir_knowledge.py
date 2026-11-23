import math
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File, Form
from pydantic import BaseModel
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_bmir_user, get_optional_bmir_user, require_bmir_role
from app.core.database import get_db
from app.models.bmir import BMIRUser, KnowledgeDocument, AuditLog

router = APIRouter(prefix="/bmir/knowledge", tags=["bmir-knowledge"])


class DocumentUploadPayload(BaseModel):
    title: str
    doc_type: str = "Research Paper"
    domain: str
    abstract: Optional[str] = None
    content: str
    keywords: Optional[str] = None
    authors: Optional[str] = None
    source_url: Optional[str] = None
    doi: Optional[str] = None
    is_confidential: bool = False


def pseudo_embedding(text: str) -> List[float]:
    """
    Deterministic pseudo-embedding vector for offline / self-contained vector search
    when external embedding API is unconfigured. Generates a normalized 8-dim vector.
    """
    seeds = [hash(text[i::8]) for i in range(8)]
    magnitude = math.sqrt(sum(s * s for s in seeds)) or 1.0
    return [round(s / magnitude, 4) for s in seeds]


def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    if not v1 or not v2 or len(v1) != len(v2):
        return 0.0
    dot = sum(a * b for a, b in zip(v1, v2))
    mag1 = math.sqrt(sum(a * a for a in v1))
    mag2 = math.sqrt(sum(b * b for b in v2))
    return dot / (mag1 * mag2) if mag1 and mag2 else 0.0


@router.get("")
async def search_knowledge_base(
    q: Optional[str] = Query(None, description="Search query"),
    domain: Optional[str] = Query(None, description="Filter domain"),
    doc_type: Optional[str] = Query(None, description="Filter doc type"),
    db: AsyncSession = Depends(get_db),
    current_user: Optional[BMIRUser] = Depends(get_optional_bmir_user),
):
    stmt = select(KnowledgeDocument)
    if not current_user or current_user.role in ["viewer", "external_collaborator"]:
        stmt = stmt.where(KnowledgeDocument.is_confidential == False)

    if domain:
        stmt = stmt.where(func.lower(KnowledgeDocument.domain) == domain.lower())

    if doc_type:
        stmt = stmt.where(func.lower(KnowledgeDocument.doc_type) == doc_type.lower())

    if q:
        search_pattern = f"%{q.lower()}%"
        stmt = stmt.where(
            or_(
                func.lower(KnowledgeDocument.title).like(search_pattern),
                func.lower(KnowledgeDocument.abstract).like(search_pattern),
                func.lower(KnowledgeDocument.keywords).like(search_pattern),
                func.lower(KnowledgeDocument.content).like(search_pattern),
            )
        )

    stmt = stmt.order_by(KnowledgeDocument.created_at.desc())
    result = await db.execute(stmt)
    docs = result.scalars().all()

    # If query provided, compute semantic similarity ranking
    ranked = []
    q_vec = pseudo_embedding(q) if q else None

    for d in docs:
        sim = cosine_similarity(q_vec, d.embedding_vector) if (q_vec and d.embedding_vector) else 0.5
        ranked.append({
            "id": d.id,
            "title": d.title,
            "doc_type": d.doc_type,
            "domain": d.domain,
            "abstract": d.abstract,
            "keywords": d.keywords,
            "authors": d.authors,
            "source_url": d.source_url,
            "doi": d.doi,
            "is_confidential": d.is_confidential,
            "similarity_score": round(sim, 3),
            "created_at": d.created_at.isoformat(),
        })

    if q:
        ranked.sort(key=lambda x: x["similarity_score"], reverse=True)

    return ranked


@router.get("/{id}")
async def get_document_content(
    id: str,
    db: AsyncSession = Depends(get_db),
    current_user: Optional[BMIRUser] = Depends(get_optional_bmir_user),
):
    result = await db.execute(select(KnowledgeDocument).where(KnowledgeDocument.id == id))
    doc = result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")

    if doc.is_confidential and (not current_user or current_user.role in ["viewer", "external_collaborator"]):
        raise HTTPException(status_code=403, detail="Confidential document access restricted")

    return {
        "id": doc.id,
        "title": doc.title,
        "doc_type": doc.doc_type,
        "domain": doc.domain,
        "abstract": doc.abstract,
        "content": doc.content,
        "keywords": doc.keywords,
        "authors": doc.authors,
        "source_url": doc.source_url,
        "doi": doc.doi,
        "is_confidential": doc.is_confidential,
        "created_at": doc.created_at.isoformat(),
    }


@router.post("", dependencies=[Depends(require_bmir_role(["super_admin", "founder", "research_scientist", "research_engineer"]))])
async def upload_document(
    payload: DocumentUploadPayload,
    db: AsyncSession = Depends(get_db),
    current_user: BMIRUser = Depends(get_current_bmir_user),
):
    vec = pseudo_embedding(f"{payload.title} {payload.abstract or ''} {payload.keywords or ''} {payload.content[:500]}")
    doc = KnowledgeDocument(
        title=payload.title,
        doc_type=payload.doc_type,
        domain=payload.domain,
        abstract=payload.abstract,
        content=payload.content,
        keywords=payload.keywords,
        authors=payload.authors,
        source_url=payload.source_url,
        doi=payload.doi,
        is_confidential=payload.is_confidential,
        uploaded_by_id=current_user.id,
        embedding_vector=vec,
    )
    db.add(doc)
    await db.flush()

    log = AuditLog(
        user_id=current_user.id,
        action="UPLOAD_KNOWLEDGE_DOCUMENT",
        resource_type="KnowledgeDocument",
        resource_id=doc.id,
        details={"title": doc.title, "domain": doc.domain},
    )
    db.add(log)
    await db.commit()
    return {"id": doc.id, "title": doc.title, "message": "Document indexed into BMIR RAG knowledge base successfully"}

