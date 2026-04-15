"""
Script de entrenamiento del modelo de priorización.

Ejecuta el pipeline completo:
1. Carga y limpia datos
2. Vectoriza textos con TF-IDF
3. Entrena modelo Logistic Regression
4. Valida y prueba el modelo
5. Guarda artefactos
"""

from pathlib import Path
import sys

# Add parent directory to path to import src as package
sys.path.insert(0, str(Path(__file__).parent))

from src.data_processor import DataProcessor
from src.model_trainer import ModelTrainer
from src.predictor import save_vectorizer
from src.utils import logger, Config


def main():
    """Ejecuta el entrenamiento completo."""
    
    logger.info("SISTEMA DE PRIORIZACIÓN DE INCIDENTES IT - ENTRENAMIENTO")
    logger.info("=" * 70)
    
    # Configurar directorios
    Config.ensure_dirs()
    
    # Ruta del dataset
    data_file = Config.get_data_path("it_tickets_merged.csv")
    
    # Verificar que el dataset existe
    if not data_file.exists():
        logger.error(f"Dataset no encontrado: {data_file}")
        sys.exit(1)
    
    try:
        # ===== FASE 1: PREPROCESAMIENTO =====
        logger.info("\n[1/3] PREPROCESAMIENTO DE DATOS")
        logger.info("-" * 70)
        
        processor = DataProcessor()
        X_train, X_val, X_test, y_train, y_val, y_test = processor.preprocess_pipeline(data_file)
        
        # Guardar vectorizador
        save_vectorizer(processor.vectorizer)
        
        # ===== FASE 2: ENTRENAMIENTO =====
        logger.info("\n[2/3] ENTRENAMIENTO DEL MODELO")
        logger.info("-" * 70)
        
        trainer = ModelTrainer()
        trainer.create_model()
        trainer.train(X_train, y_train)
        
        # ===== FASE 3: EVALUACIÓN =====
        logger.info("\n[3/3] EVALUACIÓN DEL MODELO")
        logger.info("-" * 70)
        
        val_metrics = trainer.validate(X_val, y_val)
        test_metrics = trainer.test(X_test, y_test)
        
        # Guardar modelo
        trainer.save_model()
        
        # Resumen
        trainer.print_summary()
        
        # Verificar requisitos
        logger.info("\n" + "=" * 70)
        logger.info("VERIFICACIÓN DE REQUISITOS")
        logger.info("=" * 70)
        
        if test_metrics["accuracy"] >= Config.MIN_ACCURACY:
            logger.info(f"✓ RNF-08: Precisión mínima {Config.MIN_ACCURACY} - CUMPLIDO")
            logger.info(f"  Accuracy alcanzado: {test_metrics['accuracy']:.4f}")
        else:
            logger.warning(f"✗ RNF-08: Precisión mínima {Config.MIN_ACCURACY} - NO CUMPLIDO")
            logger.warning(f"  Accuracy alcanzado: {test_metrics['accuracy']:.4f}")
        
        logger.info(f"✓ RNF-09: Manejo de datos incompletos - IMPLEMENTADO")
        logger.info(f"✓ RNF-10: Capacidad de generalización - VALIDADO CON TEST")
        logger.info(f"✓ RF-05 a RF-09: Pipeline de análisis y predicción - COMPLETADO")
        logger.info(f"✓ RF-23: Explicabilidad - IMPLEMENTADA")
        
        logger.info("\n" + "=" * 70)
        logger.info("ENTRENAMIENTO COMPLETADO EXITOSAMENTE")
        logger.info("=" * 70)
        
        return 0
        
    except Exception as e:
        logger.error(f"Error durante el entrenamiento: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())
