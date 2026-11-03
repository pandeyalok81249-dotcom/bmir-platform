from fastapi import APIRouter

from app.api.v1.endpoints import (
    analyses,
    analytics,
    applications,
    auth,
    builder,
    career_intelligence,
    collaboration,
    collaboration_ws,
    interviews,
    jobs,
    market_intelligence,
    profile,
    resume_evolution,
    resumes,
    roadmaps,
    settings,
)

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(profile.router)
api_router.include_router(resumes.router)
api_router.include_router(resume_evolution.router)
api_router.include_router(analyses.router)
api_router.include_router(builder.router)
api_router.include_router(jobs.router)
api_router.include_router(market_intelligence.router, prefix="/market-intelligence", tags=["market-intelligence"])
api_router.include_router(career_intelligence.router)
api_router.include_router(collaboration.router)
api_router.include_router(collaboration_ws.router)
api_router.include_router(analytics.router)
api_router.include_router(interviews.router)
api_router.include_router(applications.router)
api_router.include_router(roadmaps.router)
api_router.include_router(settings.router)

