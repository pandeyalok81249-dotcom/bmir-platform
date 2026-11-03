import asyncio
import json
import logging
import re
import time
from typing import Any, Dict, Optional
import httpx
from app.ai.base import AIProviderResponse, BaseAIProvider
from app.ai.sanitization import wrap_candidate_data, wrap_job_data
from app.ai.token_tracker import calculate_cost
from app.core.config import settings
from app.schemas.analysis import ResumeAnalysisResult
from app.schemas.interview import InterviewAnswerEvaluation

logger = logging.getLogger(__name__)


def clean_llm_json_response(raw_text: str) -> str:
    """
    Cleans raw LLM output, stripping markdown code block fences (```json ... ```)
    and any leading/trailing extraneous commentary.
    """
    cleaned = raw_text.strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    elif cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    return cleaned.strip()


class GeminiProvider(BaseAIProvider):
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or settings.GEMINI_API_KEY
        self.model = model or settings.GEMINI_DEFAULT_MODEL
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models"

    @property
    def provider_name(self) -> str:
        return "gemini"

    async def is_available(self) -> bool:
        """
        Non-blocking health check to verify Gemini API key presence and endpoint responsiveness.
        """
        if not self.api_key:
            return False
        url = f"{self.base_url}/{self.model}?key={self.api_key}"
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                res = await client.get(url)
                return res.status_code == 200
        except Exception:
            return False

    async def _generate_content_with_retry(
        self,
        system_instruction: str,
        prompt: str,
        max_retries: int = 3,
        base_backoff_seconds: float = 1.5,
    ) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("Gemini API key is not configured in backend settings.")

        url = f"{self.base_url}/{self.model}:generateContent?key={self.api_key}"
        payload = {
            "system_instruction": {
                "parts": [{"text": system_instruction}]
            },
            "contents": [
                {
                    "parts": [{"text": prompt}]
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.2,
            },
        }

        last_error = None
        for attempt in range(max_retries):
            start_time = time.time()
            try:
                async with httpx.AsyncClient(timeout=60.0) as client:
                    response = await client.post(url, json=payload)

                    if response.status_code == 429:
                        wait_time = base_backoff_seconds * (2 ** attempt)
                        logger.warning(f"Gemini rate limit (429). Retrying in {wait_time}s (attempt {attempt + 1}/{max_retries})...")
                        await asyncio.sleep(wait_time)
                        continue

                    response.raise_for_status()
                    res_data = response.json()

                latency_ms = int((time.time() - start_time) * 1000)
                usage = res_data.get("usageMetadata", {})
                input_tokens = usage.get("promptTokenCount", 0)
                output_tokens = usage.get("candidatesTokenCount", 0)

                candidates = res_data.get("candidates", [])
                if not candidates:
                    raise RuntimeError("Gemini returned empty candidate response.")

                raw_text = candidates[0]["content"]["parts"][0]["text"]
                cleaned_json_text = clean_llm_json_response(raw_text)
                parsed = json.loads(cleaned_json_text)

                return {
                    "parsed": parsed,
                    "input_tokens": input_tokens,
                    "output_tokens": output_tokens,
                    "latency_ms": latency_ms,
                }

            except (httpx.TimeoutException, httpx.NetworkError) as net_err:
                last_error = net_err
                wait_time = base_backoff_seconds * (2 ** attempt)
                logger.warning(f"Gemini connection timeout/error: {net_err}. Retrying in {wait_time}s...")
                await asyncio.sleep(wait_time)

            except httpx.HTTPStatusError as http_err:
                last_error = http_err
                if http_err.response.status_code in [500, 502, 503, 504]:
                    wait_time = base_backoff_seconds * (2 ** attempt)
                    logger.warning(f"Gemini transient 5xx error ({http_err.response.status_code}). Retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    raise

            except json.JSONDecodeError as json_err:
                logger.error(f"Failed to parse Gemini output as JSON: {json_err}. Raw: {raw_text[:200]}")
                raise ValueError(f"Invalid JSON response returned by Gemini model: {str(json_err)}")

        raise RuntimeError(f"Gemini API request failed after {max_retries} retries: {str(last_error)}")

    async def analyze_resume(
        self,
        resume_text: str,
        target_role: Optional[str] = None,
        career_stage: Optional[str] = None,
    ) -> AIProviderResponse:
        system_instruction = (
            "You are an expert career intelligence auditor and principal technical recruiter. "
            "Perform an evidence-grounded, honest analysis of the candidate's resume. "
            "CRITICAL RULES:\n"
            "1. NEVER invent achievements, metrics, degrees, or employers.\n"
            "2. If an achievement lacks quantified impact, cite the exact source text and recommend verified improvement.\n"
            "3. Ground all findings in real extracted evidence.\n"
            "4. Return valid JSON strictly matching the ResumeAnalysisResult schema: "
            "{\n"
            "  'overall_score': float (0-100),\n"
            "  'score_breakdown': {'structure': float, 'ats_compatibility': float, 'skills_evidence': float},\n"
            "  'summary_evaluation': str,\n"
            "  'key_strengths': list[str],\n"
            "  'priority_improvements': list[str],\n"
            "  'sections': [\n"
            "    {\n"
            "      'section_name': str,\n"
            "      'completeness_score': float (0-100),\n"
            "      'strengths': list[str],\n"
            "      'weaknesses': list[str],\n"
            "      'findings': [\n"
            "        {\n"
            "          'finding': str,\n"
            "          'severity': str ('info'|'warning'|'critical'|'strength'),\n"
            "          'source_section': str,\n"
            "          'source_text': str,\n"
            "          'recommendation': str\n"
            "        }\n"
            "      ]\n"
            "    }\n"
            "  ],\n"
            "  'skills_extracted': [\n"
            "    {\n"
            "      'skill_name': str,\n"
            "      'category': str ('technical'|'soft'|'domain'|'tool'),\n"
            "      'demonstrated_in_resume': bool,\n"
            "      'evidence_source_text': str,\n"
            "      'confidence_score': float (0.0 - 1.0)\n"
            "    }\n"
            "  ],\n"
            "  'ats_analysis': {\n"
            "    'ats_compatibility_score': float (0-100),\n"
            "    'formatting_issues': list[str],\n"
            "    'header_clarity_score': float (0-100),\n"
            "    'keyword_readability': str,\n"
            "    'table_column_warnings': list[str],\n"
            "    'contact_info_detected': {'email': bool, 'phone': bool}\n"
            "  },\n"
            "  'truthfulness_notes': list,\n"
            "  'methodology_notes': str\n"
            "}"
        )
        prompt = (
            f"Candidate Target Role: {target_role or 'General'}\n"
            f"Candidate Career Stage: {career_stage or 'Professional'}\n\n"
            f"{wrap_candidate_data(resume_text)}"
        )

        res = await self._generate_content_with_retry(system_instruction, prompt)
        cost = calculate_cost(self.model, res["input_tokens"], res["output_tokens"])
        validated = ResumeAnalysisResult.model_validate(res["parsed"])

        return AIProviderResponse(
            provider=self.provider_name,
            model=self.model,
            content=validated,
            input_tokens=res["input_tokens"],
            output_tokens=res["output_tokens"],
            latency_ms=res["latency_ms"],
            estimated_cost_usd=cost,
        )

    async def extract_job_requirements(self, job_text: str) -> AIProviderResponse:
        system_instruction = (
            "You are an expert job description requirements extractor. "
            "Extract actual requirements stated in the posting without inventing extra skills. "
            "Output JSON: {'job_title': str, 'min_experience_years': float, 'required_skills': list[str], "
            "'preferred_skills': list[str], 'required_education': list[str], 'key_responsibilities': list[str]}."
        )
        res = await self._generate_content_with_retry(system_instruction, wrap_job_data(job_text))
        cost = calculate_cost(self.model, res["input_tokens"], res["output_tokens"])
        return AIProviderResponse(
            provider=self.provider_name,
            model=self.model,
            content=res["parsed"],
            input_tokens=res["input_tokens"],
            output_tokens=res["output_tokens"],
            latency_ms=res["latency_ms"],
            estimated_cost_usd=cost,
        )

    async def improve_bullet(
        self, bullet_text: str, target_role: Optional[str] = None
    ) -> AIProviderResponse:
        system_instruction = (
            "You are a professional resume editor. Rewrite this bullet point using the STAR method. "
            "CRITICAL: Do NOT invent fake metrics, numbers, or percentages. If impact is qualitative, explain the engineering or operational context. "
            "Output JSON: {'original': str, 'improved': str, 'action_verb_used': str, 'rationale': str, 'missing_metric_prompt': str}."
        )
        prompt = f"Target Role: {target_role or 'General'}\nBullet: {bullet_text}"
        res = await self._generate_content_with_retry(system_instruction, prompt)
        cost = calculate_cost(self.model, res["input_tokens"], res["output_tokens"])
        return AIProviderResponse(
            provider=self.provider_name,
            model=self.model,
            content=res["parsed"],
            input_tokens=res["input_tokens"],
            output_tokens=res["output_tokens"],
            latency_ms=res["latency_ms"],
            estimated_cost_usd=cost,
        )

    async def evaluate_interview_answer(
        self, question: str, answer: str, role: str
    ) -> AIProviderResponse:
        system_instruction = (
            "You are a senior hiring manager. Evaluate the candidate's interview response against STAR criteria. "
            "Output JSON: {'question_id': str, 'clarity_score': float, 'star_method_adherence': str, "
            "'strengths': list[str], 'improvement_areas': list[str], 'improved_answer_sample': str}."
        )
        prompt = f"Role: {role}\nQuestion: {question}\nAnswer: {answer}"
        res = await self._generate_content_with_retry(system_instruction, prompt)
        cost = calculate_cost(self.model, res["input_tokens"], res["output_tokens"])
        return AIProviderResponse(
            provider=self.provider_name,
            model=self.model,
            content=res["parsed"],
            input_tokens=res["input_tokens"],
            output_tokens=res["output_tokens"],
            latency_ms=res["latency_ms"],
            estimated_cost_usd=cost,
        )
