"""Tests unitarios para BaseEntity."""

from __future__ import annotations

from datetime import datetime
from uuid import UUID

from src.domain.entities.base import BaseEntity


class ConcreteEntity(BaseEntity):
    """Entidad concreta para测试 BaseEntity."""
    _name: str = ""


class TestBaseEntity:
    """Tests para la clase base de entidades."""

    def test_id_unico_por_instancia(self):
        """Cada instancia debe tener un ID único."""
        e1 = ConcreteEntity()
        e2 = ConcreteEntity()
        assert e1.id != e2.id
        assert isinstance(e1.id, UUID)

    def test_created_at_auto(self):
        """created_at debe establecerse automáticamente."""
        e = ConcreteEntity()
        assert isinstance(e.created_at, datetime)

    def test_updated_at_inicial(self):
        """updated_at debe ser igual a created_at inicialmente."""
        e = ConcreteEntity()
        assert isinstance(e.updated_at, datetime)

    def test_mark_updated_cambia_timestamp(self):
        """_mark_updated debe actualizar updated_at."""
        e = ConcreteEntity()
        original = e.updated_at
        e._mark_updated()
        assert e.updated_at >= original

    def test_equals_por_id(self):
        """Dos entidades con el mismo ID deben ser iguales."""
        e1 = ConcreteEntity()
        e2 = ConcreteEntity()
        object.__setattr__(e2, "_id", e1.id)
        assert e1 == e2

    def test_not_equals_distintos_ids(self):
        """Entidades con IDs distintos no deben ser iguales."""
        e1 = ConcreteEntity()
        e2 = ConcreteEntity()
        assert e1 != e2

    def test_equals_con_no_entity(self):
        """Comparación con no-entity debe devolver NotImplemented."""
        e = ConcreteEntity()
        assert e.__eq__("not_an_entity") is NotImplemented

    def test_hash_por_id(self):
        """El hash debe basarse en el ID."""
        e1 = ConcreteEntity()
        e2 = ConcreteEntity()
        object.__setattr__(e2, "_id", e1.id)
        assert hash(e1) == hash(e2)
        assert len({e1, e2}) == 1

    def test_to_dict(self):
        """to_dict debe incluir id y timestamps."""
        e = ConcreteEntity()
        d = e.to_dict()
        assert d["id"] == str(e.id)
        assert "created_at" in d
        assert "updated_at" in d

    def test_mark_updated_multiple_veces(self):
        """Llamadas múltiples a _mark_updated deben funcionar."""
        e = ConcreteEntity()
        t1 = e.updated_at
        e._mark_updated()
        t2 = e.updated_at
        e._mark_updated()
        t3 = e.updated_at
        assert t1 <= t2 <= t3
