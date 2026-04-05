"""Servicio de IA para priorización de incidentes."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING, Optional
from pathlib import Path
import time

from src.shared.logging import get_logger
from src.shared.config import get_settings

if TYPE_CHECKING:
    from src.domain.entities.incident import Incident

settings = get_settings()
logger = get_logger("ai_service")


@dataclass
class PredictionResult:
    """Resultado de predicción de prioridad."""

    priority: int
    confidence: float
    top_features: list[str]
    reasoning: str
    processing_time_ms: float


class AIService:
    """Servicio wrapper para el módulo de IA existente."""

    def __init__(self) -> None:
        """Inicializa el servicio de IA."""
        self._predictor = None
        self._model_loaded = False
        self._model_path = Path(settings.model_path)
        self._vectorizer_path = Path(settings.vectorizer_path)

    def _ensure_model_loaded(self) -> None:
        """Carga el modelo si no está cargado."""
        if self._model_loaded:
            return

        try:
            from ...ia_module.src.predictor import PriorityPredictor

            model_file = self._model_path / "priority_classifier_v1.pkl"
            vectorizer_file = self._model_path / "priority_classifier_v1_vectorizer.pkl"

            if model_file.exists() and vectorizer_file.exists():
                self._predictor = PriorityPredictor(
                    model_path=str(model_file),
                    vectorizer_path=str(vectorizer_file)
                )
                self._model_loaded = True
                logger.info("AI model loaded successfully")
            else:
                logger.warning(f"Model files not found at {self._model_path}")
                self._predictor = None

        except Exception as e:
            logger.error(f"Failed to load AI model: {e}")
            self._predictor = None

    async def predict_priority(self, text: str) -> PredictionResult:
        """
        Predice la prioridad de un incidente.

        Args:
            text: Texto del incidente (título + descripción)

        Returns:
            Resultado de predicción
        """
        start_time = time.time()

        self._ensure_model_loaded()

        if self._predictor is None:
            logger.warning("AI model not available, using default prediction")
            return PredictionResult(
                priority=3,
                confidence=0.5,
                top_features=[],
                reasoning="Model not available",
                processing_time_ms=(time.time() - start_time) * 1000,
            )

        try:
            explanation = self._predictor.explain_prediction(text, top_k=5)

            result = PredictionResult(
                priority=explanation["predicted_priority"],
                confidence=explanation["confidence"],
                top_features=[f["feature"] for f in explanation["contributing_features"]],
                reasoning=explanation["reasoning"],
                processing_time_ms=(time.time() - start_time) * 1000,
            )

            logger.log_ai_prediction(
                incident_id="unknown",
                priority=result.priority,
                confidence=result.confidence,
                processing_time_ms=result.processing_time_ms,
                features=result.top_features,
            )

            return result

        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return PredictionResult(
                priority=3,
                confidence=0.0,
                top_features=[],
                reasoning=f"Prediction error: {str(e)}",
                processing_time_ms=(time.time() - start_time) * 1000,
            )

    async def predict_batch(self, texts: list[str]) -> list[PredictionResult]:
        """
        Predice prioridades en lote.

        Args:
            texts: Lista de textos de incidentes

        Returns:
            Lista de resultados
        """
        start_time = time.time()

        self._ensure_model_loaded()

        if self._predictor is None:
            return [
                PredictionResult(
                    priority=3,
                    confidence=0.5,
                    top_features=[],
                    reasoning="Model not available",
                    processing_time_ms=0.0,
                )
                for _ in texts
            ]

        try:
            results = self._predictor.batch_predict_with_confidence(texts)

            predictions = []
            for priority, confidence in results:
                predictions.append(PredictionResult(
                    priority=priority,
                    confidence=confidence,
                    top_features=[],
                    reasoning="Batch prediction",
                    processing_time_ms=(time.time() - start_time) * 1000 / len(texts),
                ))

            logger.info(f"Batch prediction completed for {len(texts)} incidents")
            return predictions

        except Exception as e:
            logger.error(f"Batch prediction failed: {e}")
            return [
                PredictionResult(
                    priority=3,
                    confidence=0.0,
                    top_features=[],
                    reasoning=f"Error: {str(e)}",
                    processing_time_ms=0.0,
                )
                for _ in texts
            ]

    def is_model_available(self) -> bool:
        """Verifica si el modelo está disponible."""
        self._ensure_model_loaded()
        return self._predictor is not None

    def get_model_info(self) -> dict:
        """Obtiene información del modelo."""
        return {
            "model_loaded": self._model_loaded,
            "model_path": str(self._model_path),
            "vectorizer_path": str(self._vectorizer_path),
        }
