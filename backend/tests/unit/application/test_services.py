"""Tests unitarios para servicios de la capa de aplicación."""

from __future__ import annotations

from datetime import UTC, datetime
from unittest.mock import AsyncMock, MagicMock, patch
from uuid import uuid4

import pytest
from jose import JWTError

from src.application.services.ai_service import AIService
from src.application.services.auth_service import AuthService
from src.application.services.metrics_service import MetricsService, OverviewMetrics

# =============================================================================
# AIService Tests
# =============================================================================

class TestAIService:
    """Tests para AIService."""

    def teardown_method(self):
        AIService._instance = None
        AIService._initialized = False

    def test_init_creates_service(self):
        """Inicialización debe crear servicio con modelo no cargado."""
        service = AIService()
        assert service is not None
        assert service._model_loaded is False

    def test_singleton_returns_same_instance(self):
        """Múltiples instancias deben retornar el mismo objeto."""
        s1 = AIService()
        s2 = AIService()
        assert s1 is s2

    def test_is_model_available_returns_true_when_model_exists(self):
        """Con modelo en disco, is_model_available debe cargar y retornar True."""
        service = AIService()
        assert service.is_model_available() is True

    @pytest.mark.asyncio
    async def test_predict_priority_returns_default_when_no_model(self):
        """Sin modelo debe retornar predicción por defecto."""
        service = AIService()
        with patch.object(AIService, "_ensure_model_loaded"):
            result = await service.predict_priority("test text")

        assert result is not None
        assert result.priority == 3
        assert result.confidence == 0.5
        assert result.reasoning == "Modelo no disponible"

    @pytest.mark.asyncio
    async def test_predict_priority_with_metadata(self):
        """Con metadatos debe retornar predicción por defecto."""
        service = AIService()
        with patch.object(AIService, "_ensure_model_loaded"):
            result = await service.predict_priority(
                "test text",
                metadata={"department": "IT", "incident_id": "123"},
            )

        assert result.priority == 3

    @pytest.mark.asyncio
    async def test_predict_batch_returns_defaults_when_no_model(self):
        """Batch sin modelo debe retornar defaults."""
        service = AIService()
        with patch.object(AIService, "_ensure_model_loaded"):
            results = await service.predict_batch(["text1", "text2"])

        assert len(results) == 2
        assert all(r.priority == 3 for r in results)
        assert all(r.confidence == 0.5 for r in results)

    @pytest.mark.asyncio
    async def test_predict_batch_with_metadata_list(self):
        """Batch con metadatos debe funcionar."""
        service = AIService()
        results = await service.predict_batch(
            ["text1", "text2"],
            metadata_list=[{"dept": "IT"}, {"dept": "HR"}],
        )

        assert len(results) == 2

    def test_get_model_info_returns_info(self):
        """get_model_info debe retornar diccionario con estado."""
        service = AIService()
        info = service.get_model_info()

        assert "modelo_cargado" in info
        assert "ruta_modelo" in info
        assert info["modelo_cargado"] is False

    @pytest.mark.asyncio
    async def test_predict_priority_with_mocked_model(self):
        """Con modelo mockeado debe aplicar map_ia_to_backend."""
        service = AIService()

        predictor_mock = MagicMock()
        predictor_mock.explain_prediction = MagicMock(return_value={
            "predicted_priority": 0,
            "confidence": 0.95,
            "contributing_features": [
                {"feature_name": "urgent", "score": 0.5},
                {"feature_name": "critical", "score": 0.3},
            ],
            "reasoning": "Alta urgencia detectada",
        })
        service._predictor = predictor_mock
        service._model_loaded = True

        result = await service.predict_priority(
            "Sistema caído urgente",
            metadata={"incident_id": "INC-001", "department": "IT"},
        )

        assert result.priority == 4
        assert result.confidence == 0.95
        assert len(result.top_features) > 0
        assert result.reasoning == "Alta urgencia detectada"

    @pytest.mark.asyncio
    async def test_predict_priority_error_handling(self):
        """Error en predict_priority debe retornar fallback."""
        service = AIService()

        predictor_mock = MagicMock()
        predictor_mock.explain_prediction = MagicMock(
            side_effect=Exception("Model error"),
        )
        service._predictor = predictor_mock
        service._model_loaded = True

        result = await service.predict_priority("test")

        assert result.priority == 3
        assert result.confidence == 0.0
        assert "Error" in result.reasoning

    @pytest.mark.asyncio
    async def test_predict_batch_error_handling(self):
        """Error en predict_batch debe retornar fallback."""
        service = AIService()

        predictor_mock = MagicMock()
        predictor_mock.batch_predict_with_confidence = MagicMock(
            side_effect=Exception("Batch error"),
        )
        service._predictor = predictor_mock
        service._model_loaded = True

        results = await service.predict_batch(["text1", "text2"])

        assert len(results) == 2
        assert all(r.priority == 3 for r in results)
        assert all(r.confidence == 0.0 for r in results)
        assert all("Error" in r.reasoning for r in results)

    @pytest.mark.asyncio
    async def test_predict_batch_with_mocked_results(self):
        """Batch con resultados mockeados debe aplicar mapeo."""
        service = AIService()

        predictor_mock = MagicMock()
        predictor_mock.batch_predict_with_confidence = MagicMock(
            return_value=[(0, 0.9), (2, 0.7)],
        )
        service._predictor = predictor_mock
        service._model_loaded = True

        results = await service.predict_batch(["critical", "low priority"])

        assert len(results) == 2
        assert results[0].priority == 4
        assert results[0].confidence == 0.9
        assert results[1].priority == 1
        assert results[1].confidence == 0.7
        assert results[1].reasoning == "Predicción en lote"


# =============================================================================
# MetricsService Tests
# =============================================================================

class TestMetricsService:
    """Tests para MetricsService."""

    @pytest.fixture
    def mock_session(self):
        return AsyncMock()

    @pytest.fixture
    def mock_result(self):
        result = MagicMock()
        result.scalar.return_value = 0
        result.all.return_value = []
        result.one.return_value = MagicMock(
            today=0, week=0, month=0,
            open=0, in_progress=0, resolved=0, closed=0,
            has_sla=0, sla_breach=0, ai_today=0,
            high=0, med_raw=0, low=0,
        )
        return result

    @pytest.mark.asyncio
    async def test_get_overview_metrics_empty(self, mock_session, mock_result):
        """Base de datos vacía debe retornar métricas en cero."""
        mock_session.execute.return_value = mock_result
        service = MetricsService(mock_session)

        metrics = await service.get_overview_metrics()

        assert isinstance(metrics, OverviewMetrics)
        assert metrics.total_incidents_today == 0
        assert metrics.active_users == 0
        assert metrics.active_technicians == 0
        assert metrics.avg_resolution_time_minutes == 0.0

    @pytest.mark.asyncio
    async def test_get_overview_metrics_with_data(self, mock_session):
        """Con incidentes debe calcular métricas correctamente."""
        now = datetime.now(UTC)

        async def execute_side_effect(query):
            execute_side_effect.call_count = getattr(execute_side_effect, "call_count", 0) + 1
            result = MagicMock()
            call = execute_side_effect.call_count

            if call == 1:
                result.scalar.return_value = 10
            elif call == 2:
                result.one.return_value = MagicMock(
                    today=5, week=10, month=10,
                    open=2, in_progress=3, resolved=4, closed=1,
                    has_sla=8, sla_breach=1, ai_today=3,
                    high=0, med_raw=0, low=0,
                )
            elif call == 3:
                mock_row = MagicMock()
                mock_row.resolved_at = now
                mock_row.created_at = now
                result.all.return_value = [mock_row]
            elif call == 4:
                result.scalar.return_value = 0.75
            elif call == 5:
                result.scalar.return_value = 10
            elif call == 6:
                result.scalar.return_value = 3

            return result

        mock_session.execute = execute_side_effect
        service = MetricsService(mock_session)

        metrics = await service.get_overview_metrics()

        assert metrics.total_incidents_today == 5
        assert metrics.total_incidents_week == 10
        assert metrics.incidents_open == 2
        assert metrics.sla_breach_count == 1
        assert metrics.active_users == 10
        assert metrics.active_technicians == 3

    @pytest.mark.asyncio
    async def test_get_incident_metrics(self, mock_session):
        """get_incident_metrics debe agrupar por status/priority/category."""
        async def execute_result(query):
            result = MagicMock()
            result.__iter__.return_value = iter([])
            return result

        mock_session.execute = execute_result
        service = MetricsService(mock_session)

        metrics = await service.get_incident_metrics()

        assert metrics.by_status == {}
        assert metrics.by_priority == {}
        assert metrics.by_category == {}

    @pytest.mark.asyncio
    async def test_get_ai_metrics(self, mock_session):
        """get_ai_metrics debe calcular métricas de IA."""
        mock_result = MagicMock()
        mock_result.scalar.side_effect = [5, 0.85]
        mock_result.one.return_value = MagicMock(high=3, med_raw=4, low=1)

        async def execute_side_effect(query):
            q = str(query)
            if "avg(" in q:
                res = MagicMock()
                res.scalar.return_value = 0.85
                return res
            elif "confidence" in q:
                res = MagicMock()
                res.scalar.return_value = 5
                res.one.return_value = MagicMock(high=3, med_raw=4, low=1)
                return res
            res = MagicMock()
            res.scalar.return_value = 5
            return res

        mock_session.execute = execute_side_effect
        service = MetricsService(mock_session)

        metrics = await service.get_ai_metrics()

        assert metrics.total_predictions == 5
        assert metrics.avg_confidence > 0
        assert "high" in metrics.confidence_distribution
        assert metrics.confidence_distribution["high"] == 3


# =============================================================================
# AuthService Tests
# =============================================================================

class TestAuthService:
    """Tests para AuthService."""

    @pytest.fixture
    def mock_user_repo(self):
        return AsyncMock()

    def test_init_creates_service(self, mock_user_repo):
        """Inicialización debe crear servicio."""
        service = AuthService(user_repository=mock_user_repo)
        assert service is not None

    @pytest.mark.asyncio
    async def test_register_user_success(self, mock_user_repo):
        """Registro exitoso debe crear usuario y retornarlo."""
        mock_user_repo.get_by_email = AsyncMock(return_value=None)
        mock_user_repo.get_by_username = AsyncMock(return_value=None)
        created_user = MagicMock(id=uuid4(), email="test@test.com")
        mock_user_repo.create = AsyncMock(return_value=created_user)

        with patch("src.domain.entities.user.pwd_context.hash") as mock_hash:
            mock_hash.return_value = "$2b$12$hashedpassword"
            service = AuthService(user_repository=mock_user_repo)
            user = await service.register_user(
                email="test@test.com",
                username="testuser",
                password="password123",
            )

        assert user is not None
        assert user.email == "test@test.com"
        mock_user_repo.create.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_user_duplicate_email(self, mock_user_repo):
        """Email duplicado debe lanzar ValueError."""
        mock_user_repo.get_by_email = AsyncMock(return_value=MagicMock())

        service = AuthService(user_repository=mock_user_repo)

        with pytest.raises(ValueError, match="Email already registered"):
            await service.register_user(
                email="dup@test.com",
                username="testuser",
                password="password123",
            )

    @pytest.mark.asyncio
    async def test_register_user_duplicate_username(self, mock_user_repo):
        """Username duplicado debe lanzar ValueError."""
        mock_user_repo.get_by_email = AsyncMock(return_value=None)
        mock_user_repo.get_by_username = AsyncMock(return_value=MagicMock())

        service = AuthService(user_repository=mock_user_repo)

        with pytest.raises(ValueError, match="Username already taken"):
            await service.register_user(
                email="test@test.com",
                username="dupuser",
                password="password123",
            )

    @pytest.mark.asyncio
    async def test_authenticate_success(self, mock_user_repo):
        """Autenticación exitosa debe retornar AuthResult con tokens."""
        user_id = uuid4()
        mock_user = MagicMock(
            id=user_id,
            email="test@test.com",
            is_active=True,
        )
        mock_user.verify_password = MagicMock(return_value=True)
        mock_user_repo.get_by_email = AsyncMock(return_value=mock_user)
        mock_user_repo.update = AsyncMock(return_value=mock_user)

        service = AuthService(user_repository=mock_user_repo)
        result = await service.authenticate(
            email="test@test.com",
            password="password123",
        )

        assert result is not None
        assert result.user is not None
        assert result.tokens is not None
        assert result.tokens.access_token is not None
        assert result.tokens.refresh_token is not None
        assert result.tokens.token_type == "bearer"

    @pytest.mark.asyncio
    async def test_authenticate_user_not_found(self, mock_user_repo):
        """Usuario no existente debe lanzar AuthenticationException."""
        mock_user_repo.get_by_email = AsyncMock(return_value=None)

        service = AuthService(user_repository=mock_user_repo)

        from src.shared.exceptions import AuthenticationException

        with pytest.raises(AuthenticationException, match="Invalid credentials"):
            await service.authenticate(
                email="nonexistent@test.com",
                password="password123",
            )

    @pytest.mark.asyncio
    async def test_authenticate_inactive_user(self, mock_user_repo):
        """Usuario inactivo debe lanzar AuthenticationException."""
        mock_user = MagicMock(
            email="inactive@test.com",
            is_active=False,
        )
        mock_user_repo.get_by_email = AsyncMock(return_value=mock_user)

        service = AuthService(user_repository=mock_user_repo)

        from src.shared.exceptions import AuthenticationException

        with pytest.raises(AuthenticationException, match="User account is disabled"):
            await service.authenticate(
                email="inactive@test.com",
                password="password123",
            )

    @pytest.mark.asyncio
    async def test_authenticate_wrong_password(self, mock_user_repo):
        """Contraseña incorrecta debe lanzar AuthenticationException."""
        mock_user = MagicMock(
            email="test@test.com",
            is_active=True,
        )
        mock_user.verify_password = MagicMock(return_value=False)
        mock_user_repo.get_by_email = AsyncMock(return_value=mock_user)

        service = AuthService(user_repository=mock_user_repo)

        from src.shared.exceptions import AuthenticationException

        with pytest.raises(AuthenticationException, match="Invalid credentials"):
            await service.authenticate(
                email="test@test.com",
                password="wrongpassword",
            )

    @pytest.mark.asyncio
    async def test_verify_token_valid(self, mock_user_repo):
        """Token válido debe retornar user_id."""
        with patch("src.application.services.auth_service.jwt.decode") as mock_decode:
            mock_decode.return_value = {
                "sub": "user-123",
                "type": "access",
            }

            service = AuthService(user_repository=mock_user_repo)
            user_id = await service.verify_token("valid.token.here")

            assert user_id == "user-123"

    @pytest.mark.asyncio
    async def test_verify_token_invalid_type(self, mock_user_repo):
        """Token con tipo incorrecto debe retornar None."""
        with patch("src.application.services.auth_service.jwt.decode") as mock_decode:
            mock_decode.return_value = {
                "sub": "user-123",
                "type": "refresh",
            }

            service = AuthService(user_repository=mock_user_repo)
            user_id = await service.verify_token("refresh.token.here")

            assert user_id is None

    @pytest.mark.asyncio
    async def test_verify_token_jwt_error(self, mock_user_repo):
        """Token inválido debe retornar None."""
        with patch("src.application.services.auth_service.jwt.decode") as mock_decode:
            mock_decode.side_effect = JWTError("Invalid token")

            service = AuthService(user_repository=mock_user_repo)
            user_id = await service.verify_token("invalid.token.here")

            assert user_id is None

    @pytest.mark.asyncio
    async def test_refresh_access_token_success(self, mock_user_repo):
        """Refresh token válido debe generar nuevo access token."""
        user_id = uuid4()
        mock_user = MagicMock(
            id=user_id,
            is_active=True,
        )
        mock_user_repo.get_by_id = AsyncMock(return_value=mock_user)

        with patch("src.application.services.auth_service.jwt.decode") as mock_decode:
            mock_decode.return_value = {
                "sub": str(user_id),
                "type": "refresh",
            }

            service = AuthService(user_repository=mock_user_repo)
            result = await service.refresh_access_token("valid.refresh.token")

            assert result is not None
            assert result.access_token is not None
            assert result.refresh_token == "valid.refresh.token"

    @pytest.mark.asyncio
    async def test_refresh_access_token_invalid_type(self, mock_user_repo):
        """Refresh token con tipo incorrecto debe lanzar error."""
        with patch("src.application.services.auth_service.jwt.decode") as mock_decode:
            mock_decode.return_value = {
                "sub": "user-123",
                "type": "access",
            }

            service = AuthService(user_repository=mock_user_repo)

            from src.shared.exceptions import AuthenticationException

            with pytest.raises(AuthenticationException, match="Invalid refresh token"):
                await service.refresh_access_token("access.token.here")

    @pytest.mark.asyncio
    async def test_refresh_access_token_expired(self, mock_user_repo):
        """Refresh token expirado debe lanzar error."""
        with patch("src.application.services.auth_service.jwt.decode") as mock_decode:
            mock_decode.side_effect = JWTError("Token expired")

            service = AuthService(user_repository=mock_user_repo)

            from src.shared.exceptions import AuthenticationException

            with pytest.raises(AuthenticationException, match="Invalid refresh token"):
                await service.refresh_access_token("expired.token.here")

    @pytest.mark.asyncio
    async def test_refresh_access_token_user_inactive(self, mock_user_repo):
        """Usuario inactivo en refresh debe lanzar error."""
        user_id = uuid4()
        mock_user = MagicMock(
            id=user_id,
            is_active=False,
        )
        mock_user_repo.get_by_id = AsyncMock(return_value=mock_user)

        with patch("src.application.services.auth_service.jwt.decode") as mock_decode:
            mock_decode.return_value = {
                "sub": str(user_id),
                "type": "refresh",
            }

            service = AuthService(user_repository=mock_user_repo)

            from src.shared.exceptions import AuthenticationException

            with pytest.raises(AuthenticationException, match="User not found or inactive"):
                await service.refresh_access_token("valid.refresh.token")

    @pytest.mark.asyncio
    async def test_get_user_by_id(self, mock_user_repo):
        """get_user_by_id debe delegar al repositorio."""
        user_id = uuid4()
        expected_user = MagicMock(id=user_id)
        mock_user_repo.get_by_id = AsyncMock(return_value=expected_user)

        service = AuthService(user_repository=mock_user_repo)
        user = await service.get_user_by_id(user_id)

        assert user is expected_user
        mock_user_repo.get_by_id.assert_called_once_with(user_id)

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self, mock_user_repo):
        """Usuario no encontrado debe retornar None."""
        user_id = uuid4()
        mock_user_repo.get_by_id = AsyncMock(return_value=None)

        service = AuthService(user_repository=mock_user_repo)
        user = await service.get_user_by_id(user_id)

        assert user is None
