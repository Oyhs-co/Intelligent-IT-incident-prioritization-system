"""Tests de integración entre AIService e IAIntegrationAdapter.

Verifica que AIService puede usar IAIntegrationAdapter como predictor
y que el flujo completo de predicción con mapeo de prioridades funciona.
"""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.application.services.ai_service import AIService, PredictionResult


class TestAIServiceWithIAAdapter:
    """Tests de integración AIService + IAIntegrationAdapter."""

    def teardown_method(self):
        AIService._instance = None
        AIService._initialized = False

    @pytest.mark.asyncio
    async def test_predict_priority_with_adapter_mapping(self):
        """AIService con predictor mockeado debe aplicar map_ia_to_backend."""
        service = AIService()

        predictor_mock = MagicMock()
        predictor_mock.explain_prediction = MagicMock(return_value={
            "predicted_priority": 0,
            "confidence": 0.95,
            "contributing_features": [
                {"feature": "urgent", "score": 0.5},
            ],
            "reasoning": "Alta urgencia detectada",
        })

        service._predictor = predictor_mock
        service._model_loaded = True

        result = await service.predict_priority(
            "Critical server failure",
            metadata={"incident_id": "INC-001", "department": "IT"},
        )

        assert isinstance(result, PredictionResult)
        assert result.priority == 4
        assert result.confidence == 0.95
        assert result.processing_time_ms >= 0

    @pytest.mark.asyncio
    async def test_predict_priority_all_mappings(self):
        """Verifica los 3 mapeos de prioridad a través de AIService."""
        service = AIService()
        predictor_mock = MagicMock()

        test_cases = [
            (0, 4, 0.95, "IA 0 → Backend 4"),
            (1, 2, 0.80, "IA 1 → Backend 2"),
            (2, 1, 0.70, "IA 2 → Backend 1"),
        ]

        for ia_input, expected_priority, confidence, label in test_cases:
            predictor_mock.explain_prediction = MagicMock(return_value={
                "predicted_priority": ia_input,
                "confidence": confidence,
                "contributing_features": [],
                "reasoning": "test",
            })
            service._predictor = predictor_mock
            service._model_loaded = True

            result = await service.predict_priority("test")
            assert result.priority == expected_priority, f"Fallo para {label}"
            assert result.confidence == confidence

    @pytest.mark.asyncio
    async def test_predict_batch_with_adapter(self):
        """AIService batch con predictor mockeado debe funcionar."""
        service = AIService()

        predictor_mock = MagicMock()
        predictor_mock.batch_predict_with_confidence = MagicMock(
            return_value=[(0, 0.9), (2, 0.7), (1, 0.6)],
        )
        service._predictor = predictor_mock
        service._model_loaded = True

        results = await service.predict_batch(
            ["critical", "minor", "medium"],
            metadata_list=[{"dept": "IT"}, {"dept": "HR"}, {"dept": "Eng"}],
        )

        assert len(results) == 3
        assert results[0].priority == 4
        assert results[0].confidence == 0.9
        assert results[1].priority == 1
        assert results[1].confidence == 0.7
        assert results[2].priority == 2
        assert results[2].confidence == 0.6

    @pytest.mark.asyncio
    async def test_adapter_fallback_when_model_unavailable(self):
        """Cuando el adapter no tiene modelo, AIService debe caer a fallback."""
        service = AIService()
        service._predictor = None
        service._model_loaded = False

        result = await service.predict_priority("test")

        assert result.priority == 3
        assert result.confidence == 0.5
        assert result.reasoning == "Modelo no disponible"

    @pytest.mark.asyncio
    async def test_adapter_error_propagation(self):
        """Error del adapter debe ser manejado por AIService."""
        service = AIService()

        adapter_mock = MagicMock()
        adapter_mock.predict_with_confidence = MagicMock(
            side_effect=Exception("Adapter error"),
        )
        service._predictor = adapter_mock
        service._model_loaded = True

        result = await service.predict_priority("test")

        assert result.priority == 3
        assert result.confidence == 0.0
        assert "Error" in result.reasoning

    @pytest.mark.asyncio
    async def test_is_model_available_with_adapter(self):
        """is_model_available debe reflejar estado del adapter."""
        service = AIService()
        assert service.is_model_available() is False

        service._model_loaded = True
        service._predictor = MagicMock()
        assert service.is_model_available() is True

    @pytest.mark.asyncio
    async def test_get_model_info_includes_adapter_info(self):
        """get_model_info debe incluir rutas del adapter."""
        service = AIService()
        info = service.get_model_info()

        assert "modelo_cargado" in info
        assert "ruta_modelo" in info
        assert "ruta_vectorizer" in info

    @pytest.mark.asyncio
    async def test_predict_batch_empty_with_adapter(self):
        """Batch vacío debe retornar lista vacía."""
        service = AIService()

        adapter_mock = MagicMock()
        adapter_mock.batch_predict_with_confidence = MagicMock(return_value=[])
        service._predictor = adapter_mock
        service._model_loaded = True

        results = await service.predict_batch([])

        assert len(results) == 0

    @pytest.mark.asyncio
    async def test_predict_batch_adapter_error(self):
        """Error en batch del adapter debe ser manejado."""
        service = AIService()

        adapter_mock = MagicMock()
        adapter_mock.batch_predict_with_confidence = MagicMock(
            side_effect=Exception("Batch adapter error"),
        )
        service._predictor = adapter_mock
        service._model_loaded = True

        results = await service.predict_batch(["text1", "text2"])

        assert len(results) == 2
        assert all(r.priority == 3 for r in results)
        assert all(r.confidence == 0.0 for r in results)
        assert all("Error" in r.reasoning for r in results)
