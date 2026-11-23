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
    "/roles/{role}/analytics",
    summary="Get role analytics compatible with the web dashboard",
)
async def get_role_analytics(role: str):
    overview = _market_service.get_role_market_overview(role)
    top_skills = [
        {"skill": s.skill_name, "frequency_pct": round(s.frequency_percentage, 1)}
        for s in overview.top_demanded_skills
    ]
    role_norm = role.lower()
    if "senior" in role_norm or "lead" in role_norm:
        sal = {"p25_usd": 140000, "median_usd": 175000, "p75_usd": 210000, "p90_usd": 250000}
    elif "machine learning" in role_norm or "ml" in role_norm or "data" in role_norm:
        sal = {"p25_usd": 130000, "median_usd": 165000, "p75_usd": 200000, "p90_usd": 240000}
    elif "product" in role_norm:
        sal = {"p25_usd": 125000, "median_usd": 160000, "p75_usd": 195000, "p90_usd": 235000}
    else:
        sal = {"p25_usd": 115000, "median_usd": 145000, "p75_usd": 180000, "p90_usd": 215000}

    return APIResponse(
        success=True,
        data={
            "role": role,
            "metadata": {
                "sample_size": overview.provenance.sample_size,
                "geographic_scope": overview.provenance.geographic_scope,
                "time_period": overview.provenance.time_period,
            },
            "top_skills": top_skills,
            "salary_distribution": sal,
            "demand_index": overview.demand_index,
        }
    )


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
