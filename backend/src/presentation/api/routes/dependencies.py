"""Dependencias para inyección de dependencias."""

from __future__ import annotations

from typing import Optional

from fastapi import Header, HTTPException, status

from src.application.services import AIService, AuthService
from src.infrastructure.database.repositories import UserRepository
from src.infrastructure.database import get_db_session

_ai_service: Optional[AIService] = None
_auth_service: Optional[AuthService] = None


async def get_ai_service() -> AIService:
    """Obtiene el servicio de IA."""
    global _ai_service
    if _ai_service is None:
        _ai_service = AIService()
    return _ai_service


async def get_auth_service() -> AuthService:
    """Obtiene el servicio de autenticación."""
    global _auth_service
    if _auth_service is None:
        async for session in get_db_session():
            user_repo = UserRepository(session)
            _auth_service = AuthService(user_repo)
            break
    return _auth_service


async def get_current_user(
    authorization: Optional[str] = Header(None),
) -> Optional[dict]:
    """Obtiene el usuario actual desde el token JWT."""
    if not authorization:
        return None

    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            return None

        auth_service = await get_auth_service()
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

    except (ValueError, Exception):
        return None


def require_auth(current_user: dict = None) -> dict:
    """Requiere autenticación."""
    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )
    return current_user
