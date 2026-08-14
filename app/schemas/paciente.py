from pydantic import BaseModel, ConfigDict

class PacienteBase(BaseModel):
    cedula: str
    nombre_completo: str

class PacienteCreate(PacienteBase):
    pass

class PacienteResponse(PacienteBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

