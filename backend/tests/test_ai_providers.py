import json
import pytest
from unittest.mock import AsyncMock, patch
import httpx

from app.ai.providers.gemini_provider import GeminiProvider, clean_llm_json_response
from app.ai.providers.openai_provider import OpenAIProvider
from app.ai.token_tracker import calculate_cost
from app.schemas.analysis import ResumeAnalysisResult

MOCK_ANALYSIS_JSON = {
    "overall_score": 88.5,
    "score_breakdown": {
        "structure": 90.0,
        "ats_compatibility": 85.0,
        "skills_evidence": 90.5
    },
    "summary_evaluation": "High-impact senior software engineering profile with strong distributed backend evidence.",
    "key_strengths": [
        "Consistent demonstration of FastAPI and distributed microservices architecture",
        "Clear quantifiable metrics across past projects"
    ],
    "priority_improvements": [
        "Include CI/CD deployment pipeline specifics"
    ],
    "sections": [
        {
            "section_name": "Experience",
            "completeness_score": 95.0,
            "strengths": ["Strong action verbs and metrics"],
            "weaknesses": [],
            "findings": [
                {
                    "finding": "Excellent STAR achievement description.",
                    "severity": "strength",
                    "source_section": "Experience",
                    "source_text": "Architected high-throughput REST API using FastAPI",
                    "recommendation": "Maintain this level of quantified technical precision."
                }
            ]
        }
    ],
    "skills_extracted": [
        {
            "skill_name": "FastAPI",
            "category": "technical",
            "demonstrated_in_resume": True,
            "evidence_source_text": "Architected high-throughput REST API using FastAPI",
            "confidence_score": 1.0
        },
        {
            "skill_name": "Python",
            "category": "technical",
            "demonstrated_in_resume": True,
            "evidence_source_text": "Python backend microservices",
            "confidence_score": 1.0
        },
        {
            "skill_name": "Docker",
            "category": "tool",
            "demonstrated_in_resume": True,
            "evidence_source_text": "Containerized microservices using Docker",
            "confidence_score": 1.0
        },
        {
            "skill_name": "PostgreSQL",
            "category": "technical",
            "demonstrated_in_resume": True,
            "evidence_source_text": "Relational data layers and query latencies",
            "confidence_score": 0.95
        },
        {
            "skill_name": "Flutter",
            "category": "technical",
            "demonstrated_in_resume": True,
            "evidence_source_text": "Developed cross-platform client using Flutter and Dart",
            "confidence_score": 1.0
        },
        {
            "skill_name": "Kubernetes",
            "category": "tool",
            "demonstrated_in_resume": True,
            "evidence_source_text": "Orchestrated automated deployments with Kubernetes",
            "confidence_score": 0.9
        }
    ],
    "ats_analysis": {
        "ats_compatibility_score": 92.0,
        "formatting_issues": [],
        "header_clarity_score": 95.0,
        "keyword_readability": "High",
        "table_column_warnings": [],
        "contact_info_detected": {"email": True, "phone": True}
    },
    "truthfulness_notes": [],
    "methodology_notes": "Mocked validation test run"
}


def test_clean_llm_json_response():
    # Markdown json fence stripping
    raw_markdown = f"```json\n{json.dumps(MOCK_ANALYSIS_JSON)}\n```"
    cleaned = clean_llm_json_response(raw_markdown)
    parsed = json.loads(cleaned)
    assert parsed["overall_score"] == 88.5

    # Standard json without fences
    raw_plain = json.dumps(MOCK_ANALYSIS_JSON)
    cleaned_plain = clean_llm_json_response(raw_plain)
    assert json.loads(cleaned_plain)["overall_score"] == 88.5


def test_token_cost_calculation():
    # gpt-4o-mini pricing: input 0.15/M, output 0.60/M
    cost = calculate_cost("gpt-4o-mini", 10000, 2000)
    assert cost > 0.0
    assert cost < 0.01


@pytest.mark.asyncio
async def test_gemini_provider_structured_output():
    provider = GeminiProvider(api_key="mock_gemini_key", model="gemini-1.5-flash")

    mock_response_payload = {
        "candidates": [
            {
                "content": {
                    "parts": [{"text": json.dumps(MOCK_ANALYSIS_JSON)}]
                }
            }
        ],
        "usageMetadata": {
            "promptTokenCount": 1200,
            "candidatesTokenCount": 450
        }
    }

    mock_resp = httpx.Response(
        status_code=200,
        json=mock_response_payload,
        request=httpx.Request("POST", "https://mock.url"),
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        result = await provider.analyze_resume(
            resume_text="Senior Engineer with Python and FastAPI experience.",
            target_role="Senior Backend Architect",
        )

        assert result.provider == "gemini"
        assert result.model == "gemini-1.5-flash"
        assert isinstance(result.content, ResumeAnalysisResult)
        assert result.content.overall_score == 88.5
        assert result.input_tokens == 1200
        assert result.output_tokens == 450


@pytest.mark.asyncio
async def test_openai_provider_structured_output():
    provider = OpenAIProvider(api_key="mock_openai_key", model="gpt-4o-mini")

    mock_response_payload = {
        "choices": [
            {
                "message": {
                    "content": json.dumps(MOCK_ANALYSIS_JSON)
                }
            }
        ],
        "usage": {
            "prompt_tokens": 1500,
            "completion_tokens": 500
        }
    }

    mock_resp = httpx.Response(
        status_code=200,
        json=mock_response_payload,
        request=httpx.Request("POST", "https://mock.url"),
    )

    with patch("httpx.AsyncClient.post", new_callable=AsyncMock) as mock_post:
        mock_post.return_value = mock_resp

        result = await provider.analyze_resume(
            resume_text="Senior Engineer with Python and FastAPI experience.",
            target_role="Senior Backend Architect",
        )

        assert result.provider == "openai"
        assert result.model == "gpt-4o-mini"
        assert isinstance(result.content, ResumeAnalysisResult)
        assert result.content.overall_score == 88.5
        assert result.input_tokens == 1500
        assert result.output_tokens == 500
