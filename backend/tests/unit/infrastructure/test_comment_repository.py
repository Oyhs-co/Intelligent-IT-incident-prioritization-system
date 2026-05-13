"""Tests de integración para CommentRepository."""

from __future__ import annotations

from uuid import UUID, uuid4

import pytest

from src.domain.entities.comment import Comment
from src.domain.entities.incident import Incident
from src.infrastructure.database.repositories.comment_repository import (
    CommentRepository,
)
from src.infrastructure.database.repositories.incident_repository import (
    IncidentRepository,
)


class TestCommentRepository:
    """Tests del repositorio de comentarios."""

    async def _create_incident(self, session) -> Incident:
        """Crea un incidente de prueba y lo retorna."""
        repo = IncidentRepository(session)
        i = Incident()
        i.title = "Incidente para comentarios"
        i.description = "Descripción"
        return await repo.create(i)

    async def test_create_comment(self, session):
        """Crear un comentario debe persistirlo."""
        repo = CommentRepository(session)
        incident = await self._create_incident(session)
        comment = Comment(_incident_id=incident.id, _content="Comentario de prueba")
        created = await repo.create(comment)
        assert isinstance(created.id, UUID)
        assert created.content == "Comentario de prueba"
        assert created.incident_id == incident.id

    async def test_get_by_id_found(self, session):
        """Obtener por ID existente debe retornar el comentario."""
        repo = CommentRepository(session)
        incident = await self._create_incident(session)
        comment = Comment(_incident_id=incident.id, _content="Buscar este")
        created = await repo.create(comment)
        found = await repo.get_by_id(created.id)
        assert found is not None
        assert found.id == created.id
        assert found.content == "Buscar este"

    async def test_get_by_id_not_found(self, session):
        """Obtener por ID inexistente debe retornar None."""
        repo = CommentRepository(session)
        result = await repo.get_by_id(uuid4())
        assert result is None

    async def test_update_content(self, session):
        """Actualizar el contenido debe persistirse."""
        repo = CommentRepository(session)
        incident = await self._create_incident(session)
        comment = Comment(_incident_id=incident.id, _content="Original")
        created = await repo.create(comment)
        created.content = "Actualizado"
        updated = await repo.update(created)
        assert updated.content == "Actualizado"

    async def test_update_is_internal(self, session):
        """Actualizar is_internal debe persistirse."""
        repo = CommentRepository(session)
        incident = await self._create_incident(session)
        comment = Comment(_incident_id=incident.id, _content="Interno")
        comment.is_internal = True
        created = await repo.create(comment)
        assert created.is_internal is True
        created.is_internal = False
        updated = await repo.update(created)
        assert updated.is_internal is False

    async def test_update_not_found(self, session):
        """Actualizar comentario inexistente debe lanzar ValueError."""
        repo = CommentRepository(session)
        comment = Comment(_incident_id=uuid4(), _content="test")
        object.__setattr__(comment, "_id", uuid4())
        with pytest.raises(ValueError, match="not found"):
            await repo.update(comment)

    async def test_delete_exists(self, session):
        """Eliminar un comentario existente debe retornar True."""
        repo = CommentRepository(session)
        incident = await self._create_incident(session)
        comment = Comment(_incident_id=incident.id, _content="Eliminar")
        created = await repo.create(comment)
        result = await repo.delete(created.id)
        assert result is True
        found = await repo.get_by_id(created.id)
        assert found is None

    async def test_delete_not_found(self, session):
        """Eliminar un comentario inexistente debe retornar False."""
        repo = CommentRepository(session)
        result = await repo.delete(uuid4())
        assert result is False

    async def test_list_by_incident(self, session):
        """Listar comentarios de un incidente."""
        repo = CommentRepository(session)
        incident = await self._create_incident(session)
        c1 = Comment(_incident_id=incident.id, _content="Primero")
        c2 = Comment(_incident_id=incident.id, _content="Segundo")
        await repo.create(c1)
        await repo.create(c2)
        items, total = await repo.list_by_incident(incident.id)
        assert total == 2
        assert len(items) == 2

    async def test_list_by_incident_exclude_internal(self, session):
        """Filtrar comentarios internos debe excluirlos."""
        repo = CommentRepository(session)
        incident = await self._create_incident(session)
        c1 = Comment(_incident_id=incident.id, _content="Público")
        c2 = Comment(_incident_id=incident.id, _content="Interno")
        c2.is_internal = True
        await repo.create(c1)
        await repo.create(c2)
        items, total = await repo.list_by_incident(incident.id, include_internal=False)
        assert total == 1
        assert items[0].content == "Público"

    async def test_list_by_incident_include_internal(self, session):
        """Incluir comentarios internos debe retornar todos."""
        repo = CommentRepository(session)
        incident = await self._create_incident(session)
        c1 = Comment(_incident_id=incident.id, _content="Público")
        c2 = Comment(_incident_id=incident.id, _content="Interno")
        c2.is_internal = True
        await repo.create(c1)
        await repo.create(c2)
        items, total = await repo.list_by_incident(incident.id, include_internal=True)
        assert total == 2

    async def test_list_by_incident_pagination(self, session):
        """La paginación debe funcionar."""
        repo = CommentRepository(session)
        incident = await self._create_incident(session)
        for i in range(5):
            await repo.create(Comment(_incident_id=incident.id, _content=f"Comentario {i}"))
        items, total = await repo.list_by_incident(incident.id, skip=0, limit=2)
        assert len(items) == 2
        assert total == 5
