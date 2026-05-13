"""Tests unitarios para la entidad Incident."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from uuid import UUID, uuid4

import pytest

from src.domain.entities.incident import Incident
from src.domain.value_objects.priority_level import (
    IncidentSource,
    IncidentStatus,
    PriorityLevel,
)


def _make_incident(**kwargs) -> Incident:
    """Crea un Incident con valores mínimos."""
    i = Incident()
    defaults = {
        "title": "Incidente de prueba",
        "description": "Descripción del incidente de prueba",
    }
    for k, v in {**defaults, **kwargs}.items():
        setattr(i, k, v)
    return i


class TestIncidentCreation:
    """Tests de creación básica de Incident."""

    def test_create_incident(self):
        """Crear un incidente debe tener valores por defecto correctos."""
        i = _make_incident()
        assert i.status == IncidentStatus.NEW
        assert i.priority is None
        assert i.source == IncidentSource.WEB
        assert i.urgency == 3
        assert i.impact == 3
        assert i.tags == []
        assert i.metadata == {}
        assert i.similar_incidents == []

    def test_create_with_custom_values(self):
        """Crear con valores personalizados."""
        i = _make_incident(
            title="Título personalizado",
            description="Descripción personalizada",
        )
        assert i.title == "Título personalizado"
        assert i.description == "Descripción personalizada"

    def test_id_is_uuid(self):
        """El ID debe ser un UUID."""
        i = _make_incident()
        assert isinstance(i.id, UUID)


class TestIncidentTitleValidation:
    """Tests de validación del título."""

    def test_title_empty_raise_error(self):
        """Título vacío debe lanzar ValueError."""
        i = Incident()
        with pytest.raises(ValueError, match="cannot be empty"):
            i.title = ""

    def test_title_whitespace_only_raise_error(self):
        """Título con solo espacios debe lanzar ValueError."""
        i = Incident()
        with pytest.raises(ValueError, match="cannot be empty"):
            i.title = "   "

    def test_title_too_long_raise_error(self):
        """Título mayor a 200 caracteres debe lanzar ValueError."""
        i = Incident()
        with pytest.raises(ValueError, match="cannot exceed 200"):
            i.title = "X" * 201

    def test_title_200_chars_ok(self):
        """Título de exactamente 200 caracteres debe ser válido."""
        i = Incident()
        i.title = "X" * 200
        assert len(i.title) == 200


class TestIncidentDescriptionValidation:
    """Tests de validación de la descripción."""

    def test_description_empty_raise_error(self):
        """Descripción vacía debe lanzar ValueError."""
        i = Incident()
        with pytest.raises(ValueError, match="cannot be empty"):
            i.description = ""

    def test_description_too_long_raise_error(self):
        """Descripción mayor a 5000 caracteres debe lanzar ValueError."""
        i = Incident()
        with pytest.raises(ValueError, match="cannot exceed 5000"):
            i.description = "X" * 5001

    def test_description_5000_chars_ok(self):
        """Descripción de exactamente 5000 caracteres debe ser válida."""
        i = Incident()
        i.description = "X" * 5000
        assert len(i.description) == 5000


class TestIncidentPriority:
    """Tests de asignación de prioridad."""

    def test_assign_priority(self):
        """assign_priority debe asignar prioridad y calcular SLA."""
        i = _make_incident()
        i.assign_priority(
            priority=PriorityLevel.P4_CRITICAL,
            confidence=0.95,
            explanation="Issue crítico detectado",
        )
        assert i.priority == PriorityLevel.P4_CRITICAL
        assert i.confidence_score == 0.95
        assert i.explanation == "Issue crítico detectado"
        assert i.sla_deadline is not None

    def test_assign_priority_with_similar(self):
        """assign_priority debe guardar incidentes similares."""
        i = _make_incident()
        similar_ids = [uuid4(), uuid4()]
        i.assign_priority(
            priority=PriorityLevel.P2_MEDIUM,
            confidence=0.8,
            explanation="Prioridad media",
            similar=similar_ids,
        )
        assert len(i.similar_incidents) == 2

    def test_assign_priority_with_model_version(self):
        """assign_priority debe guardar la versión del modelo."""
        i = _make_incident()
        i.assign_priority(
            priority=PriorityLevel.P2_MEDIUM,
            confidence=0.8,
            explanation="Test",
            model_version="v1.0.0",
        )
        assert i.ai_model_version == "v1.0.0"
        assert i.ai_processed_at is not None

    def test_assign_priority_sets_suggested(self):
        """assign_priority siempre guarda la sugerencia de IA."""
        i = _make_incident()
        i.assign_priority(
            priority=PriorityLevel.P3_HIGH, confidence=0.9, explanation="Test"
        )
        assert i.suggested_priority == PriorityLevel.P3_HIGH

    def test_assign_priority_only_once(self):
        """assign_priority no debe sobrescribir prioridad existente."""
        i = _make_incident()
        i.assign_priority(
            priority=PriorityLevel.P1_LOW, confidence=0.5, explanation="First"
        )
        first_priority = i.priority
        first_deadline = i.sla_deadline

        i.assign_priority(
            priority=PriorityLevel.P4_CRITICAL,
            confidence=0.99,
            explanation="Second",
        )
        assert i.priority == first_priority
        assert i.sla_deadline == first_deadline

    def test_assign_priority_invalid_confidence(self):
        """assign_priority con confidence fuera de rango debe lanzar ValueError."""
        i = _make_incident()
        with pytest.raises(ValueError, match="Confidence must be between"):
            i.assign_priority(
                priority=PriorityLevel.P2_MEDIUM, confidence=-0.1, explanation="Test"
            )
        with pytest.raises(ValueError, match="Confidence must be between"):
            i.assign_priority(
                priority=PriorityLevel.P2_MEDIUM, confidence=1.5, explanation="Test"
            )

    def test_set_priority_humano(self):
        """set_priority debe permitir a un humano definir prioridad."""
        i = _make_incident()
        i.set_priority(PriorityLevel.P4_CRITICAL)
        assert i.priority == PriorityLevel.P4_CRITICAL
        assert i.sla_deadline is not None

    def test_priority_label(self):
        """priority_label debe retornar la etiqueta de prioridad."""
        i = _make_incident()
        assert i.priority_label is None
        i.assign_priority(
            priority=PriorityLevel.P4_CRITICAL,
            confidence=0.9,
            explanation="Critical",
        )
        assert i.priority_label == "P4 (Critical)"


class TestIncidentEscalation:
    """Tests de escalación de incidentes."""

    def test_escalate_from_p1(self):
        """Escalar desde P1_LOW debe ir a P2_MEDIUM."""
        i = _make_incident()
        i.assign_priority(PriorityLevel.P1_LOW, 0.5, "Low")
        new = i.escalate()
        assert new == PriorityLevel.P2_MEDIUM
        assert i.priority == PriorityLevel.P2_MEDIUM

    def test_escalate_from_p2(self):
        """Escalar desde P2_MEDIUM debe ir a P3_HIGH."""
        i = _make_incident()
        i.assign_priority(PriorityLevel.P2_MEDIUM, 0.5, "Medium")
        new = i.escalate()
        assert new == PriorityLevel.P3_HIGH

    def test_escalate_from_p3(self):
        """Escalar desde P3_HIGH debe ir a P4_CRITICAL."""
        i = _make_incident()
        i.assign_priority(PriorityLevel.P3_HIGH, 0.5, "High")
        new = i.escalate()
        assert new == PriorityLevel.P4_CRITICAL

    def test_escalate_from_p4(self):
        """Escalar desde P4_CRITICAL debe mantener P4_CRITICAL."""
        i = _make_incident()
        i.assign_priority(PriorityLevel.P4_CRITICAL, 0.5, "Critical")
        new = i.escalate()
        assert new == PriorityLevel.P4_CRITICAL

    def test_escalate_without_priority(self):
        """Escalar sin prioridad debe ir a P3_HIGH."""
        i = _make_incident()
        new = i.escalate()
        assert new == PriorityLevel.P3_HIGH
        assert i.priority == PriorityLevel.P3_HIGH

    def test_escalate_updates_sla(self):
        """Escalar debe actualizar el SLA deadline."""
        i = _make_incident()
        i.assign_priority(PriorityLevel.P2_MEDIUM, 0.5, "Medium")
        original_deadline = i.sla_deadline
        i.escalate()
        assert i.sla_deadline is not None

    def test_should_escalate_no_priority(self):
        """Sin prioridad, should_escalate debe retornar True."""
        i = _make_incident()
        assert i.should_escalate() is True

    def test_should_escalate_p4_recent(self):
        """P4 recién creado no debe escalar."""
        i = _make_incident()
        i.assign_priority(PriorityLevel.P4_CRITICAL, 0.9, "Critical")
        # age es ~0, no debería escalar
        assert i.should_escalate() is False


class TestIncidentLifecycle:
    """Tests del ciclo de vida del incidente."""

    def test_assign_to(self):
        """assign_to debe asignar y cambiar estado a IN_PROGRESS."""
        i = _make_incident()
        tech_id = uuid4()
        i.assign_to(tech_id)
        assert i.assigned_to == tech_id
        assert i.status == IncidentStatus.IN_PROGRESS

    def test_assign_to_from_open(self):
        """assign_to desde OPEN debe cambiar a IN_PROGRESS."""
        i = _make_incident()
        i.status = IncidentStatus.OPEN
        i.assign_to(uuid4())
        assert i.status == IncidentStatus.IN_PROGRESS

    def test_assign_to_keeps_status_if_not_new_or_open(self):
        """assign_to desde IN_PROGRESS debe mantener el estado."""
        i = _make_incident()
        i.status = IncidentStatus.IN_PROGRESS
        i.assign_to(uuid4())
        assert i.status == IncidentStatus.IN_PROGRESS

    def test_resolve(self):
        """resolve debe marcar como resuelto."""
        i = _make_incident()
        resolver = uuid4()
        resolution = "Se corrigió el error"
        i.resolve(resolution=resolution, resolved_by=resolver, resolution_code="FIXED")
        assert i.status == IncidentStatus.RESOLVED
        assert i.resolution == resolution
        assert i.resolved_by == resolver
        assert i.resolution_code == "FIXED"
        assert i.resolved_at is not None

    def test_resolve_without_code(self):
        """resolve sin código debe funcionar."""
        i = _make_incident()
        i.resolve(resolution="Fixed", resolved_by=uuid4())
        assert i.status == IncidentStatus.RESOLVED
        assert i.resolution_code is None

    def test_close(self):
        """close debe cerrar el incidente."""
        i = _make_incident()
        closer = uuid4()
        i.close(closed_by=closer)
        assert i.status == IncidentStatus.CLOSED
        assert i.closed_by == closer
        assert i.closed_at is not None

    def test_reopen(self):
        """reopen debe reabrir el incidente y registrar motivo."""
        i = _make_incident()
        # Primero resolvemos
        i.resolve(resolution="Resuelto", resolved_by=uuid4())
        # Luego reabrimos
        i.reopen(reason="El problema persiste")
        assert i.status == IncidentStatus.OPEN
        assert i.metadata.get("reopen_reason") == "El problema persiste"


class TestIncidentTags:
    """Tests para manejo de tags."""

    def test_add_tag(self):
        """add_tag debe agregar una etiqueta."""
        i = _make_incident()
        i.add_tag("network")
        assert "network" in i.tags

    def test_add_tag_duplicate(self):
        """add_tag no debe duplicar etiquetas."""
        i = _make_incident()
        i.add_tag("network")
        i.add_tag("network")
        assert i.tags == ["network"]

    def test_tags_setter(self):
        """El setter de tags debe reemplazar todas las etiquetas."""
        i = _make_incident()
        i.tags = ["urgent", "production"]
        assert "urgent" in i.tags
        assert "production" in i.tags
        assert len(i.tags) == 2

    def test_tags_setter_creates_copy(self):
        """El setter de tags debe crear una copia."""
        i = _make_incident()
        original = ["a", "b"]
        i.tags = original
        original.append("c")
        assert i.tags == ["a", "b"]


class TestIncidentMetadata:
    """Tests para metadatos."""

    def test_metadata_setter(self):
        """El setter de metadata debe reemplazar los metadatos."""
        i = _make_incident()
        i.metadata = {"key": "value", "number": 42}
        assert i.metadata == {"key": "value", "number": 42}

    def test_metadata_setter_creates_copy(self):
        """El setter de metadata debe crear una copia."""
        i = _make_incident()
        original = {"a": 1}
        i.metadata = original
        original["b"] = 2
        assert i.metadata == {"a": 1}


class TestIncidentSourceSetter:
    """Tests para el setter de source."""

    def test_source_setter(self):
        """El setter de source debe cambiar la fuente."""
        i = _make_incident()
        assert i.source == IncidentSource.WEB
        i.source = IncidentSource.API
        assert i.source == IncidentSource.API

    def test_source_setter_mark_updated(self):
        """El setter de source debe marcar como actualizado."""
        i = _make_incident()
        original = i.updated_at
        i.source = IncidentSource.EMAIL
        assert i.updated_at >= original


class TestIncidentSimilarIncidents:
    """Tests para similar_incidents."""

    def test_similar_incidents_setter(self):
        """El setter de similar_incidents debe reemplazar la lista."""
        i = _make_incident()
        ids = [uuid4(), uuid4()]
        i.similar_incidents = ids
        assert len(i.similar_incidents) == 2
        assert i.similar_incidents == ids

    def test_similar_incidents_setter_creates_copy(self):
        """El setter de similar_incidents debe crear una copia."""
        i = _make_incident()
        original = [uuid4(), uuid4()]
        i.similar_incidents = original
        original.append(uuid4())
        assert len(i.similar_incidents) == 2


class TestIncidentSLA:
    """Tests de SLA."""

    def test_sla_deadline_calculated(self):
        """El SLA deadline debe calcularse al asignar prioridad."""
        i = _make_incident()
        i.assign_priority(PriorityLevel.P4_CRITICAL, 0.9, "Critical")
        assert i.sla_deadline is not None
        expected_minutes = 15  # P4_CRITICAL
        diff = (i.sla_deadline - datetime.now(UTC)).total_seconds() / 60
        assert 0 < diff <= expected_minutes + 1

    def test_is_sla_breached_no_deadline(self):
        """Sin SLA deadline, is_sla_breached debe ser False."""
        i = _make_incident()
        assert i.is_sla_breached is False

    def test_is_sla_at_risk_no_deadline(self):
        """Sin SLA deadline, is_sla_at_risk debe ser False."""
        i = _make_incident()
        assert i.is_sla_at_risk is False


class TestIncidentAge:
    """Tests de age."""

    def test_age_is_timedelta(self):
        """age debe ser un timedelta."""
        i = _make_incident()
        assert isinstance(i.age, timedelta)

    def test_age_increases(self):
        """age debe aumentar con el tiempo."""
        i = _make_incident()
        age1 = i.age
        age2 = i.age
        assert age2 >= age1


class TestIncidentToDict:
    """Tests para to_dict."""

    def test_to_dict_basic(self):
        """to_dict debe incluir campos básicos."""
        i = _make_incident()
        d = i.to_dict()
        assert d["title"] == "Incidente de prueba"
        assert d["status"] == "new"
        assert d["priority"] is None
        assert d["source"] == "web"
        assert d["tags"] == []
        assert d["metadata"] == {}
        assert "age_seconds" in d
        assert "is_sla_breached" in d

    def test_to_dict_with_priority(self):
        """to_dict debe incluir prioridad asignada."""
        i = _make_incident()
        i.assign_priority(PriorityLevel.P4_CRITICAL, 0.95, "Critical")
        d = i.to_dict()
        assert d["priority"] == 4
        assert d["priority_label"] == "P4 (Critical)"
        assert d["confidence_score"] == 0.95
        assert d["sla_deadline"] is not None
