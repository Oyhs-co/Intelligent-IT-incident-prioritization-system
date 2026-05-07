"""Tests unitarios para IncidentStatus."""

import pytest

from src.domain.value_objects.priority_level import IncidentStatus


class TestIncidentStatus:
    """Tests para el value object IncidentStatus."""

    def test_from_string_new(self):
        """from_string('new') debe retornar NEW."""
        assert IncidentStatus.from_string("new") == IncidentStatus.NEW

    def test_from_string_open(self):
        """from_string('open') debe retornar OPEN."""
        assert IncidentStatus.from_string("open") == IncidentStatus.OPEN

    def test_from_string_in_progress(self):
        """from_string('in_progress') debe retornar IN_PROGRESS."""
        assert IncidentStatus.from_string("in_progress") == IncidentStatus.IN_PROGRESS

    def test_from_string_on_hold(self):
        """from_string('on_hold') debe retornar ON_HOLD."""
        assert IncidentStatus.from_string("on_hold") == IncidentStatus.ON_HOLD

    def test_from_string_pending(self):
        """from_string('pending') debe retornar PENDING."""
        assert IncidentStatus.from_string("pending") == IncidentStatus.PENDING

    def test_from_string_resolved(self):
        """from_string('resolved') debe retornar RESOLVED."""
        assert IncidentStatus.from_string("resolved") == IncidentStatus.RESOLVED

    def test_from_string_closed(self):
        """from_string('closed') debe retornar CLOSED."""
        assert IncidentStatus.from_string("closed") == IncidentStatus.CLOSED

    def test_from_string_rejected(self):
        """from_string('rejected') debe retornar REJECTED."""
        assert IncidentStatus.from_string("rejected") == IncidentStatus.REJECTED

    def test_from_string_invalido(self):
        """from_string('invalid_status') debe lanzar ValueError."""
        with pytest.raises(ValueError):
            IncidentStatus.from_string("invalid_status")

    @pytest.mark.parametrize("status,expected", [
        (IncidentStatus.NEW, True),
        (IncidentStatus.OPEN, True),
        (IncidentStatus.IN_PROGRESS, True),
        (IncidentStatus.ON_HOLD, True),
        (IncidentStatus.PENDING, True),
        (IncidentStatus.RESOLVED, False),
        (IncidentStatus.CLOSED, False),
        (IncidentStatus.REJECTED, False),
    ])
    def test_is_active(self, status, expected):
        """is_active debe retornar True solo para estados no finales."""
        assert status.is_active == expected

    @pytest.mark.parametrize("status,expected", [
        (IncidentStatus.NEW, False),
        (IncidentStatus.OPEN, False),
        (IncidentStatus.IN_PROGRESS, False),
        (IncidentStatus.ON_HOLD, False),
        (IncidentStatus.PENDING, False),
        (IncidentStatus.RESOLVED, False),
        (IncidentStatus.CLOSED, True),
        (IncidentStatus.REJECTED, True),
    ])
    def test_is_final(self, status, expected):
        """is_final debe retornar True solo para CLOSED y REJECTED."""
        assert status.is_final == expected
