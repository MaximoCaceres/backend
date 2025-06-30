from pydantic import BaseModel, Field, field_validator
from typing import Optional
from .categoria import CategoriaResponse


class LibroBase(BaseModel):
    titulo: str
    autor: str
    isbn: str
    editorial: Optional[str] = None
    categoria_id: int

    @field_validator("titulo", "autor", "isbn")
    def validar_no_vacio(cls, v):
        if not v.strip():
            raise ValueError("El campo no puede estar vacío")
        return v
    
    @field_validator("isbn")
    def validar_isbn(cls, v):
        isbn_clear = v.replace("-", "").replace(" ", "")
        if len(isbn_clear) not in [10, 13]:
            raise ValueError("El ISBN debe tener 10 o 13 caracteres")
        return isbn_clear
    
class LibroCreate(LibroBase):
    pass

class LibroUpdate(BaseModel):
    titulo: Optional[str] = None
    autor: Optional[str] = None
    isbn: Optional[str] = None
    editorial: Optional[str] = None
    categoria_id: Optional[int] = None

    @field_validator("titulo", "autor", "isbn")
    def validar_no_vacio(cls, v):
        if v is not None and not v.strip():
            raise ValueError("El campo no puede estar vacío")
        return v
    
    @field_validator("isbn")
    def validar_isbn(cls, v):
        if v is not None:
            isbn_clear = v.replace("-", "").replace(" ", "")
            if len(isbn_clear) not in [10, 13]:
                raise ValueError("El ISBN debe tener 10 o 13 caracteres")
        return v
    
class LibroResponse(LibroBase):
    id: int
    disponible: bool = True
    categoria: CategoriaResponse

    class Config:
        orm_mode = True


class LibroBusqueda(BaseModel):
    query: str
    tipo: Optional[str] = "todos"