"""Caso de uso para crear usuarios."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional
from uuid import UUID

from src.domain.entities.user import User, UserRole
from src.domain.repositories import IUserRepository
from src.shared.logging import get_logger

if TYPE_CHECKING:
    pass

logger = get_logger("use_cases.create_user")


@dataclass
class CreateUserRequest:
    """Request para crear un usuario."""

    email: str
    username: str
    password: str
    first_name: str = ""
    last_name: str = ""
    department: Optional[str] = None
    role: UserRole = UserRole.USER


class CreateUserUseCase:
    """Caso de uso para crear un nuevo usuario."""

    def __init__(self, user_repository: IUserRepository):
        self._user_repo = user_repository

    async def execute(self, request: CreateUserRequest) -> User:
        """Ejecuta la creación de un usuario."""
        logger.info(f"Creating user", email=request.email)

        existing_email = await self._user_repo.get_by_email(request.email)
        if existing_email:
            logger.warning(f"Email already registered", email=request.email)
            raise ValueError("Email already registered")

        existing_username = await self._user_repo.get_by_username(request.username)
        if existing_username:
            logger.warning(f"Username already taken", username=request.username)
            raise ValueError("Username already taken")

        user = User()
        user.email = request.email
        user.username = request.username
        user.set_password(request.password)
        user.role = request.role
        user.first_name = request.first_name
        user.last_name = request.last_name
        user.department = request.department
        user.is_verified = True

        created_user = await self._user_repo.create(user)

        logger.info(f"User created successfully", user_id=str(created_user.id))

        return created_user
