from typing import AsyncGenerator, Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.security import decodificar_token
from app.database import AsyncSessionLocal
from app.models import Usuario, Rol


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session


# Esquema OAuth2: de aquí sale el botón "Authorize" en Swagger
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
) -> Usuario:
    # 1. Decodificar el token (valida firma y expiración)
    try:
        payload = decodificar_token(token)
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 2. Verificar que sea un token de tipo "access"
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de tipo incorrecto.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 3. Extraer el usuario (subject) del token
    username = payload.get("sub")
    if username is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token sin sujeto.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 4. Cargar el usuario con sus roles y permisos (carga ansiosa)
    consulta = (
        select(Usuario)
        .where(Usuario.username == username)
        .options(selectinload(Usuario.roles).selectinload(Rol.permisos))
    )
    resultado = await db.execute(consulta)
    usuario = resultado.scalar_one_or_none()

    if usuario is None or not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado o inactivo.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return usuario

def require_permission(codigo_permiso: str):
    async def verificar_permiso(
        usuario: Usuario = Depends(get_current_user),
    ) -> Usuario:
        permisos_usuario = {
            permiso.codigo
            for rol in usuario.roles
            for permiso in rol.permisos
        }

        if codigo_permiso not in permisos_usuario:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permiso denegado: se requiere '{codigo_permiso}'.",
            )
        return usuario

    return verificar_permiso

DbSession = Annotated[AsyncSession, Depends(get_db)]
CurrentUser = Annotated[Usuario, Depends(get_current_user)]
