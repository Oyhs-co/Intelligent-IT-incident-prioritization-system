# Arquitectura del Módulo IA

Documentación de la arquitectura del sistema de priorización de incidentes.

## Diseño de Capas

El módulo sigue una **arquitectura modular en capas** (Clean Architecture) para máxima escalabilidad:

```
┌─────────────────────────────────────────────────────────────┐
│                 CAPA DE PRESENTACIÓN                        │
│  (Scripts: train.py, predict.py, examples.py)               │
│  - Orquestación del flujo                                   │
│  - Interfaz con usuario/API                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│                CAPA DE APLICACIÓN (SERVICIOS)               │
│  - ModelTrainer (modelo_trainer.py)                         │
│  - PriorityPredictor (predictor.py)                         │
│  - DataProcessor (data_processor.py)                        │
│  Responsabilidades: Lógica de negocio, Orquestación         │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│            CAPA DE UTILIDADES & CONFIGURACIÓN               │
│  - Utils (utils.py): Config, Logger, Validación             │
│  Responsabilidades: Configuración centralizada, Logging     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│              CAPA DE PERSISTENCIA                           │
│  - scikit-learn (pickle files)                              │
│  - CSV (pandas)                                             │
│  - File System                                              │
│  Responsabilidades: Almacenamiento de datos y modelos       │
└─────────────────────────────────────────────────────────────┘
```

## Flujo de Datos

```
it_tickets_merged.csv (45,988 tickets)
    │
    ├─→ DataProcessor.load_data()
    │   └─→ Lectura CSV con pandas
    │
    ├─→ DataProcessor.clean_data()
    │   ├─→ Reemplazo NS/NA → NaN
    │   ├─→ Conversión priority a numérico
    │   ├─→ Filtrado prioridades (1-3)
    │   └─→ Filtrado textos vacíos
    │
    ├─→ DataProcessor.prepare_texts_and_labels()
    │   ├─→ Extracción de columna 'text'
    │   └─→ Extracción de etiquetas (priority)
    │
    ├─→ DataProcessor.vectorize_texts()
    │   ├─→ TfidfVectorizer.fit_transform()
    │   └─→ Matriz sparse (n_samples, n_features)
    │
    ├─→ DataProcessor.split_data()
    │   ├─→ Train: 70%
    │   ├─→ Validation: 10%
    │   └─→ Test: 20%
    │
    ├─→ ModelTrainer.train()
    │   ├─→ LogisticRegression.fit(X_train, y_train)
    │   └─→ Aprendizaje de coeficientes
    │
    ├─→ ModelTrainer.validate/test()
    │   ├─→ Evaluación con métricas
    │   ├─→ Confusion matrix
    │   └─→ Classification report
    │
    ├─→ ModelTrainer.save_model()
    │   └─→ Pickle → models/*.pkl
    │
    └─→ SALIDA (Predicciones)
```

## Sistema de Prioridades

| Valor | Etiqueta | Descripción |
|-------|----------|-------------|
| 1 | P1 (Critical) | Máxima prioridad |
| 2 | P2 (Medium) | Prioridad media |
| 3 | P3 (Low) | Baja prioridad |

## Modulos Principales

### 1. `utils.py` - Configuración y Utilidades

**Responsabilidad**: Centralizar configuración, logging y funciones de soporte.

```python
Config                    # Clase con parámetros centralizados
├── DATA_DIR            # Ruta datos
├── MODELS_DIR          # Ruta modelos
├── TF_IDF_MAX_FEATURES # 1000
├── MIN_ACCURACY        # 0.70 (RNF-08)
└── RESPONSE_TIME_SECONDS # 2 (RNF-01)

setup_logger()           # Logger formateado
validate_priority()      # Validación (1-3)
```

**Patrón**: Singleton + Factory (Config)  
**Escalabilidad**: Fácil agregar nuevos parámetros sin modificar código

### 2. `data_processor.py` - Procesamiento de Datos

**Responsabilidad**: Carga, limpieza, vectorización y preparación de datos.

```
DataProcessor
├── load_data()
│   └─→ Pandas CSV → DataFrame
├── clean_data()
│   ├─→ Reemplazo valores inválidos
│   ├─→ Conversión tipos
│   └─→ Filtrado prioridades válidas (1-3) y textos vacíos
├── prepare_texts_and_labels()
│   ├─→ Extracción de columna 'text'
│   └─→ Extracción de etiquetas de prioridad
├── vectorize_texts(fit=True/False)
│   ├─→ TfidfVectorizer (fit_transform)
│   └─→ Matriz sparse (n_samples, n_features)
├── split_data()
│   └─→ Train/Val/Test (stratified split)
└── preprocess_pipeline()
    └─→ Ejecuta todo el proceso end-to-end
```

**Patron**: Pipeline (encadenamiento de operaciones)  
**Ventaja**: Reusable, testeable, modular

**Configuración en DataProcessor:**
```python
TF-IDF: max_features=1000, min_df=2, max_df=0.8, ngram_range=(1,2)
Split:  test=20%, validation=10%, train=70% (stratified)
```

### 3. `model_trainer.py` - Entrenamiento y Evaluación

**Responsabilidad**: Crear, entrenar, validar y guardar el modelo.

```
ModelTrainer
├── create_model()
│   └─→ LogisticRegression(...)
├── train(X_train, y_train)
│   └─→ model.fit()
├── evaluate(X, y, dataset_name)
│   ├─→ Predicciones
│   └─→ Métricas (accuracy, precision, recall, f1, confusion_matrix)
├── validate(X_val, y_val)
│   └─→ evaluate() + Verificación RNF-08
├── test(X_test, y_test)
│   └─→ evaluate() + Logger
├── save_model()
│   └─→ Pickle → models/priority_classifier_v1.pkl
├── load_model()
│   └─→ Pickle ← models/priority_classifier_v1.pkl
└── predict(X) / predict_proba(X)
    └─→ Predicción
```

**Modelo Usado**: Logistic Regression
- Interpretable (coeficientes)
- Rapido (< 2ms prediccion)
- Explainable (contribucion de features)
- Escalable a mas datos

**Parámetros**:
```python
LogisticRegression(
    max_iter=1000,
    solver='lbfgs',
    class_weight='balanced'
)
```

**Patron**: Strategy (encapsular modelo)  
**Ventaja**: Facil cambiar modelo a Random Forest, XGBoost, etc.

### 4. `predictor.py` - Predicción y Explicabilidad

**Responsabilidad**: Realizar predicciones y proporcionar explicaciones (RF-23).

```
PriorityPredictor
├── predict(text)
│   └─→ Priority (1-3)
├── predict_with_confidence(text)
│   └─→ (Priority, Confidence 0-1)
├── explain_prediction(text, top_k=5)
│   ├─→ Priority predicha
│   ├─→ Confianza
│   ├─→ Probabilidades por clase
│   ├─→ Top K palabras clave
│   ├─→ Reasoning narrativo
│   └─→ {Dict con explicación completa}
├── batch_predict(texts)
│   └─→ Array predicciones
└─→ batch_predict_with_confidence(texts)
    └─→ [(Priority, Confidence), ...]
```

**Explicabilidad (RF-23)**:
```python
explanation = {
    'predicted_priority': 1,
    'priority_label': 'P1 (Critical)',
    'confidence': 0.87,
    'all_probabilities': {
        'P1 (Critical)': 0.87,
        'P2 (Medium)': 0.10,
        'P3 (Low)': 0.03
    },
    'contributing_features': [
        {'feature': 'critical', 'score': 0.45, 'importance': 'positive'},
        {'feature': 'server failure', 'score': 0.38, 'importance': 'positive'}
    ],
    'reasoning': "El sistema sugiere P1 (Critical) con 87% de confianza..."
}
```

**Patron**: Composite (multiples datos de explicacion)  
**Ventaja**: Interpretabilidad total del modelo

## Dependencias Entre Modulos

```
train.py
├─→ DataProcessor (data_processor.py)
│   └─→ Utils (utils.py)
├─→ ModelTrainer (model_trainer.py)
│   └─→ Utils (utils.py)
└─→ save_vectorizer (predictor.py)

predict.py
├─→ PriorityPredictor (predictor.py)
│   └─→ Utils (utils.py)
└─→ [Carga modelos guardados]

test/test_model.py
├─→ DataProcessor
├─→ ModelTrainer
├─→ PriorityPredictor
└─→ Utils
```

**Nota**: Dependencias unidireccionales → Bajo acoplamiento

## Patrones de Diseno

| Patrón | Módulo | Beneficio |
|--------|--------|-----------|
| **Pipeline** | DataProcessor | Reutilizable, testeable |
| **Strategy** | ModelTrainer | Intercambiable (modelo) |
| **Singleton** | Config | Configuración centralizada |
| **Factory** | save_vectorizer | Creación de artefactos |
| **Composite** | explain_prediction() | Múltiples datos explicación |

## Principios SOLID

**S (Single Responsibility)**
- DataProcessor: Procesamiento
- ModelTrainer: Entrenamiento
- PriorityPredictor: Prediccion

**O (Open/Closed)**
- Facil agregar nuevos modelos

**L (Liskov Substitution)**
- Metodos reemplazo directo

**I (Interface Segregation)**
- API minima y clara

**D (Dependency Inversion)**
- Config centralizada via Utils

## Escalabilidad

### Presente (MVP)
```
Local (single process)
└─→ Pickle files
└─→ CSV datasets
└─→ Logistic Regression
```

### Corto Plazo (v2)
```
+ Caché de modelos (Redis)
+ API FastAPI
+ Logging centralizado (ELK)
+ Docker containers
```

### Mediano Plazo (v3)
```
+ Microservicio (Model Service)
+ Monitoring (Prometheus)
+ A/B Testing (nuevos modelos)
+ Reentrenamiento automático
```

### Largo Plazo (Visión)
```
Arquitectura Microservicios:
├─→ API Gateway
├─→ Model Service
├─→ Data Service
├─→ Metrics Service
└─→ Config Service
```

**Sin cambios necesarios en `src/`** - Completamente agnóstico a infraestructura.

## Testabilidad

Estructura permite tests a múltiples niveles:

```
Unit Tests (test_model.py)
├─→ DataProcessor métodos
├─→ ModelTrainer métodos
├─→ Predictor métodos
└─→ Validation functions

Integration Tests
├─→ Pipeline completo (load → train → predict)
├─→ Salvado/carga modelos
└─→ Cross-validation

Load Tests
└─→ Predicción batch rendimiento
```

## Ciclo de Vida del Modelo

```
1. Entrenamiento (train.py)
   └─→ Genera: *.pkl

2. Validación (trainer.validate())
   └─→ Check: accuracy >= 0.70?

3. Producción (models/*.pkl)
   └─→ Servido por: PriorityPredictor

4. Monitoreo (logging, métricas)
   └─→ Track: accuracy en vivo

5. Reentrenamiento (manual con control)
   └─→ Update: *.pkl
```

## Requerimientos Soportados

| Tipo | Requisito | Implementación |
|------|-----------|---|
| **RF** | RF-05 a RF-09 | DataProcessor + ModelTrainer |
| **RF** | RF-23 | ExplainPrediction |
| **RNF** | RNF-08 (≥70%) | trainer.validate() |
| **RNF** | RNF-09 | data cleaning |
| **RNF** | RNF-10 | test set evaluation |
| **RNF** | RNF-11 | no automático |
| **RNF** | RNF-13 | explicabilidad |

---

**Versión**: 1.1.0  
**Estado**: Production-Ready  
**Escalabilidad**: Alta
**Última actualización**: Abril 2026