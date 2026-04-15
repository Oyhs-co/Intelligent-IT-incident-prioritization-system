# Integración de Nuevo Dataset: it_tickets_merged.csv

## Resumen de Cambios

Este documento detalla los cambios realizados para incorporar el nuevo dataset `it_tickets_merged.csv` al módulo IA de priorización de incidentes IT.

---

## 1. Modificaciones en Archivos Python

### 1.1 `train.py`
**Cambio**: Actualizar la ruta del archivo de datos

```diff
- data_file = Config.get_data_path("ITSM_data.csv")
+ data_file = Config.get_data_path("it_tickets_merged.csv")
```

### 1.2 `src/data_processor.py`

**Cambio 1**: Actualizar `clean_data()` para usar columnas del nuevo dataset

```diff
- numeric_cols = ["Priority", "Impact", "Urgency"]
- for col in numeric_cols:
-     if col in df_clean.columns:
-         df_clean[col] = pd.to_numeric(df_clean[col], errors="coerce")
- 
- if "Priority" in df_clean.columns:
-     initial_rows = len(df_clean)
-     df_clean = df_clean.dropna(subset=["Priority"])
-     ...
+ if "priority" in df_clean.columns:
+     df_clean["priority"] = pd.to_numeric(df_clean["priority"], errors="coerce")
+ 
+ if "priority" in df_clean.columns:
+     initial_rows = len(df_clean)
+     df_clean = df_clean.dropna(subset=["priority"])
+     ...
```

**Cambio 2**: Filtrar solo prioridades válidas 1-3

```diff
- df_clean = df_clean[df_clean["priority"].isin([1, 2, 3, 4])]
+ df_clean = df_clean[df_clean["priority"].isin([1, 2, 3])]
```

**Cambio 3**: Filtrar textos vacíos

```diff
+ if "text" in df_clean.columns:
+     df_clean = df_clean[df_clean["text"].notna() & (df_clean["text"].str.strip() != "")]
```

**Cambio 4**: Actualizar `prepare_texts_and_labels()` para usar columna `text`

```diff
- texts = df.apply(self.generate_incident_text, axis=1).tolist()
- labels = df["Priority"].astype(int).values
+ texts = df["text"].tolist()
+ labels = df["priority"].astype(int).values
```

**Cambio 5**: Eliminar método `generate_incident_text()` (ya no necesario)

### 1.3 `src/predictor.py`

**Cambio 1**: Actualizar etiquetas de prioridad

```diff
- PRIORITY_LABELS = {1: "P1 (Low)", 2: "P2 (Medium)", 3: "P3 (High)", 4: "P4 (Critical)"}
+ PRIORITY_LABELS = {1: "P1 (Critical)", 2: "P2 (Medium)", 3: "P3 (Low)"}
```

**Cambio 2**: Actualizar comentario de función

```diff
- Requisito RF-06: Generar prioridad sugerida (P1, P2, P3, P4)
+ Requisito RF-06: Generar prioridad sugerida (P1=Critical, P2=Medium, P3=Low)
```

**Cambio 3**: Actualizar índice de coeficientes

```diff
- class_index = int(prediction) - 1  # Índice en array (0-3)
+ class_index = int(prediction) - 1  # Índice en array (0-2)
```

### 1.4 `src/utils.py`

**Cambio**: Actualizar validación de prioridad

```diff
- return p in [1, 2, 3, 4]
+ return p in [1, 2, 3]
```

### 1.5 `test/test_model.py`

**Cambio 1**: Actualizar archivo de datos en setup

```diff
- self.data_file = Config.get_data_path("ITSM_data.csv")
+ self.data_file = Config.get_data_path("it_tickets_merged.csv")
```

**Cambio 2**: Actualizar verificación de columna

```diff
- self.assertIn("Priority", df.columns)
+ self.assertIn("priority", df.columns)
```

**Cambio 3**: Actualizar tests de validación de prioridad

```diff
- self.assertTrue(validate_priority(4))
+ self.assertFalse(validate_priority(4))
```

**Cambio 4**: Actualizar rango de números aleatorios

```diff
- self.y_test = np.random.randint(1, 5, 100)
+ self.y_test = np.random.randint(1, 4, 100)
```

**Cambio 5**: Actualizar forma de probabilidades

```diff
- self.assertEqual(proba.shape[1], 4)
+ self.assertEqual(proba.shape[1], 3)
```

**Cambio 6**: Actualizar tests de etiquetas

```diff
- self.assertEqual(len(labels), 4)
- self.assertIn(4, labels)
+ self.assertEqual(len(labels), 3)
+ self.assertIn(3, labels)
```

---

## 2. Sistema de Prioridades

### Antes
| Valor | Etiqueta |
|-------|----------|
| 1 | P1 (Low) |
| 2 | P2 (Medium) |
| 3 | P3 (High) |
| 4 | P4 (Critical) |

### Después
| Valor | Etiqueta | Descripción |
|-------|----------|-------------|
| 1 | P1 (Critical) | Máxima prioridad |
| 2 | P2 (Medium) | Prioridad media |
| 3 | P3 (Low) | Baja prioridad |

---

## 3. Estructura del Dataset

### `it_tickets_merged.csv`

| Columna | Tipo | Descripción |
|---------|------|-------------|
| `text` | string | Descripción textual del incidente |
| `priority` | int | Nivel de prioridad (1-3) |
| `department` | string | Departamento asociado |
| `type` | string | Tipo de ticket (Incident, Request, etc.) |
| `tags` | string | Etiquetas relacionadas |
| `source` | string | Origen del ticket |

**Volumen**: 45,988 tickets

**Distribución de prioridades**:
- P1 (Critical): 17,857 (38.8%)
- P2 (Medium): 18,744 (40.8%)
- P3 (Low): 9,387 (20.4%)

---

## 4. Documentación Actualizada

Los siguientes archivos markdown fueron actualizados:

- `docs/selccion_dataset.md` - Justificación del nuevo dataset
- `docs/MODEL.md` - Documentación del modelo
- `docs/ARQUITECTURA.md` - Arquitectura del sistema

---

## 5. Ejecución

### Entrenamiento
```bash
cd IA-module
poetry install
poetry run python train.py
```

### Predicción
```bash
poetry run python predict.py "Critical server failure"
```

### Tests
```bash
poetry run python test/test_model.py
```

---

## 6. Notas

- El modelo Logístico actual alcanza ~48% accuracy (por debajo del 70% requerido)
- Se recomienda optimización adicional (hiperparámetros, modelo alternativo, feature engineering)
- Los cambios son backward-incompatible con modelos entrenados anteriormente

---

**Fecha de integración**: Abril 2026  
**Versión**: 1.1.0