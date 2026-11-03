"""
AI Evaluation Reporting & Export.
Generates structured Markdown and JSON reports for AI evaluation benchmarks.
"""

from typing import Dict, Any
from app.ai.evaluation.evaluator import EvaluationReport


def generate_evaluation_markdown(report: EvaluationReport) -> str:
    """
    Renders an EvaluationReport as a structured Markdown document.
    """
    lines = [
        f"# AI Intelligence Quality Evaluation Report",
        f"**Evaluation ID:** `{report.evaluation_id}`  ",
        f"**Date:** {report.timestamp}  ",
        f"**Provider:** {report.provider_name} ({report.model_name})  ",
        f"**Prompt Version:** `{report.prompt_version}` (`{report.prompt_hash}`)  ",
        f"**Verdict:** **{report.verdict}**  ",
        "",
        "> [!IMPORTANT]",
        f"> {report.calibration_notice}",
        "",
        "## Summary Metrics",
        "",
        "| Metric | Result | Target Benchmark | Status |",
        "| :--- | :--- | :--- | :--- |",
        f"| **Skill Extraction F1** | `{report.mean_f1 * 100:.1f}%` | ≥ 70.0% | {'✅ Pass' if report.mean_f1 >= 0.70 else '❌ Fail'} |",
        f"| **Skill Extraction Precision** | `{report.mean_precision * 100:.1f}%` | ≥ 75.0% | {'✅ Pass' if report.mean_precision >= 0.75 else '❌ Fail'} |",
        f"| **Skill Extraction Recall** | `{report.mean_recall * 100:.1f}%` | ≥ 70.0% | {'✅ Pass' if report.mean_recall >= 0.70 else '❌ Fail'} |",
        f"| **Hallucination Rate** | `{report.mean_hallucination_rate * 100:.1f}%` | ≤ 15.0% | {'✅ Pass' if report.mean_hallucination_rate <= 0.15 else '❌ Fail'} |",
        f"| **Evidence Coverage** | `{report.mean_evidence_coverage * 100:.1f}%` | ≥ 60.0% | {'✅ Pass' if report.mean_evidence_coverage >= 0.60 else '❌ Fail'} |",
        f"| **Schema Validation Rate** | `{report.schema_validation_rate * 100:.1f}%` | 100.0% | {'✅ Pass' if report.schema_validation_rate == 1.0 else '❌ Fail'} |",
        f"| **Average Latency** | `{report.mean_latency_ms:.0f} ms` | ≤ 3000 ms | {'✅ Pass' if report.mean_latency_ms <= 3000 else '⚠️ Slow'} |",
        "",
        "## Case-by-Case Breakdown",
        "",
        "| Case ID | Persona | Status | Precision | Recall | F1 | Hallucination | Score |",
        "| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |",
    ]

    for c in report.case_results:
        lines.append(
            f"| `{c.case_id}` | {c.persona} | {c.status} | {c.precision*100:.1f}% | {c.recall*100:.1f}% | {c.f1*100:.1f}% | {c.hallucination_rate*100:.1f}% | {c.overall_score:.0f}/100 |"
        )

    if report.cross_model_comparison:
        comp = report.cross_model_comparison
        lines.extend([
            "",
            "## Cross-Model Consistency Comparison",
            f"**Model A:** {comp['provider_a']['name']} ({comp['provider_a']['model']})",
            f"**Model B:** {comp['provider_b']['name']} ({comp['provider_b']['model']})",
            f"**Consistency Verdict:** **{comp['comparison_verdict']}**",
            f"- **Mean Absolute Error (MAE):** `{comp['consistency_metrics']['mae']} pts` (Threshold: ≤ 12.0 pts)",
            f"- **Max Score Deviation:** `{comp['consistency_metrics']['max_delta']} pts`",
        ])

    return "\n".join(lines)
