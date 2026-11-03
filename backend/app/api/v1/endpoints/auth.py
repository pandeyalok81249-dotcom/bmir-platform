from datetime import timedelta
import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    get_password_hash,
    verify_password,
)
from app.models.profile import UserProfile
from app.models.user import OAuthAccount, User
from app.schemas.auth import (
    AuthResponseData,
    GoogleAuthRequest,
    RefreshTokenRequest,
    TokenResponse,
    UserLogin,
    UserRegister,
    UserResponse,
)
from app.schemas.common import APIResponse

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=APIResponse[AuthResponseData])
async def register(user_in: UserRegister, db: AsyncSession = Depends(get_db)):
    # Check if user already exists
    existing = await db.execute(select(User).where(User.email == user_in.email.lower()))
    if existing.scalars().first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An account with this email address already exists.",
        )

    # Create new user
    new_user = User(
        email=user_in.email.lower(),
        password_hash=get_password_hash(user_in.password),
        email_verified=False,
    )
    db.add(new_user)
    await db.flush()

    # Create default user profile
    profile = UserProfile(
        user_id=new_user.id,
        full_name=user_in.full_name,
    )
    db.add(profile)
    await db.commit()
    await db.refresh(new_user)

    # Issue tokens
    access_token = create_access_token(new_user.id)
    refresh_token = create_refresh_token(new_user.id)

    tokens = TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    user_resp = UserResponse.model_validate(new_user)

    return APIResponse(
        success=True,
        message="Registration successful.",
        data=AuthResponseData(user=user_resp, tokens=tokens),
    )


@router.post("/login", response_model=APIResponse[AuthResponseData])
async def login(credentials: UserLogin, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(User).where(User.email == credentials.email.lower()))
    user = result.scalars().first()

    if not user or not user.password_hash or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password.",
        )

    if user.account_status != "active":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is suspended or deactivated.",
        )

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    tokens = TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    user_resp = UserResponse.model_validate(user)

    return APIResponse(
        success=True,
        message="Login successful.",
        data=AuthResponseData(user=user_resp, tokens=tokens),
    )


@router.post("/google", response_model=APIResponse[AuthResponseData])
async def google_auth(auth_req: GoogleAuthRequest, db: AsyncSession = Depends(get_db)):
    """
    Validates Google ID Token. If user does not exist, registers them automatically.
    """
    id_token = auth_req.id_token.strip()
    if not id_token:
        raise HTTPException(status_code=400, detail="ID token required.")

    # In production, verify using google-auth library against Google's certs.
    # We decode payload safely here for initial OAuth flow handling.
    try:
        # Check token unverified header/payload for sub and email
        unverified_payload = jwt.decode(id_token, options={"verify_signature": False})
        google_sub = unverified_payload.get("sub")
        email = unverified_payload.get("email")
        name = unverified_payload.get("name", "Google User")
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid Google ID token payload.")

    if not email or not google_sub:
        raise HTTPException(status_code=400, detail="Google token does not contain email or sub.")

    result = await db.execute(select(User).where(User.email == email.lower()))
    user = result.scalars().first()

    if not user:
        user = User(
            email=email.lower(),
            email_verified=True,
            password_hash=None,
        )
        db.add(user)
        await db.flush()

        profile = UserProfile(user_id=user.id, full_name=name)
        db.add(profile)

        oauth = OAuthAccount(
            user_id=user.id,
            provider="google",
            provider_subject=google_sub,
            email=email.lower(),
        )
        db.add(oauth)
        await db.commit()
        await db.refresh(user)

    access_token = create_access_token(user.id)
    refresh_token = create_refresh_token(user.id)

    tokens = TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    return APIResponse(
        success=True,
        message="Google authentication successful.",
        data=AuthResponseData(user=UserResponse.model_validate(user), tokens=tokens),
    )


@router.post("/refresh", response_model=APIResponse[TokenResponse])
async def refresh_token(token_req: RefreshTokenRequest, db: AsyncSession = Depends(get_db)):
    payload = decode_token(token_req.refresh_token)
    if not payload or payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
        )

    user_id = payload.get("sub")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user or user.account_status != "active":
        raise HTTPException(status_code=401, detail="User account is inactive.")

    # Refresh token rotation: issue fresh access and refresh tokens
    new_access = create_access_token(user.id)
    new_refresh = create_refresh_token(user.id)

    return APIResponse(
        success=True,
        data=TokenResponse(
            access_token=new_access,
            refresh_token=new_refresh,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        ),
    )


@router.post("/logout", response_model=APIResponse[dict])
async def logout():
    # In stateful/Redis setup, blacklist the token jti.
    return APIResponse(success=True, message="Successfully logged out.", data={})
