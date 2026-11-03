from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.application import Application
from app.models.user import User
from app.schemas.application import (
    ApplicationCreate,
    ApplicationResponse,
    ApplicationUpdate,
)
from app.schemas.common import APIResponse

router = APIRouter(prefix="/applications", tags=["Application Tracker"])


@router.post("", response_model=APIResponse[ApplicationResponse])
async def create_application(
    app_in: ApplicationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    application = Application(
        user_id=current_user.id,
        company=app_in.company,
        position=app_in.position,
        job_description_id=app_in.job_description_id,
        resume_version_id=app_in.resume_version_id,
        status=app_in.status,
        application_date=app_in.application_date,
        interview_dates=app_in.interview_dates,
        notes=app_in.notes,
        follow_up_date=app_in.follow_up_date,
    )
    db.add(application)
    await db.commit()
    await db.refresh(application)

    return APIResponse(
        success=True,
        message="Application logged in tracker.",
        data=ApplicationResponse.model_validate(application),
    )


@router.get("", response_model=APIResponse[List[ApplicationResponse]])
async def list_applications(
    status_filter: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(Application).where(Application.user_id == current_user.id)
    if status_filter:
        query = query.where(Application.status == status_filter)
    query = query.order_by(desc(Application.updated_at))

    result = await db.execute(query)
    apps = result.scalars().all()
    return APIResponse(
        success=True,
        data=[ApplicationResponse.model_validate(a) for a in apps],
    )


@router.patch("/{application_id}", response_model=APIResponse[ApplicationResponse])
async def update_application(
    application_id: str,
    update_in: ApplicationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Application).where(
            Application.id == application_id,
            Application.user_id == current_user.id,
        )
    )
    application = result.scalars().first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found.")

    update_dict = update_in.model_dump(exclude_unset=True)
    for field, value in update_dict.items():
        setattr(application, field, value)

    await db.commit()
    await db.refresh(application)

    return APIResponse(
        success=True,
        message="Application updated successfully.",
        data=ApplicationResponse.model_validate(application),
    )


@router.delete("/{application_id}", response_model=APIResponse[dict])
async def delete_application(
    application_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Application).where(
            Application.id == application_id,
            Application.user_id == current_user.id,
        )
    )
    application = result.scalars().first()
    if not application:
        raise HTTPException(status_code=404, detail="Application not found.")

    await db.delete(application)
    await db.commit()
    return APIResponse(success=True, message="Application removed from tracker.", data={})

