"""
Ejemplos de uso del sistema de priorización de incidentes.

Demostra:
1. Entrenamiento del modelo
2. Predicción individual
3. Predicción con explicación
4. Predicción en lotes
"""

from pathlib import Path
import sys

# Add parent directory to path to import src as package
sys.path.insert(0, str(Path(__file__).parent))

from src.data_processor import DataProcessor
from src.model_trainer import ModelTrainer
from src.predictor import PriorityPredictor, save_vectorizer
from src.utils import Config, logger


def example_1_train_model():
    """Ejemplo 1: Entrenar el modelo."""
    print("\n" + "=" * 70)
    print("EJEMPLO 1: ENTRENAR EL MODELO")
    print("=" * 70)
    
    Config.ensure_dirs()
    data_file = Config.get_data_path("ITSM_data.csv")
    
    if not data_file.exists():
        print(f"⚠ Dataset no encontrado: {data_file}")
        print("Por favor asegúrese de que ITSM_data.csv existe en IA-module/data/")
        return False
    
    try:
        print(f"\n1. Cargando y limpiando datos desde {data_file.name}...")
        processor = DataProcessor()
        X_train, X_val, X_test, y_train, y_val, y_test = processor.preprocess_pipeline(data_file)
        
        print(f"✓ Datos preparados:")
        print(f"  - Train: {X_train.shape[0]} muestras")
        print(f"  - Validation: {X_val.shape[0]} muestras")
        print(f"  - Test: {X_test.shape[0]} muestras")
        print(f"  - Features: {X_train.shape[1]}")
        
        print(f"\n2. Entrenando modelo Logistic Regression...")
        trainer = ModelTrainer()
        trainer.create_model()
        trainer.train(X_train, y_train)
        print("✓ Modelo entrenado")
        
        print(f"\n3. Validando modelo...")
        val_metrics = trainer.validate(X_val, y_val)
        
        print(f"\n4. Evaluando en test set...")
        test_metrics = trainer.test(X_test, y_test)
        
        print(f"\n5. Guardando artefactos...")
        save_vectorizer(processor.vectorizer)
        trainer.save_model()
        print("✓ Modelo y vectorizador guardados")
        
        print(f"\n✓ ENTRENAMIENTO COMPLETADO EXITOSAMENTE")
        print(f"\nMétricas finales:")
        print(f"  Accuracy: {test_metrics['accuracy']:.4f}")
        print(f"  Precision: {test_metrics['precision']:.4f}")
        print(f"  Recall: {test_metrics['recall']:.4f}")
        print(f"  F1-Score: {test_metrics['f1']:.4f}")
        
        reach_goal = test_metrics['accuracy'] >= Config.MIN_ACCURACY
        status = "✓ CUMPLIDO" if reach_goal else "✗ NO CUMPLIDO"
        print(f"\n  Requisito RNF-08 (Precisión ≥ {Config.MIN_ACCURACY}): {status}")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def example_2_predict_single():
    """Ejemplo 2: Predicción individual."""
    print("\n" + "=" * 70)
    print("EJEMPLO 2: PREDICCIÓN INDIVIDUAL")
    print("=" * 70)
    
    Config.ensure_dirs()
    
    try:
        print("\nCargando modelo...")
        predictor = PriorityPredictor()
        print("✓ Modelo cargado")
        
        text = "Critical hardware failure in production server affecting all users"
        
        print(f"\nIncidente: {text}")
        print(f"\nRealizando predicción...")
        
        priority, confidence = predictor.predict_with_confidence(text)
        
        print(f"\n✓ Predicción completada:")
        print(f"  Prioridad: {predictor.PRIORITY_LABELS[priority]}")
        print(f"  Confianza: {confidence*100:.1f}%")
        
        return True
        
    except FileNotFoundError:
        print("✗ Modelo no encontrado. Ejecute ejemplo_1_train_model() primero.")
        return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def example_3_predict_with_explanation():
    """Ejemplo 3: Predicción con explicación."""
    print("\n" + "=" * 70)
    print("EJEMPLO 3: PREDICCIÓN CON EXPLICACIÓN (RF-23)")
    print("=" * 70)
    
    Config.ensure_dirs()
    
    try:
        print("\nCargando modelo...")
        predictor = PriorityPredictor()
        
        test_cases = [
            ("Critical database corruption requiring immediate intervention", "Caso 1: Crítico"),
            ("Minor user interface layout issue low priority", "Caso 2: Bajo"),
            ("High impact network connectivity outage affecting multiple departments", "Caso 3: Alto"),
        ]
        
        for text, title in test_cases:
            print(f"\n{'-' * 70}")
            print(f"{title}")
            print(f"{'-' * 70}")
            print(f"Incidente: {text}\n")
            
            explanation = predictor.explain_prediction(text, top_k=3)
            
            print(f"Prioridad Predicha: {explanation['priority_label']}")
            print(f"Confianza: {explanation['confidence']*100:.1f}%\n")
            
            print("Palabras clave contribuyentes:")
            for feat in explanation['contributing_features']:
                direction = "🔺" if feat['importance'] == 'positive' else "🔻"
                print(f"  {direction} {feat['feature']:20} (score: {feat['score']:+.4f})")
            
            print(f"\nRazonamiento: {explanation['reasoning']}")
        
        return True
        
    except FileNotFoundError:
        print("✗ Modelo no encontrado. Ejecute ejemplo_1_train_model() primero.")
        return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def example_4_batch_predict():
    """Ejemplo 4: Predicción en lotes."""
    print("\n" + "=" * 70)
    print("EJEMPLO 4: PREDICCIÓN EN LOTES")
    print("=" * 70)
    
    Config.ensure_dirs()
    
    try:
        print("\nCargando modelo...")
        predictor = PriorityPredictor()
        
        texts = [
            "Hardware failure critical impact",
            "Minor bug software application",
            "Network outage high impact urgent",
            "Configuration issue low priority",
            "Database corruption critical emergency",
        ]
        
        print(f"\nPrediciendo {len(texts)} incidentes en lote...\n")
        
        results = predictor.batch_predict_with_confidence(texts)
        
        # Mostrar resultados en tabla
        print(f"{'#':<3} {'Prioridad':<12} {'Confianza':<12} {'Texto':<50}")
        print("-" * 77)
        
        for i, (priority, confidence, text) in enumerate(zip(
            [r[0] for r in results],
            [r[1] for r in results],
            texts
        ), 1):
            priority_label = predictor.PRIORITY_LABELS[priority]
            text_short = text[:47] + "..." if len(text) > 50 else text
            print(f"{i:<3} {priority_label:<12} {confidence*100:>10.1f}% {text_short:<50}")
        
        print("\n✓ Predicción en lotes completada")
        
        return True
        
    except FileNotFoundError:
        print("✗ Modelo no encontrado. Ejecute ejemplo_1_train_model() primero.")
        return False
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        return False


def main():
    """Ejecuta los ejemplos."""
    
    print("\n" + "=" * 70)
    print("SISTEMA DE PRIORIZACIÓN DE INCIDENTES IT - EJEMPLOS")
    print("=" * 70)
    
    print("\nEste script demuestra el uso del sistema:")
    print("1. Entrenamiento del modelo")
    print("2. Predicción individual")
    print("3. Predicción con explicación")
    print("4. Predicción en lotes")
    
    # Ejecutar ejemplos
    success = True
    
    if not example_1_train_model():
        print("\n⚠ No se puede continuar sin modelo entrenado")
        return 1
    
    if not example_2_predict_single():
        success = False
    
    if not example_3_predict_with_explanation():
        success = False
    
    if not example_4_batch_predict():
        success = False
    
    print("\n" + "=" * 70)
    if success:
        print("✓ TODOS LOS EJEMPLOS EJECUTADOS EXITOSAMENTE")
    else:
        print("⚠ ALGUNOS EJEMPLOS TUVIERON ERRORES")
    print("=" * 70 + "\n")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
