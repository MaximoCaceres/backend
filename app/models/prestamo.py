from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.config.database import Base
from datetime import datetime

class Prestamo(Base):
    __tablename__ = "prestamos"

    id = Column(Integer, primary_key=True, autoincrement=True)
    libro_id = Column(Integer, ForeignKey("libros.id"), nullable=False)
    usuario_id = Column(Integer, ForeignKey("usuarios.id"), nullable=False)
    fecha_prestamo = Column(DateTime, default=datetime.utcnow, nullable=False)
    fecha_devolucion = Column(DateTime, nullable=True)

    # Relaciones
    libro = relationship("Libro", back_populates="prestamos")
    usuario = relationship("Usuario", back_populates="prestamos")

    @property
    def esta_activo(self):
        # Verifica si el libro ha sido prestado
        return self.fecha_devolucion is None