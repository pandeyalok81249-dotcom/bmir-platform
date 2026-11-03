"""
Schemas for Career Trajectory Simulator.
Provides multi-target role transition modeling, friction index, and ramp-up estimation.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


TRAJECTORY_SIMULATOR_DISCLAIMER = (
    "Trajectory simulation scores represent heuristic skill overlap and experience proximity models based on market datasets. "
    "They do not guarantee employment, offer timelines, or automated progression."
)


class RoleTrajectorySimulation(BaseModel):
    target_role: str
    overall_readiness_score: float = Field(..., description="0 to 100 composite transition readiness score")
    transition_friction: str = Field(..., description="'low', 'moderate', 'high', 'very_high'")
    estimated_ramp_up_time: str = Field(..., description="Estimated ramp-up duration, e.g. '1-3 months'")
    skill_alignment_score: float
    experience_relevance_score: float
    project_relevance_score: float
    education_alignment_score: float
    transferable_skills: List[str]
    critical_skill_gaps: List[str]
    priority_learning_actions: List[str]


class TrajectorySimulatorRequest(BaseModel):
    resume_id: Optional[str] = None
    target_roles: List[str] = Field(..., min_length=1, max_length=5)


class TrajectorySimulatorResponse(BaseModel):
    candidate_id: str
    current_experience_years: float
    simulations: List[RoleTrajectorySimulation]
    optimal_recommended_path: str
    comparative_summary: str
    disclaimer: str = TRAJECTORY_SIMULATOR_DISCLAIMER
