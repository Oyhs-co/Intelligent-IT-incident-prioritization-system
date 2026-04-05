"""Unit tests for application layer services."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from uuid import uuid4

from src.application.services.ai_service import AIService, PredictionResult
from src.application.services.metrics_service import MetricsService, OverviewMetrics
from src.application.services.auth_service import AuthService


class TestAIService:
    """Tests for AIService."""

    def test_init_creates_service(self):
        """Test service initialization."""
        service = AIService()
        assert service is not None
        assert service._model_loaded is False

    def test_is_model_available_returns_false_when_not_loaded(self):
        """Test model availability check."""
        service = AIService()
        assert service.is_model_available() is False

    @pytest.mark.asyncio
    async def test_predict_priority_returns_default_when_no_model(self):
        """Test prediction returns default when model unavailable."""
        service = AIService()
        result = await service.predict_priority("test text")

        assert result is not None
        assert result.priority == 3
        assert result.confidence == 0.5

    def test_get_model_info_returns_info(self):
        """Test getting model info."""
        service = AIService()
        info = service.get_model_info()

        assert "model_loaded" in info
        assert "model_path" in info


class TestMetricsService:
    """Tests for MetricsService."""

    @pytest.mark.asyncio
    async def test_get_overview_metrics_returns_metrics(self):
        """Test getting overview metrics."""
        session = AsyncMock()
        service = MetricsService(session)

        with patch("src.infrastructure.database.models.IncidentModel") as MockIncident:
            with patch("src.infrastructure.database.models.UserModel") as MockUser:
                mock_result = MagicMock()
                mock_result.scalars.return_value.all.return_value = []
                session.execute = AsyncMock(return_value=mock_result)

                metrics = await service.get_overview_metrics()

                assert isinstance(metrics, OverviewMetrics)


class TestAuthService:
    """Tests for AuthService."""

    def test_init_creates_service(self):
        """Test service initialization."""
        service = AuthService()
        assert service is not None
