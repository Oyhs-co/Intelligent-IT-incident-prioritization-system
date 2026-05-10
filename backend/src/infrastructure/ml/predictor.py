import json
import pickle
import re
import warnings
from pathlib import Path
from typing import Any

import numpy as np

from ._utils import Config, logger
from .interfaces import IClassifier, IEncoder

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
    PRIORITY_LABELS = {0: "Crítica (Critical)", 1: "Media (Medium)", 2: "Baja (Low)"}
    PRIORITY_DESCRIPTIONS = {
        0: "Critical - Requiere atención inmediata",
        1: "Medium - Requiere atención pronta",
        2: "Low - Puede ser programado"
    }

    def __init__(
        self,
        classifier: IClassifier | None = None,
        encoder: IEncoder | None = None,
        model_path: Path | None = None,
        encoder_path: Path | None = None
    ):
        self.classifier = classifier
        self.encoder = encoder
        self._shap_explainer = None
        self.meta_encoders: dict[str, Any] = {}
        self.meta_feature_columns: list[str] = []

        if self.classifier is None or self.encoder is None:
            self._load_artifacts(model_path, encoder_path)

    def _load_artifacts(
        self,
        model_path: Path | None = None,
        encoder_path: Path | None = None
    ) -> None:
        from .model_trainer import ModelTrainer

        model_file = model_path or Config.MODEL_FILE

        if encoder_path is None:
            encoder_path = model_file.parent / "encoder"

        trainer = ModelTrainer()
        try:
            trainer.load_model(model_file, encoder_path)
            self.classifier = trainer.classifier
            self.encoder = trainer.encoder
            logger.info(f"Artefactos cargados: modelo={model_file}, encoder={encoder_path}")
        except Exception as e:
            logger.error(f"Error cargando artefactos: {e}")
            raise

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
        if self.encoder is None:
            raise ValueError("Encoder no disponible. Necesario para predicción.")

    def _ensure_classifier(self) -> None:
        if self.classifier is None:
            raise ValueError("Clasificador no disponible. Necesario para predicción.")

    def _remove_boilerplate(self, text: str) -> str:
        cleaned = text
        for pattern in LLM_BOILERPLATE_PATTERNS:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
        return re.sub(r"\s+", " ", cleaned).strip()

    def _encode_metadata(self, metadata: dict[str, Any]) -> np.ndarray | None:
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
            row_tags = {t.strip() for t in str(tags_str).split(",") if t.strip()}

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

    def _encode_text(self, text: str, metadata: dict[str, Any] | None = None) -> np.ndarray:
        self._ensure_encoder()
        text = self._remove_boilerplate(text)
        X_text = self.encoder.encode([text])

        if self.meta_encoders and metadata:
            X_meta = self._encode_metadata(metadata)
            if X_meta is not None:
                X_text = np.hstack([X_text, X_meta.astype(np.float32)])

        return X_text

    def predict(self, text: str, metadata: dict[str, Any] | None = None) -> int:
        self._ensure_classifier()
        X = self._encode_text(text, metadata)
        prediction = self.classifier.predict(X)[0]
        return int(prediction)

    def predict_with_confidence(self, text: str, metadata: dict[str, Any] | None = None) -> tuple[int, float]:
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
        metadata: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        self._ensure_classifier()
        self._ensure_encoder()

        X = self._encode_text(text, metadata)

        prediction = self.classifier.predict(X)[0]
        probabilities = self.classifier.predict_proba(X)[0]
        confidence = probabilities.max()

        try:
            shap_values = self._compute_shap_values(X)
            top_features = self._extract_top_shap_features(shap_values, X, top_k)
            explanation_method = "SHAP (SHapley Additive exPlanations)"
        except Exception as e:
            logger.debug(f"SHAP no disponible ({e}), usando coeficientes del modelo")
            top_features = self._extract_top_coef_features(X, prediction, top_k)
            explanation_method = "Coeficientes del modelo"

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
        return shap_values.values[0]

    def _extract_top_shap_features(
        self,
        shap_values: np.ndarray,
        X: np.ndarray,
        top_k: int
    ) -> list[dict[str, Any]]:
        prediction = self.classifier.predict(X)[0]

        if len(shap_values.shape) > 1:
            class_shap = shap_values[prediction]
        else:
            class_shap = shap_values

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
    ) -> list[dict[str, Any]]:
        try:
            if hasattr(self.classifier, 'coef_'):
                coefficients = self.classifier.coef_[prediction]
            elif hasattr(self.classifier, 'feature_importances_'):
                coefficients = self.classifier.feature_importances_
            else:
                coefficients = np.abs(X[0])
        except Exception:
            coefficients = np.abs(X[0])

        feature_scores = coefficients * X[0]

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
        top_features: list[dict[str, Any]],
        text: str
    ) -> str:
        confidence = probabilities.max() * 100
        priority_label = self.PRIORITY_LABELS[prediction]

        reasoning = (
            f"El sistema sugiere {priority_label} "
            f"({self.PRIORITY_DESCRIPTIONS[prediction]}) con "
            f"{confidence:.1f}% de confianza.\n"
        )

        if top_features:
            reasoning += "\nFactores clave detectados en el incidente:\n"
            for i, feat in enumerate(top_features[:3], 1):
                direction = "(+)" if feat["importance"] == "positive" else "(-)"
                feature_display = feat.get('feature_name', f"Feature {feat['feature_index']}")
                feature_value = feat.get('feature_value', 0.0)
                reasoning += (
                    f"  {i}. {feature_display}{direction} "
                    f"(valor: {feature_value:.4f}, impacto: {feat['abs_score']:.4f})\n"
                )

        reasoning += f"\nTexto analizado: \"{text[:100]}...\""

        return reasoning

    def _encode_batch_texts(self, texts: list[str], metadata_list: list[dict[str, Any]] | None = None) -> np.ndarray:
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

    def batch_predict(self, texts: list[str], metadata_list: list[dict[str, Any]] | None = None) -> np.ndarray:
        self._ensure_classifier()
        self._ensure_encoder()

        if not texts:
            return np.array([], dtype=np.int32)

        X = self._encode_batch_texts(texts, metadata_list)
        predictions = self.classifier.predict(X)
        return predictions.astype(np.int32)

    def batch_predict_with_confidence(
        self,
        texts: list[str],
        metadata_list: list[dict[str, Any]] | None = None
    ) -> list[tuple[int, float]]:
        self._ensure_classifier()
        self._ensure_encoder()

        if not texts:
            return []

        X = self._encode_batch_texts(texts, metadata_list)
        predictions = self.classifier.predict(X)
        probabilities = self.classifier.predict_proba(X)

        results = [
            (int(pred), float(prob.max()))
            for pred, prob in zip(predictions, probabilities, strict=False)
        ]

        return results


def save_model_artifacts(
    classifier: IClassifier,
    encoder: IEncoder,
    save_dir: Path,
    metadata: dict[str, Any] | None = None
) -> None:
    save_dir.mkdir(parents=True, exist_ok=True)

    classifier.save(save_dir / Config.MODEL_FILE.name)

    encoder.save(save_dir / "encoder")

    if metadata:
        with open(save_dir / "metadata.json", 'w') as f:
            json.dump(metadata, f, indent=2)

    logger.info(f"Artefactos guardados en {save_dir}")


def load_model_artifacts(
    model_dir: Path
) -> tuple[IClassifier, IEncoder]:
    from .model_trainer import ModelTrainer

    trainer = ModelTrainer()
    trainer.load_model(
        model_dir / Config.MODEL_FILE.name,
        model_dir / "encoder"
    )

    if trainer.classifier is None or trainer.encoder is None:
        raise ValueError("No se pudieron cargar los artefactos")

    return trainer.classifier, trainer.encoder
