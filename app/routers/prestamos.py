from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.config.database import get_db
from app.models.usuario import Usuario
from app.schemas.libros import LibroCreate, LibroUpdate, LibroResponse, LibroBusqueda
from app.services.libro_service import LibroService
from app.security.dependencies import get_current_user, get_current_bibliotecario

router = APIRouter(prefix="/libros", tags=["Libros"])

@router.get("/", response_model=List[LibroResponse])
async def get_libros(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener lista de todos los libros
    """
    libros = LibroService.get_libros(db, skip=skip, limit=limit)
    
    # Agregar información de disponibilidad
    libros_response = []
    for libro in libros:
        disponible = LibroService.verificar_disponibilidad(db, libro.id)
        libro_dict = {
            "id": libro.id,
            "titulo": libro.titulo,
            "autor": libro.autor,
            "isbn": libro.isbn,
            "editorial": libro.editorial,
            "categoria_id": libro.categoria_id,
            "disponible": disponible,
            "categoria": libro.categoria
        }
        libros_response.append(libro_dict)
    
    return libros_response

@router.get("/disponibles", response_model=List[LibroResponse])
async def get_libros_disponibles(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener libros disponibles (sin préstamos activos)
    Consulta requerida: 1. Obtener todos los libros disponibles (Sin prestar)
    """
    libros = LibroService.get_libros_disponibles(db, skip=skip, limit=limit)
    
    libros_response = []
    for libro in libros:
        libro_dict = {
            "id": libro.id,
            "titulo": libro.titulo,
            "autor": libro.autor,
            "isbn": libro.isbn,
            "editorial": libro.editorial,
            "categoria_id": libro.categoria_id,
            "disponible": True,  # Ya están filtrados como disponibles
            "categoria": libro.categoria
        }
        libros_response.append(libro_dict)
    
    return libros_response

@router.post("/buscar", response_model=List[LibroResponse])
async def buscar_libros(
    busqueda: LibroBusqueda,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Buscar libros por título, autor o categoría
    Consulta requerida: 2. Buscar libros por título, autor o categoría
    """
    libros = LibroService.buscar_libros(db, busqueda)
    
    libros_response = []
    for libro in libros:
        disponible = LibroService.verificar_disponibilidad(db, libro.id)
        libro_dict = {
            "id": libro.id,
            "titulo": libro.titulo,
            "autor": libro.autor,
            "isbn": libro.isbn,
            "editorial": libro.editorial,
            "categoria_id": libro.categoria_id,
            "disponible": disponible,
            "categoria": libro.categoria
        }
        libros_response.append(libro_dict)
    
    return libros_response

@router.get("/categoria/{categoria_id}", response_model=List[LibroResponse])
async def get_libros_by_categoria(
    categoria_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener libros de una categoría específica
    Consulta requerida: 5. Listar todos los libros de una categoría específica
    """
    libros = LibroService.get_libros_by_categoria(db, categoria_id)
    
    libros_response = []
    for libro in libros:
        disponible = LibroService.verificar_disponibilidad(db, libro.id)
        libro_dict = {
            "id": libro.id,
            "titulo": libro.titulo,
            "autor": libro.autor,
            "isbn": libro.isbn,
            "editorial": libro.editorial,
            "categoria_id": libro.categoria_id,
            "disponible": disponible,
            "categoria": libro.categoria
        }
        libros_response.append(libro_dict)
    
    return libros_response

@router.get("/{libro_id}", response_model=LibroResponse)
async def get_libro_by_id(
    libro_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener libro por ID
    """
    libro = LibroService.get_libro_by_id(db, libro_id)
    disponible = LibroService.verificar_disponibilidad(db, libro.id)
    
    libro_dict = {
        "id": libro.id,
        "titulo": libro.titulo,
        "autor": libro.autor,
        "isbn": libro.isbn,
        "editorial": libro.editorial,
        "categoria_id": libro.categoria_id,
        "disponible": disponible,
        "categoria": libro.categoria
    }
    
    return libro_dict

@router.post("/", response_model=LibroResponse, status_code=status.HTTP_201_CREATED)
async def create_libro(
    libro_data: LibroCreate,
    current_user: Usuario = Depends(get_current_bibliotecario),
    db: Session = Depends(get_db)
):
    """
    Crear nuevo libro (solo bibliotecarios)
    """
    libro = LibroService.create_libro(db, libro_data)
    
    libro_dict = {
        "id": libro.id,
        "titulo": libro.titulo,
        "autor": libro.autor,
        "isbn": libro.isbn,
        "editorial": libro.editorial,
        "categoria_id": libro.categoria_id,
        "disponible": True,  # Nuevo libro siempre disponible
        "categoria": libro.categoria
    }
    
    return libro_dict

@router.put("/{libro_id}", response_model=LibroResponse)
async def update_libro(
    libro_id: int,
    libro_data: LibroUpdate,
    current_user: Usuario = Depends(get_current_bibliotecario),
    db: Session = Depends(get_db)
):
    """
    Actualizar libro (solo bibliotecarios)
    """
    libro = LibroService.update_libro(db, libro_id, libro_data)
    disponible = LibroService.verificar_disponibilidad(db, libro.id)
    
    libro_dict = {
        "id": libro.id,
        "titulo": libro.titulo,
        "autor": libro.autor,
        "isbn": libro.isbn,
        "editorial": libro.editorial,
        "categoria_id": libro.categoria_id,
        "disponible": disponible,
        "categoria": libro.categoria
    }
    
    return libro_dict

@router.delete("/{libro_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_libro(
    libro_id: int,
    current_user: Usuario = Depends(get_current_bibliotecario),
    db: Session = Depends(get_db)
):
    """
    Eliminar libro (solo bibliotecarios)
    """
    LibroService.delete_libro(db, libro_id)
    return None

@router.get("/{libro_id}/disponibilidad")
async def verificar_disponibilidad_libro(
    libro_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Verificar disponibilidad de un libro específico
    """
    # Verificar que el libro existe
    LibroService.get_libro_by_id(db, libro_id)
    
    disponible = LibroService.verificar_disponibilidad(db, libro_id)
    
    return {
        "libro_id": libro_id,
        "disponible": disponible,
        "mensaje": "Libro disponible" if disponible else "Libro no disponible - prestado actualmente"
    }