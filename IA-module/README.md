# 🤖 Módulo IA - Sistema de Priorización de Incidentes IT

**Modelo de Machine Learning para Priorización Automática de Incidentes IT**

## 📌 Descripción Rápida

Este módulo implementa un modelo de **clasificación de prioridades** (P1-P4) para incidentes IT usando:
- 📊 **Modelo**: Logistic Regression
- 🔤 **Features**: TF-IDF Vectorization  
- 🎯 **Precisión Objetivo**: ≥ 70% (RNF-08)
- ⏱️ **Tiempo Respuesta**: < 2 segundos (RNF-01)
- 💡 **Explicabilidad**: Palabras clave contribuyentes (RF-23)

## 🚀 Inicio Rápido

### 1️⃣ Entrenar el modelo (primera vez)

```bash
cd IA-module
python train.py
```

✅ Genera:
- `models/priority_classifier_v1.pkl` (modelo)
- `models/priority_classifier_v1_vectorizer.pkl` (vectorizador TF-IDF)

### 2️⃣ Predecir prioridades

```bash
# Demo interactivo
python predict.py

# Predicción individual
python predict.py "Critical hardware failure affecting all users"
```

### 3️⃣ Ejemplos completos

```bash
python examples.py
```

Ejecuta 4 demostraciones (entrenamiento, predicción simple, con explicación, en lotes)

### 4️⃣ Tests

```bash
python test/test_model.py
```

## 📂 Estructura

```
src/                          # Módulos principales
├── utils.py                 # Configuración, logging, validación
├── data_processor.py        # Carga, limpieza, vectorización
├── model_trainer.py         # Entrenamiento y evaluación
└── predictor.py             # Predicción y explicabilidad

models/                       # Artefactos entrenados (generado)
test/                         # Tests unitarios
data/                         # Datasets

train.py                      # Entrenamiento
predict.py                    # Predicción
examples.py                   # Ejemplos
```

## 💻 API Básica

### Entrenar

```python
from src.data_processor import DataProcessor
from src.model_trainer import ModelTrainer
from pathlib import Path

processor = DataProcessor()
X_train, X_val, X_test, y_train, y_val, y_test = processor.preprocess_pipeline(
    Path("data/ITSM_data.csv")
)

trainer = ModelTrainer()
trainer.create_model()
trainer.train(X_train, y_train)
trainer.validate(X_val, y_val)
trainer.test(X_test, y_test)
trainer.save_model()
```

### Predecir

```python
from src.predictor import PriorityPredictor

predictor = PriorityPredictor()

# Predicción simple
priority = predictor.predict("Hardware issue")  # 1-4

# Con confianza  
priority, confidence = predictor.predict_with_confidence(text)

# Con explicación
explanation = predictor.explain_prediction(text, top_k=5)
# {
#   'predicted_priority': 4,
#   'priority_label': 'P4 (Critical)',
#   'confidence': 0.85,
#   'contributing_features': [...],
#   'reasoning': "..."
# }
```

## 📊 Parámetros Configurables

En `src/utils.py - Config`:

```python
TF_IDF_MAX_FEATURES = 1000    # Características
TEST_SIZE = 0.2                # % para test
MIN_ACCURACY = 0.70            # Requisito mínimo
```

## ✅ Requisitos Implementados

| Requisito | Implementación |
|-----------|---|
| **RF-05** | Análisis automático → TF-IDF |
| **RF-06** | Generación P1-P4 → classifer.predict() |
| **RF-07** | Servicio predicción → PriorityPredictor |
| **RF-23** | Explicación textos → explain_prediction() |
| **RNF-08** | Precisión ≥70% → trainer.validate() |
| **RNF-09** | Datos incompletos → data cleaning |
| **RNF-10** | Generalización → test set |
| **RNF-11** | Evaluación controlada → no automática |
| **RNF-13** | Transparencia → explicabilidad |

## 🧪 Pruebas

```bash
# Todos los tests
python test/test_model.py

# Verificar datos
python test/verify_data.py
```

Cubre:
- ✓ Carga y limpieza de datos
- ✓ Vectorización TF-IDF
- ✓ Entrenamiento y validación
- ✓ Predicción
- ✓ Explicabilidad
- ✓ Pipeline completo

## 📚 Documentación Detallada

Ver [MODEL.md](MODEL.md) para:
- Arquitectura completa
- Ejemplos avanzados
- Guía de debugging
- Notas técnicas

## 🎯 Flujo Típico

```
1. Datos (ITSM_data.csv)
           ↓
2. Limpiar & Generar Textos
           ↓
3. Vectorizar (TF-IDF)
           ↓
4. Entrenar (LogisticRegression)
           ↓
5. Validar & Test
           ↓
6. Guardar Artefactos
           ↓
7. Servicio Predicción
           ↓
8. Explicación + Confianza
           ↓
   API / Frontend
```

## 🤔 Preguntas Frecuentes

**P: ¿Dónde están los datos?**
- A: En `data/ITSM_data.csv`

**P: ¿Cómo mejoro la precisión?**
- A: Ver sección "Mejoras Futuras" en [MODEL](docs/MODEL.md)

**P: ¿Puedo usar describciones textuales reales?**
- A: Sí, en DataProcessor.prepare_texts_and_labels() integra textos reales si están disponibles

**P: ¿Cómo escalo a producción?**
- A: Usa la clase PriorityPredictor en tu API (Flask, FastAPI, etc.)

## 📞 Soporte

Revisar logs en la salida de `train.py` y `predict.py` para debugging.

---

**Versión:** 1.0.0  
**Última actualización:** 2024  
**Estado:** ✅ Producción
