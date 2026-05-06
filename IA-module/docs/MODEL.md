# Módulo IA - Sistema de Priorización de Incidentes IT

Documentación del modelo de machine learning y su arquitectura.

## Descripción

Módulo que implementa un sistema inteligente de priorización automática de incidentes IT usando:

- **Modelo principal**: LightGBM (Gradient Boosting)
- **Modelo fallback**: Logistic Regression (ensamble opcional)
- **Codificador principal**: MiniLM-L6-v2 embeddings (384 dimensiones)
- **Codificador fallback**: TF-IDF (1000 features, bigrams)
- **Explicabilidad**: SHAP (SHapley Additive exPlanations)
- **Framework**: scikit-learn, sentence-transformers, lightgbm, shap
- **Dataset**: 45,988 tickets IT (3 clases: P1, P2, P3)

## Sistema de Prioridades

| Prioridad | Etiqueta | Descripción |
|-----------|----------|--------------|
| P1 | Critical | Incidentes de máxima urgencia - atención inmediata |
| P2 | Medium | Incidentes de prioridad media - atención pronta |
| P3 | Low | Incidentes de baja prioridad - puede ser programado |

## Estructura del Proyecto

```
IA-module/
├── src/                      # Módulos principales
│   ├── __init__.py          # Inicialización del paquete
│   ├── interfaces.py        # Interfaces abstractas (IEncoder, IClassifier)
│   ├── utils.py             # Utilidades, configuración y reportes
│   ├── encoders.py          # Codificadores (MiniLM, TF-IDF)
│   ├── classifiers.py       # Clasificadores (LightGBM, Ensemble)
│   ├── data_processor.py    # Preprocesamiento de datos
│   ├── model_trainer.py     # Entrenamiento y evaluación
│   └── predictor.py         # Predicción y explicabilidad
│
├── config/                   # Configuración
│   └── default.json         # Hiperparámetros y opciones
│
├── data/                     # Datos
│   └── it_tickets_merged.csv    # Dataset principal (45,988 tickets)
│
├── models/                   # Modelos entrenados (generado)
│   ├── priority_classifier_v1.pkl
│   ├── encoder/              # Modelo MiniLM guardado
│   └── metadata.json         # Metadatos del entrenamiento
│
├── cache/                    # Caché de embeddings (generado)
│   └── X_MiniLM_{hash}.npy  # Embeddings cacheados
│
├── logs/                     # Logs (generado)
│   ├── app.log
│   └── training_{timestamp}.log
│
├── reports/                  # Reportes de entrenamiento (generado)
│   ├── training_report_{timestamp}.md
│   └── training_config.json
│
├── test/                     # Tests
│   ├── test_model.py        # Tests unitarios
│   └── examples.py          # Ejemplos de uso
│
├── docs/                     # Documentación
│   ├── ARQUITECTURA.md      # Arquitectura del sistema
│   ├── INTEGRATION.md       # Guía de integración
│   └── MODEL.md             # Este archivo
│
├── train.py                  # Script de entrenamiento
├── predict.py                # Script de predicción
├── pyproject.toml           # Dependencias (Poetry)
└── poetry.lock              # Lock de dependencias
```

## Cómo Usar

### 1. Instalación

```bash
cd IA-module
poetry install
```

### 2. Entrenamiento del Modelo

```bash
poetry run python train.py
```

**Qué hace:**
1. Carga `data/it_tickets_merged.csv`
2. Limpia y valida datos (reemplaza NS/NA, filtra prioridades válidas)
3. Elimina boilerplate LLM de los textos (14 patrones regex)
4. Deduplica textos exactos (~29% del dataset)
5. Codifica con MiniLM-L6-v2 embeddings (384 dimensiones)
   - Usa caché si está disponible (evita ~15 min de codificación)
6. Divide datos: train 72.25%, validation 12.75%, test 15%
7. Entrena modelo LightGBM con early stopping
8. Valida y evalúa el modelo
9. Guarda artefactos en `models/`
10. Genera reporte en `reports/`

**Configuración (`config/default.json`):**

```json
{
  "minilm_model_name": "all-MiniLM-L6-v2",
  "embedding_dim": 384,
  "embedding_batch_size": 16,
  "lgb_num_leaves": 50,
  "lgb_max_depth": 7,
  "lgb_learning_rate": 0.03,
  "lgb_n_estimators": 500,
  "lgb_min_child_samples": 20,
  "lgb_reg_alpha": 0.05,
  "lgb_reg_lambda": 0.05,
  "lgb_early_stopping_rounds": 30,
  "random_state": 42,
  "test_size": 0.15,
  "validation_size": 0.15,
  "balance_classes": false,
  "min_accuracy": 0.70
}
```

**Opciones en `train.py`:**

```python
USE_MINILM = True          # True: MiniLM, False: TF-IDF
USE_ENSEMBLE = False       # True: LightGBM+LR, False: LightGBM solo
BALANCE_CLASSES = False    # Undersampling para igualar clases
DEDUPLICATE = True         # Eliminar textos duplicados
BOILERPLATE_REMOVAL = True # Eliminar frases boilerplate LLM
USE_CACHE = True           # Usar caché de embeddings
```

**Salida esperada:**
- `models/priority_classifier_v1.pkl` - Modelo entrenado
- `models/encoder/` - Codificador MiniLM-L6-v2
- `models/metadata.json` - Metadatos del entrenamiento
- `reports/training_report_{timestamp}.md` - Reporte detallado
- `reports/training_config.json` - Configuración usada

### 3. Predicción

#### Desde línea de comandos:

```bash
poetry run python predict.py "Critical server failure affecting all users"
```

#### Ejecutar demo:

```bash
poetry run python predict.py
```

Mostrará ejemplos de predicción con explicaciones.

#### Como biblioteca:

```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "IA-module"))

from src.predictor import PriorityPredictor

predictor = PriorityPredictor()

# Predicción simple (0=P1, 1=P2, 2=P3)
priority = predictor.predict("Server is down")

# Con confianza
priority, confidence = predictor.predict_with_confidence("Server is down")

# Con explicación completa (RF-23)
explanation = predictor.explain_prediction("Server is down", top_k=5)
print(f"Prioridad: {explanation['priority_label']}")
print(f"Confianza: {explanation['confidence']*100:.1f}%")
```

### 4. Tests

```bash
poetry run python test/test_model.py
```

## Módulos Principales

### `interfaces.py` - Interfaces Abstractas

Define contratos para componentes intercambiables:

| Interfaz | Descripción |
|----------|-------------|
| `IEncoder` | Codificación de texto a vectores numéricos |
| `IClassifier` | Clasificación multiclase con probabilidades |

Principio: Dependency Inversion (DIP)

### `encoders.py` - Codificadores de Texto

| Clase | Descripción | Dimensión |
|-------|-------------|-----------|
| `MiniLMEncoder` | Embeddings con Sentence Transformers | 384 |
| `TFIDFEncoder` | TF-IDF vectorizer (fallback) | 1000 |

**MiniLMEncoder**: Modelo `all-MiniLM-L6-v2`, optimizado para CPU, normalización de embeddings.

**TFIDFEncoder**: `TfidfVectorizer` con bigrams, `max_features=1000`.

### `classifiers.py` - Clasificadores

| Clase | Descripción |
|-------|-------------|
| `LightGBMClassifier` | Modelo principal, early stopping opcional |
| `FallbackEnsembleClassifier` | Ensamble LightGBM (60%) + LR (40%) |

**LightGBMClassifier parámetros**:
```python
LightGBMClassifier(
    n_classes=3,
    num_leaves=50,
    max_depth=7,
    learning_rate=0.03,
    n_estimators=500,
    min_child_samples=20,
    reg_alpha=0.05,
    reg_lambda=0.05,
    early_stopping_rounds=30,
    random_state=42
)
```

### `data_processor.py` - Procesamiento de Datos

**Pipeline completo:**

```python
processor = DataProcessor()

# Pipeline end-to-end
X_train, X_val, X_test, y_train, y_val, y_test, encoder = processor.preprocess_pipeline(
    input_file=Path("data/it_tickets_merged.csv"),
    use_embeddings=True,
    deduplicate=True,
    use_cache=True
)
```

**Características:**
- Limpieza de valores inválidos (NS, NA)
- Eliminación de boilerplate LLM (14 patrones regex)
- Deduplicación exacta de textos
- Caché de embeddings (.npy) con hash SHA256
- División estratificada train/val/test
- Soporte para meta-features (department, type, tags)
- Balanceo de clases (undersampling opcional)

### `model_trainer.py` - Entrenamiento

```python
trainer = ModelTrainer()
trainer.train(X_train, y_train, X_val, y_val)

# Validación
val_metrics = trainer.validate(X_val, y_val)

# Test
test_metrics = trainer.test(X_test, y_test)

# Guardar
trainer.save_model()
```

**Métricas Capturadas:**
- Accuracy, Precision (weighted), Recall (weighted), F1-Score
- Confusion Matrix, Classification Report
- Gap validation-test (RNF-10)

### `predictor.py` - Predicción y Explicabilidad

```python
predictor = PriorityPredictor()

# Predicción simple (0-2)
priority = predictor.predict(text)

# Con confianza
priority, confidence = predictor.predict_with_confidence(text)

# Con explicación (RF-23)
explanation = predictor.explain_prediction(text, top_k=5)

# Batch
priorities = predictor.batch_predict(texts)
results = predictor.batch_predict_with_confidence(texts)
```

**Explicación Incluye:**
- Prioridad predicha (P1-P3)
- Nivel de confianza (0-100%)
- Probabilidades por clase
- Top 5 features contribuyentes
- Método de explicación (SHAP o coeficientes)
- Razonamiento textual

## Configuración

Parámetros centralizados en `src/utils.py` (clase `Config`) y `config/default.json`.

```python
# Embeddings
MINILM_MODEL_NAME = "all-MiniLM-L6-v2"
EMBEDDING_DIM = 384
EMBEDDING_BATCH_SIZE = 16

# LightGBM
LGB_NUM_LEAVES = 50
LGB_MAX_DEPTH = 7
LGB_LEARNING_RATE = 0.03
LGB_N_ESTIMATORS = 500
LGB_MIN_CHILD_SAMPLES = 20
LGB_REG_ALPHA = 0.05
LGB_REG_LAMBDA = 0.05
LGB_EARLY_STOPPING_ROUNDS = 30

# División de datos
TEST_SIZE = 0.15           # 15% para test
VALIDATION_SIZE = 0.15     # 15% para validation

# Requerimientos
MIN_ACCURACY = 0.70        # RNF-08: Precisión mínima 70%
RESPONSE_TIME_SECONDS = 2  # RNF-01: < 2 segundos
```

## Flujo de Datos

```
it_tickets_merged.csv (45,988 tickets)
    ↓
[DataProcessor]
    ├─ load_data()
    ├─ clean_data() + remove_boilerplate()
    ├─ deduplicate_data()
    ├─ prepare_texts_and_labels()
    ├─ encode_texts() → MiniLM Embeddings (384-dim)
    │   └─ [Caché: si disponible, skip encoding]
    └─ split_data() → train/val/test
    ↓
[ModelTrainer]
    ├─ create_model() → LightGBM (via ModelFactory)
    ├─ train() + early stopping
    ├─ validate() → check RNF-08
    ├─ test() → check RNF-10
    └─ save_model() → priority_classifier_v1.pkl + encoder/
    ↓
[PriorityPredictor]
    ├─ predict()              → Prioridad (0-2)
    ├─ predict_with_confidence() → (Prioridad, Confianza)
    └─ explain_prediction()   → Explicación con SHAP
    ↓
API / Frontend
```

## Requisitos Implementados

### Requisitos Funcionales (RF)

| ID | Requisito | Implementación |
|----|-----------|---------------|
| RF-05 | Análisis automático del incidente | DataProcessor + MiniLM |
| RF-06 | Generación de prioridad sugerida | PriorityPredictor.predict() |
| RF-07 | Servicio de predicción | PriorityPredictor (batch + individual) |
| RF-08 | Uso de datos históricos | it_tickets_merged.csv (45,988 tickets) |
| RF-09 | Reentrenamiento controlado | train.py (manual) |
| RF-23 | Explicación de predicción | explain_prediction() con SHAP |

### Requisitos No Funcionales (RNF)

| ID | Requisito | Implementación |
|----|-----------|---------------|
| RNF-01 | Response time < 2s | LightGBM optimizado, caché |
| RNF-08 | Precisión mínima 70% | Validación en trainer.validate() |
| RNF-09 | Manejo de datos incompletos | Limpieza y validación en DataProcessor |
| RNF-10 | Capacidad de generalización | Train/val/test split + gap analysis |
| RNF-11 | Evaluación controlada | Sin auto-reentrenamiento en producción |
| RNF-12 | Supervisión humana | Predicción es "sugerida", no final |
| RNF-13 | Transparencia | Explicabilidad integrada (SHAP) |

## Ejemplos de Uso

### Entrenamiento Básico

```python
from src.data_processor import DataProcessor
from src.model_trainer import ModelTrainer
from pathlib import Path

# Preprocesar
processor = DataProcessor()
X_train, X_val, X_test, y_train, y_val, y_test, encoder = processor.preprocess_pipeline(
    Path("data/it_tickets_merged.csv")
)

# Entrenar
trainer = ModelTrainer(encoder=encoder)
trainer.train(X_train, y_train, X_val, y_val)

# Validar
trainer.validate(X_val, y_val)
trainer.test(X_test, y_test)

# Guardar
trainer.save_model()
```

### Predicción con Explicación

```python
from src.predictor import PriorityPredictor

predictor = PriorityPredictor()

text = "Critical hardware failure affecting all users"
explanation = predictor.explain_prediction(text)

print(f"Prioridad: {explanation['priority_label']}")
print(f"Confianza: {explanation['confidence']*100:.1f}%")
print(f"Método: {explanation['explanation_method']}")
```

### Predicción en Lote

```python
texts = [
    "Hardware failure impact",
    "Software bug low urgency",
    "Network connectivity critical"
]

predictions = predictor.batch_predict(texts)
results = predictor.batch_predict_with_confidence(texts)
```

## Notas y Limitaciones

1. **Accuracy**: El modelo usa MiniLM-L6-v2 + LightGBM con hiperparámetros optimizados. Si no se alcanza el 70%, considerar:
   - Ajustar hiperparámetros (num_leaves, max_depth, learning_rate)
   - Usar embeddings más avanzados (MPNet)
   - Agregar meta-features (department, type, tags)
   - Ensemble de modelos

2. **Escalabilidad**: Arquitectura modular permite migración a microservicios sin cambios significativos.

3. **Caché**: Los embeddings se cachean automáticamente. Si cambian los datos, el caché se invalida por hash mismatch.

4. **Rendimiento**:
   - Predicción individual: ~50-100ms (CPU, sin embeddings)
   - Codificación MiniLM: ~2-3ms por texto (batch_size=16)
   - Batch prediction: depende del tamaño y CPU

5. **Meta-features**: Desactivadas por defecto. Requieren que el backend pase metadata (`department`, `type`, `tags`) al predecir.

## Dependencias

| Paquete | Uso |
|---------|-----|
| sentence-transformers | Codificación MiniLM-L6-v2 |
| lightgbm | Modelo principal de clasificación |
| scikit-learn | TF-IDF, métricas, utilidades |
| shap | Explicabilidad de predicciones |
| numpy | Operaciones numéricas |
| pandas | Procesamiento de datos |

## Debugging

### Logs

Los logs se guardan en `logs/`:
- `app.log`: Logs generales de la aplicación
- `training_{timestamp}.log`: Logs específicos de entrenamiento

Cada fase del pipeline loggea información detallada.

### Reportes

Cada entrenamiento genera un reporte en `reports/`:
- `training_report_{timestamp}.md`: Métricas, matriz de confusión, clasificación
- `training_config.json`: Configuración usada

### Tests

```bash
# Ejecutar todos los tests
poetry run python test/test_model.py
```

## Referencias

- Scikit-learn: https://scikit-learn.org/
- LightGBM: https://lightgbm.readthedocs.io/
- Sentence Transformers: https://www.sbert.net/
- SHAP: https://shap.readthedocs.io/
- MiniLM-L6-v2: https://huggingface.co/sentence-transformers/all-MiniLM-L6-v2

## Autor

Equipo IA - Sistema de Priorización de Incidentes IT

Versión: 2.0.0
Última actualización: Mayo 2026
