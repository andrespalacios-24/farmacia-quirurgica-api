from pydantic import BaseModel, ConfigDict

class PacienteBase(BaseModel):
    cedula: str
    nombres: str
    apellidos: str

class PacienteCreate(PacienteBase):
    pass

class PacienteResponse(PacienteBase):
    id: int
    model_config = ConfigDict(from_attributes=True)

