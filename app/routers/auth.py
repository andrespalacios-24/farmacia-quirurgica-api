import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select

from app.api.deps import DbSession
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    verify_password,
)
from app.models import User
from app.schemas import TokenResponse, RefreshRequest 

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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Verify the account is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Inactive user.",
        )

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
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Verify it is a "refresh" token
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect token type.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token without subject.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Confirm the user still exists and is active
    result = await db.execute(
        select(User).where(User.username == username)
    )
    user = result.scalar_one_or_none()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 4. Issue a new access (and refresh) token
    new_access = create_access_token(user.username)
    new_refresh = create_refresh_token(user.username)

    return TokenResponse(
        access_token=new_access,
        refresh_token=new_refresh,
    )