"""Unit tests for application layer use cases."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from uuid import uuid4

from src.application.use_cases.incidents.create_incident import (
    CreateIncidentUseCase,
    CreateIncidentRequest,
)
from src.application.use_cases.incidents.classify_incident import (
    ClassifyIncidentUseCase,
)
from src.application.use_cases.incidents.list_incidents import (
    ListIncidentsUseCase,
)
from src.application.use_cases.incidents.get_incident import (
    GetIncidentUseCase,
)


@pytest.fixture
def mock_incident_repository():
    """Create a mock incident repository."""
    return AsyncMock()


@pytest.fixture
def mock_event_repository():
    """Create a mock event repository."""
    return AsyncMock()


@pytest.fixture
def mock_ai_service():
    """Create a mock AI service."""
    service = MagicMock()
    service.predict_priority = AsyncMock()
    return service


class TestCreateIncidentUseCase:
    """Tests for CreateIncidentUseCase."""

    @pytest.mark.asyncio
    async def test_execute_creates_incident(
        self,
        mock_incident_repository,
        mock_event_repository,
        mock_ai_service,
    ):
        """Test creating an incident."""
        incident_id = uuid4()
        mock_incident_repository.get_next_ticket_number = AsyncMock(return_value="INC-001")
        mock_incident_repository.create = AsyncMock(return_value=MagicMock(
            id=incident_id,
            ticket_number="INC-001",
            title="Test",
            description="Test description",
            urgency=3,
            impact=3,
            priority=None,
            status=MagicMock(value="new"),
            category=None,
        ))
        mock_event_repository.create = AsyncMock(return_value=MagicMock())

        use_case = CreateIncidentUseCase(
            mock_incident_repository,
            mock_event_repository,
            mock_ai_service,
        )

        request = CreateIncidentRequest(
            title="Test",
            description="Test description",
            urgency=3,
            impact=3,
        )

        result = await use_case.execute(request)

        assert result is not None
        mock_incident_repository.create.assert_called_once()
        mock_event_repository.create.assert_called_once()


class TestClassifyIncidentUseCase:
    """Tests for ClassifyIncidentUseCase."""

    @pytest.mark.asyncio
    async def test_execute_classifies_incident(
        self,
        mock_incident_repository,
        mock_event_repository,
        mock_ai_service,
    ):
        """Test classifying an incident."""
        incident_id = uuid4()
        mock_incident = MagicMock(
            id=incident_id,
            title="Test",
            description="Test description",
            priority=None,
        )
        mock_incident_repository.get_by_id = AsyncMock(return_value=mock_incident)
        mock_incident_repository.update = AsyncMock(return_value=mock_incident)
        mock_event_repository.create = AsyncMock(return_value=MagicMock())

        mock_ai_service.predict_priority = AsyncMock(return_value=MagicMock(
            priority=2,
            confidence=0.85,
            reasoning="Test reasoning",
            top_features=["feature1", "feature2"],
            processing_time_ms=50.0,
        ))

        use_case = ClassifyIncidentUseCase(
            mock_incident_repository,
            mock_event_repository,
            mock_ai_service,
        )

        result = await use_case.execute(incident_id)

        assert result is not None
        assert result.priority == 2
        assert result.confidence == 0.85

    @pytest.mark.asyncio
    async def test_execute_raises_error_for_missing_incident(
        self,
        mock_incident_repository,
        mock_event_repository,
        mock_ai_service,
    ):
        """Test error when incident not found."""
        mock_incident_repository.get_by_id = AsyncMock(return_value=None)

        use_case = ClassifyIncidentUseCase(
            mock_incident_repository,
            mock_event_repository,
            mock_ai_service,
        )

        with pytest.raises(ValueError):
            await use_case.execute(uuid4())


class TestListIncidentsUseCase:
    """Tests for ListIncidentsUseCase."""

    @pytest.mark.asyncio
    async def test_execute_lists_incidents(
        self,
        mock_incident_repository,
    ):
        """Test listing incidents."""
        mock_incident_repository.list = AsyncMock(return_value=MagicMock(
            items=[],
            total=0,
            skip=0,
            limit=10,
        ))

        use_case = ListIncidentsUseCase(mock_incident_repository)

        result = await use_case.execute(skip=0, limit=10)

        assert result is not None
        assert hasattr(result, "items")
        assert hasattr(result, "total")


class TestGetIncidentUseCase:
    """Tests for GetIncidentUseCase."""

    @pytest.mark.asyncio
    async def test_execute_returns_incident(
        self,
        mock_incident_repository,
    ):
        """Test getting an incident."""
        incident_id = uuid4()
        mock_incident = MagicMock(id=incident_id, title="Test")
        mock_incident_repository.get_by_id = AsyncMock(return_value=mock_incident)

        use_case = GetIncidentUseCase(mock_incident_repository)

        result = await use_case.execute(incident_id)

        assert result is not None
        assert result.id == incident_id

    @pytest.mark.asyncio
    async def test_execute_raises_error_for_missing_incident(
        self,
        mock_incident_repository,
    ):
        """Test error when incident not found."""
        mock_incident_repository.get_by_id = AsyncMock(return_value=None)

        use_case = GetIncidentUseCase(mock_incident_repository)

        with pytest.raises(ValueError):
            await use_case.execute(uuid4())
