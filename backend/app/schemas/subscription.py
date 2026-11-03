from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field


class TierLimitInfo(BaseModel):
    tier: str
    name: str
    price_usd_monthly: float
    max_resumes_per_month: int
    max_ai_analyses_per_month: int
    max_interviews_per_month: int
    max_simulations_per_month: int
    included_features: List[str]


class UserSubscriptionResponse(BaseModel):
    id: str
    user_id: str
    tier: str
    status: str
    current_period_start: datetime
    current_period_end: Optional[datetime] = None
    cancel_at_period_end: bool

    model_config = ConfigDict(from_attributes=True)


class UsageQuotaResponse(BaseModel):
    month_period: str
    tier: str
    resumes_uploaded: int
    max_resumes: int
    ai_analyses_run: int
    max_ai_analyses: int
    interviews_conducted: int
    max_interviews: int
    simulations_run: int
    max_simulations: int


class UpgradeSubscriptionRequest(BaseModel):
    target_tier: str = Field(..., pattern="^(free|pro|professional)$")
    payment_method_id: Optional[str] = "pm_default_verified"


class EntitlementCheckResponse(BaseModel):
    feature: str
    allowed: bool
    current_tier: str
    required_tier: Optional[str] = None
    reason: Optional[str] = None
