import asyncio
import hashlib
import json
import logging
import re
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.ai.factory import AIFactory
from app.core.database import async_session_maker
from app.core.redis import JobQueueManager
from app.models.analysis import ResumeAnalysis
from app.models.audit import AIUsageLog
from app.models.resume import Resume, ResumeVersion
from app.schemas.analysis import (
    ATSAssessment,
    EvidenceFinding,
    ResumeAnalysisResult,
    SectionAssessment,
    SkillEvidenceItem,
)
from app.services.document_parser import DocumentParser

logger = logging.getLogger(__name__)


class ResumeAnalyzerService:
    @staticmethod
    def compute_deterministic_audit(text: str, sections: Dict[str, str]) -> ResumeAnalysisResult:
        """
        Deterministic parsing and rules-based analysis baseline.
        Ensures evidence-grounded scoring without fake statistics.
        """
        words = text.split()
        word_count = len(words)

        # 1. Section Completeness
        expected_sections = ["summary", "experience", "education", "skills", "projects"]
        present_sections = [s for s in expected_sections if s in sections]
        structure_score = round((len(present_sections) / len(expected_sections)) * 100, 1)

        section_assessments: List[SectionAssessment] = []
        for sec in expected_sections:
            if sec in sections:
                sec_text = sections[sec]
                sec_words = len(sec_text.split())
                score = min(100.0, round((sec_words / 40.0) * 100, 1))
                findings = []
                if sec == "experience":
                    lines = sec_text.splitlines()
                    for line in lines:
                        if len(line.split()) > 4 and not re.search(r"\d+%?|\$\d+", line):
                            findings.append(
                                EvidenceFinding(
                                    finding="Action bullet lacks quantified outcome or measurable metric.",
                                    severity="warning",
                                    source_section="experience",
                                    source_text=line[:120],
                                    recommendation="Add verified metric or technical scope to substantiate this achievement.",
                                )
                            )
                section_assessments.append(
                    SectionAssessment(
                        section_name=sec.capitalize(),
                        completeness_score=score,
                        strengths=[f"Found valid {sec} section with substantial detail."] if score > 70 else [],
                        weaknesses=[f"{sec.capitalize()} could be expanded with more specificity."] if score <= 70 else [],
                        findings=findings,
                    )
                )
            else:
                section_assessments.append(
                    SectionAssessment(
                        section_name=sec.capitalize(),
                        completeness_score=0.0,
                        strengths=[],
                        weaknesses=[f"Missing {sec.capitalize()} section."],
                        findings=[
                            EvidenceFinding(
                                finding=f"{sec.capitalize()} section not detected.",
                                severity="critical" if sec in ["experience", "skills"] else "warning",
                                source_section=sec,
                                source_text=None,
                                recommendation=f"Add a dedicated {sec.capitalize()} section to improve ATS structure and clarity.",
                            )
                        ],
                    )
                )

        # 2. Skills Extraction (Deterministic regex against standard keywords)
        tech_keywords = [
            "python", "javascript", "typescript", "dart", "flutter", "react", "docker",
            "kubernetes", "sql", "postgresql", "fastapi", "aws", "gcp", "git", "ci/cd",
            "redis", "rest api", "graphql", "linux", "java", "c++", "c#"
        ]
        lower_text = text.lower()
        extracted_skills = []
        for kw in tech_keywords:
            if re.search(r"\b" + re.escape(kw) + r"\b", lower_text):
                in_exp = "experience" in sections and kw in sections["experience"].lower()
                extracted_skills.append(
                    SkillEvidenceItem(
                        skill_name=kw.capitalize(),
                        category="technical",
                        demonstrated_in_resume=in_exp,
                        evidence_source_text=f"Referenced in {'Experience' if in_exp else 'Skills'} section",
                        confidence_score=1.0 if in_exp else 0.7,
                    )
                )

        # 3. ATS Assessment
        ats_score = 90.0
        formatting_issues = []
        if word_count < 150:
            ats_score -= 25.0
            formatting_issues.append("Resume length is unusually brief (under 150 words).")
        if "experience" not in sections:
            ats_score -= 20.0
            formatting_issues.append("Standard 'Experience' heading not identified by parser.")

        ats = ATSAssessment(
            ats_compatibility_score=max(30.0, ats_score),
            formatting_issues=formatting_issues,
            header_clarity_score=structure_score,
            keyword_readability="High" if len(extracted_skills) >= 5 else "Moderate",
            table_column_warnings=[],
            contact_info_detected={
                "email": bool(re.search(r"[\w\.-]+@[\w\.-]+\.\w+", text)),
                "phone": bool(re.search(r"(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}", text)),
            },
        )

        overall = round(
            (structure_score * 0.3)
            + (ats.ats_compatibility_score * 0.3)
            + (min(100.0, len(extracted_skills) * 10) * 0.4),
            1,
        )

        return ResumeAnalysisResult(
            overall_score=overall,
            score_breakdown={
                "structure": structure_score,
                "ats_compatibility": ats.ats_compatibility_score,
                "skills_evidence": min(100.0, len(extracted_skills) * 10),
            },
            summary_evaluation=f"Analysis completed across {word_count} words and {len(extracted_skills)} verified skill indicators.",
            key_strengths=[
                f"Demonstrated {len(extracted_skills)} technical competencies in resume body.",
                f"Detected standard structural sections with {structure_score}% completeness.",
            ],
            priority_improvements=[
                "Ensure every bullet point in experience contains quantifiable impact.",
                "Verify that all listed skills are evidenced in practical experience descriptions.",
            ],
            sections=section_assessments,
            skills_extracted=extracted_skills,
            ats_analysis=ats,
            truthfulness_notes=[],
            methodology_notes="Deterministic parsing and extraction baseline",
        )

    @classmethod
    async def process_analysis_job(
        cls,
        analysis_id: str,
        resume_id: str,
        user_id: str,
        target_role: Optional[str] = None,
        career_stage: Optional[str] = None,
        preferred_provider: Optional[str] = None,
    ) -> None:
        """
        Asynchronous worker task: Executes full analysis pipeline in the background.
        Updates persistent database records and Redis job queue stage status.
        """
        logger.info(f"STARTING process_analysis_job for {analysis_id}")
        session_factory = getattr(cls, "session_factory", None) or async_session_maker
        async with session_factory() as session:
            try:
                # 1. Update status: processing
                await JobQueueManager.set_job_status(
                    job_id=analysis_id,
                    status="processing",
                    stage_description="Reading extracted resume document...",
                )

                a_res = await session.execute(select(ResumeAnalysis).where(ResumeAnalysis.id == analysis_id))
                analysis_record = a_res.scalars().first()
                if not analysis_record:
                    logger.error(f"Analysis record {analysis_id} not found in database.")
                    return

                analysis_record.status = "processing"
                await session.commit()

                # 2. Fetch Resume
                r_res = await session.execute(select(Resume).where(Resume.id == resume_id))
                resume = r_res.scalars().first()
                if not resume:
                    raise ValueError(f"Resume {resume_id} not found.")

                raw_text = resume.extracted_text or ""
                sections = DocumentParser.segment_sections(raw_text)

                # 3. Stage: AI Reasoning
                await JobQueueManager.set_job_status(
                    job_id=analysis_id,
                    status="processing",
                    stage_description="Evaluating experience and role alignment with AI...",
                )

                provider = AIFactory.get_provider(preferred_provider)
                ai_success = False

                try:
                    ai_resp = await provider.analyze_resume(
                        resume_text=raw_text,
                        target_role=target_role,
                        career_stage=career_stage,
                    )
                    analysis_record.provider = ai_resp.provider
                    analysis_record.model = ai_resp.model
                    analysis_record.overall_score = ai_resp.content.overall_score
                    analysis_record.result_json = ai_resp.content.model_dump()
                    analysis_record.status = "completed"
                    analysis_record.completed_at = datetime.now(timezone.utc)

                    # Log usage
                    usage_log = AIUsageLog(
                        user_id=user_id,
                        provider=ai_resp.provider,
                        model=ai_resp.model,
                        operation="resume_analysis",
                        input_tokens=ai_resp.input_tokens,
                        output_tokens=ai_resp.output_tokens,
                        estimated_cost_usd=ai_resp.estimated_cost_usd,
                        status="success",
                        latency_ms=ai_resp.latency_ms,
                    )
                    session.add(usage_log)
                    ai_success = True

                except Exception as e:
                    logger.warning(f"AI Provider call failed, falling back to deterministic audit: {str(e)}")

                if not ai_success:
                    deterministic_result = cls.compute_deterministic_audit(raw_text, sections)
                    analysis_record.provider = "deterministic"
                    analysis_record.model = "deterministic-parser-v1"
                    analysis_record.overall_score = deterministic_result.overall_score
                    analysis_record.result_json = deterministic_result.model_dump()
                    analysis_record.status = "completed"
                    analysis_record.completed_at = datetime.now(timezone.utc)

                await session.commit()

                # 4. Job queue completion
                await JobQueueManager.set_job_status(
                    job_id=analysis_id,
                    status="completed",
                    stage_description="Career intelligence report ready.",
                    result=analysis_record.result_json,
                )

            except asyncio.CancelledError:
                logger.info(f"Analysis job {analysis_id} was cancelled.")
                a_res = await session.execute(select(ResumeAnalysis).where(ResumeAnalysis.id == analysis_id))
                analysis_record = a_res.scalars().first()
                if analysis_record:
                    analysis_record.status = "failed"
                    analysis_record.error_details = "Cancelled by user."
                    await session.commit()

            except Exception as ex:
                logger.error(f"Error in analysis job {analysis_id}: {ex}", exc_info=True)
                a_res = await session.execute(select(ResumeAnalysis).where(ResumeAnalysis.id == analysis_id))
                analysis_record = a_res.scalars().first()
                if analysis_record:
                    analysis_record.status = "failed"
                    analysis_record.error_details = str(ex)
                    await session.commit()

                await JobQueueManager.set_job_status(
                    job_id=analysis_id,
                    status="failed",
                    stage_description="Analysis encountered an error.",
                    error=str(ex),
                )
