from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from app.config.database import get_db
from app.models.usuario import Usuario
from app.schemas.prestamo import PrestamoCreate, PrestamoResponse, PrestamoDevolucion, PrestamoHistorial
from app.services.prestamos_services import PrestamoService
from app.security.dependencies import get_current_user, get_current_bibliotecario

router = APIRouter(prefix="/prestamos", tags=["Préstamos"])

@router.post("/", response_model=PrestamoResponse, status_code=status.HTTP_201_CREATED)
async def create_prestamo(
    prestamo_data: PrestamoCreate,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Registrar nuevo préstamo
    El usuario_id se obtiene del token JWT del usuario actual
    """
    prestamo = PrestamoService.create_prestamo(db, prestamo_data, current_user.id)
    return prestamo

@router.get("/mis-prestamos/activos", response_model=List[PrestamoResponse])
async def get_mis_prestamos_activos(
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener préstamos activos del usuario actual
    Consulta requerida: 3. Obtener la lista de préstamos activos de un usuario
    """
    prestamos = PrestamoService.get_prestamos_activos_usuario(db, current_user.id)
    return prestamos

@router.get("/mis-prestamos/historial", response_model=List[PrestamoResponse])
async def get_mi_historial_prestamos(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener historial completo de préstamos del usuario actual
    Consulta requerida: 4. Obtener el historial de préstamos de un usuario
    """
    prestamos = PrestamoService.get_historial_prestamos_usuario(
        db, current_user.id, skip=skip, limit=limit
    )
    return prestamos

@router.get("/usuario/{usuario_id}/activos", response_model=List[PrestamoResponse])
async def get_prestamos_activos_usuario(
    usuario_id: int,
    current_user: Usuario = Depends(get_current_bibliotecario),
    db: Session = Depends(get_db)
):
    """
    Obtener préstamos activos de un usuario específico (solo bibliotecarios)
    """
    prestamos = PrestamoService.get_prestamos_activos_usuario(db, usuario_id)
    return prestamos

@router.get("/usuario/{usuario_id}/historial", response_model=List[PrestamoResponse])
async def get_historial_prestamos_usuario(
    usuario_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    current_user: Usuario = Depends(get_current_bibliotecario),
    db: Session = Depends(get_db)
):
    """
    Obtener historial de préstamos de un usuario específico (solo bibliotecarios)
    """
    prestamos = PrestamoService.get_historial_prestamos_usuario(
        db, usuario_id, skip=skip, limit=limit
    )
    return prestamos

@router.get("/activos", response_model=List[PrestamoResponse])
async def get_todos_prestamos_activos(
    current_user: Usuario = Depends(get_current_bibliotecario),
    db: Session = Depends(get_db)
):
    """
    Obtener todos los préstamos activos del sistema (solo bibliotecarios)
    """
    prestamos = PrestamoService.get_todos_prestamos_activos(db)
    return prestamos

@router.get("/{prestamo_id}", response_model=PrestamoResponse)
async def get_prestamo_by_id(
    prestamo_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Obtener préstamo por ID
    Los usuarios solo pueden ver sus propios préstamos
    Los bibliotecarios pueden ver cualquier préstamo
    """
    prestamo = PrestamoService.get_prestamo_by_id(db, prestamo_id)
    
    # Verificar permisos: solo el dueño del préstamo o bibliotecarios
    if (current_user.rol.value != "bibliotecario" and 
        prestamo.usuario_id != current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver este préstamo"
        )
    
    return prestamo

@router.patch("/{prestamo_id}/devolver", response_model=PrestamoResponse)
async def devolver_libro(
    prestamo_id: int,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Procesar devolución de libro
    Los usuarios pueden devolver sus propios libros
    Los bibliotecarios pueden procesar cualquier devolución
    """
    # Si es bibliotecario, puede devolver cualquier libro
    usuario_id = None if current_user.rol.value == "bibliotecario" else current_user.id
    
    prestamo = PrestamoService.devolver_libro(db, prestamo_id, usuario_id)
    return prestamo

@router.post("/devolver", response_model=PrestamoResponse)
async def devolver_libro_por_data(
    devolucion_data: PrestamoDevolucion,
    current_user: Usuario = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Procesar devolución de libro usando datos del body
    """
    # Si es bibliotecario, puede devolver cualquier libro
    usuario_id = None if current_user.rol.value == "bibliotecario" else current_user.id
    
    prestamo = PrestamoService.devolver_libro(db, devolucion_data.prestamo_id, usuario_id)
    return prestamo

# Endpoint adicional para administración
@router.delete("/{prestamo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_prestamo(
    prestamo_id: int,
    current_user: Usuario = Depends(get_current_bibliotecario),
    db: Session = Depends(get_db)
):
    """
    Eliminar préstamo (solo bibliotecarios) - para casos excepcionales
    """
    prestamo = PrestamoService.get_prestamo_by_id(db, prestamo_id)
    db.delete(prestamo)
    db.commit()
    return None