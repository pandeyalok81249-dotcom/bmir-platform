import secrets
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import check_resume_access, check_workspace_access, get_current_user
from app.core.database import get_db
from app.models.collaboration import (
    CollaborationEvent,
    CollaborationWorkspace,
    ResumeComment,
    ResumeRevision,
    ResumeSuggestion,
    WorkspaceInvitation,
    WorkspaceMember,
    WorkspaceResume,
)
from app.models.resume import Resume, ResumeVersion
from app.models.user import User
from app.schemas.collaboration import (
    CollaborationEventResponse,
    CommentCreate,
    CommentResponse,
    CommentUpdate,
    InvitationCreate,
    InvitationResponse,
    MemberRoleUpdate,
    RevisionCreate,
    RevisionResponse,
    SuggestionCreate,
    SuggestionResponse,
    SuggestionReviewRequest,
    WorkspaceCreate,
    WorkspaceDetailResponse,
    WorkspaceMemberResponse,
    WorkspaceResponse,
    WorkspaceUpdate,
)
from app.schemas.common import APIResponse

router = APIRouter(prefix="/collaboration", tags=["Collaboration Workspaces"])


# ==========================================
# 1. WORKSPACES
# ==========================================

@router.post("/workspaces", response_model=APIResponse[WorkspaceResponse])
async def create_workspace(
    req: WorkspaceCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    workspace = CollaborationWorkspace(
        owner_id=current_user.id,
        name=req.name.strip(),
        description=req.description.strip() if req.description else None,
    )
    db.add(workspace)
    await db.flush()

    # Automatically add creator as owner member
    owner_member = WorkspaceMember(
        workspace_id=workspace.id,
        user_id=current_user.id,
        role="owner",
    )
    db.add(owner_member)

    # Event log
    event = CollaborationEvent(
        workspace_id=workspace.id,
        resume_id="workspace_root",
        user_id=current_user.id,
        event_type="workspace_created",
        payload={"workspace_name": workspace.name},
    )
    db.add(event)
    await db.commit()
    await db.refresh(workspace)

    resp = WorkspaceResponse(
        id=workspace.id,
        owner_id=workspace.owner_id,
        name=workspace.name,
        description=workspace.description,
        member_count=1,
        resume_count=0,
        user_role="owner",
        created_at=workspace.created_at,
        updated_at=workspace.updated_at,
    )
    return APIResponse(success=True, message="Workspace created.", data=resp)


@router.get("/workspaces", response_model=APIResponse[List[WorkspaceResponse]])
async def list_workspaces(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Fetch all workspaces where user is owner or member
    q = (
        select(CollaborationWorkspace, WorkspaceMember.role)
        .join(WorkspaceMember, WorkspaceMember.workspace_id == CollaborationWorkspace.id)
        .where(WorkspaceMember.user_id == current_user.id)
        .order_by(desc(CollaborationWorkspace.created_at))
    )
    res = await db.execute(q)
    rows = res.all()

    workspaces_out = []
    for ws, role in rows:
        m_count_res = await db.execute(
            select(func.count(WorkspaceMember.id)).where(WorkspaceMember.workspace_id == ws.id)
        )
        r_count_res = await db.execute(
            select(func.count(WorkspaceResume.id)).where(WorkspaceResume.workspace_id == ws.id)
        )
        m_count = m_count_res.scalar() or 1
        r_count = r_count_res.scalar() or 0

        workspaces_out.append(
            WorkspaceResponse(
                id=ws.id,
                owner_id=ws.owner_id,
                name=ws.name,
                description=ws.description,
                member_count=m_count,
                resume_count=r_count,
                user_role=role,
                created_at=ws.created_at,
                updated_at=ws.updated_at,
            )
        )

    return APIResponse(success=True, data=workspaces_out)


@router.get("/workspaces/{workspace_id}", response_model=APIResponse[WorkspaceDetailResponse])
async def get_workspace_detail(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    workspace, user_role = await check_workspace_access(workspace_id, current_user, db, "viewer")

    # Fetch members
    m_res = await db.execute(
        select(WorkspaceMember, User)
        .join(User, User.id == WorkspaceMember.user_id)
        .where(WorkspaceMember.workspace_id == workspace_id)
    )
    members_data = []
    for member, user in m_res.all():
        members_data.append(
            WorkspaceMemberResponse(
                id=member.id,
                workspace_id=member.workspace_id,
                user_id=member.user_id,
                role=member.role,
                user_name=user.email.split("@")[0],
                user_email=user.email,
                created_at=member.created_at,
            )
        )

    # Fetch shared resumes
    r_res = await db.execute(
        select(WorkspaceResume.resume_id).where(WorkspaceResume.workspace_id == workspace_id)
    )
    shared_ids = [row[0] for row in r_res.all()]

    resp = WorkspaceDetailResponse(
        id=workspace.id,
        owner_id=workspace.owner_id,
        name=workspace.name,
        description=workspace.description,
        member_count=len(members_data),
        resume_count=len(shared_ids),
        user_role=user_role,
        members=members_data,
        shared_resume_ids=shared_ids,
        created_at=workspace.created_at,
        updated_at=workspace.updated_at,
    )
    return APIResponse(success=True, data=resp)


@router.patch("/workspaces/{workspace_id}", response_model=APIResponse[WorkspaceResponse])
async def update_workspace(
    workspace_id: str,
    req: WorkspaceUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    workspace, _ = await check_workspace_access(workspace_id, current_user, db, "owner")
    if req.name:
        workspace.name = req.name.strip()
    if req.description is not None:
        workspace.description = req.description.strip()
    workspace.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(workspace)

    return APIResponse(
        success=True,
        message="Workspace updated.",
        data=WorkspaceResponse(
            id=workspace.id,
            owner_id=workspace.owner_id,
            name=workspace.name,
            description=workspace.description,
            user_role="owner",
            created_at=workspace.created_at,
            updated_at=workspace.updated_at,
        ),
    )


@router.delete("/workspaces/{workspace_id}", response_model=APIResponse[dict])
async def delete_workspace(
    workspace_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    workspace, _ = await check_workspace_access(workspace_id, current_user, db, "owner")
    await db.delete(workspace)
    await db.commit()
    return APIResponse(success=True, message="Workspace deleted.")


@router.post("/workspaces/{workspace_id}/resumes/{resume_id}", response_model=APIResponse[dict])
async def share_resume_to_workspace(
    workspace_id: str,
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    workspace, _ = await check_workspace_access(workspace_id, current_user, db, "editor")
    resume, _ = await check_resume_access(resume_id, current_user, db, "owner")

    existing = await db.execute(
        select(WorkspaceResume).where(
            WorkspaceResume.workspace_id == workspace_id,
            WorkspaceResume.resume_id == resume_id,
        )
    )
    if existing.scalars().first():
        return APIResponse(success=True, message="Resume already shared to workspace.")

    link = WorkspaceResume(workspace_id=workspace_id, resume_id=resume_id)
    db.add(link)

    event = CollaborationEvent(
        workspace_id=workspace_id,
        resume_id=resume_id,
        user_id=current_user.id,
        event_type="resume_shared",
        payload={"resume_title": resume.title},
    )
    db.add(event)
    await db.commit()

    return APIResponse(success=True, message="Resume successfully shared to workspace.")


@router.delete("/workspaces/{workspace_id}/resumes/{resume_id}", response_model=APIResponse[dict])
async def unshare_resume_from_workspace(
    workspace_id: str,
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_workspace_access(workspace_id, current_user, db, "editor")
    link_res = await db.execute(
        select(WorkspaceResume).where(
            WorkspaceResume.workspace_id == workspace_id,
            WorkspaceResume.resume_id == resume_id,
        )
    )
    link = link_res.scalars().first()
    if link:
        await db.delete(link)
        await db.commit()
    return APIResponse(success=True, message="Resume removed from workspace.")


# ==========================================
# 2. INVITATIONS & MEMBERSHIP
# ==========================================

@router.post("/workspaces/{workspace_id}/invitations", response_model=APIResponse[InvitationResponse])
async def create_invitation(
    workspace_id: str,
    req: InvitationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    workspace, _ = await check_workspace_access(workspace_id, current_user, db, "editor")

    token = secrets.token_urlsafe(32)
    expires_at = datetime.now(timezone.utc) + timedelta(days=req.expiry_days)

    invitation = WorkspaceInvitation(
        workspace_id=workspace_id,
        invited_by_id=current_user.id,
        invitee_email=req.invitee_email.lower(),
        role=req.role,
        token=token,
        status="pending",
        expires_at=expires_at,
    )
    db.add(invitation)

    event = CollaborationEvent(
        workspace_id=workspace_id,
        resume_id="workspace_root",
        user_id=current_user.id,
        event_type="invitation_sent",
        payload={"invitee_email": req.invitee_email, "role": req.role},
    )
    db.add(event)
    await db.commit()
    await db.refresh(invitation)

    return APIResponse(
        success=True,
        message="Invitation created successfully.",
        data=InvitationResponse.model_validate(invitation),
    )


@router.post("/invitations/{token}/accept", response_model=APIResponse[dict])
async def accept_invitation(
    token: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    res = await db.execute(
        select(WorkspaceInvitation).where(WorkspaceInvitation.token == token)
    )
    invitation = res.scalars().first()
    if not invitation:
        raise HTTPException(status_code=404, detail="Invitation not found or invalid token.")

    if invitation.status != "pending":
        raise HTTPException(status_code=400, detail=f"Invitation has already been {invitation.status}.")

    now = datetime.now(timezone.utc)
    exp = invitation.expires_at
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    if exp < now:
        invitation.status = "expired"
        await db.commit()
        raise HTTPException(status_code=400, detail="Invitation has expired.")

    # Check if already a member
    m_check = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == invitation.workspace_id,
            WorkspaceMember.user_id == current_user.id,
        )
    )
    existing_member = m_check.scalars().first()

    if existing_member:
        invitation.status = "accepted"
        await db.commit()
        return APIResponse(success=True, message="You are already a member of this workspace.")

    # Add member
    member = WorkspaceMember(
        workspace_id=invitation.workspace_id,
        user_id=current_user.id,
        role=invitation.role,
    )
    db.add(member)
    invitation.status = "accepted"

    event = CollaborationEvent(
        workspace_id=invitation.workspace_id,
        resume_id="workspace_root",
        user_id=current_user.id,
        event_type="member_joined",
        payload={"user_email": current_user.email, "role": invitation.role},
    )
    db.add(event)
    await db.commit()

    return APIResponse(
        success=True,
        message="Invitation accepted. You are now a workspace member.",
        data={"workspace_id": invitation.workspace_id, "role": invitation.role},
    )


@router.delete("/workspaces/{workspace_id}/invitations/{invitation_id}", response_model=APIResponse[dict])
async def revoke_invitation(
    workspace_id: str,
    invitation_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_workspace_access(workspace_id, current_user, db, "editor")
    inv_res = await db.execute(
        select(WorkspaceInvitation).where(
            WorkspaceInvitation.id == invitation_id,
            WorkspaceInvitation.workspace_id == workspace_id,
        )
    )
    invitation = inv_res.scalars().first()
    if invitation:
        invitation.status = "revoked"
        await db.commit()
    return APIResponse(success=True, message="Invitation revoked.")


@router.patch("/workspaces/{workspace_id}/members/{user_id}", response_model=APIResponse[dict])
async def update_member_role(
    workspace_id: str,
    user_id: str,
    req: MemberRoleUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_workspace_access(workspace_id, current_user, db, "owner")
    m_res = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id,
        )
    )
    member = m_res.scalars().first()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found in workspace.")

    member.role = req.role
    await db.commit()
    return APIResponse(success=True, message="Member role updated.", data={"role": member.role})


@router.delete("/workspaces/{workspace_id}/members/{user_id}", response_model=APIResponse[dict])
async def remove_member(
    workspace_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Owner can remove anyone; members can remove themselves (leave)
    if current_user.id != user_id:
        await check_workspace_access(workspace_id, current_user, db, "owner")
    else:
        await check_workspace_access(workspace_id, current_user, db, "viewer")

    m_res = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == user_id,
        )
    )
    member = m_res.scalars().first()
    if member:
        if member.role == "owner" and current_user.id == user_id:
            raise HTTPException(status_code=400, detail="Owner cannot leave without transferring ownership.")
        await db.delete(member)
        await db.commit()

    return APIResponse(success=True, message="Member removed from workspace.")


# ==========================================
# 3. COMMENTS
# ==========================================

@router.get("/resumes/{resume_id}/comments", response_model=APIResponse[List[CommentResponse]])
async def list_comments(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_resume_access(resume_id, current_user, db, "viewer")
    c_res = await db.execute(
        select(ResumeComment, User)
        .join(User, User.id == ResumeComment.user_id)
        .where(ResumeComment.resume_id == resume_id, ResumeComment.status != "deleted")
        .order_by(desc(ResumeComment.created_at))
    )
    output = []
    for comment, author in c_res.all():
        output.append(
            CommentResponse(
                id=comment.id,
                resume_id=comment.resume_id,
                resume_version_id=comment.resume_version_id,
                user_id=comment.user_id,
                author_name=author.email.split("@")[0],
                section=comment.section,
                selected_text=comment.selected_text,
                comment_text=comment.comment_text,
                status=comment.status,
                created_at=comment.created_at,
                updated_at=comment.updated_at,
            )
        )
    return APIResponse(success=True, data=output)


@router.post("/resumes/{resume_id}/comments", response_model=APIResponse[CommentResponse])
async def add_comment(
    resume_id: str,
    req: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_resume_access(resume_id, current_user, db, "reviewer")

    comment = ResumeComment(
        resume_id=resume_id,
        resume_version_id=req.resume_version_id,
        user_id=current_user.id,
        section=req.section,
        selected_text=req.selected_text,
        comment_text=req.comment_text.strip(),
        status="active",
    )
    db.add(comment)
    await db.commit()
    await db.refresh(comment)

    return APIResponse(
        success=True,
        message="Comment added.",
        data=CommentResponse(
            id=comment.id,
            resume_id=comment.resume_id,
            resume_version_id=comment.resume_version_id,
            user_id=comment.user_id,
            author_name=current_user.email.split("@")[0],
            section=comment.section,
            selected_text=comment.selected_text,
            comment_text=comment.comment_text,
            status=comment.status,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
        ),
    )


@router.patch("/comments/{comment_id}", response_model=APIResponse[CommentResponse])
async def update_comment(
    comment_id: str,
    req: CommentUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    c_res = await db.execute(select(ResumeComment).where(ResumeComment.id == comment_id))
    comment = c_res.scalars().first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found.")

    _, role = await check_resume_access(comment.resume_id, current_user, db, "reviewer")

    # Author can edit text; reviewers/editors can resolve
    if req.comment_text:
        if comment.user_id != current_user.id and role != "owner":
            raise HTTPException(status_code=403, detail="Only the comment author or resume owner can edit the text.")
        comment.comment_text = req.comment_text.strip()

    if req.status:
        comment.status = req.status

    comment.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(comment)

    return APIResponse(
        success=True,
        message="Comment updated.",
        data=CommentResponse(
            id=comment.id,
            resume_id=comment.resume_id,
            resume_version_id=comment.resume_version_id,
            user_id=comment.user_id,
            author_name=current_user.email.split("@")[0],
            section=comment.section,
            selected_text=comment.selected_text,
            comment_text=comment.comment_text,
            status=comment.status,
            created_at=comment.created_at,
            updated_at=comment.updated_at,
        ),
    )


@router.delete("/comments/{comment_id}", response_model=APIResponse[dict])
async def delete_comment(
    comment_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    c_res = await db.execute(select(ResumeComment).where(ResumeComment.id == comment_id))
    comment = c_res.scalars().first()
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found.")

    _, role = await check_resume_access(comment.resume_id, current_user, db, "reviewer")
    if comment.user_id != current_user.id and role not in ["owner", "editor"]:
        raise HTTPException(status_code=403, detail="Unauthorized to delete this comment.")

    comment.status = "deleted"
    await db.commit()
    return APIResponse(success=True, message="Comment deleted.")


# ==========================================
# 4. SUGGESTIONS
# ==========================================

@router.get("/resumes/{resume_id}/suggestions", response_model=APIResponse[List[SuggestionResponse]])
async def list_suggestions(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_resume_access(resume_id, current_user, db, "viewer")
    s_res = await db.execute(
        select(ResumeSuggestion, User)
        .join(User, User.id == ResumeSuggestion.user_id)
        .where(ResumeSuggestion.resume_id == resume_id)
        .order_by(desc(ResumeSuggestion.created_at))
    )
    output = []
    for sug, author in s_res.all():
        output.append(
            SuggestionResponse(
                id=sug.id,
                resume_id=sug.resume_id,
                resume_version_id=sug.resume_version_id,
                user_id=sug.user_id,
                author_name=author.email.split("@")[0],
                section=sug.section,
                original_text=sug.original_text,
                suggested_text=sug.suggested_text,
                rationale=sug.rationale,
                status=sug.status,
                reviewed_by_id=sug.reviewed_by_id,
                reviewed_at=sug.reviewed_at,
                created_at=sug.created_at,
            )
        )
    return APIResponse(success=True, data=output)


@router.post("/resumes/{resume_id}/suggestions", response_model=APIResponse[SuggestionResponse])
async def add_suggestion(
    resume_id: str,
    req: SuggestionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_resume_access(resume_id, current_user, db, "reviewer")

    sug = ResumeSuggestion(
        resume_id=resume_id,
        resume_version_id=req.resume_version_id,
        user_id=current_user.id,
        section=req.section,
        original_text=req.original_text.strip(),
        suggested_text=req.suggested_text.strip(),
        rationale=req.rationale.strip() if req.rationale else None,
        status="pending",
    )
    db.add(sug)
    await db.commit()
    await db.refresh(sug)

    return APIResponse(
        success=True,
        message="Suggestion submitted for author review.",
        data=SuggestionResponse(
            id=sug.id,
            resume_id=sug.resume_id,
            resume_version_id=sug.resume_version_id,
            user_id=sug.user_id,
            author_name=current_user.email.split("@")[0],
            section=sug.section,
            original_text=sug.original_text,
            suggested_text=sug.suggested_text,
            rationale=sug.rationale,
            status=sug.status,
            created_at=sug.created_at,
        ),
    )


@router.post("/suggestions/{suggestion_id}/review", response_model=APIResponse[SuggestionResponse])
async def review_suggestion(
    suggestion_id: str,
    req: SuggestionReviewRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    s_res = await db.execute(select(ResumeSuggestion).where(ResumeSuggestion.id == suggestion_id))
    sug = s_res.scalars().first()
    if not sug:
        raise HTTPException(status_code=404, detail="Suggestion not found.")

    # Only editor or owner can review/apply suggestions
    await check_resume_access(sug.resume_id, current_user, db, "editor")

    if sug.status != "pending":
        raise HTTPException(status_code=400, detail=f"Suggestion is already {sug.status}.")

    sug.status = "accepted" if req.action == "accept" else "rejected"
    sug.reviewed_by_id = current_user.id
    sug.reviewed_at = datetime.now(timezone.utc)

    # If accepted, also record a revision event
    if req.action == "accept":
        rev_count_res = await db.execute(
            select(func.max(ResumeRevision.revision_number)).where(
                ResumeRevision.resume_id == sug.resume_id
            )
        )
        curr_rev = rev_count_res.scalar() or 0
        new_rev = ResumeRevision(
            resume_id=sug.resume_id,
            author_id=current_user.id,
            revision_number=curr_rev + 1,
            base_revision_number=curr_rev,
            patch_data={
                "section": sug.section,
                "original": sug.original_text,
                "replacement": sug.suggested_text,
                "source_suggestion_id": sug.id,
            },
            description=f"Applied suggestion from reviewer on {sug.section}",
        )
        db.add(new_rev)

    await db.commit()
    await db.refresh(sug)

    return APIResponse(
        success=True,
        message=f"Suggestion {sug.status}.",
        data=SuggestionResponse(
            id=sug.id,
            resume_id=sug.resume_id,
            resume_version_id=sug.resume_version_id,
            user_id=sug.user_id,
            section=sug.section,
            original_text=sug.original_text,
            suggested_text=sug.suggested_text,
            rationale=sug.rationale,
            status=sug.status,
            reviewed_by_id=sug.reviewed_by_id,
            reviewed_at=sug.reviewed_at,
            created_at=sug.created_at,
        ),
    )


# ==========================================
# 5. REVISIONS & CONFLICT DETECTION
# ==========================================

@router.get("/resumes/{resume_id}/revisions", response_model=APIResponse[List[RevisionResponse]])
async def list_revisions(
    resume_id: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_resume_access(resume_id, current_user, db, "viewer")
    r_res = await db.execute(
        select(ResumeRevision)
        .where(ResumeRevision.resume_id == resume_id)
        .order_by(desc(ResumeRevision.revision_number))
    )
    revs = r_res.scalars().all()
    return APIResponse(
        success=True,
        data=[RevisionResponse.model_validate(r) for r in revs],
    )


@router.post("/resumes/{resume_id}/revisions", response_model=APIResponse[RevisionResponse])
async def commit_revision(
    resume_id: str,
    req: RevisionCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Optimistic Concurrency Control: Checks that client's base_revision_number matches
    the current head revision. If another collaborator committed in between, rejects with 409 Conflict.
    """
    await check_resume_access(resume_id, current_user, db, "editor")

    max_res = await db.execute(
        select(func.max(ResumeRevision.revision_number)).where(
            ResumeRevision.resume_id == resume_id
        )
    )
    current_head = max_res.scalar() or 0

    if req.base_revision_number != current_head:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=(
                f"Conflict detected. Your base revision is {req.base_revision_number}, but current head is {current_head}. "
                "Please reload the latest revisions before applying changes."
            ),
        )

    new_rev_number = current_head + 1
    revision = ResumeRevision(
        resume_id=resume_id,
        author_id=current_user.id,
        revision_number=new_rev_number,
        base_revision_number=req.base_revision_number,
        patch_data=req.patch_data,
        description=req.description,
    )
    db.add(revision)
    await db.commit()
    await db.refresh(revision)

    return APIResponse(
        success=True,
        message=f"Revision {new_rev_number} committed successfully.",
        data=RevisionResponse.model_validate(revision),
    )


# ==========================================
# 6. ACTIVITY EVENTS
# ==========================================

@router.get("/workspaces/{workspace_id}/events", response_model=APIResponse[List[CollaborationEventResponse]])
async def list_workspace_events(
    workspace_id: str,
    limit: int = Query(50, ge=1, le=200),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await check_workspace_access(workspace_id, current_user, db, "viewer")
    e_res = await db.execute(
        select(CollaborationEvent, User)
        .join(User, User.id == CollaborationEvent.user_id)
        .where(CollaborationEvent.workspace_id == workspace_id)
        .order_by(desc(CollaborationEvent.created_at))
        .limit(limit)
    )
    events = []
    for ev, user in e_res.all():
        events.append(
            CollaborationEventResponse(
                id=ev.id,
                workspace_id=ev.workspace_id,
                resume_id=ev.resume_id,
                user_id=ev.user_id,
                user_name=user.email.split("@")[0],
                event_type=ev.event_type,
                payload=ev.payload,
                created_at=ev.created_at,
            )
        )
    return APIResponse(success=True, data=events)
