"""
Career Trajectory Simulator Service.
Models simultaneous multi-target role transitions, estimating ramp-up time,
friction tiers, and skill overlap against verified market profiles.
"""

from typing import List, Dict, Any, Optional

from app.schemas.trajectory_simulator import (
    RoleTrajectorySimulation,
    TrajectorySimulatorResponse,
    TRAJECTORY_SIMULATOR_DISCLAIMER
)
from app.services.market_intelligence import JobMarketIntelligenceService


class CareerTrajectorySimulatorService:
    def __init__(self):
        self.market_service = JobMarketIntelligenceService()

    def simulate_trajectories(
        self,
        candidate_id: str,
        user_skills: List[str],
        user_experience_years: float,
        target_roles: List[str]
    ) -> TrajectorySimulatorResponse:
        """
        Simulates transition paths for 1-5 target roles simultaneously.
        """
        simulations: List[RoleTrajectorySimulation] = []

        for role in target_roles:
            gap_res = self.market_service.analyze_market_fit(
                target_role=role,
                user_skills=user_skills,
                user_experience_years=user_experience_years
            )

            skill_score = gap_res.market_match_score
            median_exp = gap_res.market_median_experience_years

            # Experience relevance
            if user_experience_years >= median_exp:
                exp_score = min(100.0, 85.0 + (user_experience_years - median_exp) * 3.0)
            else:
                exp_score = max(30.0, 85.0 - (median_exp - user_experience_years) * 15.0)

            # Project relevance heuristic from skill score
            proj_score = round(min(100.0, skill_score * 0.95 + (10.0 if user_experience_years >= 3.0 else 0.0)), 1)
            edu_score = 88.0

            # Composite overall readiness score
            # 50% skills, 30% experience, 15% projects, 5% education
            overall_readiness = round(
                skill_score * 0.50 + exp_score * 0.30 + proj_score * 0.15 + edu_score * 0.05,
                1
            )

            # Friction level & ramp-up time
            if overall_readiness >= 80.0:
                friction = "low"
                ramp_up = "1-3 months (immediate bridge via portfolio reinforcement)"
            elif overall_readiness >= 65.0:
                friction = "moderate"
                ramp_up = "3-6 months (targeted technical skill building)"
            elif overall_readiness >= 45.0:
                friction = "high"
                ramp_up = "6-12 months (structured domain training & side projects)"
            else:
                friction = "very_high"
                ramp_up = "12-18 months (foundational career pivot requirement)"

            crit_gaps = [sk.skill_name for sk in gap_res.missing_critical_skills]
            priority_actions = gap_res.actionable_recommendations

            simulations.append(
                RoleTrajectorySimulation(
                    target_role=role,
                    overall_readiness_score=overall_readiness,
                    transition_friction=friction,
                    estimated_ramp_up_time=ramp_up,
                    skill_alignment_score=skill_score,
                    experience_relevance_score=round(exp_score, 1),
                    project_relevance_score=proj_score,
                    education_alignment_score=edu_score,
                    transferable_skills=gap_res.matching_skills,
                    critical_skill_gaps=crit_gaps,
                    priority_learning_actions=priority_actions
                )
            )

        # Sort simulations by highest readiness score
        simulations.sort(key=lambda s: s.overall_readiness_score, reverse=True)
        best_path = simulations[0].target_role if simulations else "None"

        summary = (
            f"Evaluated {len(target_roles)} potential role paths for candidate with {user_experience_years:.1f} years of experience. "
            f"The lowest-friction transition is '{best_path}' with a readiness index of {simulations[0].overall_readiness_score}/100. "
            f"{'Identified critical bridge skill: ' + simulations[0].critical_skill_gaps[0] if simulations[0].critical_skill_gaps else 'Demonstrates high direct alignment across core requirements.'}"
        )

        return TrajectorySimulatorResponse(
            candidate_id=candidate_id,
            current_experience_years=user_experience_years,
            simulations=simulations,
            optimal_recommended_path=best_path,
            comparative_summary=summary
        )
