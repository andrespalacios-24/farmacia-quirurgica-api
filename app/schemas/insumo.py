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


# -------------------------------------------------------------------
# Bandejas para el flujo de inventario (La hoja de gastos)
# -------------------------------------------------------------------

class RetiroInsumoCreate(BaseModel):
    insumo_id: int
    procedimiento_id: int
    usuario_id: int           
    cantidad_retirada: int
    observaciones: Optional[str] = None