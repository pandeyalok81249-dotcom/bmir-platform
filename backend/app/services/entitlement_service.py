from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.subscription import UserSubscription, UserUsageQuota
from app.schemas.subscription import (
    EntitlementCheckResponse,
    TierLimitInfo,
    UsageQuotaResponse,
)


TIERS_METADATA: Dict[str, TierLimitInfo] = {
    "free": TierLimitInfo(
        tier="free",
        name="Free Tier",
        price_usd_monthly=0.0,
        max_resumes_per_month=3,
        max_ai_analyses_per_month=5,
        max_interviews_per_month=3,
        max_simulations_per_month=2,
        included_features=[
            "basic_analysis",
            "basic_job_match",
            "standard_builder",
            "standard_interviews",
        ],
    ),
    "pro": TierLimitInfo(
        tier="pro",
        name="Professional Pro",
        price_usd_monthly=19.99,
        max_resumes_per_month=25,
        max_ai_analyses_per_month=100,
        max_interviews_per_month=50,
        max_simulations_per_month=30,
        included_features=[
            "basic_analysis",
            "basic_job_match",
            "standard_builder",
            "standard_interviews",
            "evidence_graph",
            "trajectory_simulator",
            "market_intelligence",
            "star_interview_evaluation",
            "pdf_generation",
            "version_evolution",
        ],
    ),
    "professional": TierLimitInfo(
        tier="professional",
        name="Executive & Enterprise",
        price_usd_monthly=49.99,
        max_resumes_per_month=999999,
        max_ai_analyses_per_month=999999,
        max_interviews_per_month=999999,
        max_simulations_per_month=999999,
        included_features=[
            "basic_analysis",
            "basic_job_match",
            "standard_builder",
            "standard_interviews",
            "evidence_graph",
            "trajectory_simulator",
            "market_intelligence",
            "star_interview_evaluation",
            "pdf_generation",
            "version_evolution",
            "collaboration_workspaces",
            "realtime_collab",
            "priority_support",
        ],
    ),
}


class EntitlementService:
    """
    Manages server-side subscription tiers, quota enforcement,
    usage tracking, and paywall/entitlement evaluation.
    """

    def get_tier_info(self, tier: str) -> TierLimitInfo:
        return TIERS_METADATA.get(tier.lower(), TIERS_METADATA["free"])

    def get_all_tiers(self) -> List[TierLimitInfo]:
        return list(TIERS_METADATA.values())

    async def get_or_create_subscription(
        self, db: AsyncSession, user_id: str
    ) -> UserSubscription:
        res = await db.execute(
            select(UserSubscription).where(UserSubscription.user_id == user_id)
        )
        sub = res.scalars().first()
        if not sub:
            now = datetime.now(timezone.utc)
            sub = UserSubscription(
                user_id=user_id,
                tier="free",
                status="active",
                current_period_start=now,
                current_period_end=now + timedelta(days=365),
                cancel_at_period_end=False,
            )
            db.add(sub)
            await db.commit()
            await db.refresh(sub)
        return sub

    async def get_or_create_quota(
        self, db: AsyncSession, user_id: str
    ) -> UserUsageQuota:
        current_month = datetime.now(timezone.utc).strftime("%Y-%m")
        res = await db.execute(
            select(UserUsageQuota).where(
                UserUsageQuota.user_id == user_id,
                UserUsageQuota.month_period == current_month,
            )
        )
        quota = res.scalars().first()
        if not quota:
            quota = UserUsageQuota(
                user_id=user_id,
                month_period=current_month,
                resumes_uploaded=0,
                ai_analyses_run=0,
                interviews_conducted=0,
                simulations_run=0,
            )
            db.add(quota)
            await db.commit()
            await db.refresh(quota)
        return quota

    async def get_usage_overview(
        self, db: AsyncSession, user_id: str
    ) -> UsageQuotaResponse:
        sub = await self.get_or_create_subscription(db, user_id)
        quota = await self.get_or_create_quota(db, user_id)
        limits = self.get_tier_info(sub.tier)

        return UsageQuotaResponse(
            month_period=quota.month_period,
            tier=sub.tier,
            resumes_uploaded=quota.resumes_uploaded,
            max_resumes=limits.max_resumes_per_month,
            ai_analyses_run=quota.ai_analyses_run,
            max_ai_analyses=limits.max_ai_analyses_per_month,
            interviews_conducted=quota.interviews_conducted,
            max_interviews=limits.max_interviews_per_month,
            simulations_run=quota.simulations_run,
            max_simulations=limits.max_simulations_per_month,
        )

    async def check_feature(
        self, db: AsyncSession, user_id: str, feature: str
    ) -> EntitlementCheckResponse:
        sub = await self.get_or_create_subscription(db, user_id)
        tier_info = self.get_tier_info(sub.tier)

        is_allowed = feature in tier_info.included_features
        if is_allowed:
            return EntitlementCheckResponse(
                feature=feature,
                allowed=True,
                current_tier=sub.tier,
            )

        # Find required tier
        required = "pro"
        for t_name, t_meta in TIERS_METADATA.items():
            if feature in t_meta.included_features:
                required = t_name
                break

        return EntitlementCheckResponse(
            feature=feature,
            allowed=False,
            current_tier=sub.tier,
            required_tier=required,
            reason=f"Feature '{feature}' requires an active {required.capitalize()} subscription tier.",
        )

    async def check_and_increment_quota(
        self, db: AsyncSession, user_id: str, metric: str
    ) -> Tuple[bool, int, int]:
        """
        Validates usage against tier quota limits.
        If allowed, increments count and commits.
        Returns (is_allowed, current_count, limit).
        """
        sub = await self.get_or_create_subscription(db, user_id)
        quota = await self.get_or_create_quota(db, user_id)
        limits = self.get_tier_info(sub.tier)

        metric_lower = metric.lower()
        if metric_lower in ["resumes", "resume"]:
            current = quota.resumes_uploaded
            max_limit = limits.max_resumes_per_month
            if current >= max_limit:
                return False, current, max_limit
            quota.resumes_uploaded += 1
        elif metric_lower in ["analyses", "analysis", "ai"]:
            current = quota.ai_analyses_run
            max_limit = limits.max_ai_analyses_per_month
            if current >= max_limit:
                return False, current, max_limit
            quota.ai_analyses_run += 1
        elif metric_lower in ["interviews", "interview"]:
            current = quota.interviews_conducted
            max_limit = limits.max_interviews_per_month
            if current >= max_limit:
                return False, current, max_limit
            quota.interviews_conducted += 1
        elif metric_lower in ["simulations", "simulation", "trajectory"]:
            current = quota.simulations_run
            max_limit = limits.max_simulations_per_month
            if current >= max_limit:
                return False, current, max_limit
            quota.simulations_run += 1
        else:
            return True, 0, 999999

        await db.commit()
        await db.refresh(quota)
        return True, current + 1, max_limit

    async def upgrade_tier(
        self, db: AsyncSession, user_id: str, new_tier: str
    ) -> UserSubscription:
        sub = await self.get_or_create_subscription(db, user_id)
        now = datetime.now(timezone.utc)
        sub.tier = new_tier.lower()
        sub.status = "active"
        sub.current_period_start = now
        sub.current_period_end = now + timedelta(days=30)
        sub.cancel_at_period_end = False

        await db.commit()
        await db.refresh(sub)
        return sub

    async def cancel_subscription(
        self, db: AsyncSession, user_id: str
    ) -> UserSubscription:
        sub = await self.get_or_create_subscription(db, user_id)
        sub.cancel_at_period_end = True
        await db.commit()
        await db.refresh(sub)
        return sub


entitlement_service = EntitlementService()
