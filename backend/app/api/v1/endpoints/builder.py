from typing import Any, Dict, Optional
from fastapi import APIRouter, Depends, HTTPException, Response
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.factory import AIFactory
from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.resume import Resume, ResumeVersion
from app.models.user import User
from app.schemas.common import APIResponse
from app.services.pdf_service import PDFGeneratorService

router = APIRouter(prefix="/resume-builder", tags=["Resume Builder"])


class BulletImprovementRequest(BaseModel):
    bullet_text: str = Field(..., min_length=5)
    target_role: Optional[str] = None


class SummaryGenerationRequest(BaseModel):
    target_role: str
    existing_skills: list[str] = []
    experience_summary: str = ""


class PDFExportRequest(BaseModel):
    resume_id: Optional[str] = None
    resume_content: Dict[str, Any]
    template_name: str = "professional"  # professional, minimal, technical


@router.post("/improve-bullet", response_model=APIResponse[dict])
async def improve_bullet(
    req: BulletImprovementRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        provider = AIFactory.get_provider()
        res = await provider.improve_bullet(req.bullet_text, req.target_role)
        return APIResponse(success=True, data=res.content)
    except Exception as e:
        # Fallback deterministic rewrite
        original = req.bullet_text.strip()
        improved = f"Led and implemented {original[0].lower() + original[1:] if len(original) > 1 else original}, optimizing execution and ensuring architectural maintainability."
        return APIResponse(
            success=True,
            data={
                "original": req.bullet_text,
                "improved": improved,
                "action_verb_used": "Led / Implemented",
                "rationale": "Transformed passive phrasing into strong action verb orientation.",
                "missing_metric_prompt": "Consider adding concrete figures (e.g. latency reduced, users served, or scale handled) if available.",
            },
        )


@router.post("/export-pdf")
async def export_pdf(
    req: PDFExportRequest,
    current_user: User = Depends(get_current_user),
):
    try:
        pdf_bytes = PDFGeneratorService.generate_resume_pdf(
            resume_content=req.resume_content,
            template_name=req.template_name,
        )
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f'attachment; filename="resume_{req.template_name}.pdf"'
            },
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF generation failed: {str(e)}")

