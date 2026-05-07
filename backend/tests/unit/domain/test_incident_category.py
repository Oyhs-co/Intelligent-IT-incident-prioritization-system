"""Tests unitarios para IncidentCategory."""

import pytest

from src.domain.value_objects.priority_level import IncidentCategory


class TestIncidentCategory:
    """Tests para el value object IncidentCategory."""

    @pytest.mark.parametrize("input_str,expected", [
        ("infrastructure", IncidentCategory.INFRASTRUCTURE),
        ("application", IncidentCategory.APPLICATION),
        ("network", IncidentCategory.NETWORK),
        ("security", IncidentCategory.SECURITY),
        ("database", IncidentCategory.DATABASE),
        ("hardware", IncidentCategory.HARDWARE),
        ("software", IncidentCategory.SOFTWARE),
        ("access", IncidentCategory.ACCESS),
        ("other", IncidentCategory.OTHER),
    ])
    def test_from_string_validos(self, input_str, expected):
        """from_string debe retornar la categoría correcta."""
        assert IncidentCategory.from_string(input_str) == expected

    def test_from_string_case_insensitive(self):
        """from_string debe ser case insensitive."""
        assert IncidentCategory.from_string("NETWORK") == IncidentCategory.NETWORK
        assert IncidentCategory.from_string("Network") == IncidentCategory.NETWORK

    def test_from_string_invalido_retorna_other(self):
        """from_string con valor inválido debe retornar OTHER."""
        assert IncidentCategory.from_string("invalid_category") == IncidentCategory.OTHER
        assert IncidentCategory.from_string("") == IncidentCategory.OTHER

    def test_todos_los_valores(self):
        """Debe tener todos los valores definidos."""
        expected_values = [
            "infrastructure", "application", "network", "security",
            "database", "hardware", "software", "access", "other",
        ]
        values = [e.value for e in IncidentCategory]
        assert all(v in values for v in expected_values)
