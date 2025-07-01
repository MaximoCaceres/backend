from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.config.database import get_db
from app.models.usuario import Usuario
from app.schemas.categoria import CategoriaCreate, CategoriaUpdate, CategoriaResponse, CategoriaContarLibros
from app.services.categoria_services import CategoriaService
from app.security.dependencies import get_current_user, get_current_bibliotecario

router = APIRouter(prefix="/categorias", tags=["Categorias"])

@router.get("/", response_model=List[CategoriaResponse],status_code=status.HTTP_200_OK)
async def get_categorias(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener lista de categorías
    """
    categorias = CategoriaService.get_categorias(db, skip=skip, limit=limit)
    return categorias

@router.get("/con-conteo", response_model=List[CategoriaContarLibros],status_code=status.HTTP_200_OK)
async def get_categorias_with_count(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener categorías con conteo de libros
    """
    categorias = CategoriaService.get_categorias_with_count(db)
    return [
        CategoriaContarLibros(
            id=cat["id"],
            nombre=cat["nombre"],
            descripcion=cat["descripcion"],
            cantidad_libros=cat["libros_count"]
        )
        for cat in categorias
    ]

@router.get("/{categoria_id}", response_model=CategoriaResponse,status_code=status.HTTP_200_OK)
async def get_categoria_by_id(
    categoria_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener categoría por ID
    """
    categoria = CategoriaService.get_categoria_by_id(db, categoria_id)
    return categoria

@router.post("/", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED)
async def create_categoria(
    categoria_data: CategoriaCreate,
    current_user: Usuario = Depends(get_current_bibliotecario),
    db: Session = Depends(get_db)
):
    """
    Crear nueva categoría (solo bibliotecarios)
    """
    categoria = CategoriaService.create_categoria(db, categoria_data)
    return categoria

@router.put("/{categoria_id}", response_model=CategoriaResponse)
async def update_categoria(
    categoria_id: int,
    categoria_data: CategoriaUpdate,
    current_user: Usuario = Depends(get_current_bibliotecario),
    db: Session = Depends(get_db)
):
    """
    Actualizar categoría (solo bibliotecarios)
    """
    categoria = CategoriaService.update_categoria(db, categoria_id, categoria_data)
    return categoria

@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_categoria(
    categoria_id: int,
    current_user: Usuario = Depends(get_current_bibliotecario),
    db: Session = Depends(get_db)
):
    """
    Eliminar categoría (solo bibliotecarios)
    """
    CategoriaService.delete_categoria(db, categoria_id)
    return None