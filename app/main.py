from app.config.database import get_db, SessionLocal, create_database, engine, Base
from app.config.settings import settings
from app.middleware import error_handler
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.routers import libros, prestamos, categoria, usuario, auth, dashboard
from app.security.dependencies import get_current_user

create_database()

app = FastAPI(title="Gestion biblioteca", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(error_handler.ErrorHandlerMiddleware)

app.include_router(libros.router, tags=["Libros"])
app.include_router(prestamos.router, tags=["Préstamos"])
app.include_router(categoria.router, tags=["Categorias"])
app.include_router(usuario.router, tags=["Usuarios"])
app.include_router(auth.router, tags=["Autenticación"])
app.include_router(dashboard.router, tags=["Dashboard"])

@app.get("/")
def get_users(db = Depends(get_db)):
    return {"message": "API de gestión de biblioteca en funcionamiento"}