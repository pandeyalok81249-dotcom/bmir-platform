from typing import Any, Dict, List, Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_bmir_user, require_bmir_role
from app.core.database import get_db
from app.models.bmir import BMIRUser, FeasibilityEvaluation, InnovationRoadmap, Innovation, AuditLog

router = APIRouter(prefix="/bmir/intelligence", tags=["bmir-intelligence"])


class FeasibilityInput(BaseModel):
    innovation_id: Optional[str] = None
    title: str
    scientific_feasibility: float
    engineering_feasibility: float
    material_availability: float
    manufacturing_readiness: float
    development_complexity: float
    energy_efficiency: float
    economic_viability: float
    environmental_impact: float
    safety_compliance: float
    limitations_and_risks: Optional[str] = None
    prerequisites: Optional[str] = None
    confidence_level: str = "Medium"


class RoadmapGenerateInput(BaseModel):
    innovation_id: Optional[str] = None
    title: str
    phases: List[Dict[str, Any]]
    estimated_timeline_months: int = 12


@router.get("/feasibility/{innovation_id}")
async def get_feasibility_by_innovation(innovation_id: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(FeasibilityEvaluation)
        .where(FeasibilityEvaluation.innovation_id == innovation_id)
        .order_by(FeasibilityEvaluation.created_at.desc())
    )
    result = await db.execute(stmt)
    item = result.scalars().first()
    if not item:
        raise HTTPException(status_code=404, detail="Feasibility evaluation not found for this innovation")

    return {
        "id": item.id,
        "innovation_id": item.innovation_id,
        "title": item.title,
        "overall_score": item.overall_score,
        "scientific_feasibility": item.scientific_feasibility,
        "engineering_feasibility": item.engineering_feasibility,
        "material_availability": item.material_availability,
        "manufacturing_readiness": item.manufacturing_readiness,
        "development_complexity": item.development_complexity,
        "energy_efficiency": item.energy_efficiency,
        "economic_viability": item.economic_viability,
        "environmental_impact": item.environmental_impact,
        "safety_compliance": item.safety_compliance,
        "limitations_and_risks": item.limitations_and_risks,
        "prerequisites": item.prerequisites,
        "confidence_level": item.confidence_level,
        "created_at": item.created_at.isoformat(),
    }


@router.post("/feasibility/evaluate", dependencies=[Depends(require_bmir_role(["super_admin", "founder", "research_scientist", "research_engineer"]))])
async def save_feasibility_evaluation(
    payload: FeasibilityInput,
    db: AsyncSession = Depends(get_db),
    current_user: BMIRUser = Depends(get_current_bmir_user),
):
    # Calculate overall weighted score
    scores = [
        payload.scientific_feasibility,
        payload.engineering_feasibility,
        payload.material_availability,
        payload.manufacturing_readiness,
        (100 - payload.development_complexity),  # lower complexity is better
        payload.energy_efficiency,
        payload.economic_viability,
        payload.environmental_impact,
        payload.safety_compliance,
    ]
    overall = round(sum(scores) / len(scores), 1)

    fe = FeasibilityEvaluation(
        innovation_id=payload.innovation_id,
        title=payload.title,
        scientific_feasibility=payload.scientific_feasibility,
        engineering_feasibility=payload.engineering_feasibility,
        material_availability=payload.material_availability,
        manufacturing_readiness=payload.manufacturing_readiness,
        development_complexity=payload.development_complexity,
        energy_efficiency=payload.energy_efficiency,
        economic_viability=payload.economic_viability,
        environmental_impact=payload.environmental_impact,
        safety_compliance=payload.safety_compliance,
        overall_score=overall,
        limitations_and_risks=payload.limitations_and_risks,
        prerequisites=payload.prerequisites,
        confidence_level=payload.confidence_level,
    )
    db.add(fe)
    await db.commit()
    return {"id": fe.id, "overall_score": overall, "message": "Feasibility evaluation stored successfully"}


@router.get("/roadmap/{innovation_id}")
async def get_roadmap_by_innovation(innovation_id: str, db: AsyncSession = Depends(get_db)):
    stmt = (
        select(InnovationRoadmap)
        .where(InnovationRoadmap.innovation_id == innovation_id)
        .order_by(InnovationRoadmap.created_at.desc())
    )
    result = await db.execute(stmt)
    rd = result.scalars().first()
    if not rd:
        raise HTTPException(status_code=404, detail="Roadmap not found for this innovation")

    return {
        "id": rd.id,
        "innovation_id": rd.innovation_id,
        "title": rd.title,
        "phases": rd.phases_json,
        "estimated_timeline_months": rd.estimated_timeline_months,
        "status": rd.status,
        "created_at": rd.created_at.isoformat(),
    }


@router.post("/roadmap/save", dependencies=[Depends(require_bmir_role(["super_admin", "founder", "research_scientist", "research_engineer"]))])
async def save_innovation_roadmap(
    payload: RoadmapGenerateInput,
    db: AsyncSession = Depends(get_db),
    current_user: BMIRUser = Depends(get_current_bmir_user),
):
    rd = InnovationRoadmap(
        innovation_id=payload.innovation_id,
        title=payload.title,
        phases_json=payload.phases,
        estimated_timeline_months=payload.estimated_timeline_months,
        status="Active",
    )
    db.add(rd)
    await db.commit()
    return {"id": rd.id, "message": "Roadmap saved successfully"}

