"""
Pydantic schemas for Job Market Intelligence Engine.
Ensures strict data attribution, transparent provenance, and no fabricated statistics.
"""

from datetime import datetime, timezone
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


MARKET_DATA_DISCLAIMER = (
    "Market statistics represent observational aggregate samples compiled from authorized public datasets "
    "(O*NET 28.0, Bureau of Labor Statistics, and standardized industry aggregations). "
    "They do not constitute real-time live scrapers, individual hiring guarantees, or certified salary promises."
)


class MarketDataProvenance(BaseModel):
    source_name: str = "O*NET 28.0 Database & Compliant Tech Job Cohort Aggregate"
    collection_timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    sample_size: int = Field(..., description="Number of verified job listings or labor survey respondents analyzed")
    geographic_scope: str = Field(..., description="Geographic bounding (e.g. US National, Remote)")
    time_period: str = Field(..., description="Collection timeframe (e.g. 2024 Q1 - 2024 Q3)")
    data_limitations: List[str] = Field(
        default_factory=lambda: [
            "Sample covers formal publicly posted engineering and product job descriptions",
            "Excludes non-standard internal promotions and private recruitment contracts",
            "Skill mentions reflect stated requirements, not actual on-the-job usage depth"
        ]
    )
    disclaimer: str = MARKET_DATA_DISCLAIMER


class SkillDemandStat(BaseModel):
    skill_name: str
    frequency_percentage: float = Field(..., description="Percentage of job postings requiring this skill (0.0 to 100.0)")
    trend: str = Field(..., description="'growing', 'stable', or 'declining'")
    growth_rate_yoy: float = Field(..., description="Year-over-year mention growth percentage (+% / -%)")
    category: str = Field(..., description="'language', 'framework', 'database', 'cloud', 'architecture', 'methodology'")
    importance_tier: str = Field(..., description="'critical', 'preferred', 'emerging'")


class RoleMarketOverview(BaseModel):
    role_title: str
    normalized_soc_code: Optional[str] = None
    demand_index: float = Field(..., description="Relative hiring volume index (0 to 100)")
    experience_distribution: Dict[str, float] = Field(
        ...,
        description="Share of job postings by experience tier, e.g. {'0-2 yrs': 12.0, '3-5 yrs': 55.0, '6+ yrs': 33.0}"
    )
    top_demanded_skills: List[SkillDemandStat]
    common_certifications: List[str]
    provenance: MarketDataProvenance


class LocationComparisonStat(BaseModel):
    location: str
    role_title: str
    relative_job_volume_index: float
    remote_eligible_percentage: float
    top_differentiating_skills: List[str]
    provenance: MarketDataProvenance


class MarketGapAnalysisRequest(BaseModel):
    target_role: str
    user_skills: List[str]
    user_experience_years: float = 0.0


class MarketGapAnalysisResult(BaseModel):
    role_title: str
    market_match_score: float = Field(..., description="0 to 100 alignment against top demanded market skills")
    matching_skills: List[str]
    missing_critical_skills: List[SkillDemandStat]
    missing_recommended_skills: List[SkillDemandStat]
    experience_fit_verdict: str
    user_experience_years: float
    market_median_experience_years: float
    actionable_recommendations: List[str]
    provenance: MarketDataProvenance
