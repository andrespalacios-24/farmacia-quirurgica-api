# app/models/insumo.py
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from app.models.common import PyObjectId
from app.models.usuarios import RolUsuario

class DescripcionInsumo(BaseModel):
    uso: str
    cirugias_habituales: List[str] = []
    especificaciones_tecnicas: str

class InsumoBase(BaseModel):
    nombre: str = Field(..., min_length=2)
    categoria: str
    imagen_url: Optional[str] = None
    descripcion: DescripcionInsumo
    stock: int = Field(..., ge=0)  # ge=0 garantiza stock mayor o igual a 0
    unidad: str
    restringido_a: List[RolUsuario] = []
    requiere_orden: bool = False

class InsumoCreate(InsumoBase):
    pass

class InsumoResponse(InsumoBase):
    id: PyObjectId = Field(alias="_id")
    creado_en: datetime = Field(default_factory=datetime.utcnow)
    actualizado_en: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True
    }