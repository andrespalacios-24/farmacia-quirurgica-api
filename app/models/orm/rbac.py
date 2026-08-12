from typing import List, Optional
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Table, Column, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base
# ----------------------------------------------------------------------
# TABLAS DE ASOCIACIÓN (Muchos a Muchos)
# ----------------------------------------------------------------------

# Tabla intermedia: Usuario <-> Rol
usuario_rol = Table(
    "usuario_rol",
    Base.metadata,
    Column("usuario_id", ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True),
    Column("rol_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)

# Tabla intermedia: Rol <-> Permiso
rol_permiso = Table(
    "rol_permiso",
    Base.metadata,
    Column("rol_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permiso_id", ForeignKey("permisos.id", ondelete="CASCADE"), primary_key=True),
)


# ----------------------------------------------------------------------
# MODELOS ORM
# ----------------------------------------------------------------------

class Permiso(Base):
    """
    Define un permiso granular dentro del sistema.
    Ejemplo: codigo="usuarios:crear", descripcion="Permite registrar nuevos usuarios"
    """
    __tablename__ = "permisos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    codigo: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relación M:N con Roles
    roles: Mapped[List["Rol"]] = relationship(
        secondary=rol_permiso, 
        back_populates="permisos"
    )

    def __repr__(self) -> str:
        return f"<Permiso(codigo='{self.codigo}')>"


class Rol(Base):
    """
    Representa los roles de usuario en el sistema.
    Ejemplo: nombre="ADMIN", "INSTRUMENTADOR", "FARMACEUTICO"
    """
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nombre: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    descripcion: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    # Relación M:N con Permisos
    permisos: Mapped[List[Permiso]] = relationship(
        secondary=rol_permiso, 
        back_populates="roles"
    )

    # Relación M:N con Usuarios
    usuarios: Mapped[List["Usuario"]] = relationship(
        secondary=usuario_rol, 
        back_populates="roles"
    )

    def __repr__(self) -> str:
        return f"<Rol(nombre='{self.nombre}')>"


class Usuario(Base):
    """
    Representa a los usuarios del sistema de farmacia quirúrgica.
    """
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    nombre_completo: Mapped[str] = mapped_column(String(150), nullable=False)
    activo: Mapped[bool] = mapped_column(Boolean, default=True, server_default="true", nullable=False)
    
    fecha_creacion: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )

    # Relación M:N con Roles
    roles: Mapped[List[Rol]] = relationship(
        secondary=usuario_rol, 
        back_populates="usuarios"
    )

    # Relaciones 1:N con Retiros y Devoluciones (Trazabilidad)
    retiros_realizados: Mapped[List["RetiroInsumo"]] = relationship(  # type: ignore
        "RetiroInsumo", 
        back_populates="usuario"
    )
    devoluciones_recibidas: Mapped[List["DevolucionInsumo"]] = relationship(  # type: ignore
        "DevolucionInsumo", 
        back_populates="usuario_recibe"
    )
    def __repr__(self) -> str:
        return f"<Usuario(username='{self.username}', email='{self.email}')>"

