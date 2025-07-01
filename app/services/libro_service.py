from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import or_, and_
from typing import List, Optional
from app.models.libros import Libro
from app.models.categoria import Categoria
from app.models.prestamo import Prestamo
from app.schemas.libros import LibroCreate, LibroUpdate, LibroBusqueda
from app.security.exceptions import (
    libro_not_found_exception, 
    categoria_not_found_exception,
    duplicate_isbn_exception
)


class LibroService:
    
    @staticmethod
    def get_libro_by_id(db: Session, libro_id: int) -> Libro:
        """
        Obtener libro por ID
        """
        libro = db.query(Libro).filter(Libro.id == libro_id).first()
        if not libro:
            raise libro_not_found_exception()
        return libro
    
    @staticmethod
    def get_libros(db: Session, skip: int = 0, limit: int = 100) -> List[Libro]:
        """
        Obtener lista de libros
        """
        return db.query(Libro).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_libros_disponibles(db: Session) -> List[Libro]:
        """
        Obtener libros disponibles (sin préstamos activos)
        """
        # Subquery para obtener libros con préstamos activos
        prestamos_activos = db.query(Prestamo.libro_id).filter(
            Prestamo.fecha_devolucion.is_(None)
        ).subquery()
        
        # Query principal excluyendo libros con préstamos activos
        return db.query(Libro).filter(
            ~Libro.id.in_(prestamos_activos)
            )
    
    @staticmethod
    def buscar_libros(db: Session, busqueda: LibroBusqueda) -> List[Libro]:
        """
        Buscar libros por título, autor o categoría
        """
        query = db.query(Libro).join(Categoria)
        
        if busqueda.tipo == "titulo":
            query = query.filter(Libro.titulo.contains(busqueda.query))
        elif busqueda.tipo == "autor":
            query = query.filter(Libro.autor.contains(busqueda.query))
        elif busqueda.tipo == "categoria":
            query = query.filter(Categoria.nombre.contains(busqueda.query))
        else:  # busqueda.tipo == "todos"
            query = query.filter(
                or_(
                    Libro.titulo.contains(busqueda.query),
                    Libro.autor.contains(busqueda.query),
                    Categoria.nombre.contains(busqueda.query)
                )
            )
        
        return query.all()
    
    @staticmethod
    def get_libros_by_categoria(db: Session, categoria_id: int) -> List[Libro]:
        """
        Obtener libros por categoría
        """
        # Verificar que la categoría existe
        categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
        if not categoria:
            raise categoria_not_found_exception()
        
        return db.query(Libro).filter(Libro.categoria_id == categoria_id).all()
    
    @staticmethod
    def create_libro(db: Session, libro_data: LibroCreate) -> Libro:
        """
        Crear nuevo libro
        """
        # Verificar que la categoría existe
        categoria = db.query(Categoria).filter(Categoria.id == libro_data.categoria_id).first()
        if not categoria:
            raise categoria_not_found_exception()
        
        try:
            db_libro = Libro(
                titulo=libro_data.titulo,
                autor=libro_data.autor,
                isbn=libro_data.isbn,
                editorial=libro_data.editorial,
                categoria_id=libro_data.categoria_id
            )
            db.add(db_libro)
            db.commit()
            db.refresh(db_libro)
            return db_libro
        except IntegrityError:
            db.rollback()
            raise duplicate_isbn_exception()
    
    @staticmethod
    def update_libro(db: Session, libro_id: int, libro_data: LibroUpdate) -> Libro:
        """
        Actualizar libro existente
        """
        libro = LibroService.get_libro_by_id(db, libro_id)
        
        update_data = libro_data.dict(exclude_unset=True)
        
        # Verificar categoría si se está actualizando
        if 'categoria_id' in update_data:
            categoria = db.query(Categoria).filter(Categoria.id == update_data['categoria_id']).first()
            if not categoria:
                raise categoria_not_found_exception()
        
        for field, value in update_data.items():
            setattr(libro, field, value)
        
        try:
            db.commit()
            db.refresh(libro)
            return libro
        except IntegrityError:
            db.rollback()
            raise duplicate_isbn_exception()
    
    @staticmethod
    def delete_libro(db: Session, libro_id: int) -> bool:
        """
        Eliminar libro (solo si no tiene préstamos activos)
        """
        libro = LibroService.get_libro_by_id(db, libro_id)
        
        # Verificar si tiene préstamos activos
        prestamo_activo = db.query(Prestamo).filter(
            and_(
                Prestamo.libro_id == libro_id,
                Prestamo.fecha_devolucion.is_(None)
            )
        ).first()
        
        if prestamo_activo:
            raise Exception("No se puede eliminar el libro porque tiene un préstamo activo")
        
        db.delete(libro)
        db.commit()
        return True
    
    @staticmethod
    def verificar_disponibilidad(db: Session, libro_id: int) -> bool:
        """
        Verificar si un libro está disponible para préstamo
        """
        prestamo_activo = db.query(Prestamo).filter(
            and_(
                Prestamo.libro_id == libro_id,
                Prestamo.fecha_devolucion.is_(None)
            )
        ).first()
        
        return prestamo_activo is None