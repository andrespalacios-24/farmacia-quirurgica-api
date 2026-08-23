from pydantic import BaseModel, EmailStr, ConfigDict

class UsuarioBase(BaseModel):
    username: str
    email: EmailStr
    nombre_completo: str
    activo: bool = True

class UsuarioCreate(UsuarioBase):
    contrasena: str
    roles: list[str] = []

class RolResumen(BaseModel):
    id: int
    nombre: str
    model_config = ConfigDict(from_attributes=True)


class UsuarioResponse(UsuarioBase):
    id: int
    roles: list[RolResumen] = []
    model_config = ConfigDict(from_attributes=True)