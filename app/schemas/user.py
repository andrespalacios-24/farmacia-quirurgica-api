from pydantic import BaseModel, EmailStr, ConfigDict

class UserBase(BaseModel):
    username: str
    email: EmailStr
    full_name: str
    is_active: bool = True

class UserCreate(UserBase):
    password: str
    roles: list[str] = []

class RoleSummary(BaseModel):
    id: int
    name: str
    model_config = ConfigDict(from_attributes=True)


class UserResponse(UserBase):
    id: int
    roles: list[RoleSummary] = []
    model_config = ConfigDict(from_attributes=True)