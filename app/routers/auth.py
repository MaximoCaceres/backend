from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session

from app.config.database import get_db
from app.schemas.usuario import UsuarioCreate, UsuarioLogin, Token, UsuarioResponse
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Autenticación"])
security = HTTPBearer()

@router.post("/register", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UsuarioCreate,
    db: Session = Depends(get_db)
):
    """
    Registrar nuevo usuario
    """
    user = AuthService.register_user(db, user_data)
    return user

@router.post("/login", response_model=Token)
async def login(
    login_data: UsuarioLogin,
    db: Session = Depends(get_db)
):
    """
    Iniciar sesión y obtener token JWT
    """
    user = AuthService.authenticate_user(db, login_data)
    token_data = AuthService.create_user_token(user)
    return token_data