from typing import AsyncGenerator, Optional, Tuple
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import decode_token
from app.models.collaboration import (
    CollaborationWorkspace,
    WorkspaceMember,
    WorkspaceResume,
)
from app.models.resume import Resume
from app.models.user import User

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_STR}/auth/login"
)

ROLE_HIERARCHY = {
    "owner": 4,
    "editor": 3,
    "reviewer": 2,
    "viewer": 1,
}


async def get_current_user(
    db: AsyncSession = Depends(get_db),
    token: str = Depends(oauth2_scheme),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        raise credentials_exception

    user_id: str = payload.get("sub")
    if not user_id:
        raise credentials_exception

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise credentials_exception
    if user.account_status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive or suspended",
        )
    return user


async def check_workspace_access(
    workspace_id: str,
    current_user: User,
    db: AsyncSession,
    min_role: str = "viewer",
) -> Tuple[CollaborationWorkspace, str]:
    """
    Verifies that current_user has access to workspace_id with at least min_role.
    Returns (workspace, effective_role).
    Raises 404 if workspace does not exist or user has no membership (for cross-tenant security).
    Raises 403 if user is a member but role level is below min_role.
    """
    res = await db.execute(
        select(CollaborationWorkspace).where(CollaborationWorkspace.id == workspace_id)
    )
    workspace = res.scalars().first()
    if not workspace:
        raise HTTPException(status_code=404, detail="Workspace not found.")

    if workspace.owner_id == current_user.id:
        return workspace, "owner"

    m_res = await db.execute(
        select(WorkspaceMember).where(
            WorkspaceMember.workspace_id == workspace_id,
            WorkspaceMember.user_id == current_user.id,
        )
    )
    membership = m_res.scalars().first()
    if not membership:
        raise HTTPException(status_code=404, detail="Workspace not found.")

    user_level = ROLE_HIERARCHY.get(membership.role, 0)
    req_level = ROLE_HIERARCHY.get(min_role, 1)

    if user_level < req_level:
        raise HTTPException(
            status_code=403,
            detail=f"Insufficient permissions. Required: {min_role}, current: {membership.role}",
        )

    return workspace, membership.role


async def check_resume_access(
    resume_id: str,
    current_user: User,
    db: AsyncSession,
    min_role: str = "viewer",
) -> Tuple[Resume, str]:
    """
    Validates ownership or active workspace collaboration access for a resume.
    Returns (resume, effective_role).
    Prevents unauthorized access even if UUID is guessed.
    """
    r_res = await db.execute(select(Resume).where(Resume.id == resume_id))
    resume = r_res.scalars().first()
    if not resume:
        raise HTTPException(status_code=404, detail="Resume not found.")

    # Direct owner
    if resume.user_id == current_user.id:
        return resume, "owner"

    # Check shared workspace membership
    w_res = await db.execute(
        select(CollaborationWorkspace, WorkspaceMember.role)
        .join(WorkspaceResume, WorkspaceResume.workspace_id == CollaborationWorkspace.id)
        .join(WorkspaceMember, WorkspaceMember.workspace_id == CollaborationWorkspace.id)
        .where(
            WorkspaceResume.resume_id == resume_id,
            WorkspaceMember.user_id == current_user.id,
        )
    )
    shared = w_res.first()

    # Also check if current_user is the owner of any workspace sharing this resume
    if not shared:
        own_w_res = await db.execute(
            select(CollaborationWorkspace)
            .join(WorkspaceResume, WorkspaceResume.workspace_id == CollaborationWorkspace.id)
            .where(
                WorkspaceResume.resume_id == resume_id,
                CollaborationWorkspace.owner_id == current_user.id,
            )
        )
        owned_w = own_w_res.scalars().first()
        if owned_w:
            return resume, "owner"

    if not shared:
        raise HTTPException(status_code=404, detail="Resume not found.")

    workspace, role = shared
    user_level = ROLE_HIERARCHY.get(role, 0)
    req_level = ROLE_HIERARCHY.get(min_role, 1)

    if user_level < req_level:
        raise HTTPException(
            status_code=403,
            detail=f"Insufficient permissions for resume. Required: {min_role}, current: {role}",
        )

    return resume, role
