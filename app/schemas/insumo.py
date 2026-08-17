from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field, computed_field
from enum import Enum


class InsumoBase(BaseModel):
    codigo_barras: str = Field(..., max_length=100)
    nombre: str = Field(..., max_length=150)
    descripcion: Optional[str] = None
    
    stock_actual: int = Field(default=0, ge=0) # ge=0 impide que haya stock negativo
    stock_minimo: int = Field(default=5, ge=0)
    
    unidad_medida: str = Field(default="Unidad", max_length=30)
    lote: Optional[str] = Field(default=None, max_length=50)
    fecha_vencimiento: Optional[datetime] = None

class InsumoCreate(InsumoBase):
    pass

class InsumoResponse(InsumoBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

    @computed_field
    @property
    def es_critico(self) -> bool:
        return self.stock_actual <= self.stock_minimo


# -------------------------------------------------------------------
# Bandejas para el flujo de inventario (La hoja de gastos)
# -------------------------------------------------------------------

class RetiroInsumoCreate(BaseModel):
    insumo_id: int
    procedimiento_id: int
    usuario_id: int           
    cantidad_retirada: int
    observaciones: Optional[str] = None

# -------------------------------------------------------------------
# Devolución de Insumos (Reintegración al inventario)
# -------------------------------------------------------------------

class EstadoInsumo(str, Enum):
    ESTERIL_INTACTO = "Estéril/Intacto"
    DANADO = "Dañado"
    ABIERTO = "Abierto"

class DevolucionInsumoCreate(BaseModel):
    retiro_id: int
    usuario_recibe_id: int
    cantidad_devuelta: int = Field(..., gt=0)
    estado_insumo: EstadoInsumo
    observaciones: Optional[str] = None



# -------------------------------------------------------------------
# Esquemas de resumen para el historial de movimientos
# -------------------------------------------------------------------

class UsuarioResumen(BaseModel):
    id: int
    nombre_completo: str
    model_config = ConfigDict(from_attributes=True)


class InsumoResumen(BaseModel):
    id: int
    nombre: str
    codigo_barras: str
    unidad_medida: str
    model_config = ConfigDict(from_attributes=True)


class ProcedimientoResumen(BaseModel):
    id: int
    descripcion: str
    quirofano: str
    model_config = ConfigDict(from_attributes=True)

class RetiroResumen(BaseModel):
    id: int
    cantidad_retirada: int
    insumo: InsumoResumen
    model_config = ConfigDict(from_attributes=True)


class RetiroInsumoResponse(BaseModel):
    id: int
    insumo_id: int
    usuario_id: int
    procedimiento_id: int
    cantidad_retirada: int
    fecha_retiro: datetime
    observaciones: Optional[str] = None
    insumo: InsumoResumen
    usuario: UsuarioResumen
    procedimiento: ProcedimientoResumen
    model_config = ConfigDict(from_attributes=True)


class DevolucionInsumoResponse(BaseModel):
    id: int
    retiro_id: int
    usuario_recibe_id: int
    cantidad_devuelta: int
    estado_insumo: EstadoInsumo
    fecha_devolucion: datetime
    observaciones: Optional[str] = None
    usuario_recibe: UsuarioResumen
    retiro: RetiroResumen
    model_config = ConfigDict(from_attributes=True)