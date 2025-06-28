from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from typing import List, Optional
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioUpdate
from app.security.security import get_password_hash
from app.security.exceptions import usuario_not_found_exception, duplicate_email_exception



class UsuarioService:
    
    @staticmethod
    def get_usuario_by_id(db: Session, usuario_id: int) -> Usuario:
        """
        Obtener usuario por ID
        """
        usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
        if not usuario:
            raise usuario_not_found_exception()
        return usuario
    
    @staticmethod
    def get_usuario_by_email(db: Session, email: str) -> Optional[Usuario]:
        """
        Obtener usuario por email
        """
        return db.query(Usuario).filter(Usuario.email == email).first()
    
    @staticmethod
    def get_usuarios(db: Session, skip: int = 0, limit: int = 100) -> List[Usuario]:
        """
        Obtener lista de usuarios
        """
        return db.query(Usuario).offset(skip).limit(limit).all()
    
    @staticmethod
    def create_usuario(db: Session, usuario_data: UsuarioCreate) -> Usuario:
        """
        Crear nuevo usuario
        """
        try:
            hashed_password = get_password_hash(usuario_data.contraseña)
            db_usuario = Usuario(
                nombre=usuario_data.nombre,
                email=usuario_data.email,
                contraseña=hashed_password,
                rol=usuario_data.rol
            )
            db.add(db_usuario)
            db.commit()
            db.refresh(db_usuario)
            return db_usuario
        except IntegrityError:
            db.rollback()
            raise duplicate_email_exception()
    
    @staticmethod
    def update_usuario(db: Session, usuario_id: int, usuario_data: UsuarioUpdate) -> Usuario:
        """
        Actualizar usuario existente
        """
        usuario = UsuarioService.get_usuario_by_id(db, usuario_id)
        
        update_data = usuario_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(usuario, field, value)
        
        try:
            db.commit()
            db.refresh(usuario)
            return usuario
        except IntegrityError:
            db.rollback()
            raise duplicate_email_exception()
    
    @staticmethod
    def delete_usuario(db: Session, usuario_id: int) -> bool:
        """
        Eliminar usuario
        """
        usuario = UsuarioService.get_usuario_by_id(db, usuario_id)
        db.delete(usuario)
        db.commit()
        return True
