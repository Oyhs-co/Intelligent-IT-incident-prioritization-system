# Módulo IA - Sistema de Priorización de Incidentes IT

Documentación del modelo de machine learning y su arquitectura.

## Descripcion

Módulo que implementa un sistema inteligente de priorización automática de incidentes IT usando:
- **Modelo**: Logistic Regression (RFC-06, RF-05)
- **Vectorización**: TF-IDF (extracción de características)
- **Explicabilidad**: Análisis de palabras clave (RF-23)
- **Framework**: scikit-learn

## Sistema de Prioridades

| Prioridad | Etiqueta | Descripción |
|-----------|----------|--------------|
| P1 | Critical | Incidentes de máxima urgencia |
| P2 | Medium | Incidentes de prioridad media |
| P3 | Low | Incidentes de baja prioridad |

## Estructura del Proyecto

```
IA-module/
├── src/                      # Módulos principales
│   ├── __init__.py          # Inicialización del paquete
│   ├── utils.py             # Utilidades y configuración
│   ├── data_processor.py    # Preprocesamiento de datos
│   ├── model_trainer.py     # Entrenamiento y evaluación
│   └── predictor.py         # Predicción y explicabilidad
│
├── data/                     # Datos
│   ├── it_tickets_merged.csv    # Dataset principal (45,988 tickets)
│   ├── aa_dataset-tickets-multi-lang-5-2-50-version.csv
│   └── IT Support Ticket Data.csv
│
├── models/                   # Modelos entrenados (generado)
│   ├── priority_classifier_v1.pkl
│   └── priority_classifier_v1_vectorizer.pkl
│
├── test/                     # Tests
│   ├── test_model.py        # Tests unitarios
│   └── examples.py          # Ejemplos de uso
│
├── docs/                     # Documentación
│   └── seleccion_dataset.md # Análisis de datasets
│
├── train.py                 # Script de entrenamiento
├── predict.py               # Script de predicción
└── pyproject.toml           # Dependencias (Poetry)

```

## Como Usar

### 1. Entrenamiento del Modelo

```bash
cd IA-module
poetry run python train.py
```

**Qué hace:**
- Carga `it_tickets_merged.csv`
- Limpia y valida datos
- Extrae textos de la columna `text`
- Vectoriza con TF-IDF (1000 features)
- Entrena Logistic Regression
- Valida y evalúa el modelo
- Guarda artefactos en `models/`

**Salida esperada:**
- `models/priority_classifier_v1.pkl` - Modelo entrenado
- `models/priority_classifier_v1_vectorizer.pkl` - Vectorizador TF-IDF
- Métricas de desempeño (Accuracy, Precision, Recall, F1)

### 2. Predicción

#### Desde línea de comandos:

```bash
poetry run python predict.py "Critical server failure affecting all users"
```

#### Ejecutar demo:

```bash
poetry run python predict.py
```

Mostrará ejemplos de predicción con explicaciones.

### 3. Tests

```bash
poetry run python test/test_model.py
```

## Modulos Principales

### `utils.py` - Configuración y Utilidades
- `Config`: Clase para parámetros centrales
- `setup_logger()`: Logging estandarizado
- `validate_priority()`: Validación de prioridades (1-3)
- Rutas y configuraciones centralizadas

### `data_processor.py` - Procesamiento de Datos

**Clase: `DataProcessor`**

```python
processor = DataProcessor()

# Pipeline completo
X_train, X_val, X_test, y_train, y_val, y_test = processor.preprocess_pipeline(
    Path("data/it_tickets_merged.csv")
)

# Pasos individuales
df = processor.load_data(file_path)
df_clean = processor.clean_data(df)
texts, labels = processor.prepare_texts_and_labels(df_clean)
X = processor.vectorize_texts(texts, fit=True)
```

**Características:**
- Limpieza de valores inválidos (NS, NA)
- Filtrado de textos vacíos
- Validación de prioridades (1-3)
- División train/validation/test automática
- TF-IDF con parámetros optimizados

### `model_trainer.py` - Entrenamiento

**Clase: `ModelTrainer`**

```python
trainer = ModelTrainer()
trainer.create_model()
trainer.train(X_train, y_train)

# Validación
val_metrics = trainer.validate(X_val, y_val)

# Test
test_metrics = trainer.test(X_test, y_test)

# Guardar
trainer.save_model()
```

**Métricas Capturadas:**
- Accuracy
- Precision (weighted)
- Recall (weighted)
- F1-Score
- Confusion Matrix
- Classification Report

### `predictor.py` - Predicción y Explicabilidad

**Clase: `PriorityPredictor`**

```python
predictor = PriorityPredictor()

# Predicción simple
priority = predictor.predict(text)  # Retorna 1-3

# Con confianza
priority, confidence = predictor.predict_with_confidence(text)

# Con explicación (RF-23)
explanation = predictor.explain_prediction(text, top_k=5)
```

**Explicación Incluye:**
- Prioridad predicha (P1-P3)
- Nivel de confianza (0-100%)
- Probabilidades por clase
- Top 5 palabras clave contribuyentes
- Razonamiento textual

## Configuracion

Todos los parámetros centralizados en `src/utils.py - Config`:

```python
# Parámetros del modelo
TF_IDF_MAX_FEATURES = 1000      # Características TF-IDF
TF_IDF_MIN_DF = 2                # Frecuencia mínima de documento
TF_IDF_MAX_DF = 0.8              # Frecuencia máxima en corpus

# División de datos
TEST_SIZE = 0.2                  # 20% para test
VALIDATION_SIZE = 0.1            # 10% para validation

# Requerimientos
MIN_ACCURACY = 0.70              # RNF-08: Precisión mínima 70%
RESPONSE_TIME_SECONDS = 2        # RNF-01: < 2 segundos
```

## Flujo de Datos

```
it_tickets_merged.csv
    ↓
[DataProcessor]
    ├─ load_data()
    ├─ clean_data()
    ├─ prepare_texts_and_labels()
    └─ vectorize_texts()  → TF-IDF Features
    ↓
    X_train, y_train  (vectores y etiquetas)
    ↓
[ModelTrainer]
    ├─ create_model()  → LogisticRegression
    ├─ train()
    ├─ validate()
    ├─ test()
    └─ save_model()
    ↓
    priority_classifier_v1.pkl
    ↓
[PriorityPredictor]
    ├─ predict()              → Prioridad (1-3)
    ├─ predict_with_confidence() → (Prioridad, Confianza)
    └─ explain_prediction()   → Explicación con palabras clave
    ↓
API / Frontend
```

## Requisitos Implementados

### Requisitos Funcionales (RF)
- **RF-05**: Analisis automatico del incidente (TextProcessing + TF-IDF)
- **RF-06**: Generacion de prioridad sugerida (Prediccion 1-3)
- **RF-07**: Servicio de prediccion (PriorityPredictor.predict())
- **RF-08**: Uso de datos historicos (it_tickets_merged.csv)
- **RF-09**: Reentrenamiento controlado (train.py)
- **RF-23**: Explicacion de prediccion (explain_prediction())

### Requisitos No Funcionales (RNF)
- **RNF-08**: Precision minima 70% (validacion en trainer.validate())
- **RNF-09**: Manejo de datos incompletos (limpieza y fillna)
- **RNF-10**: Capacidad de generalizacion (train/val/test split)
- **RNF-11**: Evaluacion controlada (no hay automatica en prodencion)
- **RNF-12**: Supervision humana (prediccion es "sugerida", no final)
- **RNF-13**: Transparencia (explicabilidad integrada)

## Ejemplos de Uso

### Entrenamiento Básico

```python
from src.data_processor import DataProcessor
from src.model_trainer import ModelTrainer
from pathlib import Path

# Preprocesar
processor = DataProcessor()
X_train, X_val, X_test, y_train, y_val, y_test = processor.preprocess_pipeline(
    Path("data/it_tickets_merged.csv")
)

# Entrenar
trainer = ModelTrainer()
trainer.create_model()
trainer.train(X_train, y_train)

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
print(f"Palabras clave: {[f['feature'] for f in explanation['contributing_features']]}")
```

### Batch Prediction

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

1. **Accuracy actual**: El modelo Logístico actual alcanza ~48% accuracy. Se requiere optimización (hiperparámetros, mejor modelo, feature engineering).

2. **Escalabilidad**: El modelo es un monolito modular, pero la arquitectura permite migración futura a microservicios sin cambios significativos en el código.

3. **Mejoras Futuras**:
   - Ajuste de hiperparámetros
   - Usar embeddings (Word2Vec, BERT)
   - Ensemble de modelos
   - Feature engineering más sofisticado
   - Detección de anomalías

4. **Rendimiento**:
   - Predicción individual: ~10-50ms
   - Batch prediction: depende del tamaño

## Debugging

### Logs detallados

Los logs incluyen información de cada fase. Ver `setup_logger()` en utils.py

### Tests

```bash
# Ejecutar todos los tests
poetry run python test/test_model.py
```

## Referencias

- Scikit-learn: https://scikit-learn.org/
- TF-IDF: https://en.wikipedia.org/wiki/Tf%E2%80%93idf
- Logistic Regression: https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html

## Autor

Equipo IA - Sistema de Priorización de Incidentes IT

Versión: 1.1.0