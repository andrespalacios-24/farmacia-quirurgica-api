from pydantic import BaseModel, EmailStr, ConfigDict

class UsuarioBase(BaseModel):
    username: str
    email: EmailStr
    nombre_completo: str
    activo: bool = True

class UsuarioCreate(UsuarioBase):
    contrasena: str

class UsuarioResponse(UsuarioBase):
    id: int
    model_config = ConfigDict(from_attributes=True)