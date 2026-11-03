from typing import Any, Dict
from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings as app_settings
from app.core.database import get_db
from app.models.profile import UserProfile
from app.models.user import User
from app.schemas.common import APIResponse

router = APIRouter(prefix="/settings", tags=["Settings"])


class AIPreferencesUpdate(BaseModel):
    preferred_provider: str  # 'gemini' or 'openai'
    analysis_detail_level: str = "standard"  # brief, standard, deep_audit
    writing_tone: str = "professional"  # professional, executive, technical


@router.get("", response_model=APIResponse[Dict[str, Any]])
async def get_settings(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    p_res = await db.execute(select(UserProfile).where(UserProfile.user_id == current_user.id))
    profile = p_res.scalars().first()
    prefs = profile.preferences if profile else {}

    data = {
        "account": {
            "email": current_user.email,
            "email_verified": current_user.email_verified,
            "account_status": current_user.account_status,
        },
        "ai_preferences": {
            "preferred_provider": prefs.get("preferred_provider", app_settings.PREFERRED_AI_PROVIDER),
            "analysis_detail_level": prefs.get("analysis_detail_level", "standard"),
            "writing_tone": prefs.get("writing_tone", "professional"),
            "available_providers": {
                "gemini": {
                    "is_configured": bool(app_settings.GEMINI_API_KEY),
                    "default_model": app_settings.GEMINI_DEFAULT_MODEL,
                },
                "openai": {
                    "is_configured": bool(app_settings.OPENAI_API_KEY),
                    "default_model": app_settings.OPENAI_DEFAULT_MODEL,
                },
            },
        },
    }
    return APIResponse(success=True, data=data)


@router.patch("/ai-preferences", response_model=APIResponse[Dict[str, Any]])
async def update_ai_preferences(
    prefs_in: AIPreferencesUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    p_res = await db.execute(select(UserProfile).where(UserProfile.user_id == current_user.id))
    profile = p_res.scalars().first()
    if not profile:
        profile = UserProfile(user_id=current_user.id, full_name="User")
        db.add(profile)

    current_prefs = dict(profile.preferences or {})
    current_prefs.update(prefs_in.model_dump())
    profile.preferences = current_prefs

    await db.commit()
    await db.refresh(profile)

    return APIResponse(
        success=True,
        message="AI preferences updated successfully.",
        data=current_prefs,
    )

