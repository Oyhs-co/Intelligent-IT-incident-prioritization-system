"""Tests unitarios para las funciones de mapeo de prioridades IA ↔ Backend."""

import pytest

from src.domain.value_objects.priority_level import (
    PriorityLevel,
    map_ia_to_backend,
    map_backend_to_ia,
)


class TestMapIaToBackend:
    """Tests para map_ia_to_backend()."""

    @pytest.mark.parametrize("ia_input,expected", [
        (0, PriorityLevel.P4_CRITICAL),
        (1, PriorityLevel.P2_MEDIUM),
        (2, PriorityLevel.P1_LOW),
    ])
    def test_mapeo_correcto(self, ia_input, expected):
        """map_ia_to_backend debe mapear correctamente 0→4, 1→2, 2→1."""
        assert map_ia_to_backend(ia_input) == expected

    @pytest.mark.parametrize("invalid", [-1, 3, 5, 999])
    def test_valor_invalido(self, invalid):
        """map_ia_to_backend debe lanzar ValueError para valores inválidos."""
        with pytest.raises(ValueError, match="Prioridad de IA inválida"):
            map_ia_to_backend(invalid)


class TestMapBackendToIa:
    """Tests para map_backend_to_ia()."""

    @pytest.mark.parametrize("backend_input,expected", [
        (PriorityLevel.P1_LOW, 2),
        (PriorityLevel.P2_MEDIUM, 1),
        (PriorityLevel.P3_HIGH, 0),
        (PriorityLevel.P4_CRITICAL, 0),
    ])
    def test_mapeo_correcto(self, backend_input, expected):
        """map_backend_to_ia debe mapear 1→2, 2→1, 3→0, 4→0."""
        assert map_backend_to_ia(backend_input) == expected
