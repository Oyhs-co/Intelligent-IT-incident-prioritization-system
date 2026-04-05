"""Caso de uso para listar usuarios."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from src.domain.entities.user import User
from src.domain.repositories import IUserRepository
from src.shared.logging import get_logger

if TYPE_CHECKING:
    pass

logger = get_logger("use_cases.list_users")


@dataclass
class ListUsersResult:
    """Resultado de listar usuarios."""

    items: list[User]
    total: int
    skip: int
    limit: int


class ListUsersUseCase:
    """Caso de uso para listar usuarios."""

    def __init__(self, user_repository: IUserRepository):
        self._user_repo = user_repository

    async def execute(
        self,
        skip: int = 0,
        limit: int = 100,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> ListUsersResult:
        """Ejecuta el listado de usuarios."""
        logger.info(f"Listing users", skip=skip, limit=limit)

        users, total = await self._user_repo.list_all(
            skip=skip,
            limit=limit,
            role=role,
            is_active=is_active,
        )

        logger.info(f"Users listed", total=total, returned=len(users))

        return ListUsersResult(
            items=users,
            total=total,
            skip=skip,
            limit=limit,
        )
