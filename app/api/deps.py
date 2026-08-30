from typing import AsyncGenerator, Annotated

import jwt
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import decode_token
from app.database import AsyncSessionLocal
from app.models import User, Role


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


# OAuth2 schema: this provides the "Authorize" button in Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    # 1. Decode the token (validates signature and expiration)
    try:
        payload = decode_token(token)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Verify it is an "access" token
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect token type.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Extract the user (subject) from the token
    username = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token without subject.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 4. Load the user with their roles and permissions (eager loading)
    query = (
        select(User)
        .where(User.username == username)
        .options(selectinload(User.roles).selectinload(Role.permissions))
    )
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found or inactive.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user

def require_permission(permission_code: str):
    async def verify_permission(
        user: User = Depends(get_current_user),
    ) -> User:
        user_permissions = {
            permission.code
            for role in user.roles
            for permission in role.permissions
        }

        if permission_code not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: requires '{permission_code}'.",
            )
        return user

    return verify_permission


DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


async def get_locale(accept_language: str | None = Header(default=None)) -> str:
    """
    FastAPI dependency to extract and sanitize the requested language.
    Returns 'es' by default if the header is missing or unsupported.
    """
    if not accept_language:
        return "es"
    
    # Very basic parsing: just take the first two letters of the primary language
    # E.g., "en-US,en;q=0.9" -> "en"
    primary_lang = accept_language.split(",")[0].split("-")[0].strip().lower()
    
    if primary_lang in ["es", "en"]:
        return primary_lang
        
    return "es"