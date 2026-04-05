"""Unit tests for domain entities."""

import pytest
from uuid import uuid4

from src.domain.entities.incident import Incident
from src.domain.entities.user import User, UserRole
from src.domain.value_objects import PriorityLevel, IncidentStatus


class TestIncident:
    """Tests for Incident entity."""

    def test_create_incident(self):
        """Test creating an incident."""
        incident = Incident()
        incident.title = "Test Incident"
        incident.description = "Test Description"

        assert incident.title == "Test Incident"
        assert incident.description == "Test Description"
        assert incident.status == IncidentStatus.NEW
        assert incident.priority is None

    def test_assign_priority(self):
        """Test assigning priority to an incident."""
        incident = Incident()
        incident.title = "Test"
        incident.description = "Test"

        incident.assign_priority(
            priority=PriorityLevel.P4_CRITICAL,
            confidence=0.95,
            explanation="Critical issue detected"
        )

        assert incident.priority == PriorityLevel.P4_CRITICAL
        assert incident.confidence_score == 0.95
        assert incident.explanation == "Critical issue detected"
        assert incident.sla_deadline is not None

    def test_escalate_incident(self):
        """Test escalating an incident."""
        incident = Incident()
        incident.title = "Test"
        incident.description = "Test"
        incident.assign_priority(PriorityLevel.P2_MEDIUM, 0.8, "Medium priority")

        old_priority = incident.priority
        new_priority = incident.escalate()

        assert new_priority == PriorityLevel.P3_HIGH
        assert incident.priority == PriorityLevel.P3_HIGH

    def test_should_escalate(self):
        """Test should_escalate method."""
        incident = Incident()
        incident.title = "Test"
        incident.description = "Test"
        incident.assign_priority(PriorityLevel.P4_CRITICAL, 0.9, "Critical")

        assert incident.should_escalate() is True


class TestUser:
    """Tests for User entity."""

    def test_create_user(self):
        """Test creating a user."""
        user = User()
        user.email = "test@example.com"
        user.username = "testuser"
        user.set_password("password123")

        assert user.email == "test@example.com"
        assert user.username == "testuser"
        assert user.is_active is True
        assert user.verify_password("password123") is True

    def test_invalid_email(self):
        """Test invalid email raises error."""
        user = User()
        with pytest.raises(ValueError):
            user.email = "invalid-email"

    def test_password_verification(self):
        """Test password verification."""
        user = User()
        user.set_password("secret123")

        assert user.verify_password("secret123") is True
        assert user.verify_password("wrong") is False
