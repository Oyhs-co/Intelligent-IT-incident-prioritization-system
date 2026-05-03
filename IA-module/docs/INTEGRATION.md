# Integración: Entradas y Salidas

Este documento detalla las entradas y salidas del modelo entrenado para integración externa vía API o uso directo de la biblioteca.

## Interfaz del Modelo

El modelo entrenado es accesible a través de la clase `PriorityPredictor` en `src/predictor.py`. Proporciona métodos para predicción, puntuación de confianza y explicabilidad.

### Entradas

Todos los métodos de predicción aceptan una sola cadena o una lista de cadenas que representan la descripción del incidente.

**Entrada de Texto Único:**
- Tipo: `str`
- Descripción: Descripción textual del incidente de TI
- Ejemplo: `"Falló el servidor crítico afectando a todos los usuarios"`

**Entrada de Texto en Lote:**
- Tipo: `List[str]`
- Descripción: Lista de descripciones de incidentes
- Ejemplo: `["Servidor caído", "Error menor de UI", "Problema de latencia de red"]`

### Salidas

#### 1. Predicción Básica (`predict`)
Devuelve el nivel de prioridad predicho como un entero.

- Tipo de retorno: `int`
- Valores: 
  - `1` → P1 (Crítico)
  - `2` → P2 (Medio)
  - `3` → P3 (Bajo)

#### 2. Predicción con Confianza (`predict_with_confidence`)
Devuelve una tupla de (prioridad, confianza).

- Tipo de retorno: `Tuple[int, float]`
- Prioridad: Igual que arriba (1-3)
- Confianza: Flotante entre 0.0 y 1.0 que representa la confianza del modelo

#### 3. Explicación Completa (`explain_prediction`)
Devuelve un diccionario con explicación detallada (para cumplimiento de RF-23).

```python
{
    'predicted_priority': int,           # 1, 2, o 3
    'priority_label': str,               # "P1 (Crítico)", etc.
    'confidence': float,                 # 0.0 a 1.0
    'all_probabilities': {               # Probabilidad por clase
        'P1 (Crítico)': float,
        'P2 (Medio)': float,
        'P3 (Bajo)': float
    },
    'contributing_features': [           # Palabras clave principales
        {
            'feature': str,              # Palabra clave/término
            'score': float,              # Puntuación de contribución
            'importance': str            # 'positiva' o 'negativa'
        },
        ...
    ],
    'reasoning': str                     # Explicación en lenguaje natural
}
```

### Ejemplos de Uso

#### Como Biblioteca
```python
from src.predictor import PriorityPredictor

predictor = PriorityPredictor()

# Predicción única
texto = "Fallo crítico de conexión a la base de datos"
prioridad = predictor.predict(texto)  # Devuelve 1

# Con confianza
prioridad, confianza = predictor.predict_with_confidence(texto)

# Explicación completa
explicacion = predictor.explain_prediction(texto)
print(f"Prioridad: {explicacion['priority_label']}")
print(f"Confianza: {explicacion['confidence']*100:.1f}%")
```

#### Procesamiento en Lote
```python
textos = [
    "Fallo de hardware del servidor",
    "Usuario olvidó contraseña",
    "Aplicación ejecutándose lenta"
]

# Prioridades en lote
prioridades = predictor.batch_predict(textos)

# Lote con confianza
resultados = predictor.batch_predict_with_confidence(textos)

# Explicaciones en lote
explicaciones = [predictor.explain_prediction(t) for t in textos]
```

### Ejemplo de Endpoint de API (FastAPI)
Si se expone mediante API REST:

```python
from fastapi import FastAPI
from pydantic import BaseModel
from src.predictor import PriorityPredictor

app = FastAPI()
predictor = PriorityPredictor()

class PredictionRequest(BaseModel):
    texto: str

class PredictionResponse(BaseModel):
    prioridad: int
    prioridad_etiqueta: str
    confianza: float
    explicacion: dict

@app.post("/predecir", response_model=PredictionResponse)
def predecir_prioridad(solicitud: PredictionRequest):
    prioridad, confianza = predictor.predict_with_confidence(solicitud.texto)
    explicacion = predictor.explain_prediction(solicitud.texto)
    return {
        "prioridad": prioridad,
        "prioridad_etiqueta": explicacion["priority_label"],
        "confianza": confianza,
        "explicacion": explicacion
    }
```

### Artefactos del Modelo
Para despliegue externo, se requieren los siguientes artefactos:
1. `models/priority_classifier_v1.pkl` - Modelo entrenado de LogisticRegression
2. `models/priority_classifier_v1_vectorizer.pkl` - Vectorizador TF-IDF

### Versionamiento
- Versión del modelo: `v1.0.0`
- El contrato de entrada/salida es estable para esta versión
- Cualquier cambio rotundo incrementará la versión mayor

### Características de Rendimiento
- Latencia de predicción individual: < 50ms (CPU)
- Rendimiento de predicción en lote: ~1000 predicciones/segundo
- Huella de memoria: ~150MB (modelo + vectorizador)

### Manejo de Errores
- Entrada de texto vacío: Devuelve prioridad 3 (Bajo) con baja confianza
- Textos muy largos: Se trunca automáticamente a 5000 caracteres
- Entradas no cadena: Lanzará TypeError

### Notas de Integración
1. El modelo espera texto limpio (no se necesita preprocesamiento especial)
2. Seguro para hilos: Múltiples hilos pueden compartir la misma instancia del predictor
3. No hay dependencias externas más allá de scikit-learn y numpy
4. Para uso en producción, considere almacenar en caché la instancia del predictor