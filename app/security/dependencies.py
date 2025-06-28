from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.config.database import get_db
from app.models.usuario import Usuario, RolEnum
from app.security.security import verify_token
from typing import Optional

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> Usuario:
    """
    Se obtiene el usuaru actual desde el Token JWT
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="no se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token = credentials.credentials
    email = verify_token(token)
    if email is None:
        raise credentials_exception
    
    user = db.query(Usuario).filter(Usuario.email == email).first()
    if user is None:
        raise credentials_exception
    
    return user

async def get_current_bibliotecario(
    current_user: Usuario = Depends(get_current_user)
) -> Usuario:
    """
    se verifica que el usuario actual sea un bibliotecario
    """
    if current_user.rol != RolEnum.BIBLIOTECARIO:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para realizar esta acción",
        )
    return current_user
