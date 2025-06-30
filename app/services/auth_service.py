from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioCreate, UsuarioLogin
from app.security.security import verify_password,get_password_hash,create_access_token
from app.security.exceptions import invalid_credentials_exception, duplicate_email_exception
from datetime import timedelta
from app.config.settings import settings


class AuthService:
    
    @staticmethod
    def register_user(db: Session, user_data: UsuarioCreate) -> Usuario:
        """
        Registra un nuevo usuario en la base de datos.
        """
        try:
            hashed_password = get_password_hash(user_data.password.get_secret_value())
            new_user = Usuario(
                nombre=user_data.nombre,
                email=user_data.email,
                password=hashed_password,
                rol=user_data.rol
            )
            db.add(new_user)
            db.commit()
            db.refresh(new_user)
            return new_user
        except IntegrityError:
            db.rollback()
            raise duplicate_email_exception
        
    @staticmethod
    def authenticate_user(db: Session, login_data: UsuarioLogin) -> str:
        """
        Autentica al usuario y devuelve un token JWT si las credenciales son válidas.
        """
        user = db.query(Usuario).filter(Usuario.email == login_data.email).first()
        plain_password = login_data.password.get_secret_value()
        if not user or not verify_password(plain_password, user.password):
            raise invalid_credentials_exception
        return user
    
    @staticmethod
    def create_user_token(user: Usuario) -> dict:
        """
        Crea un token JWT para el usuario autenticado.
        """
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.email, "role": user.rol.value}, expires_delta=access_token_expires
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user
        }