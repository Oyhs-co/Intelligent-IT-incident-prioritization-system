"""Tests de integración para UserRepository."""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest

from src.domain.entities.user import User, UserRole
from src.infrastructure.database.repositories.user_repository import UserRepository


def _make_user(**kwargs) -> User:
    """Crea un User con valores mínimos para pruebas."""
    u = User()
    defaults = {
        "email": "test@example.com",
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
    }
    for k, v in {**defaults, **kwargs}.items():
        setattr(u, k, v)
    return u


class TestUserRepositoryCreate:
    """Tests de creación de usuarios."""

    async def test_create_user(self, session):
        """Crear un usuario debe persistirlo y asignarle un ID."""
        repo = UserRepository(session)
        user = _make_user()
        created = await repo.create(user)
        assert isinstance(created.id, UUID)
        assert created.email == "test@example.com"

    async def test_create_user_normalizes_email(self, session):
        """El email debe guardarse en minúsculas."""
        repo = UserRepository(session)
        user = _make_user(email="Test@Example.COM")
        created = await repo.create(user)
        assert created.email == "test@example.com"


class TestUserRepositoryGetById:
    """Tests de búsqueda por ID."""

    async def test_get_by_id_found(self, session):
        """Obtener por ID existente debe retornar el usuario."""
        repo = UserRepository(session)
        user = _make_user()
        created = await repo.create(user)
        found = await repo.get_by_id(created.id)
        assert found is not None
        assert found.id == created.id
        assert found.email == created.email

    async def test_get_by_id_not_found(self, session):
        """Obtener por ID inexistente debe retornar None."""
        repo = UserRepository(session)
        result = await repo.get_by_id(uuid4())
        assert result is None

    async def test_get_by_email(self, session):
        """Obtener por email debe funcionar (case insensitive)."""
        repo = UserRepository(session)
        user = _make_user(email="findme@example.com")
        created = await repo.create(user)
        found = await repo.get_by_email("FINDME@example.com")
        assert found is not None
        assert found.id == created.id

    async def test_get_by_email_not_found(self, session):
        """Obtener por email inexistente debe retornar None."""
        repo = UserRepository(session)
        result = await repo.get_by_email("noexiste@example.com")
        assert result is None

    async def test_get_by_username(self, session):
        """Obtener por username debe funcionar."""
        repo = UserRepository(session)
        user = _make_user(username="uniqueuser")
        created = await repo.create(user)
        found = await repo.get_by_username("uniqueuser")
        assert found is not None
        assert found.id == created.id

    async def test_get_by_username_not_found(self, session):
        """Obtener por username inexistente debe retornar None."""
        repo = UserRepository(session)
        result = await repo.get_by_username("noexiste")
        assert result is None


class TestUserRepositoryUpdate:
    """Tests de actualización de usuarios."""

    async def test_update_user(self, session):
        """Actualizar un usuario debe persistir los cambios."""
        repo = UserRepository(session)
        user = _make_user()
        created = await repo.create(user)
        created.first_name = "NombreActualizado"
        created.role = UserRole.ADMIN
        updated = await repo.update(created)
        assert updated.first_name == "NombreActualizado"
        assert updated.role == UserRole.ADMIN

    async def test_update_not_found(self, session):
        """Actualizar usuario inexistente debe lanzar ValueError."""
        repo = UserRepository(session)
        user = _make_user()
        object.__setattr__(user, "_id", uuid4())
        with pytest.raises(ValueError, match="not found"):
            await repo.update(user)


class TestUserRepositoryDelete:
    """Tests de eliminación de usuarios."""

    async def test_delete_exists(self, session):
        """Eliminar un usuario existente debe retornar True."""
        repo = UserRepository(session)
        user = _make_user()
        created = await repo.create(user)
        result = await repo.delete(created.id)
        assert result is True
        found = await repo.get_by_id(created.id)
        assert found is None

    async def test_delete_not_found(self, session):
        """Eliminar un usuario inexistente debe retornar False."""
        repo = UserRepository(session)
        result = await repo.delete(uuid4())
        assert result is False


class TestUserRepositoryListAll:
    """Tests de listado con filtros."""

    async def test_list_all_no_filters(self, session):
        """Listar sin filtros debe retornar todos."""
        repo = UserRepository(session)
        u1 = _make_user(email="user1@example.com", username="user1")
        u2 = _make_user(email="user2@example.com", username="user2")
        await repo.create(u1)
        await repo.create(u2)
        items, total = await repo.list_all()
        assert total >= 2

    async def test_list_all_with_role_filter(self, session):
        """Filtrar por rol debe retornar solo los que coinciden."""
        repo = UserRepository(session)
        u1 = _make_user(email="admin@example.com", username="admin1")
        u1.role = UserRole.ADMIN
        u2 = _make_user(email="user@example.com", username="regular")
        await repo.create(u1)
        await repo.create(u2)
        items, total = await repo.list_all(role="admin")
        assert all(item.role == UserRole.ADMIN for item in items)

    async def test_list_all_with_active_filter(self, session):
        """Filtrar por is_active debe retornar solo los que coinciden."""
        repo = UserRepository(session)
        u1 = _make_user(email="active@example.com", username="active1")
        u2 = _make_user(email="inactive@example.com", username="inactive1")
        u2.is_active = False
        await repo.create(u1)
        await repo.create(u2)
        items, total = await repo.list_all(is_active=True)
        assert all(item.is_active for item in items)
        items_inactive, total_inactive = await repo.list_all(is_active=False)
        assert all(not item.is_active for item in items_inactive)

    async def test_list_all_pagination(self, session):
        """La paginación debe funcionar correctamente."""
        repo = UserRepository(session)
        for i in range(5):
            await repo.create(_make_user(
                email=f"user{i}@example.com",
                username=f"user{i}",
            ))
        items, total = await repo.list_all(skip=0, limit=2)
        assert len(items) == 2
        assert total >= 5
