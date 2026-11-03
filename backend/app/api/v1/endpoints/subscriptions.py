from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.subscription import (
    EntitlementCheckResponse,
    TierLimitInfo,
    UpgradeSubscriptionRequest,
    UsageQuotaResponse,
    UserSubscriptionResponse,
)
from app.services.entitlement_service import entitlement_service

router = APIRouter(prefix="/subscriptions", tags=["Subscriptions & Entitlements"])


@router.get("/tiers", response_model=APIResponse[List[TierLimitInfo]])
async def get_subscription_tiers():
    tiers = entitlement_service.get_all_tiers()
    return APIResponse(success=True, data=tiers)


@router.get("/me", response_model=APIResponse[UserSubscriptionResponse])
async def get_my_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    sub = await entitlement_service.get_or_create_subscription(db, current_user.id)
    return APIResponse(
        success=True,
        data=UserSubscriptionResponse.model_validate(sub),
    )


@router.get("/usage", response_model=APIResponse[UsageQuotaResponse])
async def get_my_usage_quota(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    usage = await entitlement_service.get_usage_overview(db, current_user.id)
    return APIResponse(success=True, data=usage)


@router.get("/check/{feature}", response_model=APIResponse[EntitlementCheckResponse])
async def check_feature_entitlement(
    feature: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    check_result = await entitlement_service.check_feature(db, current_user.id, feature)
    return APIResponse(success=True, data=check_result)


@router.post("/upgrade", response_model=APIResponse[UserSubscriptionResponse])
async def upgrade_subscription(
    req: UpgradeSubscriptionRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    sub = await entitlement_service.upgrade_tier(db, current_user.id, req.target_tier)
    return APIResponse(
        success=True,
        message=f"Successfully transitioned to {req.target_tier.capitalize()} tier.",
        data=UserSubscriptionResponse.model_validate(sub),
    )


@router.post("/cancel", response_model=APIResponse[UserSubscriptionResponse])
async def cancel_subscription(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    sub = await entitlement_service.cancel_subscription(db, current_user.id)
    return APIResponse(
        success=True,
        message="Subscription set to cancel at the end of the current billing cycle.",
        data=UserSubscriptionResponse.model_validate(sub),
    )
