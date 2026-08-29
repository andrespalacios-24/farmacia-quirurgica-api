# app/core/security.py
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.config import settings

# Global hashing factory (the same one used by the seed)
password_hash = PasswordHash.recommended()


def hash_password(password: str) -> str:
    return password_hash.hash(password)


def verify_password(password: str, saved_hash: str) -> bool:
    return password_hash.verify(password, saved_hash)


def _create_token(sub: str, token_type: str, expires_in_minutes: int) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "type": token_type,
        "iat": now,
        "exp": now + timedelta(minutes=expires_in_minutes),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_access_token(username: str) -> str:
    return _create_token(username, "access", settings.ACCESS_TOKEN_EXPIRE_MINUTES)


def create_refresh_token(username: str) -> str:
    return _create_token(username, "refresh", settings.REFRESH_TOKEN_EXPIRE_MINUTES)


def decode_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])