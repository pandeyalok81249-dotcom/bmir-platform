"""
Resume Evidence Graph Service.
Constructs bipartite directed evidence graphs linking skills to experiences,
projects, certifications, and target job requirements.
"""

from typing import List, Dict, Any, Optional, Set
import re
import uuid

from app.schemas.evidence_graph import (
    EvidenceNode,
    EvidenceEdge,
    EvidenceGraphSummary,
    ResumeEvidenceGraphResponse,
)


METRIC_REGEX = re.compile(
    r'(\$\d+[\d,]*(\.\d+)?([kKmMbB])?|\d+([.,]\d+)?%|\b\d+\s*(ms|seconds|minutes|hours|days|requests|rps|req/s|users|engineers|microservices)\b|\b(reduced|increased|scaled|cut|saved|improved)\s+.*?\b\d+)',
    re.IGNORECASE
)


class EvidenceGraphService:
    def __init__(self):
        pass

    def _extract_bullets(self, text: str) -> List[str]:
        """Extracts bullet lines from text."""
        lines = text.split("\n")
        bullets = []
        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith(("-", "*", "•", "–")) or re.match(r'^\d+\.', stripped):
                clean_bullet = re.sub(r'^[-*•–\d.]+\s*', '', stripped)
                if len(clean_bullet) > 15:
                    bullets.append(clean_bullet)
            elif len(stripped) > 40 and any(w in stripped.lower() for w in ["developed", "designed", "built", "led", "engineered", "implemented", "scaled"]):
                bullets.append(stripped)
        return bullets

    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extracts recognizable technical and professional skills."""
        canonical_skills = [
            "Python", "Go", "Java", "C++", "JavaScript", "TypeScript", "SQL", "Bash",
            "PostgreSQL", "MySQL", "Redis", "MongoDB", "Elasticsearch", "Apache Kafka", "RabbitMQ",
            "Docker", "Kubernetes", "AWS", "GCP", "Azure", "Terraform", "CI/CD", "GitHub Actions",
            "FastAPI", "Django", "Flask", "React", "Vue", "Next.js", "Redux", "Tailwind CSS",
            "PyTorch", "TensorFlow", "Scikit-learn", "LightGBM", "XGBoost", "BigQuery", "Spark",
            "Microservices", "Distributed Systems", "REST APIs", "gRPC", "GraphQL",
            "Product Strategy", "Roadmap", "Scrum", "Agile", "User Research", "Jira", "Amplitude"
        ]
        found = []
        for sk in canonical_skills:
            pattern = r'\b' + re.escape(sk.lower()) + r'\b'
            if re.search(pattern, text.lower()):
                found.append(sk)
        return found

    def build_graph(
        self,
        resume_id: str,
        resume_text: str,
        target_role: Optional[str] = None,
        job_requirements: Optional[List[str]] = None
    ) -> ResumeEvidenceGraphResponse:
        """
        Builds the complete evidence graph with nodes and calibrated edges.
        """
        bullets = self._extract_bullets(resume_text)
        detected_skills = self._extract_skills_from_text(resume_text)

        nodes: List[EvidenceNode] = []
        edges: List[EvidenceEdge] = []

        skill_node_map: Dict[str, str] = {}
        bullet_node_map: Dict[int, str] = {}
        skill_evidence_strength: Dict[str, str] = {}

        # 1. Create Skill Nodes
        for sk in detected_skills:
            nid = f"node_skill_{uuid.uuid4().hex[:8]}"
            skill_node_map[sk] = nid
            nodes.append(
                EvidenceNode(
                    id=nid,
                    node_type="skill",
                    label=sk,
                    section="SKILLS",
                    metadata={"canonical_name": sk}
                )
            )
            # Default strength to mention_only
            skill_evidence_strength[sk] = "mention_only"

        # 2. Create Experience Bullet Nodes
        for idx, bullet in enumerate(bullets):
            bid = f"node_bullet_{idx}_{uuid.uuid4().hex[:6]}"
            bullet_node_map[idx] = bid
            has_metric = bool(METRIC_REGEX.search(bullet))
            nodes.append(
                EvidenceNode(
                    id=bid,
                    node_type="experience_bullet",
                    label=bullet[:80] + ("..." if len(bullet) > 80 else ""),
                    section="EXPERIENCE",
                    metadata={
                        "full_text": bullet,
                        "has_quantitative_metric": has_metric,
                        "metric_snippet": METRIC_REGEX.search(bullet).group(0) if has_metric else None
                    }
                )
            )

            # Link mentioned skills in this bullet
            for sk, snid in skill_node_map.items():
                pattern = r'\b' + re.escape(sk.lower()) + r'\b'
                if re.search(pattern, bullet.lower()):
                    if has_metric:
                        strength = "strong_evidence"
                        reasoning = f"Corroborated by verified quantitative metric: '{METRIC_REGEX.search(bullet).group(0)}'"
                        skill_evidence_strength[sk] = "strong_evidence"
                    else:
                        strength = "partial_evidence"
                        reasoning = "Mentioned in production experience bullet without quantitative metric"
                        if skill_evidence_strength[sk] != "strong_evidence":
                            skill_evidence_strength[sk] = "partial_evidence"

                    edges.append(
                        EvidenceEdge(
                            id=f"edge_{uuid.uuid4().hex[:8]}",
                            source_node_id=bid,
                            target_node_id=snid,
                            strength=strength,
                            source_quote=bullet,
                            reasoning=reasoning,
                            confidence=0.95 if strength == "strong_evidence" else 0.80
                        )
                    )

        # 3. Job Requirement Nodes (if provided)
        if job_requirements:
            for j_idx, req in enumerate(job_requirements):
                jid = f"node_jobreq_{j_idx}_{uuid.uuid4().hex[:6]}"
                nodes.append(
                    EvidenceNode(
                        id=jid,
                        node_type="job_requirement",
                        label=req,
                        section="JOB_REQUIREMENTS",
                        metadata={"requirement_text": req}
                    )
                )

                # Connect skills to job requirement
                for sk, snid in skill_node_map.items():
                    if sk.lower() in req.lower() or req.lower() in sk.lower():
                        current_str = skill_evidence_strength.get(sk, "no_evidence")
                        edges.append(
                            EvidenceEdge(
                                id=f"edge_job_{uuid.uuid4().hex[:8]}",
                                source_node_id=snid,
                                target_node_id=jid,
                                strength=current_str,
                                source_quote=None,
                                reasoning=f"Skill '{sk}' fulfills job requirement with evidence grade: {current_str}",
                                confidence=0.90
                            )
                        )

        # Compute summary metrics
        total_skills = len(detected_skills)
        strong_count = sum(1 for s in skill_evidence_strength.values() if s == "strong_evidence")
        partial_count = sum(1 for s in skill_evidence_strength.values() if s == "partial_evidence")
        mention_count = sum(1 for s in skill_evidence_strength.values() if s == "mention_only")
        unsub_count = sum(1 for s in skill_evidence_strength.values() if s in ["no_evidence", "not_assessable"])

        if total_skills > 0:
            score = round(100.0 * (strong_count * 1.0 + partial_count * 0.5 + mention_count * 0.1) / total_skills, 1)
        else:
            score = 0.0

        findings = []
        if mention_count > 0:
            mention_skills = [sk for sk, s in skill_evidence_strength.items() if s == "mention_only"][:4]
            findings.append(
                f"{mention_count} skills ({', '.join(mention_skills)}) appear without direct experience bullet corroboration."
            )
        if strong_count > 0:
            strong_skills = [sk for sk, s in skill_evidence_strength.items() if s == "strong_evidence"][:4]
            findings.append(
                f"{strong_count} skills ({', '.join(strong_skills)}) have strong quantitative impact metrics."
            )

        summary = EvidenceGraphSummary(
            total_skills=total_skills,
            strong_evidence_count=strong_count,
            partial_evidence_count=partial_count,
            mention_only_count=mention_count,
            unsubstantiated_count=unsub_count,
            overall_evidence_score=score,
            critical_findings=findings
        )

        return ResumeEvidenceGraphResponse(
            resume_id=resume_id,
            target_role=target_role,
            nodes=nodes,
            edges=edges,
            summary=summary
        )
