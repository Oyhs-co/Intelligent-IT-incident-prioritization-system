"""
Script de predicción usando el modelo entrenado.

Demuestra:
- Predicción de prioridad
- Explicación de predicción
- Predicción con confianza
"""

from pathlib import Path
import sys

# Add parent directory to path to import src as package
sys.path.insert(0, str(Path(__file__).parent))

from src.predictor import PriorityPredictor
from src.utils import logger

def format_explanation(explanation: dict) -> str:
    """Formatea la explicación de forma legible."""
    
    output = []
    output.append("\n" + "=" * 70)
    output.append("PREDICCIÓN DE PRIORIDAD DEL INCIDENTE")
    output.append("=" * 70)
    
    # Predicción y confianza
    output.append(f"\n✓ Prioridad Predicha: {explanation['priority_label']}")
    output.append(f"  Confianza: {explanation['confidence'] * 100:.1f}%")
    
    # Probabilidades por clase
    output.append(f"\n  Probabilidades por clase:")
    for label, prob in explanation['all_probabilities'].items():
        bar_length = int(prob * 30)
        bar = "█" * bar_length + "░" * (30 - bar_length)
        output.append(f"    {label:20} [{bar}] {prob*100:5.1f}%")
    
    # Palabras clave
    if explanation['contributing_features']:
        output.append(f"\n  Palabras clave contribuyentes:")
        for feature in explanation['contributing_features']:
            direction = "↑" if feature['importance'] == 'positive' else "↓"
            output.append(
                f"    {direction} {feature['feature']:20} (score: {feature['score']:+.4f})"
            )
    
    # Razonamiento
    output.append(f"\n  Razonamiento:")
    output.append(f"    {explanation['reasoning']}")
    
    output.append("\n" + "=" * 70 + "\n")
    
    return "\n".join(output)


def predict_single(text: str) -> None:
    """Realiza predicción para un texto individual."""
    
    try:
        logger.info("Cargando modelo e inicializando predictor...")
        predictor = PriorityPredictor()
        
        logger.info(f"Analizando incidente: {text[:100]}...")
        
        # Predicción con explicación
        explanation = predictor.explain_prediction(text, top_k=5)
        
        # Mostrar resultado
        print(format_explanation(explanation))
        
    except FileNotFoundError as e:
        logger.error(f"Error: {str(e)}")
        logger.info("Por favor, ejecute train.py primero para entrenar el modelo.")
        return 1
    except Exception as e:
        logger.error(f"Error durante predicción: {str(e)}", exc_info=True)
        return 1
    
    return 0


def demo_predictions() -> None:
    """Ejecuta demostraciones con ejemplos."""
    
    test_cases = [
        "Category: Hardware Failure. Type: Desktop Application. Impact Level: Critical. Urgency: Critical. Status: Closed.",
        "Category: Software Bug. Type: Web Based Application. Impact Level: Low. Urgency: Low. Status: Closed.",
        "Category: Access Control. Type: Database. Impact Level: High. Urgency: High. Status: Failed. Resolution: Configuration Change.",
        "Category: Network Connectivity. Type: Infrastructure. Impact Level: High. Urgency: Critical. Status: Closed. Resolution: Hardware Replacement."
    ]
    
    try:
        logger.info("Cargando modelo para demo...")
        predictor = PriorityPredictor()
        
        logger.info("Ejecutando predicciones de demostración...")
        
        for i, text in enumerate(test_cases, 1):
            print(f"\n{'='*70}")
            print(f"EJEMPLO {i}")
            print(f"{'='*70}")
            print(f"Incidente: {text}\n")
            
            explanation = predictor.explain_prediction(text, top_k=3)
            print(format_explanation(explanation))
            
    except FileNotFoundError:
        logger.error("Modelo no encontrado. Ejecute train.py primero.")
    except Exception as e:
        logger.error(f"Error: {str(e)}", exc_info=True)


def main():
    """Punto de entrada principal."""
    
    logger.info("=" * 70)
    logger.info("SISTEMA DE PRIORIZACIÓN DE INCIDENTES IT - PREDICCIÓN")
    logger.info("=" * 70)
    
    # Ejemplos de uso
    if len(sys.argv) > 1:
        # Predicción desde argumentos
        text = " ".join(sys.argv[1:])
        return predict_single(text)
    else:
        # Ejecución de demo
        print("\nUsage:")
        print("  python predict.py <incident_description>")
        print("\nEjemplos:")
        print("  python predict.py 'Category: Hardware. Impact: Critical'")
        print("\nEjecutando demostraciones...\n")
        
        demo_predictions()
        return 0


if __name__ == "__main__":
    sys.exit(main())
