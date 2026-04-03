"""
Procesamiento y preparación de datos para el modelo de priorización.

Incluye:
- Carga de datos
- Limpieza y validación
- Generación de características
- División train/test
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Tuple, List
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from .utils import logger, Config


class DataProcessor:
    """Procesa y prepara datos para entrenamiento del modelo."""
    
    def __init__(self, random_state: int = Config.RANDOM_STATE):
        """
        Inicializa el procesador.
        
        Args:
            random_state: Semilla para reproducibilidad
        """
        self.random_state = random_state
        self.vectorizer = None
        self.feature_names = None
        
    def load_data(self, filepath: Path) -> pd.DataFrame:
        """
        Carga datos desde CSV.
        
        Args:
            filepath: Ruta al archivo CSV
            
        Returns:
            DataFrame con los datos
        """
        if not filepath.exists():
            raise FileNotFoundError(f"No se encontró el archivo: {filepath}")
        
        logger.info(f"Cargando datos desde {filepath}")
        df = pd.read_csv(filepath)
        logger.info(f"Datos cargados: {df.shape[0]} filas, {df.shape[1]} columnas")
        
        return df
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Limpia y valida los datos.
        
        Args:
            df: DataFrame con datos crudos
            
        Returns:
            DataFrame limpio
        """
        logger.info("Iniciando limpieza de datos")
        df_clean = df.copy()
        
        # Reemplazar valores no estándar
        df_clean.replace({"NS": np.nan, "NA": np.nan}, inplace=True)
        
        # Convertir Priority, Impact, Urgency a numéricos
        numeric_cols = ["Priority", "Impact", "Urgency"]
        for col in numeric_cols:
            if col in df_clean.columns:
                df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
        
        # Eliminar filas sin Priority (target variable)
        if "Priority" in df_clean.columns:
            initial_rows = len(df_clean)
            df_clean = df_clean.dropna(subset=["Priority"])
            removed = initial_rows - len(df_clean)
            logger.info(f"Se eliminaron {removed} filas sin Priority")
        
        # Filtrar prioridades válidas (1-4)
        if "Priority" in df_clean.columns:
            df_clean = df_clean[df_clean["Priority"].isin([1, 2, 3, 4])]
            logger.info(f"Después de filtrar: {len(df_clean)} filas válidas")
        
        logger.info(f"Limpieza completada: {len(df_clean)} filas")
        return df_clean
    
    def generate_incident_text(self, row: pd.Series) -> str:
        """
        Genera texto de descripción de incidente a partir de metadatos.
        
        Esto es necesario porque ITSM_data.csv no tiene descripción textual.
        Combina campos estructurados para crear un texto más realista.
        
        Args:
            row: Fila del DataFrame
            
        Returns:
            Texto del incidente
        """
        parts = []
        
        # Categoría
        if pd.notna(row.get("Category")):
            parts.append(f"Category: {row['Category']}")
        
        # Subcategoría
        if pd.notna(row.get("CI_Subcat")):
            parts.append(f"Type: {row['CI_Subcat']}")
        
        # Impacto
        if pd.notna(row.get("Impact")):
            impact_map = {1: "Low", 2: "Medium", 3: "High", 4: "Critical"}
            parts.append(f"Impact Level: {impact_map.get(row['Impact'], 'Unknown')}")
        
        # Urgencia
        if pd.notna(row.get("Urgency")):
            urgency_map = {1: "Low", 2: "Medium", 3: "High", 4: "Critical"}
            parts.append(f"Urgency: {urgency_map.get(row['Urgency'], 'Unknown')}")
        
        # Estado
        if pd.notna(row.get("Status")):
            parts.append(f"Status: {row['Status']}")
        
        # Código de cierre
        if pd.notna(row.get("Closure_Code")):
            parts.append(f"Resolution: {row['Closure_Code']}")
        
        text = ". ".join(parts)
        return text if text else "Incident with no details"
    
    def prepare_texts_and_labels(self, df: pd.DataFrame) -> Tuple[List[str], np.ndarray]:
        """
        Prepara textos de incidentes y etiquetas de prioridad.
        
        Args:
            df: DataFrame con datos limpios
            
        Returns:
            Tupla (lista de textos, array de etiquetas)
        """
        logger.info("Generando textos de incidentes desde metadatos")
        
        # Generar textos a partir de los datos disponibles
        texts = df.apply(self.generate_incident_text, axis=1).tolist()
        
        # Etiquetas de prioridad
        labels = df["Priority"].astype(int).values
        
        logger.info(f"Textos generados: {len(texts)}")
        logger.info(f"Distribución de prioridades:\n{pd.Series(labels).value_counts().sort_index()}")
        
        return texts, labels
    
    def vectorize_texts(
        self, 
        texts: List[str], 
        fit: bool = True
    ) -> np.ndarray:
        """
        Convierte textos a características TF-IDF.
        
        Args:
            texts: Lista de textos
            fit: Si True, entrena el vectorizador; si False, usa el existente
            
        Returns:
            Matriz de características TF-IDF
        """
        if fit:
            logger.info("Entrenando TF-IDF vectorizador")
            self.vectorizer = TfidfVectorizer(
                max_features=Config.TF_IDF_MAX_FEATURES,
                min_df=Config.TF_IDF_MIN_DF,
                max_df=Config.TF_IDF_MAX_DF,
                ngram_range=(1, 2),
                lowercase=True
            )
            features = self.vectorizer.fit_transform(texts)
            self.feature_names = self.vectorizer.get_feature_names_out()
            logger.info(f"Características creadas: {features.shape[1]}")
        else:
            if self.vectorizer is None:
                raise ValueError("Vectorizador no entrenado. Use fit=True primero.")
            logger.info("Usando vectorizador preentrenado")
            features = self.vectorizer.transform(texts)
        
        return features
    
    def split_data(
        self,
        X: np.ndarray,
        y: np.ndarray,
        test_size: float = Config.TEST_SIZE,
        validation_size: float = Config.VALIDATION_SIZE
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Divide datos en train/validation/test.
        
        Args:
            X: Features
            y: Labels
            test_size: Proporción para test
            validation_size: Proporción para validation (del training)
            
        Returns:
            Tupla (X_train, X_val, X_test, y_train, y_val, y_test)
        """
        logger.info("Dividiendo datos en train/validation/test")
        
        # Primero separar test
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y,
            test_size=test_size,
            random_state=self.random_state,
            stratify=y
        )
        
        # Luego separar validation del training
        val_size_adjusted = validation_size / (1 - test_size)
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp,
            test_size=val_size_adjusted,
            random_state=self.random_state,
            stratify=y_temp
        )
        
        logger.info(f"Train: {X_train.shape[0]}, Val: {X_val.shape[0]}, Test: {X_test.shape[0]}")
        
        return X_train, X_val, X_test, y_train, y_val, y_test
    
    def preprocess_pipeline(
        self,
        input_file: Path
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """
        Pipeline completo de preprocesamiento.
        
        Args:
            input_file: Ruta al archivo CSV de entrada
            
        Returns:
            Datos divididos en train/val/test
        """
        logger.info("=" * 50)
        logger.info("INICIANDO PIPELINE DE PREPROCESAMIENTO")
        logger.info("=" * 50)
        
        # 1. Cargar datos
        df = self.load_data(input_file)
        
        # 2. Limpiar datos
        df_clean = self.clean_data(df)
        
        # 3. Generar textos y etiquetas
        texts, labels = self.prepare_texts_and_labels(df_clean)
        
        # 4. Vectorizar
        X = self.vectorize_texts(texts, fit=True)
        
        # 5. Dividir datos
        X_train, X_val, X_test, y_train, y_val, y_test = self.split_data(X, labels)
        
        logger.info("=" * 50)
        logger.info("PIPELINE DE PREPROCESAMIENTO COMPLETADO")
        logger.info("=" * 50)
        
        return X_train, X_val, X_test, y_train, y_val, y_test
    
    def preprocess_single_text(self, text: str) -> np.ndarray:
        """
        Preprocesa un texto individual para predicción.
        
        Args:
            text: Texto del incidente
            
        Returns:
            Features vectorizadas
        """
        if self.vectorizer is None:
            raise ValueError("Vectorizador no disponible")
        return self.vectorizer.transform([text])
