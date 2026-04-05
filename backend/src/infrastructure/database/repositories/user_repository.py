"""Repositorio de usuarios implementado con SQLAlchemy."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.user import User, UserRole
from src.domain.repositories import IUserRepository
from ..models.user_model import UserModel

if TYPE_CHECKING:
    pass


class UserRepository(IUserRepository):
    """Implementación del repositorio de usuarios."""

    def __init__(self, session: AsyncSession):
        self._session = session

    def _model_to_entity(self, model: UserModel) -> User:
        """Convierte modelo ORM a entidad de dominio."""
        user = User()
        user._id = UUID(model.id)
        user._email = model.email
        user._username = model.username
        user._hashed_password = model.hashed_password
        user._role = UserRole(model.role)
        user._first_name = model.first_name
        user._last_name = model.last_name
        user._department = model.department
        user._is_active = model.is_active
        user._is_verified = model.is_verified
        user._last_login = model.last_login
        user._created_at = model.created_at
        user._updated_at = model.updated_at
        return user

    def _entity_to_model(self, entity: User) -> UserModel:
        """Convierte entidad de dominio a modelo ORM."""
        return UserModel(
            id=str(entity.id),
            email=entity.email,
            username=entity.username,
            hashed_password=entity._hashed_password,
            role=entity.role.value,
            first_name=entity.first_name,
            last_name=entity.last_name,
            department=entity.department,
            is_active=entity.is_active,
            is_verified=entity.is_verified,
            last_login=entity.last_login,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def create(self, user: User) -> User:
        """Crea un nuevo usuario."""
        model = self._entity_to_model(user)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._model_to_entity(model)

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        """Obtiene un usuario por su ID."""
        stmt = select(UserModel).where(UserModel.id == str(user_id))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._model_to_entity(model)

    async def get_by_email(self, email: str) -> Optional[User]:
        """Obtiene un usuario por su email."""
        stmt = select(UserModel).where(UserModel.email == email.lower())
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._model_to_entity(model)

    async def get_by_username(self, username: str) -> Optional[User]:
        """Obtiene un usuario por su username."""
        stmt = select(UserModel).where(UserModel.username == username.lower())
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._model_to_entity(model)

    async def update(self, user: User) -> User:
        """Actualiza un usuario existente."""
        stmt = select(UserModel).where(UserModel.id == str(user.id))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            raise ValueError(f"User {user.id} not found")

        model.email = user.email
        model.username = user.username
        model.hashed_password = user._hashed_password
        model.role = user.role.value
        model.first_name = user.first_name
        model.last_name = user.last_name
        model.department = user.department
        model.is_active = user.is_active
        model.is_verified = user.is_verified
        model.last_login = user.last_login

        await self._session.flush()
        await self._session.refresh(model)
        return self._model_to_entity(model)

    async def delete(self, user_id: UUID) -> bool:
        """Elimina un usuario."""
        stmt = select(UserModel).where(UserModel.id == str(user_id))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return False
        await self._session.delete(model)
        await self._session.flush()
        return True

    async def list_all(
        self,
        skip: int = 0,
        limit: int = 100,
        role: Optional[str] = None,
        is_active: Optional[bool] = None,
    ) -> tuple[list[User], int]:
        """Lista usuarios con filtros."""
        stmt = select(UserModel)
        count_stmt = select(func.count(UserModel.id))

        if role:
            stmt = stmt.where(UserModel.role == role)
            count_stmt = count_stmt.where(UserModel.role == role)
        if is_active is not None:
            stmt = stmt.where(UserModel.is_active == is_active)
            count_stmt = count_stmt.where(UserModel.is_active == is_active)

        stmt = stmt.order_by(UserModel.created_at.desc()).offset(skip).limit(limit)

        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar() or 0

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        users = [self._model_to_entity(m) for m in models]
        return users, total
