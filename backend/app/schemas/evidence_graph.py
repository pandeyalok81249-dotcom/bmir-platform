"""
Schemas for Resume Evidence Graph.
Bipartite directed graph connecting skills, experience bullets, projects,
certifications, and job requirements with calibrated evidence strength.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field


EVIDENCE_GRAPH_DISCLAIMER = (
    "Evidence categorization reflects automated parsing of textual corroboration within the provided resume document. "
    "Mention-only classifications indicate that skills were listed without corresponding project or work experience bullet citations."
)


class EvidenceNode(BaseModel):
    id: str
    node_type: str = Field(..., description="'skill', 'experience_bullet', 'project', 'certification', 'job_requirement'")
    label: str
    section: Optional[str] = None
    metadata: Dict[str, Any] = Field(default_factory=dict)


class EvidenceEdge(BaseModel):
    id: str
    source_node_id: str
    target_node_id: str
    strength: str = Field(
        ...,
        description="'strong_evidence', 'partial_evidence', 'mention_only', 'no_evidence', 'not_assessable'"
    )
    source_quote: Optional[str] = None
    reasoning: str
    confidence: float = 1.0


class EvidenceGraphSummary(BaseModel):
    total_skills: int
    strong_evidence_count: int
    partial_evidence_count: int
    mention_only_count: int
    unsubstantiated_count: int
    overall_evidence_score: float = Field(..., description="0 to 100 metric reflecting grounding depth")
    critical_findings: List[str] = Field(default_factory=list)


class ResumeEvidenceGraphResponse(BaseModel):
    resume_id: str
    target_role: Optional[str] = None
    nodes: List[EvidenceNode]
    edges: List[EvidenceEdge]
    summary: EvidenceGraphSummary
    disclaimer: str = EVIDENCE_GRAPH_DISCLAIMER
