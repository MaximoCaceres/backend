from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from typing import List
from datetime import datetime
from app.models.prestamo import Prestamo
from app.models.libros import Libro
from app.models.usuario import Usuario
from app.models.categoria import Categoria
from app.schemas.prestamo import PrestamoCreate
from app.security.exceptions import prestamo_not_found_exception,libro_not_found_exception,libro_no_disponible_exception,usuario_not_found_exception


class PrestamoService:
    
    @staticmethod
    def get_prestamo_by_id(db: Session, prestamo_id: int) -> Prestamo:
        """
        Obtener préstamo por ID
        """
        prestamo = db.query(Prestamo).filter(Prestamo.id == prestamo_id).first()
        if not prestamo:
            raise prestamo_not_found_exception()
        return prestamo
    
    @staticmethod
    def get_prestamos_activos_usuario(db: Session, usuario_id: int) -> List[Prestamo]:
        """
        Obtener préstamos activos de un usuario
        """
        return db.query(Prestamo).filter(
            and_(
                Prestamo.usuario_id == usuario_id,
                Prestamo.fecha_devolucion.is_(None)
            )
        ).all()
    
    @staticmethod
    def get_historial_prestamos_usuario(db: Session, usuario_id: int) -> List[Prestamo]:
        """
        Obtener historial completo de préstamos de un usuario
        """
        return db.query(Prestamo).filter(
            Prestamo.usuario_id == usuario_id
        ).order_by(Prestamo.fecha_prestamo.desc()).all()
    
    @staticmethod
    def get_todos_prestamos_activos(db: Session) -> List[Prestamo]:
        """
        Obtener todos los préstamos activos del sistema
        """
        return db.query(Prestamo).filter(
            Prestamo.fecha_devolucion.is_(None)
        ).all()
    
    @staticmethod
    def create_prestamo(db: Session, prestamo_data: PrestamoCreate, usuario_id: int) -> Prestamo:
        """
        Crear nuevo préstamo
        """
        # Verificar que el libro existe
        libro = db.query(Libro).filter(Libro.id == prestamo_data.libro_id).first()
        if not libro:
            raise libro_not_found_exception()
        
        # Verificar que el usuario existe
        usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not usuario:
            raise usuario_not_found_exception()
        
        # Verificar disponibilidad del libro
        prestamo_activo = db.query(Prestamo).filter(
            and_(
                Prestamo.libro_id == prestamo_data.libro_id,
                Prestamo.fecha_devolucion.is_(None)
            )
        ).first()
        
        if prestamo_activo:
            raise libro_no_disponible_exception()
        
        # Crear el préstamo
        db_prestamo = Prestamo(
            libro_id=prestamo_data.libro_id,
            usuario_id=usuario_id,
            fecha_prestamo=datetime.utcnow()
        )
        
        db.add(db_prestamo)
        db.commit()
        db.refresh(db_prestamo)
        return db_prestamo
    
    @staticmethod
    def devolver_libro(db: Session, prestamo_id: int, usuario_id: int = None) -> Prestamo:
        """
        Procesar devolución de libro
        """
        prestamo = PrestamoService.get_prestamo_by_id(db, prestamo_id)
        
        # Verificar que el préstamo está activo
        if prestamo.fecha_devolucion is not None:
            raise Exception("Este préstamo ya fue devuelto")
        
        # Si se especifica usuario_id, verificar que coincida (para clientes)
        if usuario_id and prestamo.usuario_id != usuario_id:
            raise Exception("No tienes permisos para devolver este libro")
        
        # Registrar fecha de devolución
        prestamo.fecha_devolucion = datetime.utcnow()
        
        db.commit()
        db.refresh(prestamo)
        return prestamo
    
    @staticmethod
    def get_estadisticas_dashboard(db: Session) -> dict:
        """
        Obtener estadísticas para el dashboard
        """
        # Total de libros
        total_libros = db.query(Libro).count()
        
        # Préstamos activos
        prestamos_activos = db.query(Prestamo).filter(
            Prestamo.fecha_devolucion.is_(None)
        ).count()
        
        # Total de usuarios
        total_usuarios = db.query(Usuario).count()
        
        # Categoría más popular (más libros prestados)
        categoria_popular = db.query(
            Categoria.nombre,
            func.count(Prestamo.id).label('prestamos_count')
        ).join(
            Libro, Categoria.id == Libro.categoria_id
        ).join(
            Prestamo, Libro.id == Prestamo.libro_id
        ).group_by(
            Categoria.id, Categoria.nombre
        ).order_by(
            func.count(Prestamo.id).desc()
        ).first()
        
        return {
            "total_libros": total_libros,
            "prestamos_activos": prestamos_activos,
            "total_usuarios": total_usuarios,
            "categoria_mas_popular": {
                "nombre": categoria_popular.nombre if categoria_popular else "N/A",
                "prestamos": categoria_popular.prestamos_count if categoria_popular else 0
            }
        }