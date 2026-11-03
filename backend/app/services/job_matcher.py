import re
from typing import Any, Dict, List
from app.models.job import JobDescription, JobMatch
from app.models.resume import ResumeVersion
from app.schemas.job_match import JobMatchResult, SkillMatchDetail


class JobMatcherService:
    @staticmethod
    def match(resume_content: Dict[str, Any], job_reqs: Dict[str, Any]) -> JobMatchResult:
        required_skills = [s.lower().strip() for s in job_reqs.get("required_skills", [])]
        preferred_skills = [s.lower().strip() for s in job_reqs.get("preferred_skills", [])]

        # Extract full resume text
        resume_text_parts = []
        if isinstance(resume_content, dict):
            for k, v in resume_content.items():
                if isinstance(v, str):
                    resume_text_parts.append(v)
                elif isinstance(v, list):
                    for item in v:
                        if isinstance(item, str):
                            resume_text_parts.append(item)
                        elif isinstance(item, dict):
                            resume_text_parts.extend([str(val) for val in item.values()])
        full_resume_text = " ".join(resume_text_parts).lower()
        experience_text = str(resume_content.get("experience", "")).lower()

        skill_details: List[SkillMatchDetail] = []
        matched_required_count = 0
        missing_critical: List[str] = []

        # Check required skills
        for skill in required_skills:
            if not skill:
                continue
            has_word = bool(re.search(r"\b" + re.escape(skill) + r"\b", full_resume_text))
            has_evidence = bool(re.search(r"\b" + re.escape(skill) + r"\b", experience_text))

            if has_word and has_evidence:
                status = "verified_demonstrated"
                matched_required_count += 1
                evidence = f"Demonstrated in work experience context"
            elif has_word:
                status = "mentioned_only"
                matched_required_count += 0.5
                evidence = f"Listed in skills section without explicit project/experience narrative"
            else:
                status = "missing"
                missing_critical.append(skill.capitalize())
                evidence = None

            skill_details.append(
                SkillMatchDetail(
                    skill_name=skill.capitalize(),
                    is_required=True,
                    status=status,
                    evidence_text=evidence,
                )
            )

        # Check preferred skills
        matched_preferred_count = 0
        for skill in preferred_skills:
            if not skill:
                continue
            has_word = bool(re.search(r"\b" + re.escape(skill) + r"\b", full_resume_text))
            has_evidence = bool(re.search(r"\b" + re.escape(skill) + r"\b", experience_text))
            if has_word and has_evidence:
                status = "verified_demonstrated"
                matched_preferred_count += 1
            elif has_word:
                status = "mentioned_only"
                matched_preferred_count += 0.5
            else:
                status = "missing"

            skill_details.append(
                SkillMatchDetail(
                    skill_name=skill.capitalize(),
                    is_required=False,
                    status=status,
                    evidence_text="Found in candidate profile" if has_word else None,
                )
            )

        req_score = (
            round((matched_required_count / len(required_skills)) * 100, 1)
            if required_skills
            else 85.0
        )
        pref_score = (
            round((matched_preferred_count / len(preferred_skills)) * 100, 1)
            if preferred_skills
            else 80.0
        )
        overall = round((req_score * 0.75) + (pref_score * 0.25), 1)

        recommendations = []
        if missing_critical:
            recommendations.append(
                f"Candidate lacks {len(missing_critical)} core required requirements: {', '.join(missing_critical[:3])}."
            )
        if any(s.status == "mentioned_only" for s in skill_details):
            recommendations.append(
                "Several skills are listed without backing bullet points in experience. Provide concrete technical outcomes."
            )

        return JobMatchResult(
            overall_match_score=min(100.0, max(0.0, overall)),
            required_skills_match=req_score,
            preferred_skills_match=pref_score,
            experience_alignment="Strong" if req_score >= 80 else ("Moderate" if req_score >= 50 else "Weak"),
            matched_skills=skill_details,
            missing_critical_skills=missing_critical,
            recommended_positioning=recommendations,
        )

