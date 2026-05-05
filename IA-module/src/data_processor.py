"""
Procesamiento y preparación de datos para el modelo de priorización.

Incluye:
- Carga de datos
- Limpieza y validación
- Generación de características (TF-IDF o embeddings)
- División train/test

Principio DIP: DataProcessor depende de abstracciones (IEncoder), no de implementaciones concretas.
"""

from pathlib import Path
from typing import Tuple, List, Optional
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

from .encoders import MiniLMEncoder, TFIDFEncoder
from .interfaces import IEncoder
from .utils import logger, Config


class DataProcessor:
    """Procesa y prepara datos para entrenamiento del modelo.
    
    Usa inyección de dependencias para el encoder (TF-IDF o MiniLM).
    """
    
    def __init__(
        self,
        encoder: Optional[IEncoder] = None,
        random_state: int = Config.RANDOM_STATE
    ):
        """
        Inicializa el procesador.
        
        Args:
            encoder: Encoder para texto (TF-IDF, MiniLM, etc.). Si None, usa TF-IDF por defecto.
            random_state: Semilla para reproducibilidad
        """
        self.random_state = random_state
        self.encoder = encoder
        self._is_encoder_fitted = False
        
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
        
        df_clean.replace({"NS": np.nan, "NA": np.nan}, inplace=True)

        if "priority" in df_clean.columns:
            df_clean["priority"] = pd.to_numeric(df_clean["priority"], errors="coerce")
            initial_rows = len(df_clean)
            df_clean = df_clean.dropna(subset=["priority"])
            removed = initial_rows - len(df_clean)
            logger.info(f"Se eliminaron {removed} filas sin priority")
            df_clean = df_clean[df_clean["priority"].isin([1, 2, 3])]
            logger.info(f"Después de filtrar: {len(df_clean)} filas válidas")
        
        if "text" in df_clean.columns:
            df_clean = df_clean[df_clean["text"].notna() & (df_clean["text"].str.strip() != "")]
            logger.info(f"Después de filtrar textos vacíos: {len(df_clean)} filas")
        
        logger.info(f"Limpieza completada: {len(df_clean)} filas")
        return df_clean
    
    def prepare_texts_and_labels(self, df: pd.DataFrame) -> Tuple[List[str], np.ndarray]:
        """
        Prepara textos de incidentes y etiquetas de prioridad.
        
        Args:
            df: DataFrame con datos limpios
            
        Returns:
            Tupla (lista de textos, array de etiquetas ajustadas a 0-index)
        """
        logger.info("Preparando textos y etiquetas")
        
        texts = df["text"].tolist()
        
        # Convertir prioridad 1,2,3 a índices 0,1,2 (para clasificación)
        labels = (df["priority"].astype(int).values - 1).astype(np.int32)
        
        logger.info(f"Textos preparados: {len(texts)}")
        logger.info(f"Distribución de prioridades (0-2):\n{pd.Series(labels).value_counts().sort_index()}")
        
        return texts, labels
    
    def encode_texts(
        self, 
        texts: List[str], 
        batch_size: int = 32,
        fit: bool = True
    ) -> np.ndarray:
        """
        Convierte textos a features usando el encoder inyectado.
        
        Soporta tanto TF-IDF (sparse/densa) como MiniLM (embeddings).
        
        Args:
            texts: Lista de textos
            batch_size: Tamaño de lote para procesamiento en lotes
            fit: Si True, prepara/entrena el encoder
            
        Returns:
            Matriz de features (n_texts, n_features)
        """
        if self.encoder is None:
            # Fallback a TF-IDF clásico
            logger.info("Usando TF-IDF como encoder por defecto")
            self._init_tfidf_encoder(fit)
        
        logger.info(f"Codificando {len(texts)} textos...")
        
        # Codificación con batch para no saturar RAM
        features = self.encoder.encode(texts, batch_size=batch_size)
        
        if fit:
            self._is_encoder_fitted = True
        
        logger.info(f"Features obtenidas: {features.shape}")
        return features
    
    def _init_tfidf_encoder(self, fit: bool):
        """Inicializa encoder TF-IDF si no hay encoder."""
        if self.encoder is None:
            self.encoder = TFIDFEncoder(max_features=Config.TF_IDF_MAX_FEATURES)
    
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
            X: Features (pueden ser densos o sparse)
            y: Labels (0-index: 0=P1, 1=P2, 2=P3)
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
        input_file: Path,
        encoder: Optional[IEncoder] = None,
        use_embeddings: bool = True
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, IEncoder]:
        """
        Pipeline completo de preprocesamiento.
        
        Args:
            input_file: Ruta al archivo CSV de entrada
            encoder: Encoder a usar. Si None, usa MiniLM si use_embeddings=True
            use_embeddings: Si True usa MiniLM, si False usa TF-IDF
            
        Returns:
            Datos divididos train/val/test + encoder usado
        """
        logger.info("=" * 50)
        logger.info("INICIANDO PIPELINE DE PREPROCESAMIENTO")
        logger.info("=" * 50)
        
        # Inicializar encoder si se proporciona
        if encoder is not None:
            self.encoder = encoder
        elif use_embeddings:
            self.encoder = MiniLMEncoder()
        
        # 1. Cargar datos
        df = self.load_data(input_file)
        
        # 2. Limpiar datos
        df_clean = self.clean_data(df)
        
        # 3. Generar textos y etiquetas
        texts, labels = self.prepare_texts_and_labels(df_clean)
        
        # 4. Codificar (con batch para ahorrar RAM)
        # MiniLM: batch_size=16 (8GB RAM)
        # TF-IDF: no necesita batch
        batch_size = 16 if use_embeddings else None
        X = self.encode_texts(texts, batch_size=batch_size, fit=True)
        
        # 5. Dividir datos
        X_train, X_val, X_test, y_train, y_val, y_test = self.split_data(X, labels)
        
        logger.info("=" * 50)
        logger.info("PIPELINE DE PREPROCESAMIENTO COMPLETADO")
        logger.info("=" * 50)
        
        return X_train, X_val, X_test, y_train, y_val, y_test, self.encoder
    
    def encode_single_text(self, text: str) -> np.ndarray:
        """
        Preprocesa un texto individual para predicción.
        
        Args:
            text: Texto del incidente
            
        Returns:
            Features (1, n_features)
        """
        if self.encoder is None:
            raise ValueError("Encoder no disponible")
        
        features = self.encoder.encode([text])
        return features
    
    def save_encoder(self, path: Path) -> None:
        """
        Guarda el encoder entrenado.
        
        Args:
            path: Directorio donde guardar
        """
        if self.encoder is None:
            raise ValueError("Encoder no disponible")
        
        path.mkdir(parents=True, exist_ok=True)
        self.encoder.save(path)
        logger.info(f"Encoder guardado en {path}")
    
    def load_encoder(self, path: Path) -> IEncoder:
        """
        Carga un encoder desde disco.
        
        Args:
            path: Directorio del encoder guardado
            
        Returns:
            Instancia de IEncoder
        """
        # Intenta cargar como MiniLM primero
        try:
            encoder = MiniLMEncoder.load(path)
            self.encoder = encoder
            logger.info("Encoder MiniLM cargado")
            return encoder
        except Exception:
            # Fallback a TF-IDF
            encoder = TFIDFEncoder.load(path)
            self.encoder = encoder
            logger.info("Encoder TF-IDF cargado")
            return encoder

