import jwt
from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from app.api.deps import DbSession, CurrentUser
from app.core.domain_exceptions import DomainException
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.models import User
from app.schemas import TokenResponse, RefreshRequest, MeResponse 

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)


@router.post("/login", response_model=TokenResponse)
async def login(
    db: DbSession,
    form_data: OAuth2PasswordRequestForm = Depends(),
):
    # 1. Search for the user by username
    result = await db.execute(
        select(User).where(User.username == form_data.username)
    )
    user = result.scalar_one_or_none()

    # 2. Verify credentials
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise DomainException("errors.invalid_credentials", status_code=401)

    # 3. Verify the account is active
    if not user.is_active:
        raise DomainException("errors.inactive_user", status_code=403)

    # 4. Issue the access token and refresh token
    access_token = create_access_token(user.username)
    refresh_token = create_refresh_token(user.username)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=TokenResponse)
async def refresh_session(
    request: RefreshRequest,
    db: DbSession,
):
    # 1. Validate and decode the refresh token
    try:
        payload = decode_token(request.refresh_token)
    except jwt.PyJWTError:
        raise DomainException("errors.invalid_or_expired_refresh_token", status_code=401)

    # 2. Verify it is a "refresh" token
    if payload.get("type") != "refresh":
        raise DomainException("errors.incorrect_token_type", status_code=401)

    username = payload.get("sub")
    if username is None:
        raise DomainException("errors.token_without_subject", status_code=401)

    # 3. Confirm the user still exists and is active
    result = await db.execute(
        select(User).where(User.username == username)
    )
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise DomainException("errors.user_not_found_or_inactive", status_code=401)

    # 4. Issue a new access (and refresh) token
    new_access = create_access_token(user.username)
    new_refresh = create_refresh_token(user.username)

    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
    )

@router.get("/me", response_model=MeResponse)
async def get_me(user: CurrentUser):
    return user