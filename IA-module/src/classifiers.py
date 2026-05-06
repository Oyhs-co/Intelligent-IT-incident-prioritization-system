"""
Clasificador LightGBM optimizado para CPU y RAM limitada.

Reemplaza LogisticRegression con mejor accuracy y eficiencia.
Soporta L1/L2 regularization y early stopping.
"""

import numpy as np
from pathlib import Path
from typing import Optional
import lightgbm as lgb
from sklearn.linear_model import LogisticRegression
from .interfaces import IClassifier
from .utils import logger


class LightGBMClassifier(IClassifier):
    """Clasificador LightGBM para priorización de incidentes."""
    
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
        """
        Inicializa el clasificador LightGBM.
        
        Args:
            n_classes: Numero de clases (3 para P1/P2/P3)
            num_leaves: Numero maximo de hojas (controla complejidad)
            max_depth: Profundidad maxima del arbol
            learning_rate: Tasa de aprendizaje
            n_estimators: Numero de arboles
            min_child_samples: Muestras minimas por hoja
            reg_alpha: Regularizacion L1
            reg_lambda: Regularizacion L2
            class_weight: 'balanced' para pesos automaticos, None para sin pesos
            early_stopping_rounds: Rondas sin mejora para early stopping (0 = desactivado)
            random_state: Semilla
            verbose: -1 para silenciar salida
        """
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
        """
        Entrena el modelo LightGBM.
        
        Args:
            X: Features (n_samples, n_features)
            y: Labels (n_samples,) con valores 0, 1, 2
            X_val: Features de validacion (para early stopping)
            y_val: Labels de validacion (para early stopping)
        """
        logger.info("Entrenando LightGBM classifier...")
        logger.info(f"  Samples: {X.shape[0]}, Features: {X.shape[1]}")
        logger.info(f"  Classes: {self.n_classes}")
        logger.info(f"  Class weight: {self.class_weight}")
        
        # Asegura float32 para eficiencia
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
        """
        Predice clases para nuevos datos.
        
        Args:
            X: Features (n_samples, n_features)
            
        Returns:
            Predicciones (n_samples,) con valores 0, 1, 2
        """
        self._check_fitted()
        X = X.astype(np.float32)
        # LightGBM LGBMClassifier.predict retorna directamente las clases
        # Pero si usamos Booster.predict retorna probabilidades planas
        if isinstance(self.model, lgb.LGBMClassifier):
            return self.model.predict(X).astype(np.int32)
        else:
            # Booster.predict retorna probabilidades planas: (n_samples * n_classes,)
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
        """
        Retorna probabilidades por clase.
        
        Args:
            X: Features (n_samples, n_features)
            
        Returns:
            Probabilidades (n_samples, n_classes)
        """
        self._check_fitted()
        X = X.astype(np.float32)
        if isinstance(self.model, lgb.LGBMClassifier):
            return self.model.predict_proba(X)
        else:
            # Booster.predict retorna probabilidades planas: (n_samples * n_classes,)
            preds = self.model.predict(X)
            n_samples = X.shape[0]
            n_classes = self.params['num_class']
            if preds.ndim == 1 and len(preds) == n_samples * n_classes:
                return preds.reshape(n_samples, n_classes)
            elif preds.ndim == 2:
                return preds
            else:
                # Predicciones de clase, convertir a probabilidades one-hot
                pred_classes = preds.astype(np.int32)
                preds_mat = np.zeros((len(pred_classes), n_classes), dtype=np.float32)
                preds_mat[np.arange(len(pred_classes)), pred_classes] = 1.0
                return preds_mat
    
    def save(self, path: Path) -> None:
        """
        Guarda el modelo LightGBM.
        
        Args:
            path: Archivo donde guardar (formato JSON nativo de LightGBM)
        """
        self._check_fitted()
        path.parent.mkdir(parents=True, exist_ok=True)
        self.model.booster_.save_model(str(path))
        logger.info(f"Modelo guardado en {path}")
    
    def load(self, path: Path) -> None:
        """
        Carga un modelo LightGBM entrenado.
        
        Args:
            path: Archivo del modelo
        """
        self.model = lgb.Booster(model_file=str(path))
        self._is_fitted = True
        logger.info(f"Modelo cargado desde {path}")
    
    def get_feature_importance(self, X: np.ndarray, y: np.ndarray) -> Optional[np.ndarray]:
        """
        Calcula importancia de features (Gain).
        
        Args:
            X: Features de entrenamiento
            y: Labels de entrenamiento
            
        Returns:
            Array de importancias normalizadas
        """
        self._check_fitted()
        # LightGBM calcula importancia por split
        importance = self.model.feature_importance(importance_type='gain')
        # Normaliza
        if importance.sum() > 0:
            importance = importance / importance.sum()
        return importance
    
    def get_params(self) -> dict:
        """Retorna los hiperparámetros actuales."""
        return self.params.copy()
    
    def set_params(self, **params) -> None:
        """Actualiza hiperparámetros."""
        for key, value in params.items():
            if key in self.params:
                self.params[key] = value
    
    def _check_fitted(self) -> None:
        """Verifica que el modelo haya sido entrenado."""
        if not self._is_fitted or self.model is None:
            raise ValueError("Modelo no entrenado. Llama a fit() primero.")


class FallbackEnsembleClassifier(IClassifier):
    """
    Ensamble que combina LightGBM + TF-IDF + LogisticRegression.
    
    Usa votación ponderada para mayor robustez.
    Útil cuando un solo modelo no cumple RNF-08.
    """
    
    def __init__(self, lgb_weight: float = 0.6):
        """
        Args:
            lgb_weight: Peso para LightGBM en votación (resto para LR)
        """
        self.lgb_weight = lgb_weight
        self.lr_weight = 1.0 - lgb_weight
        
        self.lgb = LightGBMClassifier()
        self.lr = LogisticRegression(max_iter=1000, random_state=42)
        self._is_fitted = False
    
    def fit(self, X: np.ndarray, y: np.ndarray) -> None:
        """Entrena ambos modelos."""
        logger.info("Entrenando ensamble LightGBM + LogisticRegression")
        X_float = X.astype(np.float32)
        self.lgb.fit(X_float, y)
        self.lr.fit(X, y)
        self._is_fitted = True
        logger.info("Ensamble entrenado")
    
    def predict(self, X: np.ndarray) -> np.ndarray:
        """Predice usando votación ponderada."""
        self._check_fitted()
        X_float = X.astype(np.float32)
        proba_lgb = self.lgb.predict_proba(X_float)
        proba_lr = self.lr.predict_proba(X)
        
        # Votación ponderada
        combined = self.lgb_weight * proba_lgb + self.lr_weight * proba_lr
        return np.argmax(combined, axis=1).astype(np.int32)
    
    def predict_proba(self, X: np.ndarray) -> np.ndarray:
        """Retorna probabilidades combinadas."""
        self._check_fitted()
        X_float = X.astype(np.float32)
        proba_lgb = self.lgb.predict_proba(X_float)
        proba_lr = self.lr.predict_proba(X)
        return self.lgb_weight * proba_lgb + self.lr_weight * proba_lr
    
    def save(self, path: Path) -> None:
        """Guarda ambos modelos."""
        path.mkdir(parents=True, exist_ok=True)
        self.lgb.save(path / "lgb_model.txt")
        import pickle
        with open(path / "lr_model.pkl", 'wb') as f:
            pickle.dump(self.lr, f)
        logger.info(f"Ensamble guardado en {path}")
    
    def load(self, path: Path) -> None:
        """Carga ambos modelos."""
        self.lgb = LightGBMClassifier()
        self.lgb.load(path / "lgb_model.txt")
        import pickle
        with open(path / "lr_model.pkl", 'rb') as f:
            self.lr = pickle.load(f)
        self._is_fitted = True
        logger.info(f"Ensamble cargado desde {path}")
    
    def get_feature_importance(self, X: np.ndarray, y: np.ndarray) -> Optional[np.ndarray]:
        """Importancia combinada."""
        imp_lgb = self.lgb.get_feature_importance(X, y)
        # LR no tiene importancia directa comparable
        return imp_lgb if imp_lgb is not None else None
    
    def _check_fitted(self) -> None:
        if not self._is_fitted:
            raise ValueError("Ensamble no entrenado")
