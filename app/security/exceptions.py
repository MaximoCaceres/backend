from fastapi import HTTPException, status


class BibliotecaException(Exception):
    """Base exception para el sistema de biblioteca"""
    pass


class UsuarioNotFoundException(BibliotecaException):
    """Usuario no encontrado"""
    pass


class LibroNotFoundException(BibliotecaException):
    """Libro no encontrado"""
    pass


class LibroNoDisponibleException(BibliotecaException):
    """Libro no disponible para préstamo"""
    pass


class PrestamoNotFoundException(BibliotecaException):
    """Préstamo no encontrado"""
    pass


class CategoriaNotFoundException(BibliotecaException):
    """Categoría no encontrada"""
    pass


class DuplicateResourceException(BibliotecaException):
    """Recurso duplicado"""
    pass


# HTTP Exceptions
def usuario_not_found_exception():
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Usuario no encontrado"
    )


def libro_not_found_exception():
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Libro no encontrado"
    )


def libro_no_disponible_exception():
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="El libro no está disponible para préstamo"
    )


def prestamo_not_found_exception():
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Préstamo no encontrado"
    )


def categoria_not_found_exception():
    return HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail="Categoría no encontrada"
    )


def duplicate_email_exception():
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Ya existe un usuario con este email"
    )


def duplicate_isbn_exception():
    return HTTPException(
        status_code=status.HTTP_409_CONFLICT,
        detail="Ya existe un libro con este ISBN"
    )


def invalid_credentials_exception():
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Email o contraseña incorrectos",
        headers={"WWW-Authenticate": "Bearer"},
    )