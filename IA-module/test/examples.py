"""
Ejemplos de uso del sistema de priorización.

Demuestra:
1. Entrenamiento del modelo (solo si no existe)
2. Predicción individual
3. Predicción con explicación
4. Predicción en lotes

Compatible con MiniLM-L6-v2 + LightGBM (v2.0)
"""

from pathlib import Path
import sys

# Add parent directory to path to import src as package
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_processor import DataProcessor
from src.model_trainer import ModelTrainer, ModelFactory
from src.predictor import PriorityPredictor
from src.utils import Config, logger


def check_model_exists():
    """Verifica si el modelo y encoder ya existen."""
    model_exists = Config.MODEL_FILE.exists()
    encoder_exists = Config.ENCODER_DIR.exists()
    return model_exists and encoder_exists


def example_1_train_model():
    """Ejemplo 1: Entrenar el modelo (solo si no existe)."""
    print("\n" + "=" * 70)
    print("EJEMPLO 1: ENTRENAR EL MODELO (si no existe)")
    print("=" * 70)
    
    Config.ensure_dirs()
    data_file = Config.get_data_path("it_tickets_merged.csv")
    
    if not data_file.exists():
        print(f"⚠ Dataset no encontrado: {data_file}")
        print("Por favor asegúrese de que it_tickets_merged.csv existe en IA-module/data/")
        return False
    
    # Verificar si modelo ya existe
    if check_model_exists():
        print("\n[OK] Modelo ya existe. Saltando entrenamiento.")
        print(f"  Modelo: {Config.MODEL_FILE}")
        print(f"  Encoder: {Config.ENCODER_DIR}")
        print("  \nPara re-entrenar, elimine los archivos del modelo primero.")
        return True
    
    try:
        print(f"\n1. Cargando y limpiando datos desde {data_file.name}...")
        processor = DataProcessor()
        
        # Pipeline con MiniLM (embeddings)
        result = processor.preprocess_pipeline(
            input_file=data_file,
            encoder=None,
            use_embeddings=True  # True para MiniLM
        )
        X_train, X_val, X_test, y_train, y_val, y_test, encoder = result
        
        print("[OK] Datos preparados:")
        print(f"  - Train: {X_train.shape[0]} muestras")
        print(f"  - Validation: {X_val.shape[0]} muestras")
        print(f"  - Test: {X_test.shape[0]} muestras")
        print(f"  - Features: {X_train.shape[1]} (embeddings MiniLM)")
        
        print(f"\n2. Entrenando LightGBM classifier...")
        classifier = ModelFactory.create_lightgbm(
            n_classes=3,
            num_leaves=31,
            max_depth=6,
            learning_rate=0.05
        )
        
        trainer = ModelTrainer(
            classifier=classifier,
            encoder=encoder,
            random_state=Config.RANDOM_STATE
        )
        trainer.train(X_train, y_train)
        print("[OK] Modelo entrenado")
        
        print("[OK] Validando modelo...")
        val_metrics = trainer.validate(X_val, y_val)
        
        print("[OK] Evaluando en test set...")
        test_metrics = trainer.test(X_test, y_test)
        
        print("[OK] Guardando artefactos...")
        trainer.save_model(
            model_path=Config.MODEL_FILE,
            encoder_path=Config.ENCODER_DIR,
            metadata={
                "use_minilm": True,
                "encoder_type": "MiniLMEncoder",
                "classifier_type": "LightGBMClassifier"
            }
        )
        print("[OK] Modelo y encoder guardados")
        
        print("\n[OK] ENTRENAMIENTO COMPLETADO EXITOSAMENTE")
        print(f"\nMétricas finales:")
        print(f"  Accuracy: {test_metrics['accuracy']:.4f}")
        print(f"  Precision: {test_metrics['precision']:.4f}")
        print(f"  Recall: {test_metrics['recall']:.4f}")
        print(f"  F1-Score: {test_metrics['f1']:.4f}")
        
        reach_goal = test_metrics['accuracy'] >= Config.MIN_ACCURACY
        status = "✓ CUMPLIDO" if reach_goal else "✗ NO CUMPLIDO"
        print(f"\n  [OK] Requisito RNF-08 (Precisión ≥ {Config.MIN_ACCURACY}): {status}")
        
        if test_metrics['accuracy'] >= 0.85:
            print(f"  META ASPIRACIONAL (≥85%): ¡ALCANZADA!")
        
        return True
        
    except Exception as e:
        print(f"✗ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def load_predictor():
    """Carga el predictor (entrena si no existe)."""
    if not check_model_exists():
        print("\n[WARNING] Modelo no encontrado. Entrenando primero...")
        if not example_1_train_model():
            raise RuntimeError("No se pudo entrenar el modelo")
    
    return PriorityPredictor()


def example_2_predict_single():
    """Ejemplo 2: Predicción individual."""
    print("\n" + "=" * 70)
    print("EJEMPLO 2: PREDICCIÓN INDIVIDUAL")
    print("=" * 70)
    
    Config.ensure_dirs()
    
    try:
        print("\nCargando modelo...")
        predictor = load_predictor()
        print("[OK] Modelo cargado")
        
        text = "Critical hardware failure in production server affecting all users"
        
        print(f"\nIncidente: {text}")
        print(f"\nRealizando predicción...")
        
        priority, confidence = predictor.predict_with_confidence(text)
        
        print("[OK] Predicción completada:")
        print(f"  Prioridad: {predictor.PRIORITY_LABELS[priority]}")
        print(f"  Confianza: {confidence*100:.1f}%")
        
        return True
        
    except Exception as e:
        print("[ERROR] Error: {}".format(str(e)))
        import traceback
        traceback.print_exc()
        return False


def example_3_predict_with_explanation():
    """Ejemplo 3: Predicción con explicación (SHAP)."""
    print("\n" + "=" * 70)
    print("EJEMPLO 3: PREDICCIÓN CON EXPLICACIÓN (RF-23)")
    print("=" * 70)
    
    Config.ensure_dirs()
    
    try:
        print("\nCargando modelo...")
        predictor = load_predictor()
        
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
            print(f"Descripción: {explanation['priority_description']}")
            print(f"Confianza: {explanation['confidence']*100:.1f}%\n")
            
            print("Factores clave (explicabilidad):")
            for feat in explanation['contributing_features']:
                direction = "↑↑" if feat['importance'] == 'positive' else "↓↓"
                sign = "+" if feat['importance'] == 'positive' else "-"
            print(f"  [{sign}] Feature {feat['feature_index']:3d} (impacto: {feat['abs_score']:+.4f})")
            
            print(f"\nRazonamiento: {explanation['reasoning']}")
        
        return True
        
    except Exception as e:
        print("[ERROR] Error: {}".format(str(e)))
        import traceback
        traceback.print_exc()
        return False


def example_4_batch_predict():
    """Ejemplo 4: Predicción en lotes."""
    print("\n" + "=" * 70)
    print("EJEMPLO 4: PREDICCIÓN EN LOTES")
    print("=" * 70)
    
    Config.ensure_dirs()
    
    try:
        print("\nCargando modelo...")
        predictor = load_predictor()
        
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
        print(f"{'#':<3} {'Prioridad':<15} {'Confianza':<12} {'Texto':<45}")
        print("-" * 75)
        
        for i, (priority, confidence, text) in enumerate(zip(
            [r[0] for r in results],
            [r[1] for r in results],
            texts
        ), 1):
            priority_label = predictor.PRIORITY_LABELS[priority]
            text_short = text[:42] + "..." if len(text) > 45 else text
            print(f"{i:<3} {priority_label:<15} {confidence*100:>10.1f}% {text_short:<45}")
        
        print("\n[OK] Predicción en lotes completada")
        
        return True
        
    except Exception as e:
         print("[ERROR] Error: {}".format(str(e)))
         import traceback
         traceback.print_exc()
         return False


def main():
    """Ejecuta los ejemplos."""
    
    print("\n" + "=" * 70)
    print("SISTEMA DE PRIORIZACIÓN DE INCIDENTES IT - EJEMPLOS")
    print("=" * 70)
    
    print("\nEste script demuestra el uso del sistema:")
    print("1. Entrenamiento del modelo (MiniLM-L6-v2 + LightGBM)")
    print("   - Solo se ejecuta si el modelo no existe")
    print("2. Predicción individual")
    print("3. Predicción con explicación (SHAP)")
    print("4. Predicción en lotes")
    
    # Ejecutar ejemplos
    success = True
    
    if not example_1_train_model():
        print("\n[WARNING] No se puede continuar sin modelo entrenado")
        return 1
    
    if not example_2_predict_single():
        success = False
    
    if not example_3_predict_with_explanation():
        success = False
    
    if not example_4_batch_predict():
        success = False
    
    print("\n" + "=" * 70)
    if success:
        print("[OK] TODOS LOS EJEMPLOS EJECUTADOS EXITOSAMENTE")
    else:
        print("[WARNING] ALGUNOS EJEMPLOS TUVIERON ERRORES")
    print("=" * 70 + "\n")
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
