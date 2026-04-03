"""
Utilidades generales para el sistema de priorización.

Incluye:
- Funciones de logging
- Manejo de configuración
- Validación de datos
"""

import logging
import json
from pathlib import Path
from typing import Dict, Any, Optional

def setup_logger(name: str, log_file: Optional[str] = None) -> logging.Logger:
    """
    Configura un logger con formato estándar.
    
    Args:
        name: Nombre del logger
        log_file: Ruta opcional para archivo de log
        
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    
    # Handler en consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler en archivo si se especifica
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def load_config(config_path: Path) -> Dict[str, Any]:
    """
    Carga la configuración desde un archivo JSON.
    
    Args:
        config_path: Ruta al archivo de configuración
        
    Returns:
        Diccionario con configuración
    """
    if not config_path.exists():
        raise FileNotFoundError(f"Archivo de configuración no encontrado: {config_path}")
    
    with open(config_path, "r", encoding="utf-8") as f:
        config = json.load(f)
    
    return config


def save_config(config: Dict[str, Any], config_path: Path) -> None:
    """
    Guarda la configuración en un archivo JSON.
    
    Args:
        config: Diccionario de configuración
        config_path: Ruta donde guardar
    """
    config_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


def validate_priority(priority: Any) -> bool:
    """
    Valida que la prioridad sea válida (1-4).
    
    Args:
        priority: Valor de prioridad
        
    Returns:
        True si es válida, False si no
    """
    try:
        p = int(priority)
        return p in [1, 2, 3, 4]
    except (ValueError, TypeError):
        return False


class Config:
    """Configuración central del sistema."""
    
    # Rutas
    DATA_DIR = Path(__file__).parent.parent / "data"
    MODELS_DIR = Path(__file__).parent.parent / "models"
    
    # Modelo
    MODEL_NAME = "priority_classifier_v1"
    MODEL_FILE = MODELS_DIR / f"{MODEL_NAME}.pkl"
    VECTORIZER_FILE = MODELS_DIR / f"{MODEL_NAME}_vectorizer.pkl"
    
    # Parámetros
    TF_IDF_MAX_FEATURES = 1000
    TF_IDF_MIN_DF = 2
    TF_IDF_MAX_DF = 0.8
    
    RANDOM_STATE = 42
    TEST_SIZE = 0.2
    VALIDATION_SIZE = 0.1
    
    # Requerimientos
    MIN_ACCURACY = 0.70  # RNF-08: Precisión mínima 70%
    RESPONSE_TIME_SECONDS = 2  # RNF-01: < 2 segundos
    
    @classmethod
    def get_data_path(cls, filename: str) -> Path:
        """Obtiene la ruta completa de un archivo de datos."""
        return cls.DATA_DIR / filename
    
    @classmethod
    def ensure_dirs(cls) -> None:
        """Crea directorios necesarios si no existen."""
        cls.MODELS_DIR.mkdir(parents=True, exist_ok=True)
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)


logger = setup_logger(__name__)
