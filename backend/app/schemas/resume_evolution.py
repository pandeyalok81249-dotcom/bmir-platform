from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class AchievementImprovement(BaseModel):
    section: str
    original_bullet: str
    improved_bullet: str
    nature_of_improvement: str
    metric_added: Optional[str] = None


class ContentDiff(BaseModel):
    section: str
    added: List[str] = []
    removed: List[str] = []
    unchanged_count: int = 0


class PotentialRegression(BaseModel):
    severity: str  # critical, warning, info
    description: str
    original_text: Optional[str] = None
    recommendation: str


class ScoreComparison(BaseModel):
    v1_score: Optional[float] = None
    v2_score: Optional[float] = None
    score_delta: Optional[float] = None
    v1_methodology: Optional[str] = "1.0"
    v2_methodology: Optional[str] = "1.0"
    methodologies_compatible: bool = True
    methodology_explanation: Optional[str] = None


class ResumeEvolutionDiffResponse(BaseModel):
    resume_id: str
    base_version_id: str
    base_version_number: int
    compare_version_id: str
    compare_version_number: int
    content_diffs: List[ContentDiff] = []
    improved_achievements: List[AchievementImprovement] = []
    newly_evidenced_skills: List[str] = []
    role_alignment_delta: float = 0.0
    readability_delta: Dict[str, Any] = {}
    potential_regressions: List[PotentialRegression] = []
    score_comparison: ScoreComparison
    summary: str

    model_config = ConfigDict(from_attributes=True)


class VersionRestoreResponse(BaseModel):
    resume_id: str
    restored_from_version_number: int
    new_version_number: int
    new_version_id: str
    message: str

    model_config = ConfigDict(from_attributes=True)

