"""Servicio de IA para priorización de incidentes."""

from __future__ import annotations

import sys
import time
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Optional

from src.shared.logging import get_logger
from src.shared.config import get_settings
from src.domain.value_objects import map_ia_to_backend

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
    """Servicio wrapper para el módulo de IA existente.

    Implementa singleton para evitar recargar el modelo (500MB RAM) en cada request.
    Aplica map_ia_to_backend() para convertir prioridades de IA (0-2) al rango del backend (1-4).
    """

    _instance: Optional[AIService] = None
    _initialized: bool = False

    def __new__(cls) -> AIService:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        """Inicializa el servicio de IA (solo una vez por singleton)."""
        if AIService._initialized:
            return
        AIService._initialized = True

        self._predictor = None
        self._model_loaded = False
        self._model_path = Path(settings.model_path)
        self._vectorizer_path = Path(settings.vectorizer_path)
        self._model_timeout = 30.0

    def _ensure_model_loaded(self) -> None:
        """Carga el modelo si no está cargado."""
        if self._model_loaded:
            return

        try:
            ia_module = str(Path(__file__).parent.parent.parent.parent.parent / "IA-module")
            if ia_module not in sys.path:
                sys.path.insert(0, ia_module)

            from src.predictor import PriorityPredictor

            model_file = self._model_path / "priority_classifier_v1.pkl"
            encoder_dir = self._vectorizer_path / "encoder"

            if model_file.exists() and encoder_dir.exists():
                self._predictor = PriorityPredictor(
                    model_path=Path(str(model_file)),
                    encoder_path=Path(str(encoder_dir)),
                )
                self._model_loaded = True
                logger.info("Modelo IA cargado exitosamente")
            else:
                logger.warning(f"Archivos de modelo no encontrados en {self._model_path}")
                self._predictor = None

        except Exception as e:
            logger.error(f"Error al cargar modelo IA: {e}")
            self._predictor = None

    async def predict_priority(
        self,
        text: str,
        metadata: Optional[dict] = None,
    ) -> PredictionResult:
        """Predice la prioridad de un incidente.

        Args:
            text: Texto del incidente (título + descripción)
            metadata: Metadatos opcionales (department, type, tags)

        Returns:
            Resultado con prioridad mapeada al rango 1-4
        """
        start_time = time.time()

        self._ensure_model_loaded()

        if self._predictor is None:
            logger.warning("Modelo IA no disponible, usando predicción por defecto")
            return PredictionResult(
                priority=3,
                confidence=0.5,
                top_features=[],
                reasoning="Modelo no disponible",
                processing_time_ms=(time.time() - start_time) * 1000,
            )

        try:
            explanation = self._predictor.explain_prediction(
                text,
                top_k=5,
                metadata=metadata,
            )

            ia_priority = explanation["predicted_priority"]
            backend_priority = map_ia_to_backend(ia_priority)

            result = PredictionResult(
                priority=backend_priority.value,
                confidence=explanation.get("confidence", 0.0),
                top_features=[
                    f["feature"]
                    for f in explanation.get("contributing_features", [])
                ],
                reasoning=explanation.get("reasoning", ""),
                processing_time_ms=(time.time() - start_time) * 1000,
            )

            logger.log_ai_prediction(
                incident_id=metadata.get("incident_id", "unknown") if metadata else "unknown",
                priority=result.priority,
                confidence=result.confidence,
                processing_time_ms=result.processing_time_ms,
                features=result.top_features,
            )

            return result

        except Exception as e:
            logger.error(f"Predicción fallida: {e}")
            return PredictionResult(
                priority=3,
                confidence=0.0,
                top_features=[],
                reasoning=f"Error de predicción: {str(e)}",
                processing_time_ms=(time.time() - start_time) * 1000,
            )

    async def predict_batch(
        self,
        texts: list[str],
        metadata_list: Optional[list[dict]] = None,
    ) -> list[PredictionResult]:
        """Predice prioridades en lote.

        Args:
            texts: Lista de textos de incidentes
            metadata_list: Lista opcional de metadatos por texto

        Returns:
            Lista de resultados con prioridades mapeadas
        """
        start_time = time.time()

        self._ensure_model_loaded()

        if self._predictor is None:
            return [
                PredictionResult(
                    priority=3,
                    confidence=0.5,
                    top_features=[],
                    reasoning="Modelo no disponible",
                    processing_time_ms=0.0,
                )
                for _ in texts
            ]

        try:
            results = self._predictor.batch_predict_with_confidence(
                texts,
                metadata_list=metadata_list,
            )

            predictions = []
            for priority, confidence in results:
                backend_priority = map_ia_to_backend(priority)
                predictions.append(PredictionResult(
                    priority=backend_priority.value,
                    confidence=confidence,
                    top_features=[],
                    reasoning="Predicción en lote",
                    processing_time_ms=(time.time() - start_time) * 1000 / len(texts),
                ))

            logger.info(f"Predicción en lote completada para {len(texts)} incidentes")
            return predictions

        except Exception as e:
            logger.error(f"Predicción en lote fallida: {e}")
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
            "modelo_cargado": self._model_loaded,
            "ruta_modelo": str(self._model_path),
            "ruta_vectorizer": str(self._vectorizer_path),
        }
