import difflib
import hashlib
import logging
import re
from typing import Any, Dict, List, Optional, Set, Tuple
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.analysis import ResumeAnalysis
from app.models.resume import Resume, ResumeVersion
from app.schemas.resume_evolution import (
    AchievementImprovement,
    ContentDiff,
    PotentialRegression,
    ResumeEvolutionDiffResponse,
    ScoreComparison,
    VersionRestoreResponse,
)

logger = logging.getLogger(__name__)


class ResumeEvolutionService:
    """
    Resume Evolution Intelligence Service.
    Performs structural, semantic, and analytical comparison between
    two resume versions with regression detection and provenance tracking.
    """

    @classmethod
    def compare_versions(
        cls,
        resume_id: str,
        v1: ResumeVersion,
        v2: ResumeVersion,
        v1_analysis: Optional[ResumeAnalysis] = None,
        v2_analysis: Optional[ResumeAnalysis] = None,
    ) -> ResumeEvolutionDiffResponse:
        c1 = v1.resume_content or {}
        c2 = v2.resume_content or {}

        all_sections = sorted(list(set(c1.keys()).union(set(c2.keys()))))
        content_diffs: List[ContentDiff] = []
        improved_achievements: List[AchievementImprovement] = []
        potential_regressions: List[PotentialRegression] = []

        total_words_v1 = sum(len(str(val).split()) for val in c1.values())
        total_words_v2 = sum(len(str(val).split()) for val in c2.values())

        # 1. Section & Line-level Diff
        for sec in all_sections:
            text1 = str(c1.get(sec, ""))
            text2 = str(c2.get(sec, ""))

            lines1 = [l.strip() for l in text1.splitlines() if l.strip()]
            lines2 = [l.strip() for l in text2.splitlines() if l.strip()]

            added = [l for l in lines2 if l not in lines1]
            removed = [l for l in lines1 if l not in lines2]
            unchanged = len([l for l in lines1 if l in lines2])

            content_diffs.append(
                ContentDiff(
                    section=sec.capitalize(),
                    added=added,
                    removed=removed,
                    unchanged_count=unchanged,
                )
            )

            # Check for Section-level Regressions
            if text1 and not text2:
                potential_regressions.append(
                    PotentialRegression(
                        severity="critical",
                        description=f"Entire '{sec.capitalize()}' section was removed in version {v2.version_number}.",
                        original_text=text1[:150],
                        recommendation=f"Restore the '{sec.capitalize()}' section to preserve structural completeness.",
                    )
                )

            # 2. Check for Bullet-level Metric Regressions & Achievement Improvements
            for r_line in removed:
                metric_match = re.search(r"(\d+[\.,]?\d*%?|\$\d+[\.,]?\d*[kmbt]?|\d+k)", r_line, re.IGNORECASE)
                if metric_match:
                    # Check if there is a corresponding added line with the metric
                    matched_in_added = any(metric_match.group(0).lower() in a_line.lower() for a_line in added)
                    if not matched_in_added:
                        potential_regressions.append(
                            PotentialRegression(
                                severity="warning",
                                description=f"Quantified achievement metric '{metric_match.group(0)}' was removed in version {v2.version_number}.",
                                original_text=r_line[:140],
                                recommendation="Retain concrete metrics to ensure strong STAR evidence in hiring audits.",
                            )
                        )

            # Detect Achievement Upgrades (Weak phrasing -> Strong action + metric)
            for a_line in added:
                has_metric = bool(re.search(r"(\d+[\.,]?\d*%?|\$\d+|\d+k)", a_line, re.IGNORECASE))
                has_strong_verb = any(v in a_line.lower() for v in ["architected", "engineered", "optimized", "spearheaded", "accelerated", "reduced", "scaled"])
                if has_metric and has_strong_verb:
                    # Find closest semantic predecessor from removed lines
                    close_matches = difflib.get_close_matches(a_line, removed, n=1, cutoff=0.3)
                    orig = close_matches[0] if close_matches else "Previously unstated or unstructured claim"
                    improved_achievements.append(
                        AchievementImprovement(
                            section=sec.capitalize(),
                            original_bullet=orig,
                            improved_bullet=a_line,
                            nature_of_improvement="Upgraded with strong technical action verb and quantified outcome.",
                            metric_added=re.search(r"(\d+[\.,]?\d*%?|\$\d+|\d+k)", a_line, re.IGNORECASE).group(0),
                        )
                    )

        # 3. Newly Evidenced Skills
        skills_v1 = cls._extract_skills_from_content(c1)
        skills_v2 = cls._extract_skills_from_content(c2)
        new_skills = sorted(list(skills_v2 - skills_v1))

        # 4. Score & Methodology Comparison
        v1_score = v1_analysis.overall_score if v1_analysis else None
        v2_score = v2_analysis.overall_score if v2_analysis else None
        score_delta = round(v2_score - v1_score, 1) if (v1_score is not None and v2_score is not None) else None

        v1_meth = v1_analysis.analysis_version if v1_analysis else "1.0"
        v2_meth = v2_analysis.analysis_version if v2_analysis else "1.0"
        compatible = (v1_meth == v2_meth)
        meth_explanation = None
        if not compatible:
            meth_explanation = (
                f"Version {v1.version_number} was evaluated with engine v{v1_meth}, while Version {v2.version_number} "
                f"was evaluated with engine v{v2_meth}. Direct score difference includes methodology enhancements."
            )

        score_comp = ScoreComparison(
            v1_score=v1_score,
            v2_score=v2_score,
            score_delta=score_delta,
            v1_methodology=v1_meth,
            v2_methodology=v2_meth,
            methodologies_compatible=compatible,
            methodology_explanation=meth_explanation,
        )

        readability_delta = {
            "v1_word_count": total_words_v1,
            "v2_word_count": total_words_v2,
            "word_count_delta": total_words_v2 - total_words_v1,
            "sections_count_v1": len(c1),
            "sections_count_v2": len(c2),
        }

        # Role alignment delta
        alignment_delta = round((score_delta * 0.8), 1) if score_delta is not None else 0.0

        summary = (
            f"Comparing Version {v1.version_number} to Version {v2.version_number}: "
            f"Detected {len(improved_achievements)} improved STAR achievements, {len(new_skills)} newly evidenced skills, "
            f"and {len(potential_regressions)} potential regressions."
        )

        return ResumeEvolutionDiffResponse(
            resume_id=resume_id,
            base_version_id=v1.id,
            base_version_number=v1.version_number,
            compare_version_id=v2.id,
            compare_version_number=v2.version_number,
            content_diffs=content_diffs,
            improved_achievements=improved_achievements,
            newly_evidenced_skills=new_skills,
            role_alignment_delta=alignment_delta,
            readability_delta=readability_delta,
            potential_regressions=potential_regressions,
            score_comparison=score_comp,
            summary=summary,
        )

    @classmethod
    async def restore_version(
        cls,
        resume: Resume,
        version_id_to_restore: str,
        db: AsyncSession,
    ) -> VersionRestoreResponse:
        """
        Creates a new head version copying content from the specified historical version.
        Ensures append-only immutable provenance history without destructive in-place rollback.
        """
        v_res = await db.execute(
            select(ResumeVersion).where(
                ResumeVersion.id == version_id_to_restore,
                ResumeVersion.resume_id == resume.id,
            )
        )
        target_v = v_res.scalars().first()
        if not target_v:
            raise ValueError(f"Version {version_id_to_restore} not found for this resume.")

        # Find current highest version number
        max_res = await db.execute(
            select(func.max(ResumeVersion.version_number)).where(
                ResumeVersion.resume_id == resume.id
            )
        )
        current_max = max_res.scalar() or target_v.version_number
        new_version_num = current_max + 1

        content_str = str(target_v.resume_content)
        new_hash = hashlib.sha256(content_str.encode("utf-8")).hexdigest()

        new_version = ResumeVersion(
            resume_id=resume.id,
            version_number=new_version_num,
            resume_content=target_v.resume_content,
            content_hash=new_hash,
        )
        db.add(new_version)
        await db.commit()
        await db.refresh(new_version)

        return VersionRestoreResponse(
            resume_id=resume.id,
            restored_from_version_number=target_v.version_number,
            new_version_number=new_version.version_number,
            new_version_id=new_version.id,
            message=f"Successfully restored Version {target_v.version_number} as new Version {new_version.version_number}.",
        )

    @staticmethod
    def _extract_skills_from_content(content: Dict[str, Any]) -> Set[str]:
        raw = " ".join(str(v).lower() for v in content.values())
        catalog = {
            "python", "fastapi", "docker", "postgresql", "kubernetes",
            "redis", "flutter", "dart", "aws", "gcp", "ci/cd", "rest api", "graphql", "sql"
        }
        return {s.capitalize() for s in catalog if s in raw}

