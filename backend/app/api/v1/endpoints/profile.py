from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.profile import UserProfile
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.profile import ProfileResponse, ProfileUpdate

router = APIRouter(prefix="/profile", tags=["Profile"])


@router.get("", response_model=APIResponse[ProfileResponse])
async def get_profile(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == current_user.id))
    profile = result.scalars().first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found.")

    return APIResponse(success=True, data=ProfileResponse.model_validate(profile))


@router.patch("", response_model=APIResponse[ProfileResponse])
async def update_profile(
    profile_in: ProfileUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(UserProfile).where(UserProfile.user_id == current_user.id))
    profile = result.scalars().first()
    if not profile:
        profile = UserProfile(user_id=current_user.id, full_name=profile_in.full_name or "User")
        db.add(profile)

    update_data = profile_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if field == "education" and value is not None:
            # Convert models to dicts if needed
            setattr(profile, field, [e.model_dump() if hasattr(e, "model_dump") else e for e in value])
        else:
            setattr(profile, field, value)

    await db.commit()
    await db.refresh(profile)

    return APIResponse(
        success=True,
        message="Profile updated successfully.",
        data=ProfileResponse.model_validate(profile),
    )


@router.delete("", response_model=APIResponse[dict])
async def delete_account(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Hard delete user cascades to all resumes, analyses, applications, roadmaps
    await db.delete(current_user)
    await db.commit()
    return APIResponse(
        success=True,
        message="Account and all associated intelligence data permanently deleted.",
        data={},
    )

