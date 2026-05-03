"""
Script de predicción usando el modelo entrenado.

Demuestra:
- Predicción de prioridad
- Explicación de predicción con SHAP
- Predicción con confianza

Soporta múltiples backends (MiniLM-L6-v2 + LightGBM o TF-IDF + LR).
"""

from pathlib import Path
import sys

# Add parent directory to path to import src as package
sys.path.insert(0, str(Path(__file__).parent))

from src.predictor import PriorityPredictor
from src.utils import logger
from tqdm import tqdm


def format_explanation(explanation: dict) -> str:
    """Formatea la explicación de forma legible."""
    
    output = []
    output.append("\n" + "=" * 70)
    output.append("PREDICCIÓN DE PRIORIDAD DEL INCIDENTE")
    output.append("=" * 70)
    
    # Predicción y confianza
    output.append(f"\n✓ Prioridad Predicha: {explanation['priority_label']}")
    output.append(f"  Descripción: {explanation['priority_description']}")
    output.append(f"  Confianza: {explanation['confidence'] * 100:.1f}%")
    
    output.append(f"\n  Probabilidades por clase:")
    for label, prob in explanation['all_probabilities'].items():
        # Generar barra de progreso con tqdm
        bar = tqdm.format_meter(
            n=int(prob * 100),
            total=100,
            elapsed=0,
            ncols=30,
            bar_format='{bar}',
            ascii=False
        )
        output.append(f"    {label:20} [{bar}] {prob*100:5.1f}%")
    
    # Features contribuyentes
    if explanation['contributing_features']:
        output.append(f"\n  Factores clave (explicabilidad: {explanation['explanation_method']}):")
        for i, feat in enumerate(explanation['contributing_features'][:5], 1):
            direction = "POS" if feat['importance'] == 'positive' else "NEG"
            feature_display = feat.get('feature_name', f"Feature {feat['feature_index']}")
            feature_value = feat.get('feature_value', 0.0)
            output.append(
                f"    {i}. {direction} {feature_display} "
                f"(valor: {feature_value:.4f}, impacto: {feat['abs_score']:+.4f})"
            )
    
    # Razonamiento
    output.append(f"\n  Razonamiento:")
    output.append(f"    {explanation['reasoning']}")
    
    output.append("\n" + "=" * 70 + "\n")
    
    return "\n".join(output)


def predict_single(text: str, predictor: PriorityPredictor) -> int:
    """Realiza predicción para un texto individual."""
    
    try:
        logger.info(f"Analizando incidente: {text[:100]}...")
        
        # Predicción con explicación
        explanation = predictor.explain_prediction(text, top_k=5)
        
        # Mostrar resultado
        print(format_explanation(explanation))
        
        return explanation['predicted_priority']
        
    except FileNotFoundError as e:
        logger.error(f"Error: {str(e)}")
        logger.info("Por favor, ejecute train.py primero para entrenar el modelo.")
        return -1
    except Exception as e:
        logger.error(f"Error durante predicción: {str(e)}", exc_info=True)
        return -1


def demo_predictions(predictor: PriorityPredictor) -> None:
    """Ejecuta demostraciones con ejemplos."""
    
    test_cases = [
        {
            "text": "Category: Hardware Failure. Type: Desktop Application. Impact Level: Critical. Urgency: Critical. Status: Closed. Description: El servidor principal no responde y los usuarios no pueden acceder al sistema.",
            "label": "P1 esperada"
        },
        {
            "text": "Category: Software Bug. Type: Web Based Application. Impact Level: Low. Urgency: Low. Status: Closed. Description: Error menor en visualización de reportes que no afecta funcionalidad principal.",
            "label": "P3 esperada"
        },
        {
            "text": "Category: Access Control. Type: Database. Impact Level: High. Urgency: High. Status: Failed. Resolution: Configuration Change. Description: Usuarios no pueden acceder a la base de datos de producción.",
            "label": "P1/P2 esperada"
        },
        {
            "text": "Category: Network Connectivity. Type: Infrastructure. Impact Level: High. Urgency: Critical. Status: Closed. Resolution: Hardware Replacement. Description: Caída de red en múltiples ubicaciones afectando servicios críticos.",
            "label": "P1 esperada"
        }
    ]
    
    try:
        logger.info("Ejecutando predicciones de demostración...")
        
        for i, case in enumerate(test_cases, 1):
            print(f"\n{'='*70}")
            print(f"EJEMPLO {i}: {case['label']}")
            print(f"{'='*70}")
            print(f"Incidente: {case['text'][:100]}...\n")
            
            explanation = predictor.explain_prediction(case['text'], top_k=3)
            print(format_explanation(explanation))
            
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)


def main():
    """Punto de entrada principal."""
    
    logger.info("=" * 70)
    logger.info("SISTEMA DE PRIORIZACIÓN DE INCIDENTES IT - PREDICCIÓN")
    logger.info("=" * 70)
    
    try:
        # Inicializar predictor (carga modelo y encoder guardados)
        predictor = PriorityPredictor()
        
        # Ejemplos de uso
        if len(sys.argv) > 1:
            # Predicción desde argumentos
            text = " ".join(sys.argv[1:])
            return predict_single(text, predictor)
        else:
            # Ejecución de demo
            print("\nUsage:")
            print("  python predict.py '<incident_description>'")
            print("\nEjemplos:")
            print("  python predict.py 'Category: Hardware Impact: Critical'")
            print("\nEjecutando demostraciones predeterminadas...\n")
            
            demo_predictions(predictor)
            return 0
            
    except FileNotFoundError:
        logger.error("Modelos no encontrados. Ejecute train.py primero.")
        logger.info("\nOpciones:")
        logger.info("  python train.py              # Entrena con MiniLM")
        return 1
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)
        return 1


if __name__ == "__main__":
    sys.exit(main())