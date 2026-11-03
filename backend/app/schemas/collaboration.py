from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field


# --- Workspaces ---
class WorkspaceCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=150)
    description: Optional[str] = None


class WorkspaceUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=150)
    description: Optional[str] = None


class WorkspaceMemberResponse(BaseModel):
    id: str
    workspace_id: str
    user_id: str
    role: str  # owner, editor, reviewer, viewer
    user_name: Optional[str] = None
    user_email: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkspaceResponse(BaseModel):
    id: str
    owner_id: str
    name: str
    description: Optional[str] = None
    member_count: int = 1
    resume_count: int = 0
    user_role: str = "owner"
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class WorkspaceDetailResponse(WorkspaceResponse):
    members: List[WorkspaceMemberResponse] = []
    shared_resume_ids: List[str] = []


# --- Invitations ---
class InvitationCreate(BaseModel):
    invitee_email: EmailStr
    role: str = Field("reviewer", pattern="^(editor|reviewer|viewer)$")
    expiry_days: int = Field(7, ge=1, le=30)


class InvitationResponse(BaseModel):
    id: str
    workspace_id: str
    invitee_email: str
    role: str
    token: str
    status: str
    expires_at: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class MemberRoleUpdate(BaseModel):
    role: str = Field(..., pattern="^(editor|reviewer|viewer)$")


# --- Comments ---
class CommentCreate(BaseModel):
    resume_version_id: Optional[str] = None
    section: Optional[str] = "general"
    selected_text: Optional[str] = None
    comment_text: str = Field(..., min_length=1, max_length=3000)


class CommentUpdate(BaseModel):
    comment_text: Optional[str] = Field(None, min_length=1, max_length=3000)
    status: Optional[str] = Field(None, pattern="^(active|resolved|deleted)$")


class CommentResponse(BaseModel):
    id: str
    resume_id: str
    resume_version_id: Optional[str] = None
    user_id: str
    author_name: Optional[str] = None
    section: Optional[str] = None
    selected_text: Optional[str] = None
    comment_text: str
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Suggestions ---
class SuggestionCreate(BaseModel):
    resume_version_id: Optional[str] = None
    section: str = Field(..., min_length=1, max_length=50)
    original_text: str = Field(..., min_length=1)
    suggested_text: str = Field(..., min_length=1)
    rationale: Optional[str] = None


class SuggestionReviewRequest(BaseModel):
    action: str = Field(..., pattern="^(accept|reject)$")


class SuggestionResponse(BaseModel):
    id: str
    resume_id: str
    resume_version_id: Optional[str] = None
    user_id: str
    author_name: Optional[str] = None
    section: str
    original_text: str
    suggested_text: str
    rationale: Optional[str] = None
    status: str  # pending, accepted, rejected
    reviewed_by_id: Optional[str] = None
    reviewed_at: Optional[datetime] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Revisions & Conflict Detection ---
class RevisionCreate(BaseModel):
    base_revision_number: int
    patch_data: Dict[str, Any]
    description: Optional[str] = "Collaborative edit"


class RevisionResponse(BaseModel):
    id: str
    resume_id: str
    author_id: str
    revision_number: int
    base_revision_number: int
    patch_data: Dict[str, Any]
    description: Optional[str] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


# --- Activity Events ---
class CollaborationEventResponse(BaseModel):
    id: str
    workspace_id: str
    resume_id: str
    user_id: str
    user_name: Optional[str] = None
    event_type: str
    payload: Dict[str, Any]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

