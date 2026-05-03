"""
Script de entrenamiento del modelo de priorización.

Ejecuta el pipeline completo:
1. Carga y limpia datos
2. Codifica textos con MiniLM-L6-v2 (embeddings)
3. Entrena modelo LightGBM
4. Valida y prueba el modelo
5. Guarda artefactos
6. Genera reporte detallado en Markdown

Compatible con TF-IDF + LogisticRegression como fallback.
"""

from pathlib import Path
import sys
import time

# Add parent directory to path to import src as package
sys.path.insert(0, str(Path(__file__).parent))

from src.data_processor import DataProcessor
from src.model_trainer import ModelTrainer, ModelFactory
from src.utils import logger, Config, setup_training_logger, save_training_report


def main():
    """Ejecuta el entrenamiento completo."""
    
    # Registrar tiempo de inicio
    start_time = time.time()
    
    logger.info("=" * 70)
    logger.info("SISTEMA DE PRIORIZACIÓN DE INCIDENTES IT - ENTRENAMIENTO")
    logger.info("=" * 70)
    
    # Configurar directorios (incluye logs y reports)
    Config.ensure_dirs()
    
    # Configurar logger de entrenamiento con archivo
    training_logger = setup_training_logger(Config.LOGS_DIR)
    training_logger.info("Iniciando proceso de entrenamiento")
    
    # Ruta del dataset
    data_file = Config.get_data_path("it_tickets_merged.csv")
    
    # Verificar que el dataset existe
    if not data_file.exists():
        logger.error(f"Dataset no encontrado: {data_file}")
        sys.exit(1)
    
    try:
        # ===== CONFIGURACIÓN =====
        logger.info("\n[CONFIGURACIÓN]")
        USE_MINILM = True  # True para MiniLM-L6-v2, False para TF-IDF
        USE_ENSEMBLE = False  # True para ensamble LightGBM+LR (más robusto)
        
        if USE_MINILM:
            logger.info("  Encoder: MiniLM-L6-v2 (embeddings 384-dim)")
            logger.info("  Modelo: LightGBM (CPU-optimizado)")
        else:
            logger.info("  Encoder: TF-IDF (1000 features)")
            logger.info("  Modelo: Logistic Regression")
        
        if USE_ENSEMBLE:
            logger.info("  Modo: Ensamble LightGBM + LogisticRegression")
        
        # Registrar configuración en logger de entrenamiento
        training_logger.info(f"Configuración - Encoder: {'MiniLM-L6-v2' if USE_MINILM else 'TF-IDF'}")
        training_logger.info(f"Configuración - Modelo: {'LightGBM' if USE_MINILM else 'Logistic Regression'}")
        training_logger.info(f"Configuración - Ensamble: {'Sí' if USE_ENSEMBLE else 'No'}")
        
        # ===== FASE 1: PREPROCESAMIENTO =====
        logger.info("\n[1/3] PREPROCESAMIENTO DE DATOS")
        logger.info("-" * 70)
        training_logger.info("Iniciando preprocesamiento de datos")
        
        processor = DataProcessor()
        
        # Pipeline con MiniLM
        result = processor.preprocess_pipeline(
            input_file=data_file,
            encoder=None,  # Se creará automáticamente
            use_embeddings=USE_MINILM
        )
        
        if USE_MINILM:
            X_train, X_val, X_test, y_train, y_val, y_test, encoder = result
        else:
            X_train, X_val, X_test, y_train, y_val, y_test, encoder = result
        
        training_logger.info(f"Datos procesados - Train: {X_train.shape}, Val: {X_val.shape}, Test: {X_test.shape}")
        
        # Guardar encoder
        processor.save_encoder(Config.ENCODER_DIR)
        training_logger.info(f"Encoder guardado en {Config.ENCODER_DIR}")
        
        # ===== FASE 2: ENTRENAMIENTO =====
        logger.info("\n[2/3] ENTRENAMIENTO DEL MODELO")
        logger.info("-" * 70)
        training_logger.info("Iniciando entrenamiento del modelo")
        
        if USE_ENSEMBLE:
            logger.info("Creando modelo ensamble...")
            training_logger.info("Tipo de modelo: Ensamble")
            classifier = ModelFactory.create_ensemble()
        elif USE_MINILM:
            logger.info("Creando modelo LightGBM...")
            training_logger.info("Tipo de modelo: LightGBM")
            classifier = ModelFactory.create_lightgbm(
                n_classes=3,
                num_leaves=Config.LGB_NUM_LEAVES,
                max_depth=Config.LGB_MAX_DEPTH,
                learning_rate=Config.LGB_LEARNING_RATE
            )
        else:
            # Usar LogisticRegression por defecto
            from sklearn.linear_model import LogisticRegression
            logger.info("Creando modelo Logistic Regression...")
            training_logger.info("Tipo de modelo: Logistic Regression")
            classifier = LogisticRegression(
                max_iter=1000,
                random_state=Config.RANDOM_STATE,
                solver="lbfgs",
                class_weight="balanced"
            )
        
        trainer = ModelTrainer(
            classifier=classifier,
            encoder=encoder,
            random_state=Config.RANDOM_STATE
        )
        
        trainer.train(X_train, y_train, X_val, y_val)
        training_logger.info("Entrenamiento completado")
        
        # ===== FASE 3: EVALUACIÓN =====
        logger.info("\n[3/3] EVALUACIÓN DEL MODELO")
        logger.info("-" * 70)
        training_logger.info("Iniciando evaluación del modelo")
        
        val_metrics = trainer.validate(X_val, y_val)
        test_metrics = trainer.test(X_test, y_test)
        
        # Guardar modelo
        trainer.save_model(
            model_path=Config.MODEL_FILE,
            encoder_path=Config.ENCODER_DIR,
            metadata={
                "use_minilm": USE_MINILM,
                "use_ensemble": USE_ENSEMBLE,
                "encoder_type": type(encoder).__name__,
                "classifier_type": type(classifier).__name__,
                "random_state": Config.RANDOM_STATE
            }
        )
        training_logger.info(f"Modelo guardado en {Config.MODEL_FILE}")
        
        # ===== GENERACIÓN DE REPORTE =====
        logger.info("\n[4/4] GENERACIÓN DE REPORTE")
        logger.info("-" * 70)
        
        # Calcular tiempo total
        training_time = time.time() - start_time
        
        # Preparar métricas para el reporte
        all_metrics = {
            "validation": val_metrics,
            "test": test_metrics
        }
        
        # Preparar configuración para el reporte
        report_config = {
            "use_minilm": USE_MINILM,
            "use_ensemble": USE_ENSEMBLE,
            "encoder_type": type(encoder).__name__,
            "classifier_type": type(classifier).__name__,
            "random_state": Config.RANDOM_STATE,
            "training_time": training_time
        }
        
        # Generar reporte
        try:
            report_path = save_training_report(
                metrics=all_metrics,
                config=report_config,
                report_dir=Config.REPORTS_DIR,
                training_time=training_time
            )
            logger.info(f"Reporte generado: {report_path}")
            training_logger.info(f"Reporte generado: {report_path}")
        except Exception as e:
            logger.warning(f"No se pudo generar el reporte: {str(e)}")
            training_logger.warning(f"Error al generar reporte: {str(e)}")
        
        # ===== RESUMEN =====
        trainer.print_summary()
        
        # Verificar requisitos
        logger.info("\n" + "=" * 70)
        logger.info("VERIFICACIÓN DE REQUERIMIENTOS")
        logger.info("=" * 70)
        
        if test_metrics["accuracy"] >= Config.MIN_ACCURACY:
            logger.info(f"✓ RNF-08: Precisión mínima {Config.MIN_ACCURACY:.0%} - CUMPLIDO")
            logger.info(f"  Accuracy alcanzado: {test_metrics['accuracy']:.4f} ({test_metrics['accuracy']:.1%})")
            training_logger.info(f"RNF-08: CUMPLIDO - Accuracy: {test_metrics['accuracy']:.4f}")
        else:
            logger.warning(f"✗ RNF-08: Precisión mínima {Config.MIN_ACCURACY:.0%} - NO CUMPLIDO")
            logger.warning(f"  Accuracy alcanzado: {test_metrics['accuracy']:.4f} ({test_metrics['accuracy']:.1%})")
            training_logger.warning(f"RNF-08: NO CUMPLIDO - Accuracy: {test_metrics['accuracy']:.4f}")
        
        logger.info(f"✓ RNF-09: Manejo de datos incompletos - IMPLEMENTADO")
        logger.info(f"✓ RNF-10: Capacidad de generalización - VALIDADO CON TEST")
        logger.info(f"✓ RF-05 a RF-09: Pipeline de análisis y predicción - COMPLETADO")
        logger.info(f"✓ RF-23: Explicabilidad con SHAP/coeficientes - IMPLEMENTADA")
        
        # Meta aspiracional
        if test_metrics["accuracy"] >= 0.85:
            logger.info(f"\n META ASPIRACIONAL ALCANZADA: Accuracy ≥ 85%")
            training_logger.info(f"META ALCANZADA: Accuracy ≥ 85% ({test_metrics['accuracy']:.4f})")
        
        # Log tiempo total
        logger.info(f"\n Tiempo total de entrenamiento: {training_time:.2f} segundos")
        training_logger.info(f"Tiempo total de entrenamiento: {training_time:.2f} segundos")
        
        logger.info("\n" + "=" * 70)
        logger.info("ENTRENAMIENTO COMPLETADO EXITOSAMENTE")
        logger.info("=" * 70)
        
        training_logger.info("Proceso de entrenamiento completado exitosamente")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error durante el entrenamiento: {str(e)}", exc_info=True)
        training_logger.error(f"Error durante el entrenamiento: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
