"""Excepciones personalizadas del sistema."""


class AppException(Exception):
    """Excepción base de la aplicación."""

    def __init__(self, message: str, code: str = "APP_ERROR"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class NotFoundException(AppException):
    """Recurso no encontrado."""

    def __init__(self, resource: str, identifier: str):
        super().__init__(
            message=f"{resource} with id '{identifier}' not found",
            code=f"{resource.upper()}_NOT_FOUND",
        )


class ValidationException(AppException):
    """Error de validación."""

    def __init__(self, message: str):
        super().__init__(message=message, code="VALIDATION_ERROR")


class AuthenticationException(AppException):
    """Error de autenticación."""

    def __init__(self, message: str = "Authentication failed"):
        super().__init__(message=message, code="AUTH_ERROR")


class AuthorizationException(AppException):
    """Error de autorización."""

    def __init__(self, message: str = "Access denied"):
        super().__init__(message=message, code="AUTHORIZATION_ERROR")


class ConflictException(AppException):
    """Conflicto de recursos."""

    def __init__(self, message: str):
        super().__init__(message=message, code="CONFLICT")


class DatabaseException(AppException):
    """Error de base de datos."""

    def __init__(self, message: str = "Database operation failed"):
        super().__init__(message=message, code="DB_ERROR")


class AIServiceException(AppException):
    """Error del servicio de IA."""

    def __init__(self, message: str = "AI service error"):
        super().__init__(message=message, code="AI_ERROR")
