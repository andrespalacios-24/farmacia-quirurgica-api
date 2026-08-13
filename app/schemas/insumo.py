from typing import Optional
from pydantic import BaseModel, ConfigDict

class InsumoBase(BaseModel):
    nombre: str
    descripcion: Optional[str] = None
    cantidad_disponible: int

class InsumoCreate(InsumoBase):
    pass

class InsumoResponse(InsumoBase):
    id: int
    model_config = ConfigDict(from_attributes=True)