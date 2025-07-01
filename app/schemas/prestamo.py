from pydantic import BaseModel
from datetime import datetime
from typing import Optional 
from .libros import LibroResponse
from .usuario import UsuarioResponse

class PrestamoBase(BaseModel):
    libro_id: int
    usuario_id: int

class PrestamoCreate(BaseModel):
    libro_id: int
    #el usuario_id se obtiene del token JWT

class PrestamoUpdate(BaseModel):
    fecha_devolucion: Optional[datetime] = None

class PrestamoResponse(PrestamoBase):
    id: int
    fecha_prestamo: datetime
    fecha_devolucion: Optional[datetime] = None
    esta_activo: bool
    libro: LibroResponse
    usuario: UsuarioResponse

    class Config:
        orm_mode = True

class PrestamoDevolucion(BaseModel):
    prestamo_id: int

class PrestamoHistorial(BaseModel):
    usuario_id: Optional[int] = None
    activos: bool = False
    page: int = 1
    size: int = 10