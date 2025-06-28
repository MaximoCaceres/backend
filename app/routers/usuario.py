from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.config.database import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioResponse, UsuarioUpdate
from app.services.usuario_services import UsuarioService
from app.security.dependencies import get_current_user, get_current_bibliotecario

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.get("/me", response_model=UsuarioResponse)
async def get_current_user_info(
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener información del usuario actual
    """
    return current_user

@router.put("/me", response_model=UsuarioResponse)
async def update_current_user(
    user_data: UsuarioUpdate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Actualizar información del usuario actual
    """
    updated_user = UsuarioService.update_usuario(db, current_user.id, user_data)
    return updated_user

@router.get("/", response_model=List[UsuarioResponse])
async def get_usuarios(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: Usuario = Depends(get_current_bibliotecario),
    db: Session = Depends(get_db)
):
    """
    Obtener lista de usuarios (solo bibliotecarios)
    """
    users = UsuarioService.get_usuarios(db, skip=skip, limit=limit)
    return users

@router.get("/{usuario_id}", response_model=UsuarioResponse)
async def get_usuario_by_id(
    usuario_id: int,
    current_user: Usuario = Depends(get_current_bibliotecario),
    db: Session = Depends(get_db)
):
    """
    Obtener usuario por ID (solo bibliotecarios)
    """
    user = UsuarioService.get_usuario_by_id(db, usuario_id)
    return user

@router.put("/{usuario_id}", response_model=UsuarioResponse)
async def update_usuario(
    usuario_id: int,
    user_data: UsuarioUpdate,
    current_user: Usuario = Depends(get_current_bibliotecario),
    db: Session = Depends(get_db)
):
    """
    Actualizar usuario por ID (solo bibliotecarios)
    """
    updated_user = UsuarioService.update_usuario(db, usuario_id, user_data)
    return updated_user

@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_usuario(
    usuario_id: int,
    current_user: Usuario = Depends(get_current_bibliotecario),
    db: Session = Depends(get_db)
):
    """
    Eliminar usuario (solo bibliotecarios)
    """
    UsuarioService.delete_usuario(db, usuario_id)
    return None