"""
Predicción y explicabilidad del modelo.

Incluye:
- Predicción de prioridades
- Explicación de predicciones (palabras clave)
- Confianza en predicciones
"""

import pickle
from pathlib import Path
from typing import Tuple, List, Dict, Optional
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer

from .utils import logger, Config


class PriorityPredictor:
    """Realiza predicciones y proporciona explicabilidad."""
    
    PRIORITY_LABELS = {1: "P1 (Critical)", 2: "P2 (Medium)", 3: "P3 (Low)"}
    
    def __init__(
        self,
        model_path: Optional[Path] = None,
        vectorizer_path: Optional[Path] = None
    ):
        """
        Inicializa el predictor.
        
        Args:
            model_path: Ruta al modelo (usa default si no se especifica)
            vectorizer_path: Ruta al vectorizador (usa default si no se especifica)
        """
        self.model = None
        self.vectorizer = None
        self.feature_names = None
        
        # Cargar modelo y vectorizador
        self._load_artifacts(model_path, vectorizer_path)
    
    def _load_artifacts(
        self,
        model_path: Optional[Path] = None,
        vectorizer_path: Optional[Path] = None
    ) -> None:
        """Carga modelo y vectorizador."""
        model_file = model_path or Config.MODEL_FILE
        vec_file = vectorizer_path or Config.VECTORIZER_FILE
        
        if model_file.exists():
            with open(model_file, "rb") as f:
                self.model = pickle.load(f)
            logger.info(f"Modelo cargado desde {model_file}")
        else:
            raise FileNotFoundError(f"Modelo no encontrado: {model_file}")
        
        if vec_file.exists():
            with open(vec_file, "rb") as f:
                self.vectorizer = pickle.load(f)
                self.feature_names = self.vectorizer.get_feature_names_out()
            logger.info(f"Vectorizador cargado desde {vec_file}")
        else:
            raise FileNotFoundError(f"Vectorizador no encontrado: {vec_file}")
    
    def predict(self, text: str) -> int:
        """
        Predice la prioridad para un texto de incidente.
        
        Requisito RF-06: Generar prioridad sugerida (P1=Critical, P2=Medium, P3=Low)
        
        Args:
            text: Descripción del incidente
            
        Returns:
            Prioridad predicha (1-3)
        """
        X = self.vectorizer.transform([text])
        prediction = self.model.predict(X)[0]
        return int(prediction)
    
    def predict_with_confidence(self, text: str) -> Tuple[int, float]:
        """
        Predice la prioridad con nivel de confianza.
        
        Args:
            text: Descripción del incidente
            
        Returns:
            Tupla (prioridad, confianza)
        """
        X = self.vectorizer.transform([text])
        prediction = self.model.predict(X)[0]
        probabilities = self.model.predict_proba(X)[0]
        confidence = probabilities.max()
        
        return int(prediction), float(confidence)
    
    def explain_prediction(
        self,
        text: str,
        top_k: int = 5
    ) -> Dict[str, any]:
        """
        Explica una predicción mostrando palabras clave contribuyentes.
        
        Requisito RF-23: Explicación con palabras clave o score
        
        Args:
            text: Descripción del incidente
            top_k: Número de palabras clave a mostrar
            
        Returns:
            Diccionario con explicación
        """
        # Vectorizar
        X = self.vectorizer.transform([text])
        
        # Predicción y probabilidades
        prediction = self.model.predict(X)[0]
        probabilities = self.model.predict_proba(X)[0]
        
        # Obtener coeficientes del modelo para la clase predicha
        # En LogisticRegression, los coeficientes indican la importancia de each feature
        class_index = int(prediction) - 1  # Índice en array (0-2)
        coefficients = self.model.coef_[class_index]
        
        # Convertir features a dense para análisis
        X_dense = X.toarray()[0]
        
        # Calcular scores (coeficiente * feature_value)
        feature_scores = coefficients * X_dense
        
        # Top palabras positivas (que contribuyen a la predicción)
        top_indices = np.argsort(np.abs(feature_scores))[-top_k:][::-1]
        
        top_features = []
        for idx in top_indices:
            if feature_scores[idx] != 0:  # Solo incluir features presentes
                top_features.append({
                    "feature": self.feature_names[idx],
                    "score": float(feature_scores[idx]),
                    "importance": "positive" if feature_scores[idx] > 0 else "negative"
                })
        
        explanation = {
            "predicted_priority": int(prediction),
            "priority_label": self.PRIORITY_LABELS[int(prediction)],
            "confidence": float(probabilities.max()),
            "all_probabilities": {
                self.PRIORITY_LABELS[i+1]: float(prob)
                for i, prob in enumerate(probabilities)
            },
            "contributing_features": top_features,
            "reasoning": self._generate_reasoning(prediction, probabilities, top_features)
        }
        
        return explanation
    
    def _generate_reasoning(
        self,
        prediction: int,
        probabilities: np.ndarray,
        top_features: List[Dict]
    ) -> str:
        """
        Genera una explicación textual de la predicción.
        
        Args:
            prediction: Prioridad predicha
            probabilities: Probabilidades de cada clase
            top_features: Características más importantes
            
        Returns:
            Texto de explicación
        """
        confidence = probabilities.max() * 100
        priority_label = self.PRIORITY_LABELS[int(prediction)]
        
        features_str = ", ".join([f['feature'] for f in top_features[:3]])
        
        reasoning = (
            f"El sistema sugiere {priority_label} con {confidence:.1f}% de confianza. "
            f"Palabras clave detectadas: {features_str}. "
        )
        
        return reasoning
    
    def batch_predict(self, texts: List[str]) -> np.ndarray:
        """
        Realiza predicciones en lotes.
        
        Args:
            texts: Lista de textos de incidentes
            
        Returns:
            Array de predicciones
        """
        X = self.vectorizer.transform(texts)
        predictions = self.model.predict(X)
        return predictions
    
    def batch_predict_with_confidence(
        self,
        texts: List[str]
    ) -> List[Tuple[int, float]]:
        """
        Realiza predicciones en lotes con confianza.
        
        Args:
            texts: Lista de textos de incidentes
            
        Returns:
            Lista de tuplas (prioridad, confianza)
        """
        X = self.vectorizer.transform(texts)
        predictions = self.model.predict(X)
        probabilities = self.model.predict_proba(X)
        
        results = [
            (int(pred), float(prob.max()))
            for pred, prob in zip(predictions, probabilities)
        ]
        
        return results


def save_vectorizer(vectorizer: TfidfVectorizer, path: Optional[Path] = None) -> None:
    """
    Guarda el vectorizador TF-IDF.
    
    Args:
        vectorizer: Vectorizador a guardar
        path: Ruta de destino (usa default si no se especifica)
    """
    save_path = path or Config.VECTORIZER_FILE
    save_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(save_path, "wb") as f:
        pickle.dump(vectorizer, f)
    
    logger.info(f"Vectorizador guardado en {save_path}")
