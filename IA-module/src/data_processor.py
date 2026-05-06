"""
Procesamiento y preparación de datos para el modelo de priorización.

Incluye:
- Carga de datos
- Limpieza y validación
- Eliminación de boilerplate y deduplicación
- Caché de embeddings para evitar recodificación
- Extracción de meta-features (department, type, tags)
- Generación de características (TF-IDF o embeddings)
- División train/test

Principio DIP: DataProcessor depende de abstracciones (IEncoder), no de implementaciones concretas.
"""

from pathlib import Path
from typing import Tuple, List, Optional
import re
import json
import hashlib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder

from .encoders import MiniLMEncoder, TFIDFEncoder
from .interfaces import IEncoder
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
        self.meta_feature_columns: List[str] = []
        self.meta_encoders: dict = {}
        
    def _compute_data_hash(self, texts: List[str], labels: np.ndarray) -> str:
        """
        Calcula un hash determinístico de los textos y etiquetas procesados.
        Se usa para identificar si ya existe un caché de embeddings válido.
        
        Args:
            texts: Lista de textos procesados
            labels: Array de etiquetas
            
        Returns:
            Hash SHA256 hexadecimal
        """
        hasher = hashlib.sha256()
        hasher.update(f"n={len(texts)}".encode())
        hasher.update(f"rs={self.random_state}".encode())
        
        sample_texts = texts[:500] + texts[-500:] if len(texts) > 1000 else texts
        for t in sample_texts:
            hasher.update(t.encode("utf-8"))
        
        hasher.update(" ".join(str(l) for l in labels[:500]).encode())
        hasher.update(" ".join(str(l) for l in labels[-500:]).encode())
        return hasher.hexdigest()[:16]
    
    def _get_cache_dir(self) -> Path:
        """Obtiene el directorio de caché."""
        cache_dir = Path(__file__).parent.parent / "cache"
        cache_dir.mkdir(parents=True, exist_ok=True)
        return cache_dir
    
    def _get_cache_path(self, data_hash: str, encoder_type: str) -> Tuple[Path, Path]:
        """
        Obtiene las rutas de los archivos de caché.
        
        Returns:
            Tupla (path de features, path de labels)
        """
        cache_dir = self._get_cache_dir()
        features_path = cache_dir / f"X_{encoder_type}_{data_hash}.npy"
        labels_path = cache_dir / f"y_{data_hash}.npy"
        return features_path, labels_path
    
    def load_cache(self, data_hash: str, encoder_type: str) -> Optional[Tuple[np.ndarray, np.ndarray]]:
        """
        Intenta cargar embeddings desde caché.
        
        Args:
            data_hash: Hash de los datos procesados
            encoder_type: Tipo de encoder usado ("MiniLM" o "TFIDF")
            
        Returns:
            Tupla (X, y) si existe caché, None si no
        """
        features_path, labels_path = self._get_cache_path(data_hash, encoder_type)
        
        if features_path.exists() and labels_path.exists():
            logger.info("=" * 50)
            logger.info("CACHÉ DE EMBEDDINGS ENCONTRADA")
            logger.info(f"  Hash: {data_hash}")
            logger.info(f"  Encoder: {encoder_type}")
            logger.info(f"  Cargando X desde {features_path.name}")
            logger.info(f"  Cargando y desde {labels_path.name}")
            
            X = np.load(features_path)
            y = np.load(labels_path)
            
            logger.info(f"  X shape: {X.shape}, y shape: {y.shape}")
            logger.info("=" * 50)
            return X, y
        
        return None
    
    def save_cache(self, data_hash: str, encoder_type: str, X: np.ndarray, y: np.ndarray) -> None:
        """
        Guarda embeddings en caché para reutilizar.
        
        Args:
            data_hash: Hash de los datos procesados
            encoder_type: Tipo de encoder usado
            X: Features codificadas
            y: Etiquetas
        """
        features_path, labels_path = self._get_cache_path(data_hash, encoder_type)
        
        np.save(features_path, X)
        np.save(labels_path, y)
        
        logger.info(f"Caché guardada: {features_path.name} ({X.shape})")
    
    def invalidate_cache(self, data_hash: str = None) -> None:
        """
        Invalida archivos de caché. Si no se pasa hash, invalida todo el caché.
        
        Args:
            data_hash: Hash específico a invalidar, o None para borrar todo
        """
        cache_dir = self._get_cache_dir()
        if not cache_dir.exists():
            return
        
        if data_hash:
            for f in cache_dir.glob(f"*{data_hash}*.npy"):
                f.unlink()
                logger.info(f"Caché invalidado: {f.name}")
        else:
            for f in cache_dir.glob("*.npy"):
                f.unlink()
            logger.info("Todo el caché ha sido invalidado")
    
    def load_data(self, filepath: Path) -> pd.DataFrame:
        """Carga datos desde CSV."""
        if not filepath.exists():
            raise FileNotFoundError(f"No se encontró el archivo: {filepath}")
        
        logger.info(f"Cargando datos desde {filepath}")
        df = pd.read_csv(filepath)
        logger.info(f"Datos cargados: {df.shape[0]} filas, {df.shape[1]} columnas")
        
        return df
    
    def remove_boilerplate(self, text: str) -> str:
        """Elimina frases boilerplate generadas por LLM del texto."""
        cleaned = text
        for pattern in LLM_BOILERPLATE_PATTERNS:
            cleaned = re.sub(pattern, "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"\s+", " ", cleaned).strip()
        return cleaned
    
    def clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Limpia y valida los datos. Elimina boilerplate LLM."""
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
            
            logger.info("Eliminando boilerplate LLM de los textos...")
            df_clean["text"] = df_clean["text"].apply(self.remove_boilerplate)
            df_clean = df_clean[df_clean["text"].str.strip() != ""]
            logger.info(f"Después de eliminar boilerplate: {len(df_clean)} filas")
        
        logger.info(f"Limpieza completada: {len(df_clean)} filas")
        return df_clean
    
    def deduplicate_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """Elimina textos duplicados exactos."""
        initial_count = len(df)
        
        df_dedup = df.drop_duplicates(subset=["text"], keep="first")
        removed = initial_count - len(df_dedup)
        
        logger.info("=" * 50)
        logger.info("DEDUPLICACIÓN DE TEXTOS")
        logger.info(f"Textos originales: {initial_count}")
        logger.info(f"Duplicados eliminados: {removed}")
        logger.info(f"Textos únicos: {len(df_dedup)}")
        logger.info("=" * 50)
        
        return df_dedup
    
    def extract_meta_features(self, df: pd.DataFrame) -> np.ndarray:
        """Extrae y codifica meta-features categóricas (department, type, tags)."""
        meta_features = []
        self.meta_encoders = {}
        self.meta_feature_columns = []
        
        if "department" in df.columns:
            logger.info("Codificando meta-feature: department")
            le = LabelEncoder()
            le.fit_transform(df["department"].fillna("Unknown"))
            self.meta_encoders["department"] = le
            
            dept_ohe = pd.get_dummies(df["department"].fillna("Unknown"), prefix="dept")
            meta_features.append(dept_ohe)
            self.meta_feature_columns.extend(dept_ohe.columns.tolist())
            logger.info(f"  Department: {len(dept_ohe.columns)} categorías")
        
        if "type" in df.columns:
            logger.info("Codificando meta-feature: type")
            le = LabelEncoder()
            le.fit_transform(df["type"].fillna("Unknown"))
            self.meta_encoders["type"] = le
            
            type_ohe = pd.get_dummies(df["type"].fillna("Unknown"), prefix="type")
            meta_features.append(type_ohe)
            self.meta_feature_columns.extend(type_ohe.columns.tolist())
            logger.info(f"  Type: {len(type_ohe.columns)} categorías")
        
        if "tags" in df.columns:
            logger.info("Codificando meta-feature: tags")
            tags_series = df["tags"].fillna("")
            all_tags = set()
            for tags_str in tags_series:
                if tags_str:
                    tags = [t.strip() for t in str(tags_str).split(",")]
                    all_tags.update(tags)
            
            all_tags = sorted([t for t in all_tags if t])
            logger.info(f"  Tags únicos: {len(all_tags)}")
            
            tag_cols = {f"tag_{t}": [] for t in all_tags}
            for tags_str in tags_series:
                row_tags = set()
                if tags_str:
                    row_tags = set(t.strip() for t in str(tags_str).split(",") if t.strip())
                for t in all_tags:
                    tag_cols[f"tag_{t}"].append(1 if t in row_tags else 0)
            
            tags_df = pd.DataFrame(tag_cols)
            meta_features.append(tags_df)
            self.meta_feature_columns.extend(tags_df.columns.tolist())
            logger.info(f"  Tags codificados: {len(tags_df.columns)}")
        
        if meta_features:
            meta_array = pd.concat(meta_features, axis=1).astype(np.float32).values
            logger.info(f"Total meta-features: {meta_array.shape[1]}")
            return meta_array
        else:
            logger.info("No se encontraron columnas para meta-features")
            return np.empty((len(df), 0), dtype=np.float32)
    
    def prepare_texts_and_labels(self, df: pd.DataFrame) -> Tuple[List[str], np.ndarray]:
        """Prepara textos de incidentes y etiquetas de prioridad."""
        logger.info("Preparando textos y etiquetas")
        
        texts = df["text"].tolist()
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
        """Convierte textos a features usando el encoder inyectado."""
        if self.encoder is None:
            logger.info("Usando TF-IDF como encoder por defecto")
            self._init_tfidf_encoder(fit)
        
        logger.info(f"Codificando {len(texts)} textos...")
        features = self.encoder.encode(texts, batch_size=batch_size)
        
        if fit:
            self._is_encoder_fitted = True
        
        logger.info(f"Features obtenidas: {features.shape}")
        return features
    
    def _init_tfidf_encoder(self, fit: bool):
        """Inicializa encoder TF-IDF si no hay encoder."""
        if self.encoder is None:
            self.encoder = TFIDFEncoder(max_features=Config.TF_IDF_MAX_FEATURES)
    
    def balance_classes(
        self,
        texts: List[str],
        labels: np.ndarray,
        random_state: Optional[int] = None
    ) -> Tuple[List[str], np.ndarray]:
        """Realiza undersampling para igualar todas las clases a la que tiene menos datos."""
        if random_state is None:
            random_state = self.random_state
            
        rng = np.random.RandomState(random_state)
        
        logger.info("=" * 50)
        logger.info("BALANCEO DE CLASES (UNDERSAMPLING)")
        logger.info("=" * 50)
        
        label_counts = pd.Series(labels).value_counts().sort_index()
        logger.info(f"Distribución original de clases:\n{label_counts}")
        
        min_count = label_counts.min()
        logger.info(f"Clase minoritaria tiene {min_count} muestras")
        logger.info(f"Se reducirán todas las clases a {min_count} muestras")
        
        balanced_texts = []
        balanced_labels = []
        
        for label in sorted(np.unique(labels)):
            mask = labels == label
            texts_for_label = [texts[i] for i in range(len(labels)) if mask[i]]
            
            if len(texts_for_label) > min_count:
                indices = rng.choice(len(texts_for_label), size=min_count, replace=False)
                sampled_texts = [texts_for_label[i] for i in indices]
                logger.info(f"  Clase {label}: {len(texts_for_label)} -> {min_count} muestras")
            else:
                sampled_texts = texts_for_label
                logger.info(f"  Clase {label}: {len(texts_for_label)} muestras (sin cambio)")
            
            balanced_texts.extend(sampled_texts)
            balanced_labels.extend([label] * len(sampled_texts))
        
        balanced_texts, balanced_labels = self._shuffle_data(
            balanced_texts, np.array(balanced_labels), rng
        )
        
        logger.info(f"Distribución después del balanceo:")
        logger.info(f"{pd.Series(balanced_labels).value_counts().sort_index()}")
        logger.info(f"Total de muestras: {len(balanced_texts)}")
        logger.info("=" * 50)
        
        return balanced_texts, balanced_labels
    
    def _shuffle_data(
        self,
        texts: List[str],
        labels: np.ndarray,
        rng: np.random.RandomState
    ) -> Tuple[List[str], np.ndarray]:
        """Mezcla los datos manteniendo la correspondencia texto-label."""
        indices = np.arange(len(texts))
        rng.shuffle(indices)
        
        shuffled_texts = [texts[i] for i in indices]
        shuffled_labels = labels[indices]
        
        return shuffled_texts, shuffled_labels
    
    def split_data(
        self,
        X: np.ndarray,
        y: np.ndarray,
        test_size: float = Config.TEST_SIZE,
        validation_size: float = Config.VALIDATION_SIZE
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Divide datos en train/validation/test."""
        logger.info("Dividiendo datos en train/validation/test")
        
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y,
            test_size=test_size,
            random_state=self.random_state,
            stratify=y
        )
        
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
        use_embeddings: bool = True,
        balance_classes: bool = False,
        use_meta_features: bool = False,
        deduplicate: bool = True,
        use_cache: bool = True
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, IEncoder]:
        """
        Pipeline completo de preprocesamiento.
        
        Args:
            input_file: Ruta al archivo CSV de entrada
            encoder: Encoder a usar. Si None, usa MiniLM si use_embeddings=True
            use_embeddings: Si True usa MiniLM, si False usa TF-IDF
            balance_classes: Si True, aplica undersampling para igualar clases
            use_meta_features: Si True, agrega department/type/tags como features
            deduplicate: Si True, elimina textos duplicados antes del split
            use_cache: Si True, usa caché de embeddings si está disponible
            
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
        
        encoder_type = type(self.encoder).__name__.replace("Encoder", "")
        
        # 1. Cargar datos
        df = self.load_data(input_file)
        
        # 2. Limpiar datos (incluye eliminación de boilerplate)
        df_clean = self.clean_data(df)
        
        # 3. Deduplicar
        if deduplicate:
            df_clean = self.deduplicate_data(df_clean)
        
        # 4. Extraer meta-features del DataFrame
        meta_features = None
        if use_meta_features:
            meta_features = self.extract_meta_features(df_clean)
        
        # 5. Generar textos y etiquetas
        texts, labels = self.prepare_texts_and_labels(df_clean)
        
        # 6. Balancear clases (opcional)
        if balance_classes:
            texts, labels = self.balance_classes(texts, labels)
        
        # 7. Intentar cargar desde caché si no hay balanceo (el balanceo cambia los datos)
        if use_cache and not balance_classes and use_embeddings:
            data_hash = self._compute_data_hash(texts, labels)
            cached = self.load_cache(data_hash, encoder_type)
            
            if cached is not None:
                X_text, _ = cached
                logger.info("CACHÉ HIT: Skipping encoding (loaded from cache)")
                if use_meta_features and meta_features is not None and meta_features.shape[1] > 0:
                    logger.info(f"Concatenando meta-features a embeddings cacheados...")
                    X = np.hstack([X_text, meta_features.astype(np.float32)])
                    logger.info(f"  Features combinadas: {X.shape[1]}")
                else:
                    X = X_text
                
                X_train, X_val, X_test, y_train, y_val, y_test = self.split_data(X, labels)
                
                logger.info("=" * 50)
                logger.info("PIPELINE DE PREPROCESAMIENTO COMPLETADO (CACHE HIT)")
                logger.info("=" * 50)
                
                return X_train, X_val, X_test, y_train, y_val, y_test, self.encoder
            else:
                logger.info("CACHE MISS: Encoding required")
        
        # 8. Codificar textos (solo si no hay caché o no aplica)
        batch_size = 16 if use_embeddings else None
        X_text = self.encode_texts(texts, batch_size=batch_size, fit=True)
        
        # 9. Guardar en caché si aplica
        if use_cache and not balance_classes and use_embeddings:
            data_hash = self._compute_data_hash(texts, labels)
            self.save_cache(data_hash, encoder_type, X_text, labels)
        
        # 10. Concatenar meta-features si están disponibles
        if meta_features is not None and meta_features.shape[1] > 0 and not balance_classes:
            logger.info(f"Concatenando meta-features a embeddings de texto...")
            logger.info(f"  Text features: {X_text.shape[1]}, Meta-features: {meta_features.shape[1]}")
            X = np.hstack([X_text, meta_features.astype(np.float32)])
            logger.info(f"  Features combinadas: {X.shape[1]}")
        else:
            if balance_classes and use_meta_features:
                logger.info("Meta-features desactivadas porque balance_classes=True")
            X = X_text
        
        # 11. Dividir datos
        X_train, X_val, X_test, y_train, y_val, y_test = self.split_data(X, labels)
        
        logger.info("=" * 50)
        logger.info("PIPELINE DE PREPROCESAMIENTO COMPLETADO")
        logger.info("=" * 50)
        
        return X_train, X_val, X_test, y_train, y_val, y_test, self.encoder
    
    def encode_single_text(self, text: str) -> np.ndarray:
        """Preprocesa un texto individual para predicción."""
        if self.encoder is None:
            raise ValueError("Encoder no disponible")
        
        features = self.encoder.encode([text])
        return features
    
    def save_encoder(self, path: Path) -> None:
        """Guarda el encoder entrenado."""
        if self.encoder is None:
            raise ValueError("Encoder no disponible")
        
        path.mkdir(parents=True, exist_ok=True)
        self.encoder.save(path)
        logger.info(f"Encoder guardado en {path}")
    
    def load_encoder(self, path: Path) -> IEncoder:
        """Carga un encoder desde disco."""
        try:
            encoder = MiniLMEncoder.load(path)
            self.encoder = encoder
            logger.info("Encoder MiniLM cargado")
            return encoder
        except Exception:
            encoder = TFIDFEncoder.load(path)
            self.encoder = encoder
            logger.info("Encoder TF-IDF cargado")
            return encoder
