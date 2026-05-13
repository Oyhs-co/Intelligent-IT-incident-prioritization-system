"""Caso de uso para actualizar usuarios."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING
from uuid import UUID

from src.domain.entities.user import User, UserRole
from src.domain.repositories import IUserRepository
from src.shared.exceptions import NotFoundException
from src.shared.logging import get_logger

if TYPE_CHECKING:
    pass

logger = get_logger("use_cases.update_user")


@dataclass
class UpdateUserRequest:
    """Request para actualizar un usuario."""

    email: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    department: str | None = None
    role: UserRole | None = None
    is_active: bool | None = None


class UpdateUserUseCase:
    """Caso de uso para actualizar un usuario."""

    def __init__(self, user_repository: IUserRepository):
        self._user_repo = user_repository

    async def execute(self, user_id: UUID, request: UpdateUserRequest) -> User:
        """Ejecuta la actualización de un usuario."""
        logger.info("Updating user", user_id=str(user_id))

        user = await self._user_repo.get_by_id(user_id)

        if user is None:
            logger.warning("User not found", user_id=str(user_id))
            raise NotFoundException("User", str(user_id))

        if request.email is not None:
            existing = await self._user_repo.get_by_email(request.email)
            if existing and existing.id != user_id:
                raise ValueError("Email already in use")
            user.email = request.email

        if request.first_name is not None:
            user.first_name = request.first_name

        if request.last_name is not None:
            user.last_name = request.last_name

        if request.department is not None:
            user.department = request.department

        if request.role is not None:
            user.role = request.role

        if request.is_active is not None:
            user.is_active = request.is_active

        updated_user = await self._user_repo.update(user)

        logger.info("User updated successfully", user_id=str(user_id))

        return updated_user
