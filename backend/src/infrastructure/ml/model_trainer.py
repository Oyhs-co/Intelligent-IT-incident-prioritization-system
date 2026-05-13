import json
import pickle
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    f1_score,
    precision_score,
    recall_score,
)

from ._utils import Config, logger
from .classifiers import FallbackEnsembleClassifier, LightGBMClassifier
from .encoders import MiniLMEncoder, TFIDFEncoder
from .interfaces import IClassifier, IEncoder


class ModelTrainer:
    def __init__(
        self,
        classifier: IClassifier | None = None,
        encoder: IEncoder | None = None,
        random_state: int = Config.RANDOM_STATE
    ):
        self.random_state = random_state
        self.classifier = classifier
        self.encoder = encoder
        self.metrics: dict[str, dict[str, Any]] = {}

    def create_model(self, n_classes: int = 3) -> IClassifier:
        logger.info("Creando modelo LightGBM classifier (por defecto)")

        model = ModelFactory.create_lightgbm(
            n_classes=n_classes,
            num_leaves=Config.LGB_NUM_LEAVES,
            max_depth=Config.LGB_MAX_DEPTH,
            learning_rate=Config.LGB_LEARNING_RATE
        )

        self.classifier = model
        return model

    def train(
        self,
        X_train: np.ndarray,
        y_train: np.ndarray,
        X_val: np.ndarray | None = None,
        y_val: np.ndarray | None = None
    ) -> None:
        if self.classifier is None:
            self.create_model()

        logger.info("Iniciando entrenamiento del modelo")
        logger.info(f"  Train samples: {X_train.shape[0]}")
        logger.info(f"  Features: {X_train.shape[1]}")
        logger.info(f"  Classes: {len(np.unique(y_train))}")

        has_val = X_val is not None and y_val is not None
        if has_val:
            logger.info(f"  Early stopping habilitado (val samples: {X_val.shape[0]})")
            self.classifier.fit(X_train, y_train, X_val=X_val, y_val=y_val)
        else:
            self.classifier.fit(X_train, y_train)

        logger.info("Entrenamiento completado")

    def evaluate(
        self,
        X: np.ndarray,
        y: np.ndarray,
        dataset_name: str = "Validation"
    ) -> dict[str, Any]:
        if self.classifier is None:
            raise ValueError("Modelo no entrenado")

        logger.info(f"Evaluando modelo en {dataset_name}")

        y_pred = self.classifier.predict(X)
        metrics = {
            "accuracy": accuracy_score(y, y_pred),
            "precision": precision_score(y, y_pred, average="weighted", zero_division=0),
            "recall": recall_score(y, y_pred, average="weighted", zero_division=0),
            "f1": f1_score(y, y_pred, average="weighted", zero_division=0),
            "confusion_matrix": confusion_matrix(y, y_pred).tolist(),
            "classification_report": classification_report(y, y_pred, zero_division=0)
        }

        logger.info(f"\n{dataset_name} Metrics:")
        logger.info(f"  Accuracy:  {metrics['accuracy']:.4f}")
        logger.info(f"  Precision: {metrics['precision']:.4f}")
        logger.info(f"  Recall:    {metrics['recall']:.4f}")
        logger.info(f"  F1-Score:  {metrics['f1']:.4f}")

        cm = metrics["confusion_matrix"]
        logger.info("\n  Confusion Matrix:")
        logger.info("    Predicted ->")
        logger.info("       P1  P2  P3")
        for i, row in enumerate(cm):
            logger.info(f"  P{i+1}  {row[0]:3d} {row[1]:3d} {row[2]:3d}")

        return metrics

    def validate(
        self,
        X_val: np.ndarray,
        y_val: np.ndarray
    ) -> dict[str, Any]:
        logger.info("\n" + "=" * 60)
        logger.info("VALIDACIÓN DEL MODELO")
        logger.info("=" * 60)

        val_metrics = self.evaluate(X_val, y_val, "Validation")

        if val_metrics["accuracy"] < Config.MIN_ACCURACY:
            logger.warning(
                f"[WARN] Accuracy ({val_metrics['accuracy']:.4f}) por debajo del mínimo "
                f"requerido ({Config.MIN_ACCURACY:.4f})"
            )
        else:
            logger.info(
                f"[OK] RNF-08: Accuracy ({val_metrics['accuracy']:.4f}) cumple requisito mínimo"
            )

        if val_metrics["accuracy"] >= 0.85:
            logger.info(
                f"[OK] Excelente: Accuracy ({val_metrics['accuracy']:.4f})"
                f">= 85% (Meta aspiracional)"
            )

        self.metrics["validation"] = val_metrics
        return val_metrics

    def test(
        self,
        X_test: np.ndarray,
        y_test: np.ndarray
    ) -> dict[str, Any]:
        logger.info("\n" + "=" * 60)
        logger.info("EVALUACIÓN EN TEST")
        logger.info("=" * 60)

        test_metrics = self.evaluate(X_test, y_test, "Test")

        if test_metrics["accuracy"] < Config.MIN_ACCURACY:
            logger.warning(
                f"⚠ Test Accuracy ({test_metrics['accuracy']:.4f}) por debajo "
                f"del mínimo requerido ({Config.MIN_ACCURACY:.4f})"
            )
        else:
            logger.info(
                f"[OK] RNF-08: Test Accuracy ({test_metrics['accuracy']:.4f}) cumple requisito"
            )

        train_val_gap = None
        if "validation" in self.metrics:
            train_val_gap = abs(self.metrics["validation"]["accuracy"] - test_metrics["accuracy"])
            logger.info(f"\n  Gap validation-test: {train_val_gap:.4f}")
            if train_val_gap < 0.05:
                logger.info("[OK] RNF-10: Buena capacidad de generalización (gap < 5%)")
            else:
                logger.warning("[WARN] RNF-10: Posible overfitting (gap > 5%)")

        self.metrics["test"] = test_metrics
        return test_metrics

    def save_model(
        self,
        model_path: Path | None = None,
        encoder_path: Path | None = None,
        metadata: dict[str, Any] | None = None
    ) -> None:
        if self.classifier is None:
            raise ValueError("No hay modelo entrenado para guardar")

        save_path = model_path or Config.MODEL_FILE
        save_path.parent.mkdir(parents=True, exist_ok=True)
        self.classifier.save(save_path)
        logger.info(f"Modelo guardado en {save_path}")

        if self.encoder is not None:
            vec_path = encoder_path or Config.ENCODER_DIR
            self.encoder.save(vec_path)
            logger.info(f"Encoder guardado en {vec_path}")

        if metadata is None:
            params = self.classifier.get_params() if hasattr(self.classifier, "get_params") else None
            metadata = {
                "metrics": self.metrics,
                "classifier_params": params,
                "random_state": self.random_state,
            }

        metadata_path = save_path.parent / "metadata.json"
        with open(metadata_path, 'w') as f:
            def default_serializer(obj):
                if isinstance(obj, np.integer):
                    return int(obj)
                elif isinstance(obj, np.floating):
                    return float(obj)
                elif isinstance(obj, np.ndarray):
                    return obj.tolist()
                raise TypeError(f"Type {type(obj)} not serializable")

            json.dump(metadata, f, indent=2, default=default_serializer)
        logger.info(f"Metadata guardada en {metadata_path}")

    def load_model(
        self,
        model_path: Path | None = None,
        encoder_path: Path | None = None
    ) -> None:
        load_path = model_path or Config.MODEL_FILE

        if not load_path.exists():
            raise FileNotFoundError(f"Archivo de modelo no encontrado: {load_path}")

        try:
            self.classifier = LightGBMClassifier()
            self.classifier.load(load_path)
            logger.info(f"Modelo LightGBM cargado desde {load_path}")
        except Exception:
            with open(load_path, 'rb') as f:
                self.classifier = pickle.load(f)
            logger.info(f"Modelo LogisticRegression cargado desde {load_path}")

        if encoder_path is not None:
            self._load_encoder(encoder_path)

    def _load_encoder(self, encoder_path: Path) -> None:
        try:
            self.encoder = MiniLMEncoder.load(encoder_path)
            logger.info(f"Encoder MiniLM cargado desde {encoder_path}")
        except Exception:
            try:
                self.encoder = TFIDFEncoder.load(encoder_path)
                logger.info(f"Encoder TF-IDF cargado desde {encoder_path}")
            except Exception:
                logger.warning(f"No se pudo cargar encoder desde {encoder_path}")

    def predict(self, X: np.ndarray) -> np.ndarray:
        if self.classifier is None:
            raise ValueError("Modelo no entrenado")
        return self.classifier.predict(X)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        if self.classifier is None:
            raise ValueError("Modelo no entrenado")
        return self.classifier.predict_proba(X)

    def predict_with_labels(self, X: np.ndarray) -> np.ndarray:
        predictions = self.predict(X)
        return predictions + 1

    def get_metrics_summary(self) -> dict[str, Any]:
        return self.metrics

    def print_summary(self) -> None:
        logger.info("\n" + "=" * 60)
        logger.info("RESUMEN DEL ENTRENAMIENTO")
        logger.info("=" * 60)

        if "validation" in self.metrics:
            logger.info("\nValidation Metrics:")
            for key, value in self.metrics["validation"].items():
                if key not in ["confusion_matrix", "classification_report"]:
                    logger.info(f"  {key}: {value:.4f}")

        if "test" in self.metrics:
            logger.info("\nTest Metrics:")
            for key, value in self.metrics["test"].items():
                if key not in ["confusion_matrix", "classification_report"]:
                    logger.info(f"  {key}: {value:.4f}")

        logger.info("=" * 60 + "\n")


class ModelFactory:
    @staticmethod
    def create_lightgbm(
        n_classes: int = 3,
        num_leaves: int = 31,
        max_depth: int = 6,
        learning_rate: float = 0.05
    ) -> IClassifier:
        return LightGBMClassifier(
            n_classes=n_classes,
            num_leaves=num_leaves,
            max_depth=max_depth,
            learning_rate=learning_rate,
            n_estimators=Config.LGB_N_ESTIMATORS,
            min_child_samples=Config.LGB_MIN_CHILD_SAMPLES,
            reg_alpha=Config.LGB_REG_ALPHA,
            reg_lambda=Config.LGB_REG_LAMBDA,
            class_weight=None,
            early_stopping_rounds=Config.LGB_EARLY_STOPPING_ROUNDS,
            random_state=Config.RANDOM_STATE,
            verbose=-1
        )

    @staticmethod
    def create_ensemble() -> IClassifier:
        return FallbackEnsembleClassifier(lgb_weight=0.6)

    @staticmethod
    def create_minilm_encoder() -> IEncoder:
        return MiniLMEncoder()

    @staticmethod
    def create_tfidf_encoder(max_features: int = 1000) -> IEncoder:
        return TFIDFEncoder(max_features=max_features)
