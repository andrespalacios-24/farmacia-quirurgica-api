from typing import AsyncGenerator, Annotated

import jwt
from fastapi import Depends, Header
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.domain_exceptions import DomainException
from app.core.security import decode_token
from app.database import AsyncSessionLocal
from app.models import User, Role


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


# OAuth2 schema: this provides the "Authorize" button in Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login", auto_error=False)


async def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> User:
    if token is None:
        raise DomainException("errors.not_authenticated", status_code=401)

    # 1. Decode the token (validates signature and expiration)
    try:
        payload = decode_token(token)
    except jwt.PyJWTError:
        raise DomainException("errors.invalid_or_expired_token", status_code=401)

    # 2. Verify it is an "access" token
    if payload.get("type") != "access":
        raise DomainException("errors.incorrect_token_type", status_code=401)

    # 3. Extract the user (subject) from the token
    username = payload.get("sub")
    if username is None:
        raise DomainException("errors.token_without_subject", status_code=401)

    # 4. Load the user with their roles and permissions (eager loading)
    query = (
        select(User)
        .where(User.username == username)
        .options(selectinload(User.roles).selectinload(Role.permissions))
    )
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if user is None or not user.is_active:
        raise DomainException("errors.user_not_found_or_inactive", status_code=401)

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
            raise DomainException("errors.permission_denied", status_code=403, permission_code=permission_code)
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