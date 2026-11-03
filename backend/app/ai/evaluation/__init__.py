"""
AI Evaluation Framework Package.
"""

from app.ai.evaluation.dataset import BENCHMARK_RESUMES, BENCHMARK_JOBS, GroundTruthResume, GroundTruthJob
from app.ai.evaluation.evaluator import AIEvaluationEngine, EvaluationReport, PROMPT_VERSION
from app.ai.evaluation.report import generate_evaluation_markdown
from app.ai.evaluation.metrics import (
    calculate_set_precision_recall_f1,
    calculate_evidence_coverage,
    calculate_hallucination_rate,
    calculate_model_consistency,
)

__all__ = [
    "BENCHMARK_RESUMES",
    "BENCHMARK_JOBS",
    "GroundTruthResume",
    "GroundTruthJob",
    "AIEvaluationEngine",
    "EvaluationReport",
    "PROMPT_VERSION",
    "generate_evaluation_markdown",
    "calculate_set_precision_recall_f1",
    "calculate_evidence_coverage",
    "calculate_hallucination_rate",
    "calculate_model_consistency",
]
