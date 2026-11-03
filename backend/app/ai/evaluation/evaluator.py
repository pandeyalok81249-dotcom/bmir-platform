"""
AI Intelligence Quality & Evaluation Engine.
Runs systematic benchmarking across synthetic ground-truth datasets,
tracking precision, recall, F1, hallucination detection, and prompt versions.
"""

from datetime import datetime, timezone
import hashlib
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from app.ai.base import BaseAIProvider
from app.ai.evaluation.dataset import BENCHMARK_RESUMES, GroundTruthResume, BENCHMARK_JOBS, GroundTruthJob
from app.ai.evaluation.metrics import (
    calculate_set_precision_recall_f1,
    calculate_evidence_coverage,
    calculate_hallucination_rate,
    calculate_model_consistency,
)
from app.schemas.analysis import ResumeAnalysisResult


PROMPT_VERSION = "2.1.0"
EVALUATION_CALIBRATION_DISCLAIMER = (
    "AI evaluation confidence scores represent heuristic match indices and rubric conformance. "
    "They are not statistically calibrated frequentist probabilities."
)


class BenchmarkCaseResult(BaseModel):
    case_id: str
    persona: str
    target_role: str
    status: str  # "SUCCESS", "VALIDATION_ERROR", "EXECUTION_ERROR"
    precision: float
    recall: float
    f1: float
    hallucination_rate: float
    evidence_coverage: float
    experience_years_error: float
    unsupported_claims_flagged: int
    unsupported_claims_expected: int
    overall_score: float
    latency_ms: int
    error_message: Optional[str] = None


class EvaluationReport(BaseModel):
    evaluation_id: str
    timestamp: str
    prompt_version: str
    prompt_hash: str
    provider_name: str
    model_name: str
    total_cases: int
    passed_cases: int
    failed_cases: int
    mean_precision: float
    mean_recall: float
    mean_f1: float
    mean_hallucination_rate: float
    mean_evidence_coverage: float
    mean_latency_ms: float
    schema_validation_rate: float
    verdict: str  # "PASSED", "CONDITIONAL_PASS", "FAILED"
    calibration_notice: str = EVALUATION_CALIBRATION_DISCLAIMER
    case_results: List[BenchmarkCaseResult]
    cross_model_comparison: Optional[Dict[str, Any]] = None


class AIEvaluationEngine:
    def __init__(self, prompt_version: str = PROMPT_VERSION):
        self.prompt_version = prompt_version
        self.prompt_hash = hashlib.sha256(prompt_version.encode("utf-8")).hexdigest()[:12]

    async def evaluate_provider(
        self,
        provider: BaseAIProvider,
        dataset: Optional[List[GroundTruthResume]] = None
    ) -> EvaluationReport:
        """
        Runs comprehensive evaluation against benchmark dataset.
        """
        cases = dataset or BENCHMARK_RESUMES
        results: List[BenchmarkCaseResult] = []
        eval_id = f"eval_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}_{provider.provider_name}"

        total_precision = 0.0
        total_recall = 0.0
        total_f1 = 0.0
        total_hallucination = 0.0
        total_coverage = 0.0
        total_latency = 0
        valid_schema_count = 0

        for case in cases:
            try:
                ai_resp = await provider.analyze_resume(
                    resume_text=case.resume_text,
                    target_role=case.target_role,
                    career_stage=case.career_stage,
                )
                content = ai_resp.content

                # Verify schema adherence
                if isinstance(content, dict):
                    # Check if valid schema
                    analysis_obj = ResumeAnalysisResult(**content)
                    valid_schema_count += 1
                elif isinstance(content, ResumeAnalysisResult):
                    analysis_obj = content
                    valid_schema_count += 1
                else:
                    raise ValueError(f"Unexpected response content type: {type(content)}")

                # Extract model predicted skills
                extracted_skills = []
                skills_list = getattr(analysis_obj, "skills_extracted", None) or getattr(analysis_obj, "skills_detected", [])
                for sk in skills_list:
                    if hasattr(sk, "skill_name"):
                        extracted_skills.append(sk.skill_name)
                    elif hasattr(sk, "name"):
                        extracted_skills.append(sk.name)
                    elif isinstance(sk, dict):
                        extracted_skills.append(sk.get("skill_name") or sk.get("name", ""))

                # Compute metrics
                pr_metrics = calculate_set_precision_recall_f1(
                    predicted=extracted_skills,
                    ground_truth=case.ground_truth_skills
                )
                
                halluc_metrics = calculate_hallucination_rate(
                    ai_extracted_skills=extracted_skills,
                    raw_resume_text=case.resume_text
                )

                # Format items for evidence coverage
                evidence_items = []
                strengths = getattr(analysis_obj, "key_strengths", []) or getattr(analysis_obj, "strengths", [])
                improvements = getattr(analysis_obj, "priority_improvements", []) or getattr(analysis_obj, "improvements", [])
                for strg in strengths:
                    evidence_items.append({"text": strg})
                for imp in improvements:
                    evidence_items.append({"text": imp})

                cov_metrics = calculate_evidence_coverage(
                    extracted_items=evidence_items,
                    resume_raw_text=case.resume_text
                )

                # Unsupported claims count from improvements or issues
                unsupported_flagged = 0
                for imp in improvements:
                    imp_lower = imp.lower()
                    if any(w in imp_lower for w in ["unsupported", "metric", "evidence", "verify", "vague", "quantify", "claim"]):
                        unsupported_flagged += 1

                exp_error = 0.0  # Normalized diff

                total_precision += pr_metrics["precision"]
                total_recall += pr_metrics["recall"]
                total_f1 += pr_metrics["f1"]
                total_hallucination += halluc_metrics["hallucination_rate"]
                total_coverage += cov_metrics["coverage_ratio"]
                total_latency += ai_resp.latency_ms

                results.append(
                    BenchmarkCaseResult(
                        case_id=case.id,
                        persona=case.persona,
                        target_role=case.target_role,
                        status="SUCCESS",
                        precision=pr_metrics["precision"],
                        recall=pr_metrics["recall"],
                        f1=pr_metrics["f1"],
                        hallucination_rate=halluc_metrics["hallucination_rate"],
                        evidence_coverage=cov_metrics["coverage_ratio"],
                        experience_years_error=exp_error,
                        unsupported_claims_flagged=unsupported_flagged,
                        unsupported_claims_expected=len(case.ground_truth_unsupported_claims),
                        overall_score=float(analysis_obj.overall_score),
                        latency_ms=ai_resp.latency_ms,
                    )
                )

            except Exception as e:
                results.append(
                    BenchmarkCaseResult(
                        case_id=case.id,
                        persona=case.persona,
                        target_role=case.target_role,
                        status="EXECUTION_ERROR",
                        precision=0.0,
                        recall=0.0,
                        f1=0.0,
                        hallucination_rate=1.0,
                        evidence_coverage=0.0,
                        experience_years_error=99.0,
                        unsupported_claims_flagged=0,
                        unsupported_claims_expected=len(case.ground_truth_unsupported_claims),
                        overall_score=0.0,
                        latency_ms=0,
                        error_message=str(e),
                    )
                )

        n = len(cases)
        passed_count = sum(1 for r in results if r.status == "SUCCESS")
        mean_p = round(total_precision / n, 4) if n else 0.0
        mean_r = round(total_recall / n, 4) if n else 0.0
        mean_f1 = round(total_f1 / n, 4) if n else 0.0
        mean_halluc = round(total_hallucination / n, 4) if n else 0.0
        mean_cov = round(total_coverage / n, 4) if n else 0.0
        mean_lat = round(total_latency / n, 1) if n else 0.0
        schema_rate = round(valid_schema_count / n, 4) if n else 0.0

        # Verdict logic
        if passed_count == n and mean_f1 >= 0.70 and mean_halluc <= 0.15 and schema_rate == 1.0:
            verdict = "PASSED"
        elif passed_count >= int(n * 0.75) and schema_rate >= 0.8:
            verdict = "CONDITIONAL_PASS"
        else:
            verdict = "FAILED"

        return EvaluationReport(
            evaluation_id=eval_id,
            timestamp=datetime.now(timezone.utc).isoformat(),
            prompt_version=self.prompt_version,
            prompt_hash=self.prompt_hash,
            provider_name=provider.provider_name,
            model_name=getattr(provider, "model", "default"),
            total_cases=n,
            passed_cases=passed_count,
            failed_cases=n - passed_count,
            mean_precision=mean_p,
            mean_recall=mean_r,
            mean_f1=mean_f1,
            mean_hallucination_rate=mean_halluc,
            mean_evidence_coverage=mean_cov,
            mean_latency_ms=mean_lat,
            schema_validation_rate=schema_rate,
            verdict=verdict,
            case_results=results,
        )

    async def compare_providers(
        self,
        provider_a: BaseAIProvider,
        provider_b: BaseAIProvider,
        dataset: Optional[List[GroundTruthResume]] = None
    ) -> Dict[str, Any]:
        """
        Runs side-by-side consistency evaluation between two AI providers
        (e.g. OpenAI vs Gemini) across the benchmark dataset.
        """
        report_a = await self.evaluate_provider(provider_a, dataset)
        report_b = await self.evaluate_provider(provider_b, dataset)

        scores_a = {r.case_id: r.overall_score for r in report_a.case_results if r.status == "SUCCESS"}
        scores_b = {r.case_id: r.overall_score for r in report_b.case_results if r.status == "SUCCESS"}

        consistency = calculate_model_consistency(scores_a, scores_b)

        comparison = {
            "provider_a": {
                "name": report_a.provider_name,
                "model": report_a.model_name,
                "mean_f1": report_a.mean_f1,
                "mean_hallucination_rate": report_a.mean_hallucination_rate,
                "verdict": report_a.verdict,
            },
            "provider_b": {
                "name": report_b.provider_name,
                "model": report_b.model_name,
                "mean_f1": report_b.mean_f1,
                "mean_hallucination_rate": report_b.mean_hallucination_rate,
                "verdict": report_b.verdict,
            },
            "consistency_metrics": consistency,
            "comparison_verdict": "CONSISTENT" if consistency["is_consistent"] else "DIVERGENT",
            "prompt_version": self.prompt_version,
        }

        report_a.cross_model_comparison = comparison
        return {
            "report_a": report_a,
            "report_b": report_b,
            "comparison": comparison
        }
