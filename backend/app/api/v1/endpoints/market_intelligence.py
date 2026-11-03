"""
API Endpoints for Job Market Intelligence.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, status

from app.api.deps import get_current_user
from app.models.user import User
from app.schemas.common import APIResponse
from app.schemas.market_intelligence import (
    RoleMarketOverview,
    LocationComparisonStat,
    MarketGapAnalysisRequest,
    MarketGapAnalysisResult,
    SkillDemandStat,
)
from app.services.market_intelligence import JobMarketIntelligenceService


router = APIRouter()
_market_service = JobMarketIntelligenceService()


@router.get(
    "/role-trends",
    response_model=APIResponse[RoleMarketOverview],
    summary="Get market demand, experience distribution, and top skills for a role",
)
async def get_role_trends(
    role: str = Query("Senior Backend Engineer", description="Target role title to inspect"),
    current_user: User = Depends(get_current_user),
):
    overview = _market_service.get_role_market_overview(role)
    return APIResponse(data=overview)


@router.get(
    "/location-comparison",
    response_model=APIResponse[List[LocationComparisonStat]],
    summary="Compare demand volume, remote eligibility, and local skill nuances across tech hubs",
)
async def get_location_comparison(
    role: str = Query("Senior Backend Engineer", description="Target role title"),
    current_user: User = Depends(get_current_user),
):
    stats = _market_service.compare_locations(role)
    return APIResponse(data=stats)


@router.post(
    "/gap-analysis",
    response_model=APIResponse[MarketGapAnalysisResult],
    summary="Evaluate user skills and experience against verified market benchmarks",
)
async def analyze_market_gap(
    request: MarketGapAnalysisRequest,
    current_user: User = Depends(get_current_user),
):
    result = _market_service.analyze_market_fit(
        target_role=request.target_role,
        user_skills=request.user_skills,
        user_experience_years=request.user_experience_years,
    )
    return APIResponse(data=result)
