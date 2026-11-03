from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, Field


class EvidenceFinding(BaseModel):
    finding: str
    severity: str = "warning"  # info, warning, critical, strength
    source_section: Optional[str] = None
    source_text: Optional[str] = None
    recommendation: str
    impact_explanation: Optional[str] = None


class SectionAssessment(BaseModel):
    section_name: str
    completeness_score: float  # 0 to 100
    strengths: List[str] = []
    weaknesses: List[str] = []
    findings: List[EvidenceFinding] = []


class SkillEvidenceItem(BaseModel):
    skill_name: str
    category: str  # technical, soft, domain, tool
    demonstrated_in_resume: bool
    evidence_source_text: Optional[str] = None
    confidence_score: float = 1.0


class ATSAssessment(BaseModel):
    ats_compatibility_score: float  # 0 to 100
    formatting_issues: List[str] = []
    header_clarity_score: float
    keyword_readability: str
    table_column_warnings: List[str] = []
    contact_info_detected: Dict[str, bool] = {}


class ResumeAnalysisResult(BaseModel):
    overall_score: float  # 0 to 100
    score_breakdown: Dict[str, float] = {}  # content, relevance, evidence, readability, structure
    summary_evaluation: str
    key_strengths: List[str] = []
    priority_improvements: List[str] = []
    sections: List[SectionAssessment] = []
    skills_extracted: List[SkillEvidenceItem] = []
    ats_analysis: ATSAssessment
    truthfulness_notes: List[EvidenceFinding] = []
    methodology_notes: str = "Evidence-grounded deterministic and contextual LLM assessment"


class ResumeAnalysisResponse(BaseModel):
    id: str
    resume_id: str
    resume_version_id: Optional[str] = None
    analysis_type: str
    provider: str
    model: str
    analysis_version: str
    overall_score: Optional[float] = None
    status: str
    result_json: Optional[ResumeAnalysisResult] = None
    error_details: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)
