import asyncio
import hashlib
import json
from typing import List, Optional
from fastapi import APIRouter, BackgroundTasks, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.core.redis import JobQueueManager
from app.models.analysis import ResumeAnalysis
from app.models.profile import UserProfile
from app.models.resume import Resume, ResumeVersion
from app.models.user import User
from app.schemas.analysis import ResumeAnalysisResponse
from app.schemas.common import APIResponse
from app.schemas.evidence_graph import ResumeEvidenceGraphResponse
from app.schemas.resume import ResumeDetailResponse, ResumeResponse, ResumeVersionResponse
from app.services.document_parser import DocumentParser
from app.services.evidence_graph import EvidenceGraphService
from app.services.resume_analyzer import ResumeAnalyzerService
from app.services.storage_service import StorageService

router = APIRouter(prefix="/resumes", tags=["Resumes"])
storage_service = StorageService()
_evidence_service = EvidenceGraphService()


@router.post("/upload", response_model=APIResponse[ResumeDetailResponse])
async def upload_resume(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    title: Optional[str] = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Validate extension
    filename = file.filename or "resume.pdf"
    file_ext = filename.split(".")[-1].lower() if "." in filename else ""
    if file_ext not in ["pdf", "docx", "doc", "txt"]:
        raise HTTPException(
            status_code=400,
            detail="Unsupported format. Only PDF, DOCX, and TXT files are accepted.",
        )

    content = await file.read()
    file_size = len(content)

    # 10MB limit
    if file_size > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds the 10MB maximum limit.")

    # Magic byte MIME verification
    valid_format, format_err = DocumentParser.validate_document_content(content, file_ext)
    if not valid_format:
        raise HTTPException(status_code=422, detail=format_err)

    # Extract text
    try:
        extracted_text = DocumentParser.extract_text(content, file_ext)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Text extraction failed: {str(e)}")

    valid_quality, quality_err = DocumentParser.assess_extraction_quality(extracted_text)
    if not valid_quality:
        raise HTTPException(status_code=422, detail=quality_err)

    # Save to storage
    storage_key = storage_service.save_file(current_user.id, filename, content)

    # Create Resume record
    resume_title = title.strip() if title else filename
    resume = Resume(
        user_id=current_user.id,
        title=resume_title,
        original_filename=filename,
        file_storage_key=storage_key,
        file_type=file_ext,
        file_size_bytes=file_size,
        extracted_text=extracted_text,
        processing_status="parsed",
    )
    db.add(resume)
    await db.flush()

    # Create initial version
    sections = DocumentParser.segment_sections(extracted_text)
    content_hash = hashlib.sha256(extracted_text.encode("utf-8")).hexdigest()
    version = ResumeVersion(
        resume_id=resume.id,
        version_number=1,
        resume_content=sections,
        content_hash=content_hash,
    )
    db.add(version)
    await db.flush()

    # Create queued analysis record
    analysis = ResumeAnalysis(
        resume_id=resume.id,
        resume_version_id=version.id,
        analysis_type="full_audit",
        provider="pending",
        model="pending",
        status="queued",
        analysis_version="1.0",
    )
    db.add(analysis)
    await db.commit()
    await db.refresh(resume)
    await db.refresh(analysis)

    # Fetch user preferences
    profile_res = await db.execute(select(UserProfile).where(UserProfile.user_id == current_user.id))
    profile = profile_res.scalars().first()
    target_role = profile.target_role if profile else None
    career_stage = profile.career_stage if profile else None

    # Register initial job status in queue
    await JobQueueManager.set_job_status(
        job_id=analysis.id,
        status="queued",
        stage_description="Analysis job queued for processing...",
    )

    # Dispatch asynchronous background processing
    task = asyncio.create_task(
        ResumeAnalyzerService.process_analysis_job(
            analysis_id=analysis.id,
            resume_id=resume.id,
            user_id=current_user.id,
            target_role=target_role,
            career_stage=career_stage,
        )
    )
    JobQueueManager.register_async_task(analysis.id, task)

    detail_resp = ResumeDetailResponse(
        id=resume.id,
        user_id=resume.user_id,
        title=resume.title,
        original_filename=resume.original_filename,
        file_type=resume.file_type,
        file_size_bytes=resume.file_size_bytes,
        processing_status=resume.processing_status,
        latest_score=None,
        extracted_text=resume.extracted_text,
        versions=[ResumeVersionResponse.model_validate(version)],
        created_at=resume.created_at,
        updated_at=resume.updated_at,
    )

    return APIResponse(
        success=True,
        message="Resume uploaded successfully. Intelligence analysis job queued.",
        data=detail_resp,
    )


@router.get("", response_model=APIResponse[List[ResumeResponse]])
async def list_resumes(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Resume)
        .where(Resume.user_id == current_user.id)
        .order_by(desc(Resume.created_at))
    )
    resumes = result.scalars().all()

    output = []
    for r in resumes:
        a_res = await db.execute(
            select(ResumeAnalysis)
            .where(ResumeAnalysis.resume_id == r.id)
            .order_by(desc(ResumeAnalysis.created_at))
        )
        latest_analysis = a_res.scalars().first()
        score = latest_analysis.overall_score if latest_analysis else None

        resp = ResumeResponse(
            id=r.id,
            user_id=r.user_id,
            title=r.title,
            original_filename=r.original_filename,
            file_type=r.file_type,
            file_size_bytes=r.file_size_bytes,
            processing_status=r.processing_status,
            latest_score=score,
            created_at=r.created_at,
            updated_at=r.updated_at,
        )
        output.append(resp)

    return APIResponse(success=True, data=output)


@router.get("/{resume_id}", response_model=APIResponse[ResumeDetailResponse])
async def get_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == current_user.id)
    )
    resume = result.scalars().first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")

    v_res = await db.execute(
        select(ResumeVersion)
        .where(ResumeVersion.resume_id == resume.id)
        .order_by(desc(ResumeVersion.version_number))
    )
    versions = v_res.scalars().all()

    a_res = await db.execute(
        select(ResumeAnalysis)
        .where(ResumeAnalysis.resume_id == resume.id)
        .order_by(desc(ResumeAnalysis.created_at))
    )
    latest_analysis = a_res.scalars().first()

    return APIResponse(
        success=True,
        data=ResumeDetailResponse(
            id=resume.id,
            user_id=resume.user_id,
            title=resume.title,
            original_filename=resume.original_filename,
            file_type=resume.file_type,
            file_size_bytes=resume.file_size_bytes,
            processing_status=resume.processing_status,
            latest_score=latest_analysis.overall_score if latest_analysis else None,
            extracted_text=resume.extracted_text,
            versions=[ResumeVersionResponse.model_validate(v) for v in versions],
            created_at=resume.created_at,
            updated_at=resume.updated_at,
        ),
    )


@router.delete("/{resume_id}", response_model=APIResponse[dict])
async def delete_resume(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == current_user.id)
    )
    resume = result.scalars().first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")

    storage_service.delete_file(resume.file_storage_key)
    await db.delete(resume)
    await db.commit()

    return APIResponse(success=True, message="Resume deleted successfully.", data={})


@router.post("/{resume_id}/analyze", response_model=APIResponse[dict])
async def trigger_analysis(
    resume_id: str,
    target_role: Optional[str] = None,
    preferred_provider: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Resume).where(Resume.id == resume_id, Resume.user_id == current_user.id)
    )
    resume = result.scalars().first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")

    v_res = await db.execute(
        select(ResumeVersion)
        .where(ResumeVersion.resume_id == resume.id)
        .order_by(desc(ResumeVersion.version_number))
    )
    latest_version = v_res.scalars().first()

    profile_res = await db.execute(select(UserProfile).where(UserProfile.user_id == current_user.id))
    profile = profile_res.scalars().first()
    role = target_role or (profile.target_role if profile else None)
    stage = profile.career_stage if profile else None

    # Create new analysis row
    analysis = ResumeAnalysis(
        resume_id=resume.id,
        resume_version_id=latest_version.id if latest_version else None,
        analysis_type="full_audit",
        provider="pending",
        model="pending",
        status="queued",
        analysis_version="1.0",
    )
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)

    await JobQueueManager.set_job_status(
        job_id=analysis.id,
        status="queued",
        stage_description="Analysis job queued for processing...",
    )

    # Launch async background task
    task = asyncio.create_task(
        ResumeAnalyzerService.process_analysis_job(
            analysis_id=analysis.id,
            resume_id=resume.id,
            user_id=current_user.id,
            target_role=role,
            career_stage=stage,
            preferred_provider=preferred_provider,
        )
    )
    JobQueueManager.register_async_task(analysis.id, task)

    return APIResponse(
        success=True,
        message="Analysis job enqueued successfully.",
        data={
            "analysis_id": analysis.id,
            "status": "queued",
            "resume_id": resume.id,
        },
    )


@router.get("/{id}/evidence-graph", response_model=APIResponse[ResumeEvidenceGraphResponse])
async def get_resume_evidence_graph(
    id: str,
    target_role: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    resume = await db.get(Resume, id)
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found")
    if resume.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to access this resume")

    v_res = await db.execute(
        select(ResumeVersion)
        .where(ResumeVersion.resume_id == resume.id)
        .order_by(desc(ResumeVersion.version_number))
    )
    latest_version = v_res.scalars().first()
    text = resume.extracted_text or ""
    if not text and latest_version and isinstance(latest_version.resume_content, dict):
        text = json.dumps(latest_version.resume_content)

    graph_res = _evidence_service.build_graph(
        resume_id=resume.id,
        resume_text=text,
        target_role=target_role,
    )
    return APIResponse(data=graph_res)
