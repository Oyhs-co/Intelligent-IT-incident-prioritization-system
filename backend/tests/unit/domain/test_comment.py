"""Tests unitarios para la entidad Comment."""

from uuid import uuid4

import pytest

from src.domain.entities.comment import Comment


class TestComment:
    """Tests para la entidad Comment."""

    def test_crear_comentario(self):
        """Crear un comentario con campos básicos."""
        incident_id = uuid4()
        user_id = uuid4()
        comment = Comment()
        comment.incident_id = incident_id
        comment.user_id = user_id
        comment.content = "Este es un comentario de prueba"
        assert comment.incident_id == incident_id
        assert comment.user_id == user_id
        assert comment.content == "Este es un comentario de prueba"
        assert comment.is_internal is False

    def test_content_empty_raise_error(self):
        """content vacío debe lanzar ValueError."""
        comment = Comment()
        with pytest.raises(ValueError, match="cannot be empty"):
            comment.content = ""

    def test_content_whitespace_only_raise_error(self):
        """content con solo espacios debe lanzar ValueError."""
        comment = Comment()
        with pytest.raises(ValueError, match="cannot be empty"):
            comment.content = "   "

    def test_is_internal_default_false(self):
        """is_internal debe ser False por defecto."""
        comment = Comment()
        assert comment.is_internal is False

    def test_is_internal_setter(self):
        """is_internal se debe poder cambiar."""
        comment = Comment()
        comment.is_internal = True
        assert comment.is_internal is True
        comment.is_internal = False
        assert comment.is_internal is False

    def test_to_dict(self):
        """to_dict debe incluir todos los campos."""
        incident_id = uuid4()
        user_id = uuid4()
        comment = Comment()
        comment.incident_id = incident_id
        comment.user_id = user_id
        comment.content = "Test content"
        comment.is_internal = True
        d = comment.to_dict()
        assert d["incident_id"] == str(incident_id)
        assert d["user_id"] == str(user_id)
        assert d["content"] == "Test content"
        assert d["is_internal"] is True
        assert "id" in d
        assert "created_at" in d
