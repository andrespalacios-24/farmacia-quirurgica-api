import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.core.security import (
    crear_access_token,
    crear_refresh_token,
    decodificar_token,
    verify_password,
)
from app.models import Usuario
from app.schemas.auth import TokenResponse, RefreshRequest

router = APIRouter(
    prefix="/auth",
    tags=["Autenticación"]
)


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    # 1. Buscar al usuario por su username
    resultado = await db.execute(
        select(Usuario).where(Usuario.username == form_data.username)
    )
    usuario = resultado.scalar_one_or_none()

    # 2. Verificar credenciales (usuario + contraseña)
    if not usuario or not verify_password(form_data.password, usuario.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contraseña incorrectos.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Verificar que la cuenta esté activa
    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuario inactivo.",
        )

    # 4. Emitir el gafete (access) y la credencial (refresh)
    access_token = crear_access_token(usuario.username)
    refresh_token = crear_refresh_token(usuario.username)

    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


@router.post("/refresh", response_model=TokenResponse)
async def renovar_sesion(
    solicitud: RefreshRequest,
    db: AsyncSession = Depends(get_db),
):
    # 1. Validar y decodificar el refresh token
    try:
        payload = decodificar_token(solicitud.refresh_token)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido o expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Verificar que sea de tipo "refresh"
    if payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de tipo incorrecto.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    username = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token sin sujeto.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Confirmar que el usuario siga existiendo y activo
    resultado = await db.execute(
        select(Usuario).where(Usuario.username == username)
    )
    usuario = resultado.scalar_one_or_none()
    if not usuario or not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 4. Emitir un nuevo access (y refresh) sin pedir re-login
    nuevo_access = crear_access_token(usuario.username)
    nuevo_refresh = crear_refresh_token(usuario.username)

    return TokenResponse(
        access_token=nuevo_access,
        refresh_token=nuevo_refresh,
    )