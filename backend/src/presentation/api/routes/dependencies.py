"""Dependencias para inyección de dependencias."""

from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status

from src.application.services import AIService, AuthService
from src.infrastructure.database import get_db_session
from src.infrastructure.database.repositories import UserRepository

_ai_service: AIService | None = None


async def get_ai_service() -> AIService:
    """Obtiene el servicio de IA."""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service


def _create_auth_service(session) -> AuthService:
    """Crea un AuthService con la sesión dada."""
    user_repo = UserRepository(session)
    return AuthService(user_repo)


async def get_current_user(
    authorization: str | None = Header(None),
    session = Depends(get_db_session),
) -> dict | None:
    """Obtiene el usuario actual desde el token JWT."""
    if not authorization:
        return None

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            return None

        auth_service = _create_auth_service(session)
        user_id = await auth_service.verify_token(token)

        if not user_id:
            return None

        from uuid import UUID
        user = await auth_service.get_user_by_id(UUID(user_id))

        if not user:
            return None

        return {
            "id": str(user.id),
            "email": user.email,
            "username": user.username,
            "role": user.role.value,
        }

    except ValueError:
        return None


def require_auth(current_user: dict = None) -> dict:
    """Requiere autenticación."""
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return current_user
