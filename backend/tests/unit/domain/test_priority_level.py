"""Tests unitarios para PriorityLevel."""

import pytest

from src.domain.value_objects.priority_level import PriorityLevel


class TestPriorityLevel:
    """Tests para el value object PriorityLevel."""

    def test_from_int_1(self):
        """from_int(1) debe retornar P1_LOW."""
        assert PriorityLevel.from_int(1) == PriorityLevel.P1_LOW

    def test_from_int_2(self):
        """from_int(2) debe retornar P2_MEDIUM."""
        assert PriorityLevel.from_int(2) == PriorityLevel.P2_MEDIUM

    def test_from_int_3(self):
        """from_int(3) debe retornar P3_HIGH."""
        assert PriorityLevel.from_int(3) == PriorityLevel.P3_HIGH

    def test_from_int_4(self):
        """from_int(4) debe retornar P4_CRITICAL."""
        assert PriorityLevel.from_int(4) == PriorityLevel.P4_CRITICAL

    def test_from_int_invalido_menor(self):
        """from_int(0) debe lanzar ValueError."""
        with pytest.raises(ValueError):
            PriorityLevel.from_int(0)

    def test_from_int_invalido_mayor(self):
        """from_int(5) debe lanzar ValueError."""
        with pytest.raises(ValueError):
            PriorityLevel.from_int(5)

    def test_from_int_invalido_negativo(self):
        """from_int(-1) debe lanzar ValueError."""
        with pytest.raises(ValueError):
            PriorityLevel.from_int(-1)

    @pytest.mark.parametrize("input_str,expected", [
        ("P1", PriorityLevel.P1_LOW),
        ("p1", PriorityLevel.P1_LOW),
        ("LOW", PriorityLevel.P1_LOW),
        ("low", PriorityLevel.P1_LOW),
        ("1", PriorityLevel.P1_LOW),
        ("P2", PriorityLevel.P2_MEDIUM),
        ("MEDIUM", PriorityLevel.P2_MEDIUM),
        ("2", PriorityLevel.P2_MEDIUM),
        ("P3", PriorityLevel.P3_HIGH),
        ("HIGH", PriorityLevel.P3_HIGH),
        ("3", PriorityLevel.P3_HIGH),
        ("P4", PriorityLevel.P4_CRITICAL),
        ("CRITICAL", PriorityLevel.P4_CRITICAL),
        ("4", PriorityLevel.P4_CRITICAL),
    ])
    def test_from_string_validos(self, input_str, expected):
        """from_string debe parsear correctamente strings válidos."""
        assert PriorityLevel.from_string(input_str) == expected

    @pytest.mark.parametrize("invalid", ["P5", "INVALID", "URGENT", "LOWEST", "", "P0", "0"])
    def test_from_string_invalidos(self, invalid):
        """from_string debe lanzar ValueError para strings inválidos."""
        with pytest.raises(ValueError):
            PriorityLevel.from_string(invalid)

    def test_label_p1_low(self):
        """P1_LOW debe tener label 'P1 (Low)'."""
        assert PriorityLevel.P1_LOW.label == "P1 (Low)"

    def test_label_p2_medium(self):
        """P2_MEDIUM debe tener label 'P2 (Medium)'."""
        assert PriorityLevel.P2_MEDIUM.label == "P2 (Medium)"

    def test_label_p3_high(self):
        """P3_HIGH debe tener label 'P3 (High)'."""
        assert PriorityLevel.P3_HIGH.label == "P3 (High)"

    def test_label_p4_critical(self):
        """P4_CRITICAL debe tener label 'P4 (Critical)'."""
        assert PriorityLevel.P4_CRITICAL.label == "P4 (Critical)"

    def test_sla_minutes_p1(self):
        """P1_LOW debe tener SLA de 480 minutos (8h)."""
        assert PriorityLevel.P1_LOW.sla_minutes == 480

    def test_sla_minutes_p2(self):
        """P2_MEDIUM debe tener SLA de 240 minutos (4h)."""
        assert PriorityLevel.P2_MEDIUM.sla_minutes == 240

    def test_sla_minutes_p3(self):
        """P3_HIGH debe tener SLA de 60 minutos (1h)."""
        assert PriorityLevel.P3_HIGH.sla_minutes == 60

    def test_sla_minutes_p4(self):
        """P4_CRITICAL debe tener SLA de 15 minutos."""
        assert PriorityLevel.P4_CRITICAL.sla_minutes == 15

    def test_color_p1_verde(self):
        """P1_LOW debe tener color verde."""
        assert PriorityLevel.P1_LOW.color == "#22C55E"

    def test_color_p2_amarillo(self):
        """P2_MEDIUM debe tener color amarillo."""
        assert PriorityLevel.P2_MEDIUM.color == "#EAB308"

    def test_color_p3_naranja(self):
        """P3_HIGH debe tener color naranja."""
        assert PriorityLevel.P3_HIGH.color == "#F97316"

    def test_color_p4_rojo(self):
        """P4_CRITICAL debe tener color rojo."""
        assert PriorityLevel.P4_CRITICAL.color == "#DC2626"
