from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.config.database import Base

class Categoria(Base):
    __tablename__ = "categorias"

    id= Column(Integer, primary_key=True, autoincrement=True)
    nombre = Column(String(50), nullable=False, unique=True)
    descripcion = Column(String(255), nullable=True)

    # Relaciones
    libros = relationship("Libro", back_populates="categoria")
