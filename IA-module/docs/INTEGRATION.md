# Integración: Entradas y Salidas

Este documento detalla las entradas y salidas del modelo entrenado para integración externa vía API o uso directo de la biblioteca.

## Interfaz del Modelo

El modelo entrenado es accesible a través de la clase `PriorityPredictor` en `src/predictor.py`. Proporciona métodos para predicción, puntuación de confianza y explicabilidad.

### Artefactos Requeridos

Para despliegue, se requieren los siguientes archivos en `models/`:

| Archivo | Descripción |
|---------|-------------|
| `priority_classifier_v1.pkl` | Modelo LightGBM entrenado |
| `encoder/` | Directorio con modelo MiniLM-L6-v2 (Sentence Transformers) |
| `metadata.json` | Metadatos del entrenamiento (configuración, métricas) |

### Entradas

Todos los métodos de predicción aceptan texto como entrada principal. Metadata opcional (`department`, `type`, `tags`) puede mejorar la precisión si está disponible.

**Entrada de Texto Único:**
- Tipo: `str`
- Descripción: Descripción textual del incidente de TI
- Ejemplo: `"Fallo crítico del servidor afectando a todos los usuarios"`

**Entrada de Texto en Lote:**
- Tipo: `List[str]`
- Descripción: Lista de descripciones de incidentes
- Ejemplo: `["Servidor caído", "Error menor de UI", "Problema de latencia de red"]`

**Metadata Opcional (por incidente):**
- Tipo: `Dict[str, Any]`
- Campos soportados:
  - `department`: Departamento (str)
  - `type`: Tipo de incidente (str)
  - `tags`: Tags separados por comas (str)
- Ejemplo: `{"department": "Technical Support", "type": "Incident", "tags": "Server, Outage"}`

### Salidas

#### 1. Predicción Básica (`predict`)
Devuelve el nivel de prioridad predicho como un entero (0-index).

- Tipo de retorno: `int`
- Valores:
  - `0` → P1 (Crítico)
  - `1` → P2 (Medio)
  - `2` → P3 (Bajo)

#### 2. Predicción con Confianza (`predict_with_confidence`)
Devuelve una tupla de (prioridad, confianza).

- Tipo de retorno: `Tuple[int, float]`
- Prioridad: 0-2 (ver arriba)
- Confianza: Flotante entre 0.0 y 1.0

#### 3. Explicación Completa (`explain_prediction`)
Devuelve un diccionario con explicación detallada (para cumplimiento de RF-23).

```python
{
    'predicted_priority': int,           # 0, 1, o 2
    'priority_label': str,               # "P1 (Critical)", "P2 (Medium)", "P3 (Low)"
    'priority_description': str,         # Descripción en español
    'confidence': float,                 # 0.0 a 1.0
    'all_probabilities': {               # Probabilidad por clase
        'P1 (Critical)': float,
        'P2 (Medium)': float,
        'P3 (Low)': float
    },
    'contributing_features': [           # Features principales
        {
            'feature_index': int,        # Índice de la feature
            'feature_name': str,         # Nombre (palabra para TF-IDF, dim_N para MiniLM)
            'feature_value': float,      # Valor de la feature
            'score': float,              # Puntuación de contribución
            'importance': str,           # 'positive' o 'negative'
            'abs_score': float           # Impacto absoluto
        },
        ...
    ],
    'explanation_method': str,           # 'SHAP' o 'Coeficientes del modelo'
    'reasoning': str,                    # Explicación en lenguaje natural
    'response_time_seconds': float       # Tiempo máximo de respuesta configurado
}
```

### Ejemplos de Uso

#### Como Biblioteca

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "IA-module"))

from src.predictor import PriorityPredictor

# Carga modelo y encoder automáticamente desde models/
predictor = PriorityPredictor()

# Predicción simple (0=P1, 1=P2, 2=P3)
texto = "Fallo crítico de conexión a la base de datos"
prioridad = predictor.predict(texto)  # Devuelve 0

# Con confianza
prioridad, confianza = predictor.predict_with_confidence(texto)

# Explicación completa
explicacion = predictor.explain_prediction(texto)
print(f"Prioridad: {explicacion['priority_label']}")
print(f"Confianza: {explicacion['confidence']*100:.1f}%")
print(f"Razonamiento: {explicacion['reasoning']}")
```

#### Con Metadata (mejora precisión)

```python
incidente = {
    "text": "Critical server failure affecting all users",
    "department": "Technical Support",
    "type": "Incident",
    "tags": "Server, Outage, Critical"
}

prioridad = predictor.predict(
    incidente["text"],
    metadata={
        "department": incidente["department"],
        "type": incidente["type"],
        "tags": incidente["tags"]
    }
)
```

#### Procesamiento en Lote

```python
textos = [
    "Fallo de hardware del servidor",
    "Usuario olvidó contraseña",
    "Aplicación ejecutándose lenta"
]

# Prioridades en lote
prioridades = predictor.batch_predict(textos)  # [0, 2, 1]

# Lote con confianza
resultados = predictor.batch_predict_with_confidence(textos)
# [(0, 0.92), (2, 0.78), (1, 0.65)]

# Explicaciones en lote
explicaciones = [predictor.explain_prediction(t) for t in textos]
```

### Ejemplo de Endpoint de API (FastAPI)

```python
from fastapi import FastAPI
from pydantic import BaseModel
from typing import Optional
from src.predictor import PriorityPredictor

app = FastAPI()
predictor = PriorityPredictor()

class PredictionRequest(BaseModel):
    text: str
    department: Optional[str] = None
    type: Optional[str] = None
    tags: Optional[str] = None

class PredictionResponse(BaseModel):
    priority: int
    priority_label: str
    confidence: float
    explanation: dict

@app.post("/predict", response_model=PredictionResponse)
def predict_priority(request: PredictionRequest):
    metadata = None
    if request.department or request.type or request.tags:
        metadata = {
            "department": request.department or "Unknown",
            "type": request.type or "Unknown",
            "tags": request.tags or ""
        }
    
    priority, confidence = predictor.predict_with_confidence(
        request.text, metadata=metadata
    )
    explanation = predictor.explain_prediction(request.text, metadata=metadata)
    
    return {
        "priority": priority,
        "priority_label": explanation["priority_label"],
        "confidence": confidence,
        "explanation": explanation
    }
```

### Versionamiento

- Versión del modelo: `v1.0.0`
- El contrato de entrada/salida es estable para esta versión
- Cualquier cambio rotundo incrementará la versión mayor
- El archivo `metadata.json` incluye configuración del entrenamiento para trazabilidad

### Características de Rendimiento

| Métrica | Valor |
|---------|-------|
| Latencia de predicción individual | < 50ms (CPU, sin incluir embeddings) |
| Latencia con embeddings MiniLM | ~100-200ms (CPU) |
| Rendimiento batch | ~100-500 predicciones/segundo |
| Huella de memoria | ~500MB (modelo + encoder MiniLM) |
| Caché de embeddings | Elimina ~15 min de codificación en reentrenamiento |

### Manejo de Errores

| Caso | Comportamiento |
|------|---------------|
| Texto vacío | Devuelve prioridad 2 (P3) con baja confianza |
| Modelo no cargado | Lanza `ValueError` con mensaje descriptivo |
| Encoder no disponible | Lanza `ValueError` |
| Texto muy largo | No hay truncamiento automático (MiniLM lo maneja) |
| Metadata incompleta | Usa valores por defecto ("Unknown") |
| SHAP no disponible | Fallback a coeficientes del modelo |

### Notas de Integración

1. **Preprocesamiento automático**: El predictor elimina boilerplate LLM automáticamente antes de codificar
2. **Thread-safe**: Múltiples hilos pueden compartir la misma instancia del predictor
3. **Dependencias**: `sentence-transformers`, `lightgbm`, `shap`, `numpy`, `scikit-learn`
4. **Producción**: Almacenar en caché la instancia del predictor para evitar recarga
5. **Meta-features**: Si el modelo fue entrenado con meta-features, la metadata es necesaria para predicciones precisas. Si no, el predictor funciona solo con texto.
6. **Rutas**: El predictor busca modelos en `models/` relativo al directorio del módulo
