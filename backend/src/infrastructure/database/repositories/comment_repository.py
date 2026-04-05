"""Repositorio de comentarios."""

from __future__ import annotations

from typing import TYPE_CHECKING, Optional
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.domain.entities.comment import Comment
from src.domain.repositories import ICommentRepository
from ..models.comment_model import CommentModel

if TYPE_CHECKING:
    pass


class CommentRepository(ICommentRepository):
    """Implementación del repositorio de comentarios."""

    def __init__(self, session: AsyncSession):
        self._session = session

    def _model_to_entity(self, model: CommentModel) -> Comment:
        """Convierte modelo ORM a entidad de dominio."""
        comment = Comment()
        comment._id = UUID(model.id)
        comment._incident_id = UUID(model.incident_id)
        comment._user_id = UUID(model.user_id) if model.user_id else None
        comment._content = model.content
        comment._is_internal = model.is_internal
        comment._created_at = model.created_at
        comment._updated_at = model.updated_at
        return comment

    def _entity_to_model(self, entity: Comment) -> CommentModel:
        """Convierte entidad de dominio a modelo ORM."""
        return CommentModel(
            id=str(entity.id),
            incident_id=str(entity.incident_id),
            user_id=str(entity.user_id) if entity.user_id else None,
            content=entity.content,
            is_internal=entity.is_internal,
            created_at=entity.created_at,
            updated_at=entity.updated_at,
        )

    async def create(self, comment: Comment) -> Comment:
        """Crea un nuevo comentario."""
        model = self._entity_to_model(comment)
        self._session.add(model)
        await self._session.flush()
        await self._session.refresh(model)
        return self._model_to_entity(model)

    async def get_by_id(self, comment_id: UUID) -> Optional[Comment]:
        """Obtiene un comentario por su ID."""
        stmt = select(CommentModel).where(CommentModel.id == str(comment_id))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return None
        return self._model_to_entity(model)

    async def update(self, comment: Comment) -> Comment:
        """Actualiza un comentario existente."""
        stmt = select(CommentModel).where(CommentModel.id == str(comment.id))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            raise ValueError(f"Comment {comment.id} not found")

        model.content = comment.content
        model.is_internal = comment.is_internal

        await self._session.flush()
        await self._session.refresh(model)
        return self._model_to_entity(model)

    async def delete(self, comment_id: UUID) -> bool:
        """Elimina un comentario."""
        stmt = select(CommentModel).where(CommentModel.id == str(comment_id))
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model is None:
            return False
        await self._session.delete(model)
        await self._session.flush()
        return True

    async def list_by_incident(
        self,
        incident_id: UUID,
        skip: int = 0,
        limit: int = 100,
        include_internal: bool = False,
    ) -> tuple[list[Comment], int]:
        """Lista comentarios de un incidente."""
        stmt = select(CommentModel).where(CommentModel.incident_id == str(incident_id))
        count_stmt = select(func.count(CommentModel.id)).where(
            CommentModel.incident_id == str(incident_id)
        )

        if not include_internal:
            stmt = stmt.where(CommentModel.is_internal == False)
            count_stmt = count_stmt.where(CommentModel.is_internal == False)

        stmt = stmt.order_by(CommentModel.created_at.desc()).offset(skip).limit(limit)

        count_result = await self._session.execute(count_stmt)
        total = count_result.scalar() or 0

        result = await self._session.execute(stmt)
        models = result.scalars().all()

        comments = [self._model_to_entity(m) for m in models]
        return comments, total
