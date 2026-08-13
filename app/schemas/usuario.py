from pydantic import BaseModel, EmailStr, ConfigDict

class UsuarioBase(BaseModel):
    correo: EmailStr
    nombres: str
    apellidos: str
    activo: bool = True

class UsuarioCreate(UsuarioBase):
    contrasena: str

class UsuarioResponse(UsuarioBase):
    id: int

    model_config = ConfigDict(from_attributes=True)