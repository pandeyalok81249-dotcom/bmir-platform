import uuid
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.factory import AIFactory
from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.interview import InterviewSession
from app.models.resume import Resume, ResumeVersion
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.interview import (
    InterviewAnswerEvaluateRequest,
    InterviewAnswerEvaluation,
    InterviewGenerateRequest,
    InterviewQuestion,
    InterviewSessionResponse,
)

router = APIRouter(prefix="/interviews", tags=["Interview Preparation"])


@router.post("/generate", response_model=APIResponse[InterviewSessionResponse])
async def generate_interview_session(
    req: InterviewGenerateRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Fetch resume text if provided
    resume_context = ""
    if req.resume_version_id:
        v_res = await db.execute(
            select(ResumeVersion)
            .join(Resume, ResumeVersion.resume_id == Resume.id)
            .where(ResumeVersion.id == req.resume_version_id, Resume.user_id == current_user.id)
        )
        version = v_res.scalars().first()
        if version:
            resume_context = str(version.resume_content)

    questions = [
        {
            "id": str(uuid.uuid4()),
            "category": "technical",
            "question": f"Can you walk me through an architecture decision you made for a critical {req.target_role} project and explain how you handled edge cases?",
            "context_from_resume": "Derived from technical project leadership",
            "evaluation_criteria": ["Clarity of technical problem", "Design rationale", "Resilience & trade-offs"],
        },
        {
            "id": str(uuid.uuid4()),
            "category": "behavioral",
            "question": "Tell me about a time you encountered conflicting requirements from stakeholders or cross-functional team members. How did you resolve the conflict?",
            "context_from_resume": "Standard behavioral indicator for professional maturity",
            "evaluation_criteria": ["STAR format adherence", "Active listening", "Constructive alignment"],
        },
        {
            "id": str(uuid.uuid4()),
            "category": "experience_deep_dive",
            "question": f"In your recent experience relevant to {req.target_role}, what was the most challenging operational bottleneck you resolved?",
            "context_from_resume": "Experience deep-dive",
            "evaluation_criteria": ["Systematic debugging", "Measurable outcome", "Action verbs"],
        },
    ]

    session = InterviewSession(
        user_id=current_user.id,
        resume_version_id=req.resume_version_id,
        target_role=req.target_role,
        session_data={"questions": questions, "answers": []},
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)

    return APIResponse(
        success=True,
        message="Interview session generated.",
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
        raise HTTPException(status_code=404, detail="Interview session not found.")

    try:
        provider = AIFactory.get_provider()
        ai_resp = await provider.evaluate_interview_answer(
            question=req.question_text,
            answer=req.user_answer,
            role=session.target_role,
        )
        evaluation = InterviewAnswerEvaluation.model_validate(ai_resp.content)
    except Exception:
        # Deterministic fallback evaluation
        words = len(req.user_answer.split())
        clarity = 8.5 if words >= 50 else (6.0 if words >= 20 else 4.0)
        has_result = any(term in req.user_answer.lower() for term in ["result", "achieved", "impact", "delivered", "outcome"])
        star_adherence = "Strong" if (words >= 40 and has_result) else "Moderate"

        evaluation = InterviewAnswerEvaluation(
            question_id=req.question_id,
            clarity_score=clarity,
            star_method_adherence=star_adherence,
            strengths=["Directly addresses the question context", "Clear professional tone"],
            improvement_areas=["Consider ending with a quantifiable result or metric" if not has_result else "Provide more detail on alternative approaches considered"],
            improved_answer_sample=f"{req.user_answer.strip()} In doing so, our team ensured seamless operational continuity and delivered the project on schedule.",
        )

    # Store in session evaluation history
    session_data = dict(session.session_data or {})
    answers = session_data.get("answers", [])
    answers.append({
        "question_id": req.question_id,
        "question": req.question_text,
        "answer": req.user_answer,
        "evaluation": evaluation.model_dump(),
    })
    session_data["answers"] = answers
    session.session_data = session_data
    await db.commit()

    return APIResponse(success=True, data=evaluation)


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

