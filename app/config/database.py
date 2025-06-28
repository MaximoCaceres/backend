from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .settings import settings

#Crear engine de la base de datos
engine = create_engine(settings.DATABASE_URL,pool_pre_ping=True,pool_recycle=300, echo=settings.DEBUG)

#crear sessionlocal
SessionLocal = sessionmaker(autocommit=False, bind=engine)

#clase base
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_database():
    Base.metadata.create_all(bind=engine)