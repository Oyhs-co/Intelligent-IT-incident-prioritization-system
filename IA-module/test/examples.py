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
import traceback

# Add parent directory to path to import src as package
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.data_processor import DataProcessor
from src.model_trainer import ModelTrainer, ModelFactory
from src.predictor import PriorityPredictor
from src.utils import Config


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
        print(f"[WARN] Dataset no encontrado: {data_file}")
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
        
        print("\n2. Entrenando LightGBM classifier...")
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
        print("\nMétricas finales:")
        print(f"  Accuracy: {test_metrics['accuracy']:.4f}")
        print(f"  Precision: {test_metrics['precision']:.4f}")
        print(f"  Recall: {test_metrics['recall']:.4f}")
        print(f"  F1-Score: {test_metrics['f1']:.4f}")
        
        reach_goal = test_metrics['accuracy'] >= Config.MIN_ACCURACY
        status = "[OK] CUMPLIDO" if reach_goal else "[X] NO CUMPLIDO"
        print(f"\n  [OK] Requisito RNF-08 (Precisión >= {Config.MIN_ACCURACY}): {status}")
        
        if test_metrics['accuracy'] >= 0.85:
            print("  META ASPIRACIONAL (>=85%): !ALCANZADA!")
        
        return True
        
    except Exception as e:
        print(f"[X] Error: {str(e)}")
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
        
        text = "Critical hardware failure in production server affecting all users. The main database server has experienced a complete disk array failure causing the entire production environment to go offline. Multiple services including customer portal, payment processing, and internal reporting tools are currently unavailable. The server room shows physical indicator lights on the RAID controller showing degraded state and backup systems have not automatically failed over. Estimated impact affects over 5000 active users and revenue-generating operations are halted. Immediate on-site technician intervention is required along with emergency data recovery procedures from the last available backup taken 6 hours ago."
        
        print(f"\nIncidente: {text}")
        print("\nRealizando predicción...")
        
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
            ("Critical database corruption requiring immediate intervention. The primary transactional database has detected widespread data integrity issues affecting multiple tables and indexes. Users are reporting incorrect account balances, missing transaction records, and failed queries across all application modules. The database administrator has confirmed that the corruption extends to both primary and replica instances. Emergency rollback procedures must be initiated immediately as this directly impacts financial operations and regulatory compliance. All write operations have been temporarily suspended to prevent further data degradation. The incident has been escalated to the senior DBA team and requires priority resolution within the next 2 hours to meet service level agreements.", "Caso 1: Crítico"),
            ("Minor user interface layout issue low priority. There is a small cosmetic misalignment on the settings page where the save button appears slightly offset from its expected position when viewed on tablets with screen resolution of 1024x768 pixels. This does not affect any functionality or user workflow as the button remains fully clickable and all settings are saved correctly. The issue was reported by a single user during routine testing and has been classified as a visual enhancement. No other pages or components are affected. This can be addressed during the next scheduled UI maintenance cycle.", "Caso 2: Bajo"),
            ("High impact network connectivity outage affecting multiple departments. The corporate network is experiencing intermittent connectivity failures across the main office building affecting departments including finance, human resources, legal, and executive management. Users are unable to access cloud-based applications, shared network drives, and VoIP phone services are dropping calls. The network operations team has identified potential issues with the core switch configuration that was modified during last nights maintenance window. Multiple access points are showing packet loss exceeding 40 percent and network latency has increased from normal 5ms to over 200ms. Business operations are significantly impacted as employees cannot process invoices, access employee records, or participate in scheduled client video conferences. Network team is currently investigating and implementing emergency routing through backup connections.", "Caso 3: Alto"),
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
                sign = "+" if feat['importance'] == 'positive' else "-"
                print(f"  [{sign}] Feature {feat['feature_index']:3d} (impacto: {feat['abs_score']:+.4f})")
            
            print(f"\nRazonamiento: {explanation['reasoning']}")
        
        return True
        
    except Exception as e:
        print("[ERROR] Error: {}".format(str(e)))
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
            "Hardware failure critical impact on production environment. The primary application server has suffered a catastrophic power supply failure resulting in immediate shutdown of all hosted services. The server hosts the main customer-facing web application and API gateway serving over 10000 requests per minute. Redundant power supplies failed to activate and automatic failover to the secondary cluster was unsuccessful due to a configuration drift discovered during the event. Operations team has initiated emergency hardware replacement but requires minimum 4 hours for delivery and installation. Business continuity plan has been activated and all non-critical scheduled deployments are on hold until full service restoration is confirmed.",
            "Minor bug software application display issue. Users have reported that the date format in the export to PDF feature shows YYYY-MM-DD format instead of the expected DD-MM-YYYY format for users in the European region. The exported data is accurate and complete, only the visual presentation of dates differs from regional preferences. This affects the monthly report generation feature used by approximately 50 users. A workaround exists where users can manually adjust the date format after export. The development team has identified the root cause as a locale configuration issue in the PDF rendering library and a fix has been scheduled for the next bi-weekly release.",
            "Network outage high impact urgent situation affecting core infrastructure. The main data center network backbone is experiencing severe degradation due to a fiber optic cable damage caused by construction work in the area. Primary and secondary network paths between data center buildings are both impacted causing complete loss of redundancy. Services affected include email systems, file sharing platforms, video conferencing infrastructure, and the internal ticketing system used by the IT support team. Emergency satellite backup links have been activated but provide only 10 percent of normal bandwidth capacity. Priority services have been allocated bandwidth but all non-essential internet access has been throttled. External vendor has been contacted for emergency cable repair with estimated restoration time of 8 to 12 hours. Critical business operations requiring manual workarounds are being coordinated through mobile communication channels.",
            "Configuration issue low priority scheduled maintenance request. A user has requested a change to their desktop computer display settings to enable dark mode theme and adjust screen brightness defaults. The request was submitted through the standard IT service portal and has been categorized as a standard configuration change. The users current settings are functional and this request is purely for comfort and preference. The helpdesk team can process this request remotely using standard remote administration tools during normal business hours. No system downtime or service interruption will be required. Average resolution time for similar requests is approximately 15 minutes. This can be batched with other scheduled configuration updates planned for end of week.",
            "Database corruption critical emergency requiring immediate data recovery actions. The financial reporting database has experienced severe tablespace corruption following an unexpected system restart during a scheduled batch processing job. Multiple financial transaction tables show inconsistent state with orphaned records and broken foreign key constraints. The month-end financial close process which is time-sensitive and regulatory mandated cannot proceed until data integrity is fully restored. The backup system shows the last verified clean backup was taken 18 hours ago meaning any transactions processed in that window will require manual reconciliation. The database team lead has been notified and emergency recovery procedures are being initiated including isolation of affected tablespaces and preparation of recovery environment. External database consultants have been engaged as additional support given the criticality and complexity of the situation.",
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
