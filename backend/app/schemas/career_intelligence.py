from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class EvidenceGroundingItem(BaseModel):
    claim: str
    inference_type: str = Field(
        ...,
        description="'verified_fact' (extracted directly from user resume/profile) or 'ai_inference' (deduced by analytics engine)",
    )
    source_evidence: Optional[str] = Field(
        default=None,
        description="Exact quote, section reference, or document source backing the claim",
    )
    reasoning: str = Field(
        ...,
        description="Transparent analytical rationale explaining why this claim or recommendation was made",
    )


class CareerProgressionAssessment(BaseModel):
    current_level: str
    progression_velocity: str  # accelerated, steady, developing, transitioning
    years_of_experience: float
    title_trajectory: List[str] = []
    findings: List[EvidenceGroundingItem] = []


class SkillGapAnalysis(BaseModel):
    verified_skills: List[str] = []
    unverified_mentioned_skills: List[str] = []
    missing_critical_skills: List[str] = []
    missing_secondary_skills: List[str] = []
    findings: List[EvidenceGroundingItem] = []


class RoleSuitabilityAnalysis(BaseModel):
    target_role: str
    suitability_score: float  # 0 to 100
    strengths: List[str] = []
    gaps: List[str] = []
    alignment_breakdown: Dict[str, float] = {}  # technical, experience, leadership, education
    findings: List[EvidenceGroundingItem] = []


class CareerTransitionAnalysis(BaseModel):
    is_transitioning: bool
    source_domain: Optional[str] = None
    target_domain: Optional[str] = None
    transition_friction_score: float  # 0 (effortless) to 100 (high friction)
    transferable_skills: List[str] = []
    bridge_recommendations: List[EvidenceGroundingItem] = []


class ExperienceRelevanceAnalysis(BaseModel):
    overall_relevance_score: float  # 0 to 100
    signal_to_noise_ratio: float  # ratio of high-impact quantifiable bullets to filler
    high_impact_experiences: List[str] = []
    low_relevance_experiences: List[str] = []
    findings: List[EvidenceGroundingItem] = []


class ProjectEvidenceAnalysis(BaseModel):
    project_depth_score: float  # 0 to 100
    verified_projects_count: int
    technical_breadth_score: float  # 0 to 100
    findings: List[EvidenceGroundingItem] = []


class CareerReadinessAssessment(BaseModel):
    market_readiness_score: float  # 0 to 100
    interview_readiness_score: float  # 0 to 100
    critical_blockers: List[str] = []
    findings: List[EvidenceGroundingItem] = []


class LearningPriorityItem(BaseModel):
    skill_name: str
    priority_level: str  # critical, high, medium
    estimated_hours: int
    expected_impact: str
    recommended_practical_project: str
    reasoning: str


class CareerSuggestionItem(BaseModel):
    suggested_role: str
    alignment_score: float  # 0 to 100
    justification: str
    key_matching_evidence: List[str] = []


class CareerGoalTracking(BaseModel):
    target_role: str
    target_timeline: Optional[str] = None
    completion_percentage: float  # 0 to 100
    milestones_completed: int
    total_milestones: int


class FullCareerIntelligenceReport(BaseModel):
    user_id: str
    generated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    methodology_version: str = "2.0-evidence-grounded"
    progression: CareerProgressionAssessment
    skill_gaps: SkillGapAnalysis
    role_suitability: RoleSuitabilityAnalysis
    transition_analysis: CareerTransitionAnalysis
    experience_relevance: ExperienceRelevanceAnalysis
    project_evidence: ProjectEvidenceAnalysis
    readiness: CareerReadinessAssessment
    learning_priorities: List[LearningPriorityItem] = []
    career_suggestions: List[CareerSuggestionItem] = []
    goal_tracking: CareerGoalTracking
    truthfulness_guarantee: str = (
        "Zero hallucination guarantee: All assessments are rigorously grounded in user-provided resume versions, "
        "job descriptions, and profile records. Inferred insights are explicitly flagged."
    )

    model_config = ConfigDict(from_attributes=True)

