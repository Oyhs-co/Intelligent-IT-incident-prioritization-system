from pathlib import Path

import lightgbm as lgb
import numpy as np
from sklearn.linear_model import LogisticRegression

from ._utils import logger
from .interfaces import IClassifier


class LightGBMClassifier(IClassifier):
    def __init__(
        self,
        n_classes: int = 3,
        num_leaves: int = 31,
        max_depth: int = 6,
        learning_rate: float = 0.05,
        n_estimators: int = 300,
        min_child_samples: int = 30,
        reg_alpha: float = 0.1,
        reg_lambda: float = 0.1,
        class_weight: str = None,
        early_stopping_rounds: int = 20,
        random_state: int = 42,
        verbose: int = -1
    ):
        self.n_classes = n_classes
        self.class_weight = None
        self.early_stopping_rounds = early_stopping_rounds
        self.params = {
            'objective': 'multiclass',
            'num_class': n_classes,
            'metric': 'multi_logloss',
            'boosting_type': 'gbdt',
            'num_leaves': num_leaves,
            'max_depth': max_depth,
            'learning_rate': learning_rate,
            'n_estimators': n_estimators,
            'min_child_samples': min_child_samples,
            'reg_alpha': reg_alpha,
            'reg_lambda': reg_lambda,
            'class_weight': class_weight,
            'random_state': random_state,
            'verbose': verbose,
            'force_row_wise': True,
            'n_jobs': -1
        }
        self.model = None
        self._is_fitted = False

    def fit(self, X: np.ndarray, y: np.ndarray, X_val: np.ndarray = None, y_val: np.ndarray = None) -> None:
        logger.info("Entrenando LightGBM classifier...")
        logger.info(f"  Samples: {X.shape[0]}, Features: {X.shape[1]}")
        logger.info(f"  Classes: {self.n_classes}")
        logger.info(f"  Class weight: {self.class_weight}")

        X = X.astype(np.float32)
        y = y.astype(np.int32)

        self.model = lgb.LGBMClassifier(**self.params)

        use_early_stopping = (self.early_stopping_rounds > 0
                              and X_val is not None and y_val is not None)

        if use_early_stopping:
            X_val = X_val.astype(np.float32)
            logger.info(f"  Early stopping: {self.early_stopping_rounds} rounds")
            logger.info(f"  Validation samples: {X_val.shape[0]}")
            self.model.fit(X, y, eval_set=[(X_val, y_val)])
        else:
            self.model.fit(X, y)

        self._is_fitted = True

        if use_early_stopping and hasattr(self.model, 'best_iteration_'):
            logger.info(f"  Best iteration: {self.model.best_iteration_}")

        logger.info("Entrenamiento completado")

    def predict(self, X: np.ndarray) -> np.ndarray:
        self._check_fitted()
        X = X.astype(np.float32)
        if isinstance(self.model, lgb.LGBMClassifier):
            return self.model.predict(X).astype(np.int32)
        else:
            preds = self.model.predict(X)
            n_samples = X.shape[0]
            n_classes = self.params['num_class']
            if preds.ndim == 1 and len(preds) == n_samples * n_classes:
                preds = preds.reshape(n_samples, n_classes)
                return np.argmax(preds, axis=1).astype(np.int32)
            elif preds.ndim == 2:
                return np.argmax(preds, axis=1).astype(np.int32)
            else:
                return preds.astype(np.int32)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        self._check_fitted()
        X = X.astype(np.float32)
        if isinstance(self.model, lgb.LGBMClassifier):
            return self.model.predict_proba(X)
        else:
            preds = self.model.predict(X)
            n_samples = X.shape[0]
            n_classes = self.params['num_class']
            if preds.ndim == 1 and len(preds) == n_samples * n_classes:
                return preds.reshape(n_samples, n_classes)
            elif preds.ndim == 2:
                return preds
            else:
                pred_classes = preds.astype(np.int32)
                preds_mat = np.zeros((len(pred_classes), n_classes), dtype=np.float32)
                preds_mat[np.arange(len(pred_classes)), pred_classes] = 1.0
                return preds_mat

    def save(self, path: Path) -> None:
        self._check_fitted()
        path.parent.mkdir(parents=True, exist_ok=True)
        self.model.booster_.save_model(str(path))
        logger.info(f"Modelo guardado en {path}")

    def load(self, path: Path) -> None:
        self.model = lgb.Booster(model_file=str(path))
        self._is_fitted = True
        logger.info(f"Modelo cargado desde {path}")

    def get_feature_importance(self, X: np.ndarray, y: np.ndarray) -> np.ndarray | None:
        self._check_fitted()
        importance = self.model.feature_importance(importance_type='gain')
        if importance.sum() > 0:
            importance = importance / importance.sum()
        return importance

    def get_params(self) -> dict:
        return self.params.copy()

    def set_params(self, **params) -> None:
        for key, value in params.items():
            if key in self.params:
                self.params[key] = value

    def _check_fitted(self) -> None:
        if not self._is_fitted or self.model is None:
            raise ValueError("Modelo no entrenado. Llama a fit() primero.")


class FallbackEnsembleClassifier(IClassifier):
    def __init__(self, lgb_weight: float = 0.6):
        self.lgb_weight = lgb_weight
        self.lr_weight = 1.0 - lgb_weight

        self.lgb = LightGBMClassifier()
        self.lr = LogisticRegression(max_iter=1000, random_state=42)
        self._is_fitted = False

    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        logger.info("Entrenando ensamble LightGBM + LogisticRegression")
        X_float = X.astype(np.float32)
        self.lgb.fit(X_float, y)
        self.lr.fit(X, y)
        self._is_fitted = True
        logger.info("Ensamble entrenado")

    def predict(self, X: np.ndarray) -> np.ndarray:
        self._check_fitted()
        X_float = X.astype(np.float32)
        proba_lgb = self.lgb.predict_proba(X_float)
        proba_lr = self.lr.predict_proba(X)

        combined = self.lgb_weight * proba_lgb + self.lr_weight * proba_lr
        return np.argmax(combined, axis=1).astype(np.int32)

    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        self._check_fitted()
        X_float = X.astype(np.float32)
        proba_lgb = self.lgb.predict_proba(X_float)
        proba_lr = self.lr.predict_proba(X)
        return self.lgb_weight * proba_lgb + self.lr_weight * proba_lr

    def save(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)
        self.lgb.save(path / "lgb_model.txt")
        import pickle
        with open(path / "lr_model.pkl", 'wb') as f:
            pickle.dump(self.lr, f)
        logger.info(f"Ensamble guardado en {path}")

    def load(self, path: Path) -> None:
        self.lgb = LightGBMClassifier()
        self.lgb.load(path / "lgb_model.txt")
        import pickle
        with open(path / "lr_model.pkl", 'rb') as f:
            self.lr = pickle.load(f)
        self._is_fitted = True
        logger.info(f"Ensamble cargado desde {path}")

    def get_feature_importance(self, X: np.ndarray, y: np.ndarray) -> np.ndarray | None:
        imp_lgb = self.lgb.get_feature_importance(X, y)
        return imp_lgb if imp_lgb is not None else None

    def _check_fitted(self) -> None:
        if not self._is_fitted:
            raise ValueError("Ensamble no entrenado")
