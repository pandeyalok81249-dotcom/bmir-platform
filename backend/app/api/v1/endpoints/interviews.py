import uuid
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm.attributes import flag_modified

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.interview import InterviewSession
from app.models.resume import Resume, ResumeVersion
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.interview import (
    FollowUpQuestionRequest,
    FollowUpQuestionResponse,
    InterviewAnswerEvaluateRequest,
    InterviewAnswerEvaluation,
    InterviewGenerateRequest,
    InterviewQuestion,
    InterviewSessionResponse,
    InterviewSessionSummary,
)
from app.services.interview_intelligence import interview_intelligence_engine

router = APIRouter(prefix="/interviews", tags=["Interview Preparation"])


@router.post("/generate", response_model=APIResponse[InterviewSessionResponse])
async def generate_interview_session(
    req: InterviewGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    resume_context = ""
    # 1. By resume_version_id
    if req.resume_version_id:
        v_res = await db.execute(
            select(ResumeVersion)
            .join(Resume, ResumeVersion.resume_id == Resume.id)
            .where(ResumeVersion.id == req.resume_version_id, Resume.user_id == current_user.id)
        )
        version = v_res.scalars().first()
        if version and version.resume_content:
            resume_context = str(version.resume_content)
    
    # 2. By resume_id
    elif req.resume_id:
        r_res = await db.execute(
            select(Resume).where(Resume.id == req.resume_id, Resume.user_id == current_user.id)
        )
        resume = r_res.scalars().first()
        if resume:
            resume_context = resume.extracted_text or ""
            
    # 3. Fallback to latest resume
    if not resume_context:
        r_res = await db.execute(
            select(Resume).where(Resume.user_id == current_user.id).order_by(desc(Resume.created_at))
        )
        resume = r_res.scalars().first()
        if resume:
            resume_context = resume.extracted_text or ""

    questions = interview_intelligence_engine.generate_adaptive_questions(
        target_role=req.target_role,
        resume_text=resume_context,
        focus_areas=req.focus_areas,
        count=req.question_count,
    )

    questions_dict = [q.model_dump() for q in questions]

    session = InterviewSession(
        user_id=current_user.id,
        resume_version_id=req.resume_version_id,
        target_role=req.target_role,
        session_data={"questions": questions_dict, "answers": []},
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    return APIResponse(
        success=True,
        message="Adaptive interview session generated.",
        data=InterviewSessionResponse.model_validate(session),
    )


@router.post("/{session_id}/evaluate", response_model=APIResponse[InterviewAnswerEvaluation])
async def evaluate_interview_answer(
    session_id: str,
    req: InterviewAnswerEvaluateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(InterviewSession).where(
            InterviewSession.id == session_id,
            InterviewSession.user_id == current_user.id,
        )
    )
    session = result.scalars().first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview session not found.")

    # Find question category if available
    session_data = dict(session.session_data or {})
    questions = session_data.get("questions", [])
    cat = "behavioral"
    for q in questions:
        if q.get("id") == req.question_id:
            cat = q.get("category", "behavioral")
            break

    evaluation = interview_intelligence_engine.evaluate_star_answer(
        question=req.question_text,
        answer=req.user_answer,
        category=cat,
        target_role=session.target_role,
    )
    evaluation.question_id = req.question_id

    # Store in session answers list
    answers = session_data.get("answers", [])
    answers.append({
        "question_id": req.question_id,
        "category": cat,
        "question": req.question_text,
        "answer": req.user_answer,
        "evaluation": evaluation.model_dump(),
    })
    session_data["answers"] = answers
    session.session_data = session_data
    flag_modified(session, "session_data")
    await db.commit()

    return APIResponse(success=True, data=evaluation)


@router.post("/{session_id}/follow-up", response_model=APIResponse[FollowUpQuestionResponse])
async def generate_interview_follow_up(
    session_id: str,
    req: FollowUpQuestionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(InterviewSession).where(
            InterviewSession.id == session_id,
            InterviewSession.user_id == current_user.id,
        )
    )
    session = result.scalars().first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview session not found.")

    follow_up = interview_intelligence_engine.generate_follow_up_question(
        question=req.previous_question,
        answer=req.user_answer,
        weakest_area=req.weakest_area,
    )
    follow_up.parent_question_id = req.question_id

    return APIResponse(success=True, data=follow_up)


@router.get("/{session_id}/summary", response_model=APIResponse[InterviewSessionSummary])
async def get_interview_session_summary(
    session_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(InterviewSession).where(
            InterviewSession.id == session_id,
            InterviewSession.user_id == current_user.id,
        )
    )
    session = result.scalars().first()
    if not session:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Interview session not found.")

    session_data = session.session_data or {}
    answers = session_data.get("answers", [])
    summary = interview_intelligence_engine.summarize_session(
        session_id=session.id,
        target_role=session.target_role,
        answers=answers,
    )

    return APIResponse(success=True, data=summary)


@router.get("/history", response_model=APIResponse[List[InterviewSessionResponse]])
async def get_interview_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(InterviewSession)
        .where(InterviewSession.user_id == current_user.id)
        .order_by(desc(InterviewSession.created_at))
    )
    sessions = result.scalars().all()
    return APIResponse(
        success=True,
        data=[InterviewSessionResponse.model_validate(s) for s in sessions],
    )
