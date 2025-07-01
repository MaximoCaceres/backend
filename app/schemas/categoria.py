from pydantic import BaseModel, field_validator
from typing import Optional

class CategoriaBase(BaseModel):
    nombre:str
    descripcion: Optional[str] = None

    @field_validator("nombre")
    def validar_nombre(cls, v):
        if not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        return v
    
class CategoriaCreate(CategoriaBase):
    pass

class CategoriaUpdate(BaseModel):
    nombre: Optional[str] = None
    descripcion: Optional[str] = None

    @field_validator("nombre")
    def validar_nombre(cls, v):
        if v is not None and not v.strip():
            raise ValueError("El nombre no puede estar vacío")
        return v
    
class CategoriaResponse(CategoriaBase):
    id: int

    class Config:
        orm_mode = True

class CategoriaContarLibros(CategoriaResponse):
    cantidad_libros: int = 0