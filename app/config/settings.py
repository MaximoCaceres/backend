from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):

    #Configuracion de la base de datos
    DATABASE_URL: str = "mysql+pymyqsl://root:Maxi123@localhost:3306/biblioteca_bd"
    #JWT
    SECRET_KEY: str ="your_secret_key_here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    #API
    API_V1_STR: str = "/api/v1"
    PROYECT_NAME: str = "Sistema de gestión de biblioteca"
    PROYECT_VERSION: str = "1.0.0"

    #ENviroment
    ENVIRONMENT: str = "development"
    DEBUG: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = True

settings = Settings()