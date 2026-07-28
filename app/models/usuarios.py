# app/models/usuario.py
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, EmailStr, Field
from app.models.common import PyObjectId

class RolUsuario(str, Enum):
    INSTRUMENTADOR = "instrumentador"
    AUXILIAR_ENFERMERIA = "auxiliar_enfermeria"
    ANESTESIOLOGO = "anestesiologo"
    FARMACIA = "farmacia"
    ADMIN = "admin"

class UsuarioBase(BaseModel):
    nombre: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    rol: RolUsuario
    activo: bool = True

class UsuarioCreate(UsuarioBase):
    password: str = Field(..., min_length=6)

class UsuarioResponse(UsuarioBase):
    id: PyObjectId = Field(alias="_id")
    creado_en: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True,
        "from_attributes": True
    }