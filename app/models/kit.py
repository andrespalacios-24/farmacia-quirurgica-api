# app/models/kit.py
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field
from app.models.common import PyObjectId

class InsumoKitItem(BaseModel):
    insumo_id: str
    cantidad_default: int = Field(..., gt=0)

class KitBase(BaseModel):
    nombre: str
    procedimiento: str
    insumos: List[InsumoKitItem]

class KitCreate(KitBase):
    pass

class KitResponse(KitBase):
    id: PyObjectId = Field(alias="_id")
    creado_en: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "populate_by_name": True
    }