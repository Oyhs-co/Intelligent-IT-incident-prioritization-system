"""Tests unitarios para IAIntegrationAdapter."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest

from src.infrastructure.ml.ia_adapter import IAIntegrationAdapter


class TestIAIntegrationAdapter:
    """Tests para IAIntegrationAdapter."""

    def teardown_method(self):
        IAIntegrationAdapter._instance = None
        IAIntegrationAdapter._initialized = False

    def test_init_creates_adapter(self):
        """Inicialización debe crear adaptador sin modelo cargado."""
        adapter = IAIntegrationAdapter()
        assert adapter is not None
        assert adapter._model_loaded is False

    def test_singleton_returns_same_instance(self):
        """Múltiples instancias deben retornar el mismo objeto."""
        a1 = IAIntegrationAdapter()
        a2 = IAIntegrationAdapter()
        assert a1 is a2

    def test_is_available_returns_false_when_not_loaded(self):
        """Sin modelo cargado debe retornar False."""
        adapter = IAIntegrationAdapter()
        assert adapter.is_available() is False

    @pytest.mark.asyncio
    async def test_predict_empty_text(self):
        """Texto vacío debe retornar prioridad por defecto (1, 0.0)."""
        adapter = IAIntegrationAdapter()
        priority, confidence = await adapter.predict("")

        assert priority == 1
        assert confidence == 0.0

    @pytest.mark.asyncio
    async def test_predict_whitespace_text(self):
        """Texto con solo espacios debe retornar prioridad por defecto."""
        adapter = IAIntegrationAdapter()
        priority, confidence = await adapter.predict("   \n  ")

        assert priority == 1
        assert confidence == 0.0

    @pytest.mark.asyncio
    async def test_predict_without_model_returns_fallback(self):
        """Sin modelo cargado debe retornar fallback (3, 0.5)."""
        adapter = IAIntegrationAdapter()
        priority, confidence = await adapter.predict("test text")

        assert priority == 3
        assert confidence == 0.5

    @pytest.mark.asyncio
    async def test_predict_with_metadata_fallback(self):
        """Con metadata pero sin modelo debe retornar fallback."""
        adapter = IAIntegrationAdapter()
        priority, confidence = await adapter.predict(
            "test text",
            metadata={"department": "IT", "type": "Incident"},
        )

        assert priority == 3
        assert confidence == 0.5

    @pytest.mark.asyncio
    async def test_predict_with_mocked_model_ia0(self):
        """IA 0 debe mapearse a backend 4 (P4_CRITICAL)."""
        adapter = IAIntegrationAdapter()

        predictor_mock = MagicMock()
        predictor_mock.predict_with_confidence = MagicMock(return_value=(0, 0.95))
        adapter._predictor = predictor_mock
        adapter._model_loaded = True

        priority, confidence = await adapter.predict("Critical server failure")

        assert priority == 4
        assert confidence == 0.95
        predictor_mock.predict_with_confidence.assert_called_once_with(
            "Critical server failure",
            metadata=None,
        )

    @pytest.mark.asyncio
    async def test_predict_with_mocked_model_ia1(self):
        """IA 1 debe mapearse a backend 2 (P2_MEDIUM)."""
        adapter = IAIntegrationAdapter()

        predictor_mock = MagicMock()
        predictor_mock.predict_with_confidence = MagicMock(return_value=(1, 0.80))
        adapter._predictor = predictor_mock
        adapter._model_loaded = True

        priority, confidence = await adapter.predict("Medium issue")

        assert priority == 2
        assert confidence == 0.80

    @pytest.mark.asyncio
    async def test_predict_with_mocked_model_ia2(self):
        """IA 2 debe mapearse a backend 1 (P1_LOW)."""
        adapter = IAIntegrationAdapter()

        predictor_mock = MagicMock()
        predictor_mock.predict_with_confidence = MagicMock(return_value=(2, 0.70))
        adapter._predictor = predictor_mock
        adapter._model_loaded = True

        priority, confidence = await adapter.predict("Minor issue")

        assert priority == 1
        assert confidence == 0.70

    @pytest.mark.asyncio
    async def test_predict_with_metadata(self):
        """Con metadata debe pasar los metadatos al predictor."""
        adapter = IAIntegrationAdapter()

        predictor_mock = MagicMock()
        predictor_mock.predict_with_confidence = MagicMock(return_value=(0, 0.90))
        adapter._predictor = predictor_mock
        adapter._model_loaded = True

        metadata = {"department": "IT", "type": "Incident", "tags": "server,outage"}
        priority, confidence = await adapter.predict("Server down", metadata=metadata)

        assert priority == 4
        predictor_mock.predict_with_confidence.assert_called_once_with(
            "Server down",
            metadata=metadata,
        )

    @pytest.mark.asyncio
    async def test_predict_with_mocked_model_error(self):
        """Error en el predictor debe retornar fallback (3, 0.0)."""
        adapter = IAIntegrationAdapter()

        predictor_mock = MagicMock()
        predictor_mock.predict_with_confidence = MagicMock(
            side_effect=Exception("Prediction failed"),
        )
        adapter._predictor = predictor_mock
        adapter._model_loaded = True

        priority, confidence = await adapter.predict("test")

        assert priority == 3
        assert confidence == 0.0

    @pytest.mark.asyncio
    async def test_batch_predict_empty(self):
        """Lista vacía debe retornar lista vacía."""
        adapter = IAIntegrationAdapter()
        results = await adapter.batch_predict([])

        assert results == []

    @pytest.mark.asyncio
    async def test_batch_predict_without_model(self):
        """Sin modelo debe retornar fallbacks."""
        adapter = IAIntegrationAdapter()
        results = await adapter.batch_predict(["text1", "text2"])

        assert len(results) == 2
        assert all(p == 3 for p, _ in results)
        assert all(c == 0.5 for _, c in results)

    @pytest.mark.asyncio
    async def test_batch_predict_with_mocked_model(self):
        """Batch con modelo debe aplicar mapeo de prioridades."""
        adapter = IAIntegrationAdapter()

        predictor_mock = MagicMock()
        predictor_mock.batch_predict_with_confidence = MagicMock(
            return_value=[(0, 0.9), (2, 0.7), (1, 0.6)],
        )
        adapter._predictor = predictor_mock
        adapter._model_loaded = True

        results = await adapter.batch_predict(["critical", "minor", "medium"])

        assert len(results) == 3
        assert results[0] == (4, 0.9)
        assert results[1] == (1, 0.7)
        assert results[2] == (2, 0.6)

    @pytest.mark.asyncio
    async def test_batch_predict_with_metadata(self):
        """Batch con metadatos debe pasarlos al predictor."""
        adapter = IAIntegrationAdapter()

        predictor_mock = MagicMock()
        predictor_mock.batch_predict_with_confidence = MagicMock(
            return_value=[(0, 0.9), (2, 0.7)],
        )
        adapter._predictor = predictor_mock
        adapter._model_loaded = True

        metadata_list = [{"dept": "IT"}, {"dept": "HR"}]
        results = await adapter.batch_predict(
            ["critical", "minor"],
            metadata_list=metadata_list,
        )

        assert len(results) == 2
        predictor_mock.batch_predict_with_confidence.assert_called_once_with(
            ["critical", "minor"],
            metadata_list=metadata_list,
        )

    @pytest.mark.asyncio
    async def test_batch_predict_error(self):
        """Error en batch debe retornar fallbacks."""
        adapter = IAIntegrationAdapter()

        predictor_mock = MagicMock()
        predictor_mock.batch_predict_with_confidence = MagicMock(
            side_effect=Exception("Batch error"),
        )
        adapter._predictor = predictor_mock
        adapter._model_loaded = True

        results = await adapter.batch_predict(["text1", "text2"])

        assert len(results) == 2
        assert all(p == 3 for p, _ in results)
        assert all(c == 0.0 for _, c in results)

    @pytest.mark.asyncio
    async def test_predict_with_explanation_empty_text(self):
        """Texto vacío en explain debe retornar explicación default."""
        adapter = IAIntegrationAdapter()
        explanation = await adapter.predict_with_explanation("")

        assert explanation["predicted_priority"] == 1
        assert explanation["confidence"] == 0.0
        assert "Texto vacío" in explanation["reasoning"]

    @pytest.mark.asyncio
    async def test_predict_with_explanation_no_model(self):
        """Sin modelo debe retornar explicación fallback."""
        adapter = IAIntegrationAdapter()
        explanation = await adapter.predict_with_explanation("test")

        assert explanation["predicted_priority"] == 3
        assert explanation["confidence"] == 0.5
        assert "Modelo no disponible" in explanation["reasoning"]

    @pytest.mark.asyncio
    async def test_predict_with_explanation_mocked(self):
        """Explain con modelo debe retornar explicación completa con prioridad mapeada."""
        adapter = IAIntegrationAdapter()

        predictor_mock = MagicMock()
        predictor_mock.explain_prediction = MagicMock(return_value={
            "predicted_priority": 0,
            "priority_label": "P1 (Critical)",
            "priority_description": "Critical - Requiere atención inmediata",
            "confidence": 0.95,
            "all_probabilities": {
                "P1 (Critical)": 0.95,
                "P2 (Medium)": 0.03,
                "P3 (Low)": 0.02,
            },
            "contributing_features": [
                {
                    "feature_index": 42,
                    "feature_name": "critical",
                    "feature_value": 1.0,
                    "score": 0.8,
                    "importance": "positive",
                    "abs_score": 0.8,
                },
            ],
            "explanation_method": "SHAP (SHapley Additive exPlanations)",
            "reasoning": "Alta urgencia detectada",
            "response_time_seconds": 0.5,
        })
        adapter._predictor = predictor_mock
        adapter._model_loaded = True

        explanation = await adapter.predict_with_explanation(
            "Critical server failure",
            metadata={"department": "IT"},
        )

        assert explanation["predicted_priority"] == 4
        assert explanation["priority_label"] == "P4 (Critical)"
        assert explanation["confidence"] == 0.95
        assert len(explanation["contributing_features"]) == 1
        assert explanation["contributing_features"][0]["feature_name"] == "critical"
        assert explanation["explanation_method"] == "SHAP (SHapley Additive exPlanations)"
        assert "Alta urgencia" in explanation["reasoning"]

    @pytest.mark.asyncio
    async def test_predict_with_explanation_maps_priority_correctly(self):
        """Verifica mapeo 0→4, 1→2, 2→1 en explicación."""
        adapter = IAIntegrationAdapter()

        predictor_mock = MagicMock()

        for ia_priority, expected_backend in [(0, 4), (1, 2), (2, 1)]:
            predictor_mock.explain_prediction = MagicMock(return_value={
                "predicted_priority": ia_priority,
                "priority_label": f"P{ia_priority + 1}",
                "priority_description": "test",
                "confidence": 0.8,
                "all_probabilities": {},
                "contributing_features": [],
                "explanation_method": "test",
                "reasoning": "test",
                "response_time_seconds": 0.5,
            })
            adapter._predictor = predictor_mock
            adapter._model_loaded = True

            explanation = await adapter.predict_with_explanation("test")
            assert explanation["predicted_priority"] == expected_backend, \
                f"IA {ia_priority} → Backend {expected_backend}"

    @pytest.mark.asyncio
    async def test_predict_with_explanation_error(self):
        """Error en explain debe retornar explicación de error."""
        adapter = IAIntegrationAdapter()

        predictor_mock = MagicMock()
        predictor_mock.explain_prediction = MagicMock(
            side_effect=Exception("SHAP error"),
        )
        adapter._predictor = predictor_mock
        adapter._model_loaded = True

        explanation = await adapter.predict_with_explanation("test")

        assert explanation["predicted_priority"] == 3
        assert explanation["confidence"] == 0.0
        assert "Error" in explanation["reasoning"]

    @pytest.mark.asyncio
    async def test_predict_all_mappings(self):
        """Verifica todos los mapeos 0→4, 1→2, 2→1."""
        adapter = IAIntegrationAdapter()
        predictor_mock = MagicMock()

        test_cases = [
            (0, 4, 0.9),
            (1, 2, 0.8),
            (2, 1, 0.7),
        ]

        for ia_input, expected_priority, expected_confidence in test_cases:
            predictor_mock.predict_with_confidence = MagicMock(
                return_value=(ia_input, expected_confidence),
            )
            adapter._predictor = predictor_mock
            adapter._model_loaded = True

            priority, confidence = await adapter.predict("test")
            assert priority == expected_priority
            assert confidence == expected_confidence

    def test_is_available_after_model_loaded(self):
        """is_available debe retornar True si modelo cargado."""
        adapter = IAIntegrationAdapter()
        adapter._model_loaded = True
        adapter._predictor = MagicMock()

        assert adapter.is_available() is True

    def test_is_available_model_loaded_but_no_predictor(self):
        """is_available debe retornar False si _model_loaded True pero _predictor None."""
        adapter = IAIntegrationAdapter()
        adapter._model_loaded = True
        adapter._predictor = None

        assert adapter.is_available() is False

    def test_reset_singleton(self):
        """Reseteo manual debe permitir nueva instancia."""
        a1 = IAIntegrationAdapter()
        assert a1 is IAIntegrationAdapter._instance

        IAIntegrationAdapter._instance = None
        IAIntegrationAdapter._initialized = False

        a2 = IAIntegrationAdapter()
        assert a2 is not a1
