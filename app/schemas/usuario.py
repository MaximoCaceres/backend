from pydantic import BaseModel, EmailStr, Field, field_validator
from typing import Optional,List,SecretStr
from enum import Enum

class RolEnum(str, Enum):
    BIBLIOTECARIO = "bibliotecario"
    CLIENTE = "cliente"

class UsuarioBase(BaseModel):
    nombre:str = Field(max_length=50)
    email: EmailStr
    rol: RolEnum = RolEnum.CLIENTE

    @field_validator("nombre")
    def validar_nombre(cls, v):
        if not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        return v
    
class UsuarioCreate(UsuarioBase):
    password: SecretStr

    @field_validator("password")
    def validar_password(cls, v):
        if len(v.get_secret_value()) < 6:
            raise ValueError("La contraseña debe tener al menos 6 caracteres")
        return v
    
class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = Field(max_length=50, default=None)
    email: Optional[EmailStr] = None
    rol: Optional[RolEnum] = None

    @field_validator("nombre")
    def validar_nombre(cls, v):
        if v is not None and not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        return v

class UsuarioResponse(UsuarioBase):
    id: int

    class Config:
        orm_mode = True

class UsuarioLogin(BaseModel):
    email: EmailStr
    password: SecretStr

class Token(BaseModel):
    access_token: str
    token_type: str 
    user: UsuarioResponse

class TokenData(BaseModel):
    email: Optional[EmailStr] = None


