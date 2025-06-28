from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import relationship
from enum import Enum as PyEnum
from app.config.database import Base

class RolEnum(str, PyEnum):
    BIBLIOTECARIO = "bibliotecario"
    CLIENTE= "cliente"

class Usuario(Base):
    __tablename__ = "usuarios"

    id = Column(Integer, primary_key=True,autoincrement=True)
    nombre = Column(String(50), nullable=False)
    email = Column(String(100), unique=True, nullable=False)
    password = Column(String(100), nullable=False)
    rol = Column(Enum(RolEnum), default=RolEnum.CLIENTE, nullable=False)

    # Relaciones
    prestamos = relationship("Prestamo", back_populates="usuario")
