from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from sqlalchemy import func
from typing import List
from app.models.categoria import Categoria
from app.models.libros import Libro
from app.schemas.categoria import CategoriaCreate, CategoriaUpdate
from app.security.exceptions import categoria_not_found_exception, DuplicateResourceException


class CategoriaService:
    
    @staticmethod
    def get_categoria_by_id(db: Session, categoria_id: int) -> Categoria:
        """
        Obtener categoría por ID
        """
        categoria = db.query(Categoria).filter(Categoria.id == categoria_id).first()
        if not categoria:
            raise categoria_not_found_exception()
        return categoria
    
    @staticmethod
    def get_categorias(db: Session, skip: int = 0, limit: int = 100) -> List[Categoria]:
        """
        Obtener lista de categorías
        """
        return db.query(Categoria).offset(skip).limit(limit).all()
    
    @staticmethod
    def get_categorias_with_count(db: Session) -> List[dict]:
        """
        Obtener categorías con conteo de libros
        """
        result = db.query(
            Categoria,
            func.count(Libro.id).label('libros_count')
        ).outerjoin(Libro).group_by(Categoria.id).all()
        
        return [
            {
                "id": categoria.id,
                "nombre": categoria.nombre,
                "descripcion": categoria.descripcion,
                "libros_count": count
            }
            for categoria, count in result
        ]
    
    @staticmethod
    def create_categoria(db: Session, categoria_data: CategoriaCreate) -> Categoria:
        """
        Crear nueva categoría
        """
        # Verificar si ya existe una categoría con ese nombre
        existing = db.query(Categoria).filter(Categoria.nombre == categoria_data.nombre).first()
        if existing:
            raise DuplicateResourceException("Ya existe una categoría con ese nombre")
        
        db_categoria = Categoria(
            nombre=categoria_data.nombre,
            descripcion=categoria_data.descripcion
        )
        db.add(db_categoria)
        db.commit()
        db.refresh(db_categoria)
        return db_categoria
    
    @staticmethod
    def update_categoria(db: Session, categoria_id: int, categoria_data: CategoriaUpdate) -> Categoria:
        """
        Actualizar categoría existente
        """
        categoria = CategoriaService.get_categoria_by_id(db, categoria_id)
        
        update_data = categoria_data.dict(exclude_unset=True)
        
        # Verificar duplicado de nombre si se está actualizando
        if 'nombre' in update_data:
            existing = db.query(Categoria).filter(
                Categoria.nombre == update_data['nombre'],
                Categoria.id != categoria_id
            ).first()
            if existing:
                raise DuplicateResourceException("Ya existe una categoría con ese nombre")
        
        for field, value in update_data.items():
            setattr(categoria, field, value)
        
        db.commit()
        db.refresh(categoria)
        return categoria
    
    @staticmethod
    def delete_categoria(db: Session, categoria_id: int) -> bool:
        """
        Eliminar categoría (solo si no tiene libros asociados)
        """
        categoria = CategoriaService.get_categoria_by_id(db, categoria_id)
        
        # Verificar si tiene libros asociados
        libros_count = db.query(Libro).filter(Libro.categoria_id == categoria_id).count()
        if libros_count > 0:
            raise DuplicateResourceException("No se puede eliminar la categoría porque tiene libros asociados")
        
        db.delete(categoria)
        db.commit()
        return True