# Arquitectura del Módulo IA

Documentación de la arquitectura del sistema de priorización de incidentes IT.

## Flujo de Datos

```
it_tickets_merged.csv (45,988 tickets)
    │
    ├-> DataProcessor.load_data()
    │   └-> Lectura CSV con pandas
    │
    ├-> DataProcessor.clean_data()
    │   ├-> Reemplazo NS/NA -> NaN
    │   ├-> Conversión priority a numérico
    │   ├-> Filtrado prioridades (1-3)
    │   ├-> Filtrado textos vacíos
    │   └-> Eliminación de boilerplate LLM
    │
    ├-> DataProcessor.deduplicate_data()
    │   └-> Elimina textos duplicados exactos (~29%)
    │
    ├-> DataProcessor.prepare_texts_and_labels()
    │   ├-> Extracción de columna 'text'
    │   └-> Extracción de etiquetas (priority)
    │
    ├-> DataProcessor.encode_texts()
    │   ├-> MiniLM-L6-v2.encode() o TF-IDF.fit_transform()
    │   └-> Matriz densa (n_samples, 384) o sparse (n_samples, n_features)
    │
    ├-> DataProcessor.split_data()
    │   ├-> Train: 72.25%
    │   ├-> Validation: 12.75%
    │   └-> Test: 15%
    │
    ├-> ModelTrainer.train()
    │   ├-> LightGBM.fit(X_train, y_train, X_val, y_val)
    │   └-> Early stopping con conjunto de validación
    │
    ├-> ModelTrainer.validate/test()
    │   ├-> Evaluación con métricas
    │   ├-> Confusion matrix
    │   └-> Classification report
    │
    ├-> ModelTrainer.save_model()
    │   ├-> Pickle -> models/priority_classifier_v1.pkl
    │   └-> Encoder -> models/encoder/
    │
    └-> SALIDA (Predicciones)
```

## Sistema de Prioridades

| Valor | Etiqueta | Descripción |
|-------|----------|-------------|
| 1 | P1 (Critical) | Requiere atención inmediata |
| 2 | P2 (Medium) | Requiere atención pronta |
| 3 | P3 (Low) | Puede ser programado |

## Modulos Principales

### 1. `utils.py` - Configuración y Utilidades

**Responsabilidad**: Centralizar configuración, logging y funciones de soporte.

```python
Config                    # Clase con parámetros centralizados
├── DATA_DIR              # Ruta datos
├── MODELS_DIR            # Ruta modelos
├── MINILM_MODEL_NAME     # "all-MiniLM-L6-v2"
├── EMBEDDING_DIM         # 384
├── EMBEDDING_BATCH_SIZE  # 16 (RAM <=8GB)
├── LGB_NUM_LEAVES        # 50
├── LGB_MAX_DEPTH         # 7
├── LGB_LEARNING_RATE     # 0.03
├── LGB_N_ESTIMATORS      # 500
├── LGB_EARLY_STOPPING    # 30 rondas
├── MIN_ACCURACY          # 0.70 (RNF-08)
└── RESPONSE_TIME_SECONDS # 2 (RNF-01)

setup_logger()           # Logger formateado con archivo y consola
setup_training_logger()  # Logger específico para entrenamiento
save_training_report()   # Genera reporte Markdown
validate_priority()      # Validación (1-3)
```

**Configuración externa**: `config/default.json` (sobreescribe valores de Config al cargar)

**Patrón**: Singleton + Factory (Config)  
**Escalabilidad**: Fácil agregar nuevos parámetros sin modificar código

### 2. `interfaces.py` - Interfaces Abstractas (SOLID)

**Responsabilidad**: Definir contratos para componentes intercambiables.

```python
IEncoder              # Interfaz para codificación de texto
├── encode(texts)     # Convierte textos a vectores
├── get_dimension()   # Retorna dimensión de salida
├── save(path)        # Guarda en disco
└── load(path)        # Carga desde disco

IClassifier           # Interfaz para clasificación multiclase
├── fit(X, y)         # Entrena el clasificador
├── predict(X)        # Predice etiquetas
├── predict_proba(X)  # Retorna probabilidades por clase
├── save(path)        # Guarda modelo
├── load(path)        # Carga modelo
└── get_feature_importance(X, y)  # Importancia de features
```

**Principio**: Dependency Inversion (DIP) - Los módulos dependen de abstracciones

### 3. `encoders.py` - Codificadores de Texto

**Implementaciones de IEncoder:**

#### MiniLMEncoder
- Usa `sentence-transformers` con modelo `all-MiniLM-L6-v2`
- Embeddings densos de 384 dimensiones
- Optimizado para CPU con batch processing
- Normalización de embeddings para cosine similarity

```python
MiniLMEncoder
├── encode(texts, batch_size=32)  → np.ndarray (n, 384)
├── get_dimension()               → 384
├── save(path)                    → Guarda modelo
└── load(path)                    → Carga modelo
```

#### TFIDFEncoder
- Usa `TfidfVectorizer` de scikit-learn
- Fallback clásico cuando no se requiere MiniLM

```python
TFIDFEncoder
├── encode(texts, batch_size=32)  → np.ndarray (n, vocab_size)
├── get_dimension()               → Tamaño del vocabulario
├── save(path)                    → Pickle del vectorizer
└── load(path)                    → Carga vectorizer
```

### 4. `classifiers.py` - Clasificadores

**Implementaciones de IClassifier:**

#### LightGBMClassifier
- Modelo principal de clasificación
- Optimizado para CPU con `force_row_wise=True` y `n_jobs=-1`
- Early stopping opcional con conjunto de validación
- Soporte para pesos de clase (class_weight='balanced')

```python
LightGBMClassifier
├── __init__(num_leaves=31, max_depth=7, learning_rate=0.03, ...)
├── fit(X_train, y_train, X_val, y_val)  # Early stopping automático
├── predict(X)                           → np.ndarray
├── predict_proba(X)                     → np.ndarray (n, 3)
├── save(path)                           → Pickle
├── load(path)                           → Carga desde pickle
└── get_feature_importance(X, y)         → np.ndarray
```

#### FallbackEnsembleClassifier
- Ensamble de LightGBM + LogisticRegression
- Pesos configurables (default: 60% LightGBM, 40% LR)
- Usado cuando un solo modelo no alcanza precisión suficiente

```python
FallbackEnsembleClassifier
├── __init__(lgb_weight=0.6)
├── fit(X_train, y_train, X_val, y_val)
├── predict(X)                           → np.ndarray
├── predict_proba(X)                     → np.ndarray (n, 3)
├── save(path)                           → Pickle
└── load(path)                           → Carga desde pickle
```

### 5. `data_processor.py` - Procesamiento de Datos

**Clase: `DataProcessor`**

Responsabilidades:
- Carga y limpieza de datos CSV
- Eliminación de boilerplate LLM (14 patrones regex)
- Deduplicación exacta de textos
- Caché de embeddings (.npy) para evitar recodificación
- Extracción de meta-features (department, type, tags)
- Balanceo de clases (undersampling opcional)
- División train/validation/test

```python
DataProcessor
├── load_data(filepath)              → DataFrame
├── clean_data(df)                   → DataFrame limpio
├── remove_boilerplate(text)         → Texto sin boilerplate
├── deduplicate_data(df)             → DataFrame sin duplicados
├── prepare_texts_and_labels(df)     → (texts, labels)
├── encode_texts(texts, batch_size, fit) → np.ndarray
├── extract_meta_features(df)        → np.ndarray (meta-features)
├── balance_classes(texts, labels)   → (texts_balanced, labels_balanced)
├── split_data(X, y)                 → (X_train, X_val, X_test, y_train, y_val, y_test)
├── preprocess_pipeline(input_file, encoder, use_embeddings, ...)
│                                    → Datos divididos + encoder
├── encode_single_text(text)         → np.ndarray (para inferencia)
├── save_encoder(path)               → Guarda encoder
└── load_encoder(path)               → Carga encoder
```

#### Caché de Embeddings
- Hash SHA256 determinístico basado en textos y etiquetas
- Archivos `.npy` en `IA-module/cache/`
- Invalidation automática si cambian los datos
- Elimina ~15 min de codificación MiniLM en ejecuciones repetidas

```python
# Ejemplo de caché
X_{encoder}_{hash}.npy    # Features cacheadas
y_{hash}.npy              # Etiquetas cacheadas
```

#### Meta-Features (Opcional)
- Codificación one-hot de `department`, `type`, `tags`
- Concatenación con embeddings de texto
- Requiere que el backend pase metadata al predecir

#### Configuración del Pipeline:
```python
# Preprocesamiento
- Boilerplate: 14 patrones regex (frases LLM)
- Deduplicación: Textos exactos duplicados
- Split: test=15%, validation=15%, train=72.25% (stratified)

# Opciones configurables
USE_MINILM=True           # MiniLM vs TF-IDF
USE_ENSEMBLE=False        # LightGBM+LR vs LightGBM solo
BALANCE_CLASSES=False     # Undersampling opcional
DEDUPLICATE=True          # Eliminar duplicados
USE_CACHE=True            # Caché de embeddings
USE_META_FEATURES=False   # Meta-features categóricas
```

**Patrones**: Pipeline (encadenamiento), Dependency Injection (encoder)  
**Ventaja**: Reusable, testeable, modular

### 6. `model_trainer.py` - Entrenamiento y Evaluación

**Clase: `ModelTrainer`**

```python
ModelTrainer
├── create_model(n_classes=3)           → IClassifier
├── train(X_train, y_train, X_val, y_val)
├── evaluate(X, y, dataset_name)        → Dict métricas
├── validate(X_val, y_val)              → Métricas + check RNF-08
├── test(X_test, y_test)                → Métricas + generalización
├── save_model(model_path, encoder_path, metadata)
├── load_model(model_path, encoder_path)
├── predict(X)                          → np.ndarray
├── predict_proba(X)                    → np.ndarray
├── predict_with_labels(X)              → np.ndarray (1-index)
├── get_metrics_summary()               → Dict
├── print_summary()                     → Log resumen
└── ModelFactory                        # Factoría de modelos
    ├── create_lightgbm(n_classes, ...)
    ├── create_ensemble()
    ├── create_minilm_encoder()
    └── create_tfidf_encoder(max_features)
```

**Métricas Capturadas:**
- Accuracy, Precision (weighted), Recall (weighted), F1-Score
- Confusion Matrix, Classification Report
- Gap validation-test (RNF-10)

### 7. `predictor.py` - Predicción y Explicabilidad

**Clase: `PriorityPredictor`**

```python
PriorityPredictor
├── predict(text, metadata=None)                    → int (0-2)
├── predict_with_confidence(text, metadata=None)    → (int, float)
├── explain_prediction(text, top_k=5, metadata=None) → Dict
├── batch_predict(texts, metadata_list=None)        → np.ndarray
├── batch_predict_with_confidence(texts, metadata_list=None) → List[(int, float)]
├── _encode_text(text, metadata)                    → np.ndarray
├── _encode_metadata(metadata)                      → np.ndarray
├── _remove_boilerplate(text)                       → str
├── _compute_shap_values(X)                         → np.ndarray
└── _load_artifacts(model_path, encoder_path)
```

**Explicabilidad (RF-23)**:
```python
explanation = {
    'predicted_priority': 1,
    'priority_label': 'P1 (Critical)',
    'priority_description': 'Critical - Requiere atención inmediata',
    'confidence': 0.87,
    'all_probabilities': {
        'P1 (Critical)': 0.87,
        'P2 (Medium)': 0.10,
        'P3 (Low)': 0.03
    },
    'contributing_features': [
        {'feature_index': 42, 'feature_name': 'critical', 'score': 0.45,
         'importance': 'positive', 'abs_score': 0.45},
        {'feature_index': 89, 'feature_name': 'server failure', 'score': 0.38,
         'importance': 'positive', 'abs_score': 0.38}
    ],
    'explanation_method': 'SHAP (SHapley Additive exPlanations)',
    'reasoning': "El sistema sugiere P1 (Critical) con 87% de confianza...",
    'response_time_seconds': 2
}
```

**Backend de explicabilidad**: SHAP (prioridad) o coeficientes del modelo (fallback)

**Meta-features en inferencia**:
- `metadata` dict opcional con `department`, `type`, `tags`
- Codificación consistente con entrenamiento (mismo orden de columnas)
- Compatible con backend que no pasa metadata (funciona solo con texto)

## Dependencias Entre Módulos

```
train.py
├-> DataProcessor (data_processor.py)
│   └-> Interfaces (interfaces.py)
│   └-> Encoders (encoders.py)
│   └-> Utils (utils.py)
├-> ModelTrainer (model_trainer.py)
│   └-> Classifiers (classifiers.py)
│   └-> Encoders (encoders.py)
│   └-> Interfaces (interfaces.py)
│   └-> Utils (utils.py)
└-> Utils (reportes, config)

predict.py
├-> PriorityPredictor (predictor.py)
│   └-> Interfaces (interfaces.py)
│   └-> Utils (utils.py)
└-> [Carga modelos guardados]

test/test_model.py
├-> DataProcessor
├-> ModelTrainer
├-> PriorityPredictor
└-> Utils
```

**Nota**: Dependencias unidireccionales → Bajo acoplamiento

## Patrones de Diseño

| Patrón | Módulo | Beneficio |
|--------|--------|-----------|
| **Pipeline** | DataProcessor | Reutilizable, testeable |
| **Strategy** | IEncoder/IClassifier | Intercambiable (encoder, modelo) |
| **Factory** | ModelFactory | Creación centralizada de modelos |
| **Dependency Injection** | DataProcessor, Predictor | Desacoplamiento de implementaciones |
| **Singleton** | Config | Configuración centralizada |
| **Composite** | explain_prediction() | Múltiples datos explicación |

## Principios SOLID

**S (Single Responsibility)**
- DataProcessor: Procesamiento de datos
- ModelTrainer: Entrenamiento y evaluación
- PriorityPredictor: Predicción y explicabilidad
- Encoders: Solo codificación de texto
- Classifiers: Solo clasificación

**O (Open/Closed)**
- IEncoder/IClassifier permiten agregar nuevos componentes sin modificar el pipeline

**L (Liskov Substitution)**
- MiniLMEncoder y TFIDFEncoder son intercambiables
- LightGBMClassifier y FallbackEnsembleClassifier son intercambiables

**I (Interface Segregation)**
- IEncoder: Solo métodos de codificación
- IClassifier: Solo métodos de clasificación

**D (Dependency Inversion)**
- DataProcessor depende de IEncoder, no de MiniLMEncoder
- ModelTrainer depende de IClassifier, no de LightGBMClassifier

## Escalabilidad

### Presente (MVP)
```
Local (single process)
├─→ Pickle files
├─→ CSV datasets
├─→ MiniLM-L6-v2 + LightGBM
└─→ Caché de embeddings (.npy)
```

### Corto Plazo (v2)
```
+ API FastAPI
+ Logging centralizado (ELK)
+ Docker containers
+ Meta-features desde backend
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
Unit Tests (test/test_model.py)
├─→ DataProcessor métodos
├─→ ModelTrainer métodos
├─→ Predictor métodos
├─→ Encoders (MiniLM, TF-IDF)
├─→ Classifiers (LightGBM, Ensemble)
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
   ├─→ Carga datos, limpia, deduplica
   ├─→ Genera embeddings (con caché)
   ├─→ Entrena LightGBM con early stopping
   └─→ Genera: *.pkl, encoder/, metadata.json, reporte.md

2. Validación (trainer.validate())
   ├─→ Check: accuracy >= 0.70? (RNF-08)
   └─→ Gap validation-test < 5%? (RNF-10)

3. Producción (models/*.pkl)
   ├─→ Servido por: PriorityPredictor
   └─→ Incluye: modelo, encoder, meta-encoders

4. Monitoreo (logging, métricas)
   └─→ Track: accuracy en vivo

5. Reentrenamiento (manual con control)
   ├─→ Invalida caché si datos cambian
   └─→ Update: *.pkl
```

## Requerimientos Soportados

| Tipo | Requisito | Implementación |
|------|-----------|---|
| **RF** | RF-05 | Analisis automático del incidente |
| **RF** | RF-06 | Generación de prioridad sugerida (0-2 → P1-P3) |
| **RF** | RF-07 | Servicio de predicción (PriorityPredictor) |
| **RF** | RF-08 | Uso de datos históricos (it_tickets_merged.csv) |
| **RF** | RF-09 | Reentrenamiento controlado (train.py) |
| **RF** | RF-23 | Explicación de predicción (explain_prediction) |
| **RNF** | RNF-01 | Response time < 2s |
| **RNF** | RNF-08 | Precisión mínima 70% |
| **RNF** | RNF-09 | Manejo de datos incompletos |
| **RNF** | RNF-10 | Capacidad de generalización |
| **RNF** | RNF-11 | Evaluación controlada |
| **RNF** | RNF-12 | Supervisión humana (predicción sugerida) |
| **RNF** | RNF-13 | Transparencia (explicabilidad) |

---

**Versión**: 2.0.0  
**Estado**: Production-Ready  
**Escalabilidad**: Alta  
**Última actualización**: Mayo 2026
