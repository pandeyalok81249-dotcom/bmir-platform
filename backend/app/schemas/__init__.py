from app.schemas.common import APIResponse, APIErrorResponse, APIErrorDetails
from app.schemas.auth import (
    UserRegister,
    UserLogin,
    GoogleAuthRequest,
    TokenResponse,
    RefreshTokenRequest,
    UserResponse,
    AuthResponseData,
)
from app.schemas.profile import ProfileUpdate, ProfileResponse, EducationItem
from app.schemas.resume import (
    ResumeCreate,
    ResumeResponse,
    ResumeDetailResponse,
    ResumeVersionResponse,
)
from app.schemas.analysis import (
    ResumeAnalysisResult,
    ResumeAnalysisResponse,
    EvidenceFinding,
    SectionAssessment,
    SkillEvidenceItem,
    ATSAssessment,
)
from app.schemas.job_match import (
    JobDescriptionCreate,
    JobDescriptionResponse,
    JobMatchRequest,
    JobMatchResponse,
    JobMatchResult,
    SkillMatchDetail,
)
from app.schemas.application import (
    ApplicationCreate,
    ApplicationUpdate,
    ApplicationResponse,
)
from app.schemas.interview import (
    InterviewGenerateRequest,
    InterviewQuestion,
    InterviewAnswerEvaluateRequest,
    InterviewAnswerEvaluation,
    InterviewSessionResponse,
)
from app.schemas.roadmap import (
    CareerRoadmapGenerateRequest,
    CareerRoadmapResponse,
    MilestoneItem,
)

__all__ = [
    "APIResponse",
    "APIErrorResponse",
    "APIErrorDetails",
    "UserRegister",
    "UserLogin",
    "GoogleAuthRequest",
    "TokenResponse",
    "RefreshTokenRequest",
    "UserResponse",
    "AuthResponseData",
    "ProfileUpdate",
    "ProfileResponse",
    "EducationItem",
    "ResumeCreate",
    "ResumeResponse",
    "ResumeDetailResponse",
    "ResumeVersionResponse",
    "ResumeAnalysisResult",
    "ResumeAnalysisResponse",
    "EvidenceFinding",
    "SectionAssessment",
    "SkillEvidenceItem",
    "ATSAssessment",
    "JobDescriptionCreate",
    "JobDescriptionResponse",
    "JobMatchRequest",
    "JobMatchResponse",
    "JobMatchResult",
    "SkillMatchDetail",
    "ApplicationCreate",
    "ApplicationUpdate",
    "ApplicationResponse",
    "InterviewGenerateRequest",
    "InterviewQuestion",
    "InterviewAnswerEvaluateRequest",
    "InterviewAnswerEvaluation",
    "InterviewSessionResponse",
    "CareerRoadmapGenerateRequest",
    "CareerRoadmapResponse",
    "MilestoneItem",
]

