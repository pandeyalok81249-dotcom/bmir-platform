from fastapi import APIRouter

from app.api.v1.endpoints import (
    bmir_auth,
    bmir_innovations,
    bmir_patents,
    bmir_projects,
    bmir_experiments,
    bmir_collaboration,
    bmir_feasibility_roadmaps,
    bmir_knowledge,
    bmir_dashboard,
    bmir_ai_gateway,
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
    subscriptions,
)

api_router = APIRouter()

# --- BMIR 2.0 Core Ecosystem Endpoints ---
api_router.include_router(bmir_auth.router)
api_router.include_router(bmir_innovations.router)
api_router.include_router(bmir_patents.router)
api_router.include_router(bmir_projects.router)
api_router.include_router(bmir_experiments.router)
api_router.include_router(bmir_collaboration.router)
api_router.include_router(bmir_feasibility_roadmaps.router)
api_router.include_router(bmir_knowledge.router)
api_router.include_router(bmir_dashboard.router)
api_router.include_router(bmir_ai_gateway.router)

# --- Legacy & Secondary Utility Routers ---
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
api_router.include_router(subscriptions.router)


