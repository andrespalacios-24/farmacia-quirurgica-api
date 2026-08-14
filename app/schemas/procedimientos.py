from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field

# 1. Nuestro "Equipo Básico"
class ProcedimientoBase(BaseModel):
    descripcion: str = Field(..., max_length=255, examples=["Apendicectomía", "Colecistectomía Laparoscópica"])
    quirofano: str = Field(..., max_length=50, examples=["Sala 1", "Quirófano Central 3"])

# 2. Lo que pide el cirujano para empezar (Creación)
class ProcedimientoCreate(ProcedimientoBase):
    paciente_id: int = Field(..., description="ID interno del paciente admitido")

class PacienteResumen(BaseModel):
    id: int
    nombre_completo: str     
    cedula: str   

    model_config = ConfigDict(from_attributes=True)

# 3. La nota de enfermería final (Respuesta del servidor)
class ProcedimientoResponse(ProcedimientoBase):
    id: int
    # paciente_id: int  <-- (Bien, lo dejaste comentado/eliminado)
    paciente: PacienteResumen  # <-- ESTA ES LA LÍNEA QUE FALTABA
    fecha_procedimiento: datetime
    
    model_config = ConfigDict(from_attributes=True)