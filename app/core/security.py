# app/core/security.py
from datetime import datetime, timedelta, timezone

import jwt
from pwdlib import PasswordHash

from app.config import settings

# Fábrica global de hashing (la misma que usa el seed)
password_hash = PasswordHash.recommended()


def hash_password(contrasena: str) -> str:
    return password_hash.hash(contrasena)


def verify_password(contrasena: str, hash_guardado: str) -> bool:
    return password_hash.verify(contrasena, hash_guardado)


def _crear_token(sub: str, tipo: str, expira_en_minutos: int) -> str:
    ahora = datetime.now(timezone.utc)
    payload = {
        "sub": sub,
        "type": tipo,
        "iat": ahora,
        "exp": ahora + timedelta(minutes=expira_en_minutos),
    }
    return jwt.encode(payload, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def crear_access_token(username: str) -> str:
    return _crear_token(username, "access", settings.ACCESS_TOKEN_EXPIRE_MINUTES)


def crear_refresh_token(username: str) -> str:
    return _crear_token(username, "refresh", settings.REFRESH_TOKEN_EXPIRE_MINUTES)


def decodificar_token(token: str) -> dict:
    return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])