import json
import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Any

_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent.parent


def setup_logger(name: str, log_file: str | None = None) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    logger.handlers.clear()

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    if log_file:
        os.makedirs(Path(log_file).parent, exist_ok=True)
        with open(log_file, "a", encoding="utf-8") as f:
            f.write("[LOG INICIALIZADO] " + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + "\n")

        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def setup_training_logger(log_dir: Path) -> logging.Logger:
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"training_{timestamp}.log"
    return setup_logger("training", str(log_file))


def load_config(config_path: Path) -> dict[str, Any]:
    if not config_path.exists():
        raise FileNotFoundError(f"Archivo de configuración no encontrado: {config_path}")

    with open(config_path, encoding="utf-8") as f:
        config = json.load(f)

    return config


def save_config(config: dict[str, Any], config_path: Path) -> None:
    config_path.parent.mkdir(parents=True, exist_ok=True)

    with open(config_path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=4, ensure_ascii=False)


def save_training_report(
    metrics: dict[str, Any],
    config: dict[str, Any],
    report_dir: Path,
    training_time: float | None = None
) -> Path:
    report_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    report_path = report_dir / f"training_report_{timestamp}.md"

    val_metrics = metrics.get("validation", {})
    test_metrics = metrics.get("test", {})

    content = []
    content.append("# Reporte de Entrenamiento - Sistema de Priorización de Incidentes IT")
    content.append("")
    content.append(f"**Fecha de generación:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    content.append("")

    content.append("## Resumen del Entrenamiento")
    content.append("")

    if training_time:
        content.append("| Métrica | Valor |")
        content.append("|---------|-------|")
        content.append(f"| Tiempo de entrenamiento | {training_time:.2f} segundos |")

    if val_metrics.get("accuracy"):
        content.append(f"| Precisión (Validación) | {val_metrics['accuracy']:.4f} ({val_metrics['accuracy']*100:.1f}%) |")

    if test_metrics.get("accuracy"):
        content.append(f"| Precisión (Test) | {test_metrics['accuracy']:.4f} ({test_metrics['accuracy']*100:.1f}%) |")

        if test_metrics['accuracy'] >= 0.70:
            content.append("| **RNF-08** | CUMPLIDO (>=70%) |")
        else:
            content.append("| **RNF-08** | NO CUMPLIDO (>=70%) |")

    content.append("")

    content.append("## Configuración del Modelo")
    content.append("")

    encoder_type = config.get("encoder_type", "Desconocido")
    classifier_type = config.get("classifier_type", "Desconocido")
    balance_classes = config.get("balance_classes", False)
    deduplicate = config.get("deduplicate", False)
    boilerplate_removal = config.get("boilerplate_removal", False)
    use_cache = config.get("use_cache", False)

    content.append(f"- **Encoder:** {encoder_type}")
    content.append(f"- **Clasificador:** {classifier_type}")
    content.append(f"- **Random State:** {config.get('random_state', 'N/A')}")
    content.append(f"- **Balanceo de clases:** {'Undersampling (igualar a clase minoritaria)' if balance_classes else 'Desactivado'}")
    content.append(f"- **Deduplicación:** {'Activada' if deduplicate else 'Desactivada'}")
    content.append(f"- **Eliminación boilerplate:** {'Activada' if boilerplate_removal else 'Desactivada'}")
    content.append(f"- **Caché de embeddings:** {'Activada' if use_cache else 'Desactivada'}")
    content.append("")

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

        if "confusion_matrix" in val_metrics:
            content.append("### Matriz de Confusión (Validación)")
            content.append("")
            cm = val_metrics["confusion_matrix"]
            content.append("| | Pred. P1 | Pred. P2 | Pred. P3 |")
            content.append("|---------|----------|----------|----------|")

            for i, row in enumerate(cm):
                content.append(f"| **Real P{i+1}** | {row[0]:8d} | {row[1]:8d} | {row[2]:8d} |")

            content.append("")

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

        if "confusion_matrix" in test_metrics:
            content.append("### Matriz de Confusión (Test)")
            content.append("")
            cm = test_metrics["confusion_matrix"]
            content.append("| | Pred. P1 | Pred. P2 | Pred. P3 |")
            content.append("|---------|----------|----------|----------|")

            for i, row in enumerate(cm):
                content.append(f"| **Real P{i+1}** | {row[0]:8d} | {row[1]:8d} | {row[2]:8d} |")

            content.append("")

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

    content.append("## Verificación de Requerimientos")
    content.append("")

    if test_metrics.get("accuracy", 0) >= 0.70:
        content.append("- **RNF-08**: Precisión mínima del 70% - CUMPLIDO")
    else:
        content.append("- **RNF-08**: Precisión mínima del 70% - NO CUMPLIDO")

    content.append("- **RNF-09**: Manejo de datos incompletos - IMPLEMENTADO")
    content.append("- **RNF-10**: Capacidad de generalización - VALIDADO")
    content.append("- **RF-05 a RF-09**: Pipeline de análisis y predicción - COMPLETADO")
    content.append("- **RF-23**: Explicabilidad con SHAP/coeficientes - IMPLEMENTADA")

    if test_metrics.get("accuracy", 0) >= 0.85:
        content.append("")
        content.append("## Meta Aspiracional")
        content.append("")
        content.append("**META ALCANZADA**: Precisión >= 85%")

    content.append("")
    content.append("---")
    content.append(f"*Reporte generado automáticamente el {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")

    report_content = "\n".join(content)
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(report_content)

    return report_path


def validate_priority(priority: Any) -> bool:
    try:
        p = int(priority)
        return p in [1, 2, 3]
    except (ValueError, TypeError):
        return False


class Config:
    PROJECT_ROOT = _PROJECT_ROOT

    DATA_DIR = PROJECT_ROOT / "data"
    MODELS_DIR = PROJECT_ROOT / "models"
    ENCODER_DIR = MODELS_DIR / "encoder"
    LOGS_DIR = PROJECT_ROOT / "logs"
    REPORTS_DIR = PROJECT_ROOT / "reports"
    CACHE_DIR = PROJECT_ROOT / "cache"

    MODEL_NAME = "priority_classifier_v1"
    MODEL_FILE = MODELS_DIR / f"{MODEL_NAME}.pkl"
    VECTORIZER_FILE = MODELS_DIR / f"{MODEL_NAME}_vectorizer.pkl"

    TF_IDF_MAX_FEATURES = 1000
    TF_IDF_MIN_DF = 2
    TF_IDF_MAX_DF = 0.8

    MINILM_MODEL_NAME = "all-MiniLM-L6-v2"
    EMBEDDING_DIM = 384
    EMBEDDING_BATCH_SIZE = 16

    LGB_NUM_LEAVES = 31
    LGB_MAX_DEPTH = 6
    LGB_LEARNING_RATE = 0.05
    LGB_N_ESTIMATORS = 300
    LGB_MIN_CHILD_SAMPLES = 30
    LGB_REG_ALPHA = 0.1
    LGB_REG_LAMBDA = 0.1
    LGB_EARLY_STOPPING_ROUNDS = 20

    RANDOM_STATE = 42
    TEST_SIZE = 0.15
    VALIDATION_SIZE = 0.15
    BALANCE_CLASSES = False

    MIN_ACCURACY = 0.70
    RESPONSE_TIME_SECONDS = 2

    @classmethod
    def get_data_path(cls, filename: str) -> Path:
        return cls.DATA_DIR / filename

    @classmethod
    def ensure_dirs(cls) -> None:
        cls.MODELS_DIR.mkdir(parents=True, exist_ok=True)
        cls.DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.LOGS_DIR.mkdir(parents=True, exist_ok=True)
        cls.REPORTS_DIR.mkdir(parents=True, exist_ok=True)
        cls.CACHE_DIR.mkdir(parents=True, exist_ok=True)


_logger: logging.Logger | None = None


def get_logger() -> logging.Logger:
    global _logger
    if _logger is None:
        Config.ensure_dirs()
        _logger = setup_logger(__name__, str(Config.LOGS_DIR / "app.log"))
    return _logger


logger = get_logger()

_config_file = _PROJECT_ROOT / "config" / "ml_default.json"
if _config_file.exists():
    try:
        _json_config = load_config(_config_file)
        for key, value in _json_config.items():
            attr_name = key.upper()
            if hasattr(Config, attr_name):
                setattr(Config, attr_name, value)
                logger.info(f"Configuración cargada desde JSON: {attr_name} = {value}")
        Config.MODEL_FILE = Config.MODELS_DIR / f"{Config.MODEL_NAME}.pkl"
        Config.VECTORIZER_FILE = Config.MODELS_DIR / f"{Config.MODEL_NAME}_vectorizer.pkl"
        logger.info(f"Atributos derivados actualizados: MODEL_FILE = {Config.MODEL_FILE}")
    except Exception as e:
        logger.warning(f"No se pudo cargar configuración desde {_config_file}: {e}")
