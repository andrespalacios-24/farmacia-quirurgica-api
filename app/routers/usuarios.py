from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.api.deps import get_db, require_permission
from app.core.security import hash_password
from app.models import Usuario, Rol
from app.schemas.usuario import UsuarioCreate, UsuarioResponse

router = APIRouter(
    prefix="/usuarios",
    tags=["Usuarios"]
)


@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def crear_usuario(
    datos: UsuarioCreate,
    db: AsyncSession = Depends(get_db),
    usuario_actual: Usuario = Depends(require_permission("usuarios:crear")),
):
    # 1. Verificar que username y email no estén en uso
    consulta_existente = select(Usuario).where(
        (Usuario.username == datos.username) | (Usuario.email == datos.email)
    )
    resultado = await db.execute(consulta_existente)
    if resultado.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="El username o email ya está registrado.",
        )

    # 2. Buscar los roles solicitados por nombre
    if datos.roles:
        consulta_roles = select(Rol).where(Rol.nombre.in_(datos.roles))
        resultado_roles = await db.execute(consulta_roles)
        roles_db = list(resultado_roles.scalars().all())
        if len(roles_db) != len(datos.roles):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uno o más roles no existen.",
            )
    else:
        roles_db = []

    # 3. Hashear la contraseña y crear el usuario
    nuevo_usuario = Usuario(
        username=datos.username,
        email=datos.email,
        nombre_completo=datos.nombre_completo,
        hashed_password=hash_password(datos.contrasena),
        activo=datos.activo,
        roles=roles_db,
    )

    db.add(nuevo_usuario)
    await db.commit()

    # 4. Re-consultar con los roles cargados para el comprobante
    consulta_completa = (
        select(Usuario)
        .where(Usuario.id == nuevo_usuario.id)
        .options(selectinload(Usuario.roles))
    )
    resultado_final = await db.execute(consulta_completa)
    usuario_completo = resultado_final.scalar_one()

    return usuario_completo