"""Caso de uso para obtener usuarios."""

from __future__ import annotations

from typing import TYPE_CHECKING
from uuid import UUID

from src.domain.entities.user import User
from src.domain.repositories import IUserRepository
from src.shared.exceptions import NotFoundException
from src.shared.logging import get_logger

if TYPE_CHECKING:
    pass

logger = get_logger("use_cases.get_user")


class GetUserUseCase:
    """Caso de uso para obtener un usuario."""

    def __init__(self, user_repository: IUserRepository):
        self._user_repo = user_repository

    async def execute(self, user_id: UUID) -> User | None:
        """Ejecuta la obtención de un usuario."""
        logger.info("Getting user", user_id=str(user_id))

        user = await self._user_repo.get_by_id(user_id)

        if user is None:
            logger.warning("User not found", user_id=str(user_id))
            raise NotFoundException("User", str(user_id))

        logger.info("User retrieved", user_id=str(user_id))
        return user

    async def execute_by_email(self, email: str) -> User | None:
        """Ejecuta la obtención de un usuario por email."""
        logger.info("Getting user by email", email=email)

        user = await self._user_repo.get_by_email(email)

        if user is None:
            logger.warning("User not found", email=email)
            raise NotFoundException("User", email)

        return user
