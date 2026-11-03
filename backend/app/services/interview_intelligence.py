import re
import uuid
from typing import Any, Dict, List, Optional

from app.schemas.interview import (
    FollowUpQuestionResponse,
    InterviewAnswerEvaluation,
    InterviewQuestion,
    InterviewSessionSummary,
    STARBreakdown,
)


class InterviewIntelligenceEngine:
    """
    Enterprise-grade Interview Intelligence Engine providing:
    - Adaptive resume-grounded question synthesis (technical, behavioral, deep-dive, situational)
    - Full STAR (Situation, Task, Action, Result) rubric evaluation with granular scoring
    - Contextual follow-up question generation targeting weak response components
    - Comprehensive session summary and interview readiness diagnostics
    """

    TECH_PATTERNS = [
        "python", "fastapi", "django", "flask", "docker", "kubernetes", "k8s",
        "react", "vue", "angular", "typescript", "javascript", "golang", "go",
        "postgresql", "postgres", "sql", "redis", "mongodb", "aws", "gcp",
        "azure", "kafka", "graphql", "rest", "microservices", "ci/cd", "terraform",
    ]

    def _extract_skills(self, text: str) -> List[str]:
        if not text:
            return []
        lower = text.lower()
        extracted = []
        for pattern in self.TECH_PATTERNS:
            if re.search(rf"\b{re.escape(pattern)}\b", lower):
                extracted.append(pattern.title() if pattern not in ["aws", "gcp", "ci/cd", "sql"] else pattern.upper())
        return extracted

    def generate_adaptive_questions(
        self,
        target_role: str,
        resume_text: str = "",
        focus_areas: Optional[List[str]] = None,
        count: int = 5,
    ) -> List[InterviewQuestion]:
        extracted_skills = self._extract_skills(resume_text)
        focus = focus_areas or []
        combined_skills = list(dict.fromkeys(focus + extracted_skills))
        
        primary_skill = combined_skills[0] if combined_skills else "distributed systems"
        secondary_skill = combined_skills[1] if len(combined_skills) > 1 else "cloud infrastructure"

        questions: List[InterviewQuestion] = []

        # 1. Technical Domain Question
        questions.append(
            InterviewQuestion(
                id=str(uuid.uuid4()),
                category="technical",
                question=f"When architecting scalable services with {primary_skill} for a {target_role} role, how do you manage concurrency, data consistency, and failure recovery under high throughput?",
                context_from_resume=f"Grounded in candidate's background with {primary_skill}",
                evaluation_criteria=[
                    f"Proficiency in {primary_skill} core semantics and concurrency models",
                    "System trade-offs between consistency and latency",
                    "Resilience patterns (circuit breakers, idempotency, retry budgets)",
                ],
                difficulty="medium",
            )
        )

        # 2. Experience Deep-Dive Question
        questions.append(
            InterviewQuestion(
                id=str(uuid.uuid4()),
                category="experience_deep_dive",
                question=f"Can you walk me through the most technically complex feature or pipeline you implemented using {secondary_skill}? What was your specific architectural contribution and what obstacles did you navigate?",
                context_from_resume=f"Derived from practical engineering impact with {secondary_skill}",
                evaluation_criteria=[
                    "Clear articulation of personal technical ownership",
                    "Handling unexpected production anomalies or bottlenecks",
                    "Quantifiable delivery impact",
                ],
                difficulty="hard",
            )
        )

        # 3. Behavioral Leadership / Conflict Question
        questions.append(
            InterviewQuestion(
                id=str(uuid.uuid4()),
                category="behavioral",
                question="Describe a scenario where you had a strong technical disagreement with a team member or stakeholder regarding system architecture or technical debt. How did you advocate for your position and reach a resolution?",
                context_from_resume="Core behavioral evaluation for engineering collaboration and influence",
                evaluation_criteria=[
                    "STAR structured response with respectful technical communication",
                    "Objective data-driven trade-off analysis over personal bias",
                    "Constructive consensus-building and commitment to delivery",
                ],
                difficulty="medium",
            )
        )

        # 4. Situational / Crisis Management Question
        questions.append(
            InterviewQuestion(
                id=str(uuid.uuid4()),
                category="situational",
                question=f"Imagine a critical production service for {target_role} starts experiencing intermittent 5xx errors and memory leaks after an urgent Friday evening deployment. What is your step-by-step containment, debugging, and mitigation strategy?",
                context_from_resume="Operational readiness and incident response diagnostics",
                evaluation_criteria=[
                    "Fast customer impact containment (rollback vs hotfix triage)",
                    "Systematic observability inspection (logs, traces, metrics, heap dumps)",
                    "Blameless post-mortem prevention planning",
                ],
                difficulty="hard",
            )
        )

        # 5. Strategic / Career Trajectory Question
        questions.append(
            InterviewQuestion(
                id=str(uuid.uuid4()),
                category="experience_deep_dive",
                question=f"Looking back at your recent engineering work, what is one major technical decision you made that you would implement differently today, and what insights led to that perspective?",
                context_from_resume="Continuous learning and architectural maturity",
                evaluation_criteria=[
                    "Introspection and intellectual honesty",
                    "Evolution of technical judgment over time",
                    "Long-term maintainability considerations",
                ],
                difficulty="staff" if "lead" in target_role.lower() or "senior" in target_role.lower() else "medium",
            )
        )

        return questions[:count]

    def evaluate_star_answer(
        self,
        question: str,
        answer: str,
        category: str = "behavioral",
        target_role: str = "",
    ) -> InterviewAnswerEvaluation:
        text = answer.strip()
        lower = text.lower()
        word_count = len(text.split())

        # Situation evaluation
        situation_keywords = ["when", "at my previous", "our team", "we were facing", "context", "background", "project", "client", "problem was"]
        has_situation = any(k in lower for k in situation_keywords)
        situation_score = 9.0 if (has_situation and word_count >= 40) else (6.5 if has_situation else 4.0)
        situation_feedback = (
            "Well-defined context with clear environmental and operational scope."
            if situation_score >= 8.0
            else "Context could be clearer; specify the business stakes, constraints, and project timeline."
        )

        # Task evaluation
        task_keywords = ["my role", "my task", "responsible for", "responsibility", "responsible", "objective", "needed to", "goal", "challenge was", "mandate", "assigned to", "ensuring", "focus was"]
        has_task = any(k in lower for k in task_keywords)
        task_score = 8.5 if (has_task and word_count >= 30) else (6.0 if has_task else 4.5)
        task_feedback = (
            "Explicitly defines individual responsibility and clear success criteria."
            if task_score >= 8.0
            else "Clarify your exact individual objective vs the broader team mandate."
        )

        # Action evaluation
        action_keywords = ["i designed", "i implemented", "i architected", "i resolved", "i led", "i investigated", "i created", "i analyzed", "i refactored", "i optimized", "i evaluated", "i built", "i developed"]
        action_verbs = ["designed", "implemented", "architected", "resolved", "led", "investigated", "created", "analyzed", "refactored", "optimized", "evaluated", "built", "developed"]
        verbs_present = sum(1 for v in action_verbs if re.search(rf"\b{v}\b", lower))
        first_person_actions = sum(1 for k in action_keywords if k in lower)
        has_first_person = " i " in lower or lower.startswith("i ") or "\ni " in lower
        
        if first_person_actions >= 2 or (has_first_person and verbs_present >= 2):
            action_score = 9.5
        elif first_person_actions == 1 or (has_first_person and verbs_present >= 1):
            action_score = 8.5
        elif has_first_person:
            action_score = 7.0
        else:
            action_score = 4.0
        
        action_feedback = (
            "Strong personal agency highlighted with crisp action verbs and technical specifics."
            if action_score >= 8.0
            else "Elevate personal ownership; specify what *you* designed and executed rather than collective team efforts."
        )

        # Result evaluation
        result_keywords = ["result", "reduced", "increased", "achieved", "delivered", "outcome", "percent", "%", "ms", "savings", "improved", "metric"]
        metric_matches = re.findall(r"\b\d+([.,]\d+)?\s*(%|x|ms|s|hours|days|k|m|usd|\$)?\b", lower)
        has_quant = len(metric_matches) > 0
        has_result = any(k in lower for k in result_keywords)
        
        if has_result and has_quant:
            result_score = 9.5
            result_feedback = "Exceptional quantified outcomes providing tangible business impact and metric verification."
        elif has_result:
            result_score = 7.0
            result_feedback = "Qualitative outcome stated, but lacks quantified metrics (e.g. latency reduction %, throughput, dollar savings)."
        else:
            result_score = 3.5
            result_feedback = "Missing distinct outcome or business result. Conclude with concrete impact delivered."

        # Clarity
        clarity_score = 9.0 if (word_count >= 60 and word_count <= 250) else (7.0 if word_count >= 30 else 4.0)

        # Overall weighted score
        overall = (
            situation_score * 0.20
            + task_score * 0.15
            + action_score * 0.35
            + result_score * 0.30
        ) * 10.0
        overall = round(min(100.0, max(0.0, overall)), 1)

        # STAR adherence tier
        star_count = sum(1 for s in [situation_score >= 6.0, task_score >= 6.0, action_score >= 6.0, result_score >= 6.0] if s)
        star_adherence = "Strong" if star_count == 4 else ("Moderate" if star_count >= 2 else "Weak")

        # Strengths & improvements
        strengths = []
        improvements = []

        if action_score >= 7.5:
            strengths.append("High personal accountability with explicit implementation details.")
        if result_score >= 7.5:
            strengths.append("Grounded in verified results and tangible business value.")
        if situation_score >= 7.5:
            strengths.append("Clear scene-setting that frames technical complexity effectively.")
        if not strengths:
            strengths.append("Directly engaged with the interview prompt.")

        if result_score < 7.5:
            improvements.append("Quantify the final result: specify metrics like % latency drop, cost saved, or user adoption.")
        if action_score < 7.5:
            improvements.append("Replace passive phrases ('it was decided') with active first-person execution ('I evaluated X and chose Y').")
        if situation_score < 7.5:
            improvements.append("Set up the initial stakes clearly before jumping directly into the technical solution.")

        # Improved sample answer
        improved_sample = (
            f"[Situation] In my previous role, our team needed to enhance our {category} capabilities. "
            f"[Task] I was tasked with redesigning the bottlenecked components to ensure resilience. "
            f"[Action] I conducted root-cause benchmarking, designed an asynchronous processing pattern, "
            f"and implemented robust fallback caching with comprehensive automated test suites. "
            f"[Result] As a result, we reduced error rates by 42% and delivered 99.95% system uptime under peak loads."
        )

        # Follow-up recommendation
        weakest = min(
            [("situation", situation_score), ("task", task_score), ("action", action_score), ("result", result_score)],
            key=lambda x: x[1],
        )
        follow_up_rec = f"Prompt for deeper evidence on the {weakest[0]} dimension."

        return InterviewAnswerEvaluation(
            question_id="",
            clarity_score=clarity_score,
            overall_score=overall,
            star_method_adherence=star_adherence,
            star_breakdown=STARBreakdown(
                situation_score=situation_score,
                situation_feedback=situation_feedback,
                task_score=task_score,
                task_feedback=task_feedback,
                action_score=action_score,
                action_feedback=action_feedback,
                result_score=result_score,
                result_feedback=result_feedback,
            ),
            strengths=strengths,
            improvement_areas=improvements,
            improved_answer_sample=improved_sample,
            follow_up_recommendation=follow_up_rec,
        )

    def generate_follow_up_question(
        self,
        question: str,
        answer: str,
        weakest_area: Optional[str] = None,
    ) -> FollowUpQuestionResponse:
        area = (weakest_area or "result").lower()

        if "result" in area:
            f_q = "What specific, quantifiable metrics (e.g. latency drop, conversion gain, throughput increase) best demonstrate the business impact of that work?"
            rationale = "Candidate provided qualitative answer; probing for quantitative rigor."
        elif "action" in area:
            f_q = "What were the major technical alternatives or trade-offs you evaluated before committing to that specific implementation?"
            rationale = "Candidate summarized the outcome; probing for technical depth and design decision-making."
        elif "situation" in area or "task" in area:
            f_q = "What were the organizational or business constraints (e.g. tight deadlines, legacy tech, regulatory requirements) that made this problem particularly challenging?"
            rationale = "Probing for context and situational complexity framing."
        else:
            f_q = "If you had to scale this architecture 10x today, what single failure mode would you address first?"
            rationale = "Probing for forward-looking engineering foresight and scalability instincts."

        return FollowUpQuestionResponse(
            follow_up_id=str(uuid.uuid4()),
            parent_question_id="",
            question=f_q,
            target_star_component=area,
            rationale=rationale,
        )

    def summarize_session(
        self,
        session_id: str,
        target_role: str,
        answers: List[Dict[str, Any]],
    ) -> InterviewSessionSummary:
        total = len(answers)
        if total == 0:
            return InterviewSessionSummary(
                session_id=session_id,
                target_role=target_role,
                total_questions_answered=0,
                average_overall_score=0.0,
                star_competency_scores={"situation": 0.0, "task": 0.0, "action": 0.0, "result": 0.0},
                category_scores={},
                top_strengths=["No answers evaluated yet."],
                priority_improvements=["Complete at least one practice question."],
                readiness_verdict="Incomplete Session",
            )

        overall_scores = []
        sit_scores = []
        task_scores = []
        act_scores = []
        res_scores = []
        cat_scores_map: Dict[str, List[float]] = {}
        all_strengths: List[str] = []
        all_improvements: List[str] = []

        for item in answers:
            eval_data = item.get("evaluation") or {}
            overall = eval_data.get("overall_score", 70.0)
            overall_scores.append(overall)

            category = item.get("category", "general")
            cat_scores_map.setdefault(category, []).append(overall)

            bd = eval_data.get("star_breakdown") or {}
            sit_scores.append(bd.get("situation_score", 7.0))
            task_scores.append(bd.get("task_score", 7.0))
            act_scores.append(bd.get("action_score", 7.0))
            res_scores.append(bd.get("result_score", 7.0))

            all_strengths.extend(eval_data.get("strengths", []))
            all_improvements.extend(eval_data.get("improvement_areas", []))

        avg_overall = round(sum(overall_scores) / total, 1)
        star_comp = {
            "situation": round(sum(sit_scores) / total, 1),
            "task": round(sum(task_scores) / total, 1),
            "action": round(sum(act_scores) / total, 1),
            "result": round(sum(res_scores) / total, 1),
        }
        category_scores = {
            cat: round(sum(scores) / len(scores), 1)
            for cat, scores in cat_scores_map.items()
        }

        # Deduplicate top strengths & improvements
        top_strengths = list(dict.fromkeys(all_strengths))[:3]
        priority_improvements = list(dict.fromkeys(all_improvements))[:3]

        if avg_overall >= 85.0:
            verdict = "Ready for Senior & Staff Interview Loops"
        elif avg_overall >= 70.0:
            verdict = "Interview Ready — Focus on Metric Quantization"
        else:
            verdict = "Needs Structured Practice on STAR Methodology"

        return InterviewSessionSummary(
            session_id=session_id,
            target_role=target_role,
            total_questions_answered=total,
            average_overall_score=avg_overall,
            star_competency_scores=star_comp,
            category_scores=category_scores,
            top_strengths=top_strengths,
            priority_improvements=priority_improvements,
            readiness_verdict=verdict,
        )


interview_intelligence_engine = InterviewIntelligenceEngine()
