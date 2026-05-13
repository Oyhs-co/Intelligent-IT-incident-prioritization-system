"""Tests unitarios para la entidad IncidentEvent."""

from uuid import uuid4

from src.domain.entities.incident_event import IncidentEvent
from src.domain.value_objects.priority_level import EventType


class TestIncidentEvent:
    """Tests para la entidad IncidentEvent."""

    def test_crear_evento_created(self):
        """Crear un evento de tipo CREATED."""
        incident_id = uuid4()
        event = IncidentEvent()
        event.incident_id = incident_id
        event.event_type = EventType.CREATED
        assert event.incident_id == incident_id
        assert event.event_type == EventType.CREATED
        assert event.old_value is None
        assert event.new_value is None

    def test_evento_con_valores(self):
        """Crear un evento con old/new value."""
        event = IncidentEvent()
        event.incident_id = uuid4()
        event.event_type = EventType.STATUS_CHANGED
        object.__setattr__(event, "_old_value", "new")
        object.__setattr__(event, "_new_value", "in_progress")
        assert event.old_value == "new"
        assert event.new_value == "in_progress"

    def test_evento_con_user_id(self):
        """Crear un evento con user_id."""
        user_id = uuid4()
        event = IncidentEvent()
        event.incident_id = uuid4()
        event.user_id = user_id
        assert event.user_id == user_id

    def test_evento_con_metadata(self):
        """Crear un evento con metadatos."""
        event = IncidentEvent()
        event.incident_id = uuid4()
        object.__setattr__(event, "_metadata", {"reason": "test"})
        assert event.metadata == {"reason": "test"}

    def test_event_type_default(self):
        """El tipo de evento por defecto debe ser CREATED."""
        event = IncidentEvent()
        event.incident_id = uuid4()
        assert event.event_type == EventType.CREATED

    def test_todos_los_event_types(self):
        """Deben existir todos los tipos de eventos de auditoría."""
        types = [
            EventType.CREATED,
            EventType.UPDATED,
            EventType.STATUS_CHANGED,
            EventType.PRIORITY_CHANGED,
            EventType.ASSIGNED,
            EventType.ESCALATED,
            EventType.RESOLVED,
            EventType.CLOSED,
            EventType.REOPENED,
            EventType.COMMENT_ADDED,
        ]
        for t in types:
            assert isinstance(t, EventType)

    def test_to_dict(self):
        """to_dict debe incluir todos los campos."""
        incident_id = uuid4()
        user_id = uuid4()
        event = IncidentEvent()
        event.incident_id = incident_id
        event.event_type = EventType.ASSIGNED
        event.user_id = user_id
        object.__setattr__(event, "_old_value", "unassigned")
        object.__setattr__(event, "_new_value", str(user_id))
        d = event.to_dict()
        assert d["incident_id"] == str(incident_id)
        assert d["event_type"] == "assigned"
        assert d["old_value"] == "unassigned"
        assert d["new_value"] == str(user_id)
        assert d["user_id"] == str(user_id)
        assert "id" in d
        assert "created_at" in d
