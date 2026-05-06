"""
Predicción y explicabilidad del modelo.

Incluye:
- Predicción de prioridades (1-3 para P1-P3)
- Explicación de predicciones con SHAP
- Confianza en predicciones

Principio SRP: Cada clase tiene una única responsabilidad.
Principio OCP: Soporta múltiples backends (TF-IDF, MiniLM).
"""

import json
import pickle
import re
from pathlib import Path
import warnings
from typing import Tuple, List, Dict, Any, Optional
import numpy as np
import pandas as pd

from .interfaces import IEncoder, IClassifier
from .utils import logger, Config

LLM_BOILERPLATE_PATTERNS = [
    r"Dear Customer Support Team,?\s*",
    r"I hope this message reaches you well\.?\s*",
    r"I hope you are doing well\.?\s*",
    r"I am reaching out to\s*",
    r"I am writing to\s*",
    r"Thank you for your time and assistance\.?\s*",
    r"Thank you for your attention to this matter\.?\s*",
    r"Best regards,?\s*",
    r"Sincerely,?\s*",
    r"Kind regards,?\s*",
    r"Please let me know if you need any further information\.?\s*",
    r"I would appreciate your prompt assistance\.?\s*",
    r"Could you please provide an update on\s*",
    r"I look forward to your response\.?\s*",
    r"Your prompt assistance would be greatly appreciated\.?\s*",
]



class PriorityPredictor:
    """Realiza predicciones y proporciona explicabilidad.
    
    Usa inyección de dependencias para encoder y clasificador.
    """
    
    PRIORITY_LABELS = {0: "P1 (Critical)", 1: "P2 (Medium)", 2: "P3 (Low)"}
    PRIORITY_DESCRIPTIONS = {
        0: "Critical - Requiere atención inmediata",
        1: "Medium - Requiere atención pronta",
        2: "Low - Puede ser programado"
    }
    
    def __init__(
        self,
        classifier: Optional[IClassifier] = None,
        encoder: Optional[IEncoder] = None,
        model_path: Optional[Path] = None,
        encoder_path: Optional[Path] = None
    ):
        self.classifier = classifier
        self.encoder = encoder
        self._shap_explainer = None
        self.meta_encoders: Dict[str, Any] = {}
        self.meta_feature_columns: List[str] = []
        
        if self.classifier is None or self.encoder is None:
            self._load_artifacts(model_path, encoder_path)
    
    def _load_artifacts(
        self,
        model_path: Optional[Path] = None,
        encoder_path: Optional[Path] = None
    ) -> None:
        """Carga modelo y encoder desde disco."""
        from .model_trainer import ModelTrainer
        
        model_file = model_path or Config.MODEL_FILE
        
        # Si no hay encoder_path, intenta cargar de directorio padre del modelo
        if encoder_path is None:
            encoder_path = model_file.parent / "encoder"
        
        # Usar ModelTrainer para cargar consistentemente
        trainer = ModelTrainer()
        try:
            trainer.load_model(model_file, encoder_path)
            self.classifier = trainer.classifier
            self.encoder = trainer.encoder
            logger.info(f"Artefactos cargados: modelo={model_file}, encoder={encoder_path}")
        except Exception as e:
            logger.error(f"Error cargando artefactos: {e}")
            raise
        
        # Cargar meta-encoders si existen
        meta_encoders_path = model_file.parent / "meta_encoders.pkl"
        if meta_encoders_path.exists():
            try:
                with open(meta_encoders_path, 'rb') as f:
                    meta_data = pickle.load(f)
                self.meta_encoders = meta_data.get('encoders', {})
                self.meta_feature_columns = meta_data.get('columns', [])
                logger.info(f"Meta-encoders cargados ({len(self.meta_feature_columns)} features)")
            except Exception as e:
                logger.debug(f"No se pudieron cargar meta-encoders: {e}")
    
    def _ensure_encoder(self) -> None:
        """Verifica que el encoder esté disponible."""
        if self.encoder is None:
            raise ValueError("Encoder no disponible. Necesario para predicción.")
    
    def _ensure_classifier(self) -> None:
        """Verifica que el clasificador esté disponible."""
        if self.classifier is None:
            raise ValueError("Clasificador no disponible. Necesario para predicción.")
    
    def _remove_boilerplate(self, text: str) -> str:
        cleaned = text
        for pattern in LLM_BOILERPLATE_PATTERNS:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
        return re.sub(r"\s+", " ", cleaned).strip()
    
    def _encode_metadata(self, metadata: Dict[str, Any]) -> Optional[np.ndarray]:
        if not self.meta_feature_columns or not metadata:
            return None
        
        row = {}
        for col in self.meta_feature_columns:
            row[col] = 0
        
        dept = metadata.get("department", "Unknown")
        type_val = metadata.get("type", "Unknown")
        tags_str = metadata.get("tags", "")
        row_tags = set()
        if tags_str:
            row_tags = set(t.strip() for t in str(tags_str).split(",") if t.strip())
        
        for col in self.meta_feature_columns:
            if col.startswith("dept_"):
                expected_val = col.replace("dept_", "")
                row[col] = 1 if str(dept) == expected_val else 0
            elif col.startswith("type_"):
                expected_val = col.replace("type_", "")
                row[col] = 1 if str(type_val) == expected_val else 0
            elif col.startswith("tag_"):
                tag_name = col.replace("tag_", "")
                row[col] = 1 if tag_name in row_tags else 0
        
        return np.array([[float(row[col]) for col in self.meta_feature_columns]], dtype=np.float32)
    
    def _encode_text(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> np.ndarray:
        self._ensure_encoder()
        text = self._remove_boilerplate(text)
        X_text = self.encoder.encode([text])
        
        if self.meta_encoders and metadata:
            X_meta = self._encode_metadata(metadata)
            if X_meta is not None:
                X_text = np.hstack([X_text, X_meta.astype(np.float32)])
        
        return X_text
    
    def predict(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> int:
        self._ensure_classifier()
        X = self._encode_text(text, metadata)
        prediction = self.classifier.predict(X)[0]
        return int(prediction)
    
    def predict_with_confidence(self, text: str, metadata: Optional[Dict[str, Any]] = None) -> Tuple[int, float]:
        self._ensure_classifier()
        X = self._encode_text(text, metadata)
        prediction = self.classifier.predict(X)[0]
        probabilities = self.classifier.predict_proba(X)[0]
        confidence = probabilities.max()
        return int(prediction), float(confidence)
    
    def explain_prediction(
        self,
        text: str,
        top_k: int = 5,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        self._ensure_classifier()
        self._ensure_encoder()
        
        X = self._encode_text(text, metadata)
        
        # Predicción y probabilidades
        prediction = self.classifier.predict(X)[0]
        probabilities = self.classifier.predict_proba(X)[0]
        confidence = probabilities.max()
        
        # Explicabilidad con SHAP o fallback a coeficientes
        try:
            shap_values = self._compute_shap_values(X)
            top_features = self._extract_top_shap_features(shap_values, X, top_k)
            explanation_method = "SHAP (SHapley Additive exPlanations)"
        except Exception as e:
            logger.debug(f"SHAP no disponible ({e}), usando coeficientes del modelo")
            top_features = self._extract_top_coef_features(X, prediction, top_k)
            explanation_method = "Coeficientes del modelo"
        
        # Generar explicación
        explanation = {
            "predicted_priority": int(prediction),
            "priority_label": self.PRIORITY_LABELS[int(prediction)],
            "priority_description": self.PRIORITY_DESCRIPTIONS[int(prediction)],
            "confidence": float(confidence),
            "all_probabilities": {
                self.PRIORITY_LABELS[i]: float(prob)
                for i, prob in enumerate(probabilities)
            },
            "contributing_features": top_features,
            "explanation_method": explanation_method,
            "reasoning": self._generate_reasoning(
                prediction, probabilities, top_features, text
            ),
            "response_time_seconds": Config.RESPONSE_TIME_SECONDS
        }
        
        return explanation
    
    def _compute_shap_values(self, X: np.ndarray) -> np.ndarray:
        """
        Calcula valores SHAP para la instancia.
        
        Args:
            X: Features codificadas
            
        Returns:
            Valores SHAP para cada feature
        """
        import shap

        if self._shap_explainer is None:
            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    self._shap_explainer = shap.Explainer(
                        self.classifier.predict_proba,
                        self.encoder.encode
                    )
            except Exception:
                background = np.zeros((1, X.shape[1]))
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    self._shap_explainer = shap.KernelExplainer(
                        self.classifier.predict_proba, background
                    )
        
        shap_values = self._shap_explainer(X)
        return shap_values.values[0]  # Solo para la primera instancia
    
    def _extract_top_shap_features(
        self,
        shap_values: np.ndarray,
        X: np.ndarray,
        top_k: int
    ) -> List[Dict[str, Any]]:
        """
        Extrae las top-k features con mayor impacto SHAP.
        
        Args:
            shap_values: Valores SHAP por feature
            X: Features originales
            top_k: Número de features a retornar
            
        Returns:
            Lista de diccionarios con features clave
        """
        # SHAP values son para la clase predicha
        prediction = self.classifier.predict(X)[0]
        
        # Para clasificación multiclase, SHAP retorna (n_classes, n_features)
        if len(shap_values.shape) > 1:
            class_shap = shap_values[prediction]
        else:
            class_shap = shap_values
        
        # Indices ordenados por impacto absoluto
        top_indices = np.argsort(np.abs(class_shap))[::-1][:top_k]
        
        features = []
        for idx in top_indices:
            value = class_shap[idx]
            feature_value = float(X[0][idx])
            feature_name = self._get_feature_name(idx)
            features.append({
                "feature_index": int(idx),
                "feature_name": feature_name,
                "feature_value": feature_value,
                "score": float(value),
                "importance": "positive" if value > 0 else "negative",
                "abs_score": float(abs(value))
            })
        
        return features
    
    def _extract_top_coef_features(
        self,
        X: np.ndarray,
        prediction: int,
        top_k: int
    ) -> List[Dict[str, Any]]:
        """
        Extrae features clave usando coeficientes del modelo (fallback).
        
        Solo funciona con modelos lineales. Para modelos no lineales,
        retorna features basadas en magnitud.
        
        Args:
            X: Features codificadas
            prediction: Clase predicha
            top_k: Número de features a retornar
            
        Returns:
            Lista de diccionarios con features clave
        """
        # Intentar obtener coeficientes
        try:
            if hasattr(self.classifier, 'coef_'):
                coefficients = self.classifier.coef_[prediction]
            elif hasattr(self.classifier, 'feature_importances_'):
                coefficients = self.classifier.feature_importances_
            else:
                # No hay coeficientes, usar magnitud de features
                coefficients = np.abs(X[0])
        except Exception:
            coefficients = np.abs(X[0])
        
        # Calcular scores
        feature_scores = coefficients * X[0]
        
        # Top features
        top_indices = np.argsort(np.abs(feature_scores))[::-1][:top_k]
        
        features = []
        for idx in top_indices:
            score = float(feature_scores[idx])
            if score != 0:
                feature_value = float(X[0][idx])
                feature_name = self._get_feature_name(idx)
                features.append({
                    "feature_index": int(idx),
                    "feature_name": feature_name,
                    "feature_value": feature_value,
                    "score": score,
                    "importance": "positive" if score > 0 else "negative",
                    "abs_score": float(abs(score))
                })
        
        return features
    
    def _get_feature_name(self, feature_index: int) -> str:
        """
        Obtiene el nombre del feature para un índice dado.
        
        Args:
            feature_index: Índice del feature
            
        Returns:
            Nombre del feature (palabra para TFIDF, o representación para embeddings)
        """
        if hasattr(self.encoder, 'vectorizer'):
            try:
                feature_names = self.encoder.vectorizer.get_feature_names_out()
                if feature_index < len(feature_names):
                    return feature_names[feature_index]
            except Exception:
                pass
        return f"dim_{feature_index}"
    
    def _generate_reasoning(
        self,
        prediction: int,
        probabilities: np.ndarray,
        top_features: List[Dict[str, Any]],
        text: str
    ) -> str:
        """
        Genera una explicación textual de la predicción.
        
        Args:
            prediction: Clase predicha (0-2)
            probabilities: Probabilidades por clase
            top_features: Features contribuyentes
            text: Texto original
            
        Returns:
            Texto de explicación
        """
        confidence = probabilities.max() * 100
        priority_label = self.PRIORITY_LABELS[prediction]
        
        # Construir explicación
        reasoning = (
            f"El sistema sugiere {priority_label} "
            f"({self.PRIORITY_DESCRIPTIONS[prediction]}) con "
            f"{confidence:.1f}% de confianza.\n"
        )
        
        if top_features:
            reasoning += f"\nFactores clave detectados en el incidente:\n"
            for i, feat in enumerate(top_features[:3], 1):
                direction = "(+)" if feat["importance"] == "positive" else "(-)"
                feature_display = feat.get('feature_name', f"Feature {feat['feature_index']}")
                feature_value = feat.get('feature_value', 0.0)
                reasoning += (
                    f"  {i}. {feature_display}{direction} "
                    f"(valor: {feature_value:.4f}, impacto: {feat['abs_score']:.4f})\n"
                )
        
        # Análisis del texto
        reasoning += f"\nTexto analizado: \"{text[:100]}...\""
        
        return reasoning
    
    def _encode_batch_texts(self, texts: List[str], metadata_list: Optional[List[Dict[str, Any]]] = None) -> np.ndarray:
        cleaned_texts = [self._remove_boilerplate(t) for t in texts]
        batch_size = 16 if 'MiniLM' in type(self.encoder).__name__ else 32
        all_encoded = []
        for i in range(0, len(cleaned_texts), batch_size):
            batch = cleaned_texts[i:i+batch_size]
            encoded = self.encoder.encode(batch)
            all_encoded.append(encoded)
        X = np.vstack(all_encoded)
        
        if self.meta_encoders and metadata_list:
            meta_parts = []
            for meta in metadata_list:
                X_meta = self._encode_metadata(meta)
                if X_meta is not None:
                    meta_parts.append(X_meta)
            if meta_parts:
                X_meta_all = np.vstack(meta_parts)
                X = np.hstack([X, X_meta_all.astype(np.float32)])
        
        return X

    def batch_predict(self, texts: List[str], metadata_list: Optional[List[Dict[str, Any]]] = None) -> np.ndarray:
        self._ensure_classifier()
        self._ensure_encoder()
        
        if not texts:
            return np.array([], dtype=np.int32)
        
        X = self._encode_batch_texts(texts, metadata_list)
        predictions = self.classifier.predict(X)
        return predictions.astype(np.int32)
    
    def batch_predict_with_confidence(
        self,
        texts: List[str],
        metadata_list: Optional[List[Dict[str, Any]]] = None
    ) -> List[Tuple[int, float]]:
        self._ensure_classifier()
        self._ensure_encoder()
        
        if not texts:
            return []
        
        X = self._encode_batch_texts(texts, metadata_list)
        predictions = self.classifier.predict(X)
        probabilities = self.classifier.predict_proba(X)
        
        results = [
            (int(pred), float(prob.max()))
            for pred, prob in zip(predictions, probabilities)
        ]
        
        return results


def save_model_artifacts(
    classifier: IClassifier,
    encoder: IEncoder,
    save_dir: Path,
    metadata: Optional[Dict[str, Any]] = None
) -> None:
    """
    Guarda todos los artefactos del modelo en un directorio.
    
    Args:
        classifier: Clasificador entrenado
        encoder: Encoder entrenado
        save_dir: Directorio donde guardar
        metadata: Metadatos adicionales
    """
    save_dir.mkdir(parents=True, exist_ok=True)
    
    # Guardar modelo
    classifier.save(save_dir / Config.MODEL_FILE.name)
    
    # Guardar encoder
    encoder.save(save_dir / "encoder")
    
    # Guardar metadata
    if metadata:
        with open(save_dir / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)
    
    logger.info(f"Artefactos guardados en {save_dir}")


def load_model_artifacts(
    model_dir: Path
) -> Tuple[IClassifier, IEncoder]:
    """
    Carga modelo y encoder desde directorio.
    
    Args:
        model_dir: Directorio con artefactos guardados
        
    Returns:
        Tupla (classifier, encoder)
    """
    from .model_trainer import ModelTrainer
    
    trainer = ModelTrainer()
    trainer.load_model(
        model_dir / Config.MODEL_FILE.name,
        model_dir / "encoder"
    )
    
    if trainer.classifier is None or trainer.encoder is None:
        raise ValueError("No se pudieron cargar los artefactos")
    
    return trainer.classifier, trainer.encoder
