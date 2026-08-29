from typing import List, Optional, TYPE_CHECKING
from datetime import datetime
from sqlalchemy import String, Boolean, DateTime, Table, Column, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

if TYPE_CHECKING:
    from app.models.orm.inventario import SupplyWithdrawal, SupplyReturn

# ----------------------------------------------------------------------
# ASSOCIATION TABLES (Many-to-Many)
# ----------------------------------------------------------------------

# Intermediate table: User <-> Role
user_role = Table(
    "usuario_rol",
    Base.metadata,
    Column("usuario_id", ForeignKey("usuarios.id", ondelete="CASCADE"), primary_key=True),
    Column("rol_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
)

# Intermediate table: Role <-> Permission
role_permission = Table(
    "rol_permiso",
    Base.metadata,
    Column("rol_id", ForeignKey("roles.id", ondelete="CASCADE"), primary_key=True),
    Column("permiso_id", ForeignKey("permisos.id", ondelete="CASCADE"), primary_key=True),
)


# ----------------------------------------------------------------------
# ORM MODELS
# ----------------------------------------------------------------------

class Permission(Base):
    """
    Defines a granular permission within the system.
    Example: code="users:create", description="Allows registering new users"
    """
    __tablename__ = "permisos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    code: Mapped[str] = mapped_column("codigo", String(100), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column("descripcion", String(255), nullable=True)

    # M:N Relationship with Roles
    roles: Mapped[List["Role"]] = relationship(
        secondary=role_permission, 
        back_populates="permissions"
    )

    def __repr__(self) -> str:
        return f"<Permission(code='{self.code}')>"


class Role(Base):
    """
    Represents user roles in the system.
    Example: name="ADMIN", "INSTRUMENTALIST", "PHARMACIST"
    """
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column("nombre", String(50), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column("descripcion", String(255), nullable=True)

    # M:N Relationship with Permissions
    permissions: Mapped[List[Permission]] = relationship(
        secondary=role_permission, 
        back_populates="roles"
    )

    # M:N Relationship with Users
    users: Mapped[List["User"]] = relationship(
        secondary=user_role, 
        back_populates="roles"
    )

    def __repr__(self) -> str:
        return f"<Role(name='{self.name}')>"


class User(Base):
    """
    Represents the users of the surgical pharmacy system.
    """
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True, nullable=False)
    email: Mapped[str] = mapped_column(String(100), unique=True, index=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    full_name: Mapped[str] = mapped_column("nombre_completo", String(150), nullable=False)
    is_active: Mapped[bool] = mapped_column("activo", Boolean, default=True, server_default="true", nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(
        "fecha_creacion",
        DateTime(timezone=True), 
        server_default=func.now(), 
        nullable=False
    )

    # M:N Relationship with Roles
    roles: Mapped[List[Role]] = relationship(
        secondary=user_role, 
        back_populates="users"
    )

    # 1:N Relationships with Withdrawals and Returns (Traceability)
    withdrawals_made: Mapped[List["SupplyWithdrawal"]] = relationship(  # type: ignore
        "SupplyWithdrawal", 
        back_populates="user"
    )
    returns_received: Mapped[List["SupplyReturn"]] = relationship(  # type: ignore
        "SupplyReturn", 
        back_populates="receiving_user"
    )
    def __repr__(self) -> str:
        return f"<User(username='{self.username}', email='{self.email}')>"
