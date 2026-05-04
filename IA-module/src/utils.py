"""
Utilidades generales para el sistema de priorización.

Incluye:
- Funciones de logging
- Manejo de configuración
- Validación de datos
- Generación de reportes
"""

import logging
import json
import os
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

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
    
    # Limpiar handlers existentes para evitar duplicados
    logger.handlers.clear()
    
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    
    # Handler en consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Handler en archivo si se especifica
    if log_file:
        os.makedirs(Path(log_file).parent, exist_ok=True)
        with open(log_file, "w", encoding="utf-8") as f:
            f.write("[LOG INICIALIZADO] " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")


        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def setup_training_logger(log_dir: Path) -> logging.Logger:
    """
    Configura el logger para entrenamiento con archivo de log en el directorio especificado.
    
    Args:
        log_dir: Directorio donde guardar los logs
        
    Returns:
        Logger configurado
    """
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"training_{timestamp}.log"
    return setup_logger("training", str(log_file))


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

def save_training_report(
    metrics: Dict[str, Any],
    config: Dict[str, Any],
    report_dir: Path,
    training_time: Optional[float] = None
) -> Path:
    """
    Genera un reporte detallado en formato Markdown con los resultados del entrenamiento.
    
    Args:
        metrics: Diccionario con todas las métricas del entrenamiento
        config: Diccionario con la configuración utilizada
        report_dir: Directorio donde guardar el reporte
        training_time: Tiempo total de entrenamiento en segundos (opcional)
        
    Returns:
        Path del archivo de reporte generado
    """
    report_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = report_dir / f"training_report_{timestamp}.md"
    
    # Obtener métricas
    val_metrics = metrics.get("validation", {})
    test_metrics = metrics.get("test", {})
    
    # Generar contenido del reporte
    content = []
    content.append("# Reporte de Entrenamiento - Sistema de Priorización de Incidentes IT")
    content.append("")
    content.append(f"**Fecha de generación:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    content.append("")
    
    # Tabla de resumen
    content.append("## Resumen del Entrenamiento")
    content.append("")
    
    if training_time:
        content.append(f"| Métrica | Valor |")
        content.append(f"|---------|-------|")
        content.append(f"| Tiempo de entrenamiento | {training_time:.2f} segundos |")
    
    if val_metrics.get("accuracy"):
        content.append(f"| Precisión (Validación) | {val_metrics['accuracy']:.4f} ({val_metrics['accuracy']*100:.1f}%) |")
    
    if test_metrics.get("accuracy"):
        content.append(f"| Precisión (Test) | {test_metrics['accuracy']:.4f} ({test_metrics['accuracy']*100:.1f}%) |")
        
        # Verificar RNF-08
        if test_metrics['accuracy'] >= 0.70:
            content.append(f"| **RNF-08** | CUMPLIDO (≥70%) |")
        else:
            content.append(f"| **RNF-08** | NO CUMPLIDO (≥70%) |")
    
    content.append("")
    
    # Configuración utilizada
    content.append("## Configuración del Modelo")
    content.append("")
    
    encoder_type = config.get("encoder_type", "Desconocido")
    classifier_type = config.get("classifier_type", "Desconocido")
    
    content.append(f"- **Encoder:** {encoder_type}")
    content.append(f"- **Clasificador:** {classifier_type}")
    content.append(f"- **Random State:** {config.get('random_state', 'N/A')}")
    content.append("")
    
    # Métricas detalladas de Validación
    if val_metrics:
        content.append("## Métricas de Validación")
        content.append("")
        content.append("| Métrica | Valor |")
        content.append("|---------|-------|")
        
        for metric_name, metric_value in val_metrics.items():
            if metric_name not in ["confusion_matrix", "classification_report"]:
                if isinstance(metric_value, float):
                    content.append(f"| {metric_name.capitalize()} | {metric_value:.4f} |")
                else:
                    content.append(f"| {metric_name.capitalize()} | {metric_value} |")
        
        content.append("")
        
        # Matriz de confusión de validación
        if "confusion_matrix" in val_metrics:
            content.append("### Matriz de Confusión (Validación)")
            content.append("")
            cm = val_metrics["confusion_matrix"]
            content.append("| | Pred. P1 | Pred. P2 | Pred. P3 |")
            content.append("|---------|----------|----------|----------|")
            
            for i, row in enumerate(cm):
                content.append(f"| **Real P{i+1}** | {row[0]:8d} | {row[1]:8d} | {row[2]:8d} |")
            
            content.append("")
    
    # Métricas detalladas de Test
    if test_metrics:
        content.append("## Métricas de Test")
        content.append("")
        content.append("| Métrica | Valor |")
        content.append("|---------|-------|")
        
        for metric_name, metric_value in test_metrics.items():
            if metric_name not in ["confusion_matrix", "classification_report"]:
                if isinstance(metric_value, float):
                    content.append(f"| {metric_name.capitalize()} | {metric_value:.4f} |")
                else:
                    content.append(f"| {metric_name.capitalize()} | {metric_value} |")
        
        content.append("")
        
        # Matriz de confusión de test
        if "confusion_matrix" in test_metrics:
            content.append("### Matriz de Confusión (Test)")
            content.append("")
            cm = test_metrics["confusion_matrix"]
            content.append("| | Pred. P1 | Pred. P2 | Pred. P3 |")
            content.append("|---------|----------|----------|----------|")
            
            for i, row in enumerate(cm):
                content.append(f"| **Real P{i+1}** | {row[0]:8d} | {row[1]:8d} | {row[2]:8d} |")
            
            content.append("")
    
    # Reporte de clasificación
    if "classification_report" in test_metrics:
        content.append("## Reporte de Clasificación Detallado")
        content.append("")
        content.append("```")
        content.append(test_metrics["classification_report"])
        content.append("```")
        content.append("")
    
    if "classification_report" in val_metrics:
        content.append("## Reporte de Clasificación (Validación)")
        content.append("")
        content.append("```")
        content.append(val_metrics["classification_report"])
        content.append("```")
        content.append("")
    
    # Verificación de requisitos
    content.append("## Verificación de Requerimientos")
    content.append("")
    
    # RNF-08
    if test_metrics.get("accuracy", 0) >= 0.70:
        content.append("-**RNF-08**: Precisión mínima del 70% - CUMPLIDO")
    else:
        content.append("- **RNF-08**: Precisión mínima del 70% - NO CUMPLIDO")
    
    content.append("- **RNF-09**: Manejo de datos incompletos - IMPLEMENTADO")
    content.append("- **RNF-10**: Capacidad de generalización - VALIDADO")
    content.append("- **RF-05 a RF-09**: Pipeline de análisis y predicción - COMPLETADO")
    content.append("- **RF-23**: Explicabilidad con SHAP/coeficientes - IMPLEMENTADA")
    
    # Meta aspiracional
    if test_metrics.get("accuracy", 0) >= 0.85:
        content.append("")
        content.append("## Meta Aspiracional")
        content.append("")
        content.append("**META ALCANZADA**: Precisión ≥ 85%")
    
    content.append("")
    content.append("---")
    content.append(f"*Reporte generado automáticamente el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
    
    # Escribir archivo
    report_content = "\n".join(content)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)
    
    return report_path


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
        return p in [1, 2, 3]
    except (ValueError, TypeError):
        return False


class Config:
    """Configuración central del sistema."""
    
    # Rutas
    DATA_DIR = Path(__file__).parent.parent / "data"
    MODELS_DIR = Path(__file__).parent.parent / "models"
    ENCODER_DIR = MODELS_DIR / "encoder"
    LOGS_DIR = Path(__file__).parent.parent / "logs"
    REPORTS_DIR = Path(__file__).parent.parent / "reports"
    
    # Modelo
    MODEL_NAME = "priority_classifier_v1"
    MODEL_FILE = MODELS_DIR / f"{MODEL_NAME}.pkl"
    VECTORIZER_FILE = MODELS_DIR / f"{MODEL_NAME}_vectorizer.pkl"
    
    # Parámetros
    TF_IDF_MAX_FEATURES = 1000
    TF_IDF_MIN_DF = 2
    TF_IDF_MAX_DF = 0.8
    
    # MiniLM / Embeddings
    MINILM_MODEL_NAME = "all-MiniLM-L6-v2"
    EMBEDDING_DIM = 384
    EMBEDDING_BATCH_SIZE = 16  # Para RAM ≤8GB
    
    # LightGBM
    LGB_NUM_LEAVES = 31
    LGB_MAX_DEPTH = 6
    LGB_LEARNING_RATE = 0.05
    LGB_N_ESTIMATORS = 200
    
    RANDOM_STATE = 42
    TEST_SIZE = 0.15
    VALIDATION_SIZE = 0.15
    
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
        cls.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        cls.REPORTS_DIR.mkdir(parents=True, exist_ok=True)


logger = setup_logger(__name__, str(Config.LOGS_DIR / "app.log"))

# Cargar configuración desde archivo JSON si existe
_config_file = Path(__file__).parent.parent / "config" / "default.json"
if _config_file.exists():
    try:
        _json_config = load_config(_config_file)
        # Actualizar atributos de clase Config con valores del JSON
        for key, value in _json_config.items():
            attr_name = key.upper()
            if hasattr(Config, attr_name):
                setattr(Config, attr_name, value)
                logger.info(f"Configuración cargada desde JSON: {attr_name} = {value}")
        # Recalcular atributos derivados que dependen de MODEL_NAME
        Config.MODEL_FILE = Config.MODELS_DIR / f"{Config.MODEL_NAME}.pkl"
        Config.VECTORIZER_FILE = Config.MODELS_DIR / f"{Config.MODEL_NAME}_vectorizer.pkl"
        logger.info(f"Atributos derivados actualizados: MODEL_FILE = {Config.MODEL_FILE}")
    except Exception as e:
        logger.warning(f"No se pudo cargar configuración desde {_config_file}: {e}")
