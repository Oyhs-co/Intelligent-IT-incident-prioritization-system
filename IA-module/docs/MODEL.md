# Módulo IA - Sistema de Priorización de Incidentes IT

Documentación del modelo de machine learning y su arquitectura.

## 📋 Descripción

Módulo que implementa un sistema inteligente de priorización automática de incidentes IT usando:
- **Modelo**: Logistic Regression (RFC-06, RF-05)
- **Vectorización**: TF-IDF (extracción de características)
- **Explicabilidad**: Análisis de palabras clave (RF-23)
- **Framework**: scikit-learn

## 🏗️ Estructura del Proyecto

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
│   ├── ITSM_data.csv        # Dataset principal
│   ├── incident_event_log.csv
│   ├── ITSM_data_cleaned.csv
│   └── all_tickets_processed_improved_v3.csv
│
├── models/                   # Modelos entrenados (generado)
│   ├── priority_classifier_v1.pkl
│   └── priority_classifier_v1_vectorizer.pkl
│
├── test/                     # Tests
│   ├── verify_data.py       # Verificación de datos
│   └── test_model.py        # Tests unitarios
│
├── docs/                     # Documentación
│   └── seleccion_dataset.md # Análisis de datasets
│
├── train.py                 # Script de entrenamiento
├── predict.py               # Script de predicción
├── MODEL.md                 # Este archivo
└── requirements.txt         # Dependencias

```

## 🚀 Cómo Usar

### 1. Entrenamiento del Modelo

```bash
cd IA-module
python train.py
```

**Qué hace:**
- Carga ITSM_data.csv
- Limpia y valida datos
- Genera textos de incidentes desde metadatos
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
python predict.py "Category: Hardware. Impact: Critical. Urgency: High"
```

#### Ejecutar demo:

```bash
python predict.py
```

Mostrará ejemplos de predicción con explicaciones.

### 3. Tests

```bash
python -m pytest test/test_model.py -v
# o
python test/test_model.py
```

## 📊 Módulos Principales

### `utils.py` - Configuración y Utilidades
- `Config`: Clase para parámetros centrales
- `setup_logger()`: Logging estandarizado
- `validate_priority()`: Validación de prioridades
- Rutas y configuraciones centralizadas

### `data_processor.py` - Procesamiento de Datos

**Clase: `DataProcessor`**

```python
processor = DataProcessor()

# Pipeline completo
X_train, X_val, X_test, y_train, y_val, y_test = processor.preprocess_pipeline(
    Path("data/ITSM_data.csv")
)

# Pasos individuales
df = processor.load_data(file_path)
df_clean = processor.clean_data(df)
texts, labels = processor.prepare_texts_and_labels(df_clean)
X = processor.vectorize_texts(texts, fit=True)
```

**Características:**
- ✓ Limpieza de valores inválidos (NS, NA)
- ✓ Generación de textos desde metadatos  
- ✓ Validación de prioridades (1-4)
- ✓ División train/validation/test automática
- ✓ TF-IDF con parámetros optimizados

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
priority = predictor.predict(text)  # Retorna 1-4

# Con confianza
priority, confidence = predictor.predict_with_confidence(text)

# Con explicación (RF-23)
explanation = predictor.explain_prediction(text, top_k=5)
```

**Explicación Incluye:**
- Prioridad predicha (P1-P4)
- Nivel de confianza (0-100%)
- Probabilidades por clase
- Top 5 palabras clave contribuyentes
- Razonamiento textual

## ⚙️ Configuración

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

## 📈 Flujo de Datos

```
ITSM_data.csv
    ↓
[DataProcessor]
    ├─ load_data()
    ├─ clean_data()
    ├─ generate_incident_text()
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
    ├─ predict()              → Prioridad (1-4)
    ├─ predict_with_confidence() → (Prioridad, Confianza)
    └─ explain_prediction()   → Explicación con palabras clave
    ↓
API / Frontend
```

## 🎯 Requisitos Implementados

### Requisitos Funcionales (RF)
- ✅ **RF-05**: Análisis automático del incidente (TextProcessing + TF-IDF)
- ✅ **RF-06**: Generación de prioridad sugerida (Predicción 1-4)
- ✅ **RF-07**: Servicio de predicción (PriorityPredictor.predict())
- ✅ **RF-08**: Uso de datos históricos (ITSM_data.csv)
- ✅ **RF-09**: Reentrenamiento controlado (train.py)
- ✅ **RF-23**: Explicación de predicción (explain_prediction())

### Requisitos No Funcionales (RNF)
- ✅ **RNF-08**: Precisión mínima 70% (validación en trainer.validate())
- ✅ **RNF-09**: Manejo de datos incompletos (limpieza y fillna)
- ✅ **RNF-10**: Capacidad de generalización (train/val/test split)
- ✅ **RNF-11**: Evaluación controlada (no hay automática en prodención)
- ✅ **RNF-12**: Supervisión humana (predicción es "sugerida", no final)
- ✅ **RNF-13**: Transparencia (explicabilidad integrada)

## 🧪 Ejemplos de Uso

### Entrenamiento Básico

```python
from src.data_processor import DataProcessor
from src.model_trainer import ModelTrainer
from pathlib import Path

# Preprocesar
processor = DataProcessor()
X_train, X_val, X_test, y_train, y_val, y_test = processor.preprocess_pipeline(
    Path("data/ITSM_data.csv")
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

## 📝 Notas y Limitaciones

1. **Datos Sintéticos**: Como ITSM_data.csv no contiene descripción textual, se generan textos a partir de metadatos. Esto es una limitación temporal.

2. **Escalabilidad**: El modelo es Un monolito modular, pero la arquitectura permite migración futura a microservicios sin cambios significativos en el código.

3. **Mejoras Futuras**:
   - Integrar descripciones textuales reales
   - Usar embeddings (Word2Vec, BERT)
   - Ensemble de modelos
   - Feature engineering más sofisticado
   - Detección de anomalías

4. **Rendimiento**:
   - Predicción individual: ~10-50ms
   - Batch prediction: depende del tamaño

## 🔍 Debugging

### Logs detallados

Los logs incluyen información de cada fase. Ver `setup_logger()` en utils.py

### Tests

```bash
# Ejecutar todos los tests
python test/test_model.py

# Específicos
python -m pytest test/test_model.py::TestDataProcessor::test_clean_data -v
```

## 📚 Referencias

- Scikit-learn: https://scikit-learn.org/
- TF-IDF: https://en.wikipedia.org/wiki/Tf%E2%80%93idf
- Logistic Regression: https://scikit-learn.org/stable/modules/generated/sklearn.linear_model.LogisticRegression.html

## ✍️ Autor

Equipo IA - Sistema de Priorización de Incidentes IT

Versión: 1.0.0
