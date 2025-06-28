from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base

class Libro(Base):
    __tablename__ = "libros"

    id = Column(Integer, primary_key=True, autoincrement=True)
    titulo = Column(String(100), nullable=False)
    autor = Column(String(100), nullable=False)
    isbn = Column(String(20), unique=True, nullable=False)
    editorial = Column(String(200), nullable=False)
    categoria_id = Column(Integer, ForeignKey("categorias.id"), nullable=False)

    # Relaciones
    categoria = relationship("Categoria", back_populates="libros")
    prestamos = relationship("Prestamo", back_populates="libro")