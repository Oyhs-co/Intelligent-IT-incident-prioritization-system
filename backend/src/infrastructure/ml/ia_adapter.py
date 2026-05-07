"""Adaptador de integración para el módulo de IA (PriorityPredictor).

Implementa el puerto IAIModel para conectar el backend con el módulo
de machine learning ubicado en IA-module/.
"""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Any, Optional

from src.application.ports.i_ai_model import IAIModel
from src.domain.value_objects import map_ia_to_backend
from src.shared.config import get_settings
from src.shared.logging import get_logger

settings = get_settings()
logger = get_logger("ia_adapter")


class IAIntegrationAdapter(IAIModel):
    """Adaptador que implementa IAIModel usando PriorityPredictor del módulo IA.

    Configura sys.path para acceder a IA-module/src, carga el predictor
    con los Path correctos desde settings.model_path, y aplica el mapeo
    de prioridades 0-2 → 1-4.

    Implementa singleton para evitar recargar el modelo (~500MB RAM) en cada request.
    """

    _instance: Optional[IAIntegrationAdapter] = None
    _initialized: bool = False

    def __new__(cls) -> IAIntegrationAdapter:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if IAIntegrationAdapter._initialized:
            return
        IAIntegrationAdapter._initialized = True

        self._predictor: Any = None
        self._model_loaded: bool = False
        self._model_path = Path(settings.model_path)
        self._predictor_cls: Any = None

    def _setup_imports(self) -> None:
        """Configura sys.path y almacena la referencia a PriorityPredictor."""
        if self._predictor_cls is not None:
            return

        ia_module = str(Path(__file__).parent.parent.parent.parent.parent / "IA-module")
        if ia_module not in sys.path:
            sys.path.insert(0, ia_module)

        try:
            from src.predictor import PriorityPredictor
            self._predictor_cls = PriorityPredictor
        except ImportError:
            logger.debug("PriorityPredictor no disponible (IA-module no instalado)")
            self._predictor_cls = None

    def _ensure_model_loaded(self) -> None:
        """Carga el modelo desde disco si no está cargado."""
        if self._model_loaded:
            return

        self._setup_imports()

        if self._predictor_cls is None:
            logger.warning("PriorityPredictor no disponible (clase no importada)")
            self._predictor = None
            return

        try:
            model_file = self._model_path / "priority_classifier_v1.pkl"
            encoder_dir = self._model_path / "encoder"

            if model_file.exists() and encoder_dir.exists():
                self._predictor = self._predictor_cls(
                    model_path=Path(str(model_file)),
                    encoder_path=Path(str(encoder_dir)),
                )
                self._model_loaded = True
                logger.info("PriorityPredictor cargado exitosamente")
            else:
                logger.warning(
                    f"Archivos de modelo no encontrados en {self._model_path}. "
                    f"Se esperaba: {model_file} y {encoder_dir}"
                )
                self._predictor = None

        except Exception as e:
            logger.error(f"Error al cargar PriorityPredictor: {e}")
            self._predictor = None

    def is_available(self) -> bool:
        """Verifica si el modelo está disponible y cargado."""
        self._ensure_model_loaded()
        return self._predictor is not None and self._model_loaded

    async def predict(self, text: str, metadata: Optional[dict] = None) -> tuple[int, float]:
        """Predice la prioridad de un texto.

        Args:
            text: Texto del incidente (título + descripción).
            metadata: Metadatos opcionales (department, type, tags).

        Returns:
            Tupla (prioridad_backend, confianza) donde prioridad está en rango 1-4.
        """
        self._ensure_model_loaded()

        if not text or not text.strip():
            logger.debug("Texto vacío recibido, retornando prioridad por defecto")
            return 1, 0.0

        if self._predictor is None:
            logger.warning("Modelo no disponible, retornando prioridad por defecto")
            return 3, 0.5

        try:
            priority, confidence = self._predictor.predict_with_confidence(
                text,
                metadata=metadata,
            )
            backend_priority = map_ia_to_backend(int(priority))
            return backend_priority.value, float(confidence)

        except Exception as e:
            logger.error(f"Error en predict: {e}")
            return 3, 0.0

    async def predict_with_explanation(
        self,
        text: str,
        metadata: Optional[dict] = None,
    ) -> dict[str, Any]:
        """Predice con explicación detallada (SHAP o coeficientes).

        Args:
            text: Texto del incidente.
            metadata: Metadatos opcionales.

        Returns:
            Diccionario con predicción, confianza, features contribuyentes y razonamiento.
            Las prioridades en el diccionario ya están mapeadas al rango 1-4.
        """
        self._ensure_model_loaded()

        if not text or not text.strip():
            return {
                "predicted_priority": 1,
                "priority_label": "P1 (Low)",
                "priority_description": "Low - Puede ser programado",
                "confidence": 0.0,
                "all_probabilities": {},
                "contributing_features": [],
                "explanation_method": "default",
                "reasoning": "Texto vacío, prioridad por defecto",
                "response_time_seconds": 2.0,
            }

        if self._predictor is None:
            return {
                "predicted_priority": 3,
                "priority_label": "P3 (High)",
                "priority_description": "High - Requiere atención",
                "confidence": 0.5,
                "all_probabilities": {},
                "contributing_features": [],
                "explanation_method": "fallback",
                "reasoning": "Modelo no disponible, prioridad por defecto",
                "response_time_seconds": 2.0,
            }

        try:
            explanation = self._predictor.explain_prediction(
                text,
                top_k=5,
                metadata=metadata,
            )

            ia_priority = explanation.get("predicted_priority", 2)
            backend = map_ia_to_backend(int(ia_priority))

            all_probs = {}
            for label, prob in explanation.get("all_probabilities", {}).items():
                label_clean = label.split("(")[0].strip() if "(" in label else label
                all_probs[label_clean] = prob

            mapped_features = []
            for feat in explanation.get("contributing_features", []):
                mapped_features.append({
                    "feature_index": feat.get("feature_index", 0),
                    "feature_name": feat.get("feature_name", ""),
                    "feature_value": feat.get("feature_value", 0.0),
                    "score": feat.get("score", 0.0),
                    "importance": feat.get("importance", "neutral"),
                    "abs_score": feat.get("abs_score", 0.0),
                })

            return {
                "predicted_priority": backend.value,
                "priority_label": backend.label,
                "priority_description": explanation.get("priority_description", ""),
                "confidence": explanation.get("confidence", 0.0),
                "all_probabilities": all_probs,
                "contributing_features": mapped_features,
                "explanation_method": explanation.get("explanation_method", "unknown"),
                "reasoning": explanation.get("reasoning", ""),
                "response_time_seconds": explanation.get("response_time_seconds", 2.0),
            }

        except Exception as e:
            logger.error(f"Error en predict_with_explanation: {e}")
            return {
                "predicted_priority": 3,
                "priority_label": "P3 (High)",
                "priority_description": "Error en predicción",
                "confidence": 0.0,
                "all_probabilities": {},
                "contributing_features": [],
                "explanation_method": "error",
                "reasoning": f"Error de predicción: {str(e)}",
                "response_time_seconds": 2.0,
            }

    async def batch_predict(
        self,
        texts: list[str],
        metadata_list: Optional[list[dict]] = None,
    ) -> list[tuple[int, float]]:
        """Predice prioridades en lote.

        Args:
            texts: Lista de textos de incidentes.
            metadata_list: Lista opcional de metadatos por texto.

        Returns:
            Lista de tuplas (prioridad_backend, confianza).
        """
        self._ensure_model_loaded()

        if not texts:
            return []

        if self._predictor is None:
            return [(3, 0.5) for _ in texts]

        try:
            results = self._predictor.batch_predict_with_confidence(
                texts,
                metadata_list=metadata_list,
            )

            mapped = []
            for priority, confidence in results:
                backend = map_ia_to_backend(int(priority))
                mapped.append((backend.value, float(confidence)))

            logger.info(
                f"Batch predict completado para {len(texts)} textos "
                f"con {len(mapped)} resultados"
            )
            return mapped

        except Exception as e:
            logger.error(f"Error en batch_predict: {e}")
            return [(3, 0.0) for _ in texts]
