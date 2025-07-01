from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

import datetime
from app.config.database import get_db
from app.models.usuario import Usuario
from app.services.prestamos_services import PrestamoService
from app.security.dependencies import get_current_bibliotecario

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/estadisticas")
async def get_estadisticas_dashboard(
    current_user: Usuario = Depends(get_current_bibliotecario),
    db: Session = Depends(get_db)
):
    """
    Obtener estadísticas para el dashboard (solo bibliotecarios)

    número total de libros en la biblioteca
    número total de préstamos activos
    número de usuarios registrados
    categoría de libros más popular (mayor cantidad de libros prestados)
    """
    estadisticas = PrestamoService.get_estadisticas_dashboard(db)
    
    return {
        "estadisticas": estadisticas,
        "mensaje": "Estadísticas del sistema de biblioteca"
    }

@router.get("/resumen")
async def get_resumen_dashboard(
    current_user: Usuario = Depends(get_current_bibliotecario),
    db: Session = Depends(get_db)
):
    """
    Obtener resumen detallado para el dashboard
    """
    estadisticas = PrestamoService.get_estadisticas_dashboard(db)
    
    # Formatear la respuesta con más detalles
    return {
        "resumen": {
            "biblioteca": {
                "total_libros": estadisticas["total_libros"],
                "libros_disponibles": estadisticas["total_libros"] - estadisticas["prestamos_activos"],
                "libros_prestados": estadisticas["prestamos_activos"]
            },
            "usuarios": {
                "total_registrados": estadisticas["total_usuarios"]
            },
            "prestamos": {
                "activos": estadisticas["prestamos_activos"],
                "porcentaje_ocupacion": round(
                    (estadisticas["prestamos_activos"] / estadisticas["total_libros"] * 100) 
                    if estadisticas["total_libros"] > 0 else 0, 2
                )
            },
            "categoria_popular": estadisticas["categoria_mas_popular"]
        },
        "timestamp": datetime.datetime.now()
    }