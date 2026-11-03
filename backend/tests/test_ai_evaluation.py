import pytest
from app.ai.evaluation.dataset import BENCHMARK_RESUMES, BENCHMARK_JOBS
from app.ai.evaluation.metrics import (
    calculate_set_precision_recall_f1,
    calculate_evidence_coverage,
    calculate_hallucination_rate,
    calculate_model_consistency,
)
from app.ai.evaluation.evaluator import AIEvaluationEngine, PROMPT_VERSION
from app.ai.evaluation.report import generate_evaluation_markdown
from app.ai.base import BaseAIProvider, AIProviderResponse
from app.schemas.analysis import ResumeAnalysisResult, SkillEvidenceItem, ATSAssessment


class MockEvalAIProvider(BaseAIProvider):
    def __init__(self, name: str = "mock_eval_provider", score_offset: float = 0.0):
        self._name = name
        self.score_offset = score_offset
        self.model = "mock-model-v3"

    @property
    def provider_name(self) -> str:
        return self._name

    async def analyze_resume(self, resume_text: str, target_role=None, career_stage=None) -> AIProviderResponse:
        # Detect some skills present in the resume
        detected = []
        for word in ["Go", "Python", "SQL", "Docker", "Kubernetes", "PostgreSQL", "Redis", "Apache Kafka", "React", "TypeScript", "PyTorch"]:
            if word.lower() in resume_text.lower():
                detected.append(
                    SkillEvidenceItem(
                        skill_name=word,
                        category="technical",
                        demonstrated_in_resume=True,
                        evidence_source_text=f"Demonstrated {word} in production",
                        confidence_score=0.95
                    )
                )

        base_score = 85.0 + self.score_offset
        result = ResumeAnalysisResult(
            overall_score=min(100.0, max(0.0, base_score)),
            score_breakdown={
                "content": 80.0,
                "relevance": 85.0,
                "evidence": 82.0,
                "readability": 88.0,
                "structure": 86.0
            },
            summary_evaluation="Strong profile with verified engineering metrics.",
            key_strengths=["Senior Backend Engineer with 7 years of experience building fault-tolerant distributed microservices"],
            priority_improvements=["Ensure vague claim has explicit metric verification: Single-handedly revolutionized retention"],
            sections=[],
            skills_extracted=detected,
            ats_analysis=ATSAssessment(
                ats_compatibility_score=90.0,
                formatting_issues=[],
                header_clarity_score=95.0,
                keyword_readability="high",
                table_column_warnings=[],
                contact_info_detected={"email": True, "location": True}
            ),
            truthfulness_notes=[]
        )
        return AIProviderResponse(
            provider=self._name,
            model=self.model,
            content=result,
            input_tokens=450,
            output_tokens=180,
            latency_ms=210,
            estimated_cost_usd=0.0012
        )

    async def extract_job_requirements(self, job_text: str) -> AIProviderResponse:
        return AIProviderResponse(provider=self._name, model=self.model, content={})

    async def improve_bullet(self, bullet_text: str, target_role=None) -> AIProviderResponse:
        return AIProviderResponse(provider=self._name, model=self.model, content={})

    async def evaluate_interview_answer(self, question: str, answer: str, role: str) -> AIProviderResponse:
        return AIProviderResponse(provider=self._name, model=self.model, content={})


def test_metrics_precision_recall_f1():
    ground_truth = ["Python", "FastAPI", "PostgreSQL", "Docker", "Kubernetes"]
    predicted = ["Python", "Docker", "Kubernetes", "React"]  # 3 TP, 1 FP, 2 FN

    metrics = calculate_set_precision_recall_f1(predicted, ground_truth)
    assert metrics["precision"] == 0.75
    assert metrics["recall"] == 0.60
    assert 0.66 <= metrics["f1"] <= 0.67
    assert metrics["true_positives"] == 3
    assert metrics["false_positives"] == 1
    assert metrics["false_negatives"] == 2


def test_hallucination_rate():
    raw_text = "Experienced with Python, Django, and PostgreSQL backend systems."
    skills = ["Python", "PostgreSQL", "Blockchain", "Quantum Computing"]

    res = calculate_hallucination_rate(skills, raw_text)
    assert res["hallucination_rate"] == 0.5  # 2 hallucinated out of 4
    assert "Blockchain" in res["hallucinated_skills"]
    assert "Quantum Computing" in res["hallucinated_skills"]


def test_evidence_coverage():
    resume_text = "Designed and deployed high-throughput event streaming platform using Apache Kafka and Go."
    items = [
        {"text": "event streaming platform using Apache Kafka and Go"},
        {"text": "completely fabricated machine learning pipeline with no mention"},
    ]
    cov = calculate_evidence_coverage(items, resume_text)
    assert cov["coverage_ratio"] == 0.5
    assert cov["grounded_items"] == 1


def test_model_consistency():
    model_a = {"case_1": 85.0, "case_2": 90.0, "case_3": 75.0}
    model_b = {"case_1": 82.0, "case_2": 88.0, "case_3": 78.0}

    consistency = calculate_model_consistency(model_a, model_b)
    # MAE = (|85-82| + |90-88| + |75-78|) / 3 = (3 + 2 + 3) / 3 = 8/3 = 2.67
    assert consistency["mae"] == 2.67
    assert consistency["max_delta"] == 3.0
    assert consistency["is_consistent"] is True


@pytest.mark.asyncio
async def test_ai_evaluation_engine_run():
    provider = MockEvalAIProvider("test_gemini")
    engine = AIEvaluationEngine(prompt_version=PROMPT_VERSION)

    report = await engine.evaluate_provider(provider, dataset=BENCHMARK_RESUMES[:2])
    assert report.total_cases == 2
    assert report.passed_cases == 2
    assert report.schema_validation_rate == 1.0
    assert report.mean_f1 > 0.0
    assert report.verdict in ["PASSED", "CONDITIONAL_PASS"]
    assert "AI evaluation confidence scores represent heuristic match indices" in report.calibration_notice

    # Test markdown report generation
    md = generate_evaluation_markdown(report)
    assert "# AI Intelligence Quality Evaluation Report" in md
    assert "Skill Extraction F1" in md
    assert report.prompt_version in md


@pytest.mark.asyncio
async def test_cross_model_comparison():
    provider_a = MockEvalAIProvider("gpt_4o", score_offset=0.0)
    provider_b = MockEvalAIProvider("gemini_1_5_pro", score_offset=4.0)

    engine = AIEvaluationEngine()
    comparison_result = await engine.compare_providers(provider_a, provider_b, dataset=BENCHMARK_RESUMES[:2])

    assert "report_a" in comparison_result
    assert "report_b" in comparison_result
    comp = comparison_result["comparison"]
    assert comp["comparison_verdict"] == "CONSISTENT"
    assert comp["consistency_metrics"]["mae"] == 4.0
