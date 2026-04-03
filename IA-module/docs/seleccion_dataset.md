# Selección del Dataset para Entrenamiento de IA en Sistema de Priorización de Incidentes IT

## Introducción

El sistema de priorización inteligente de incidentes IT requiere un conjunto de datos adecuado para entrenar modelos de IA capaces de asignar prioridades a incidentes basados en características como impacto, urgencia, categoría y otros metadatos relevantes. En este documento, se analiza los datasets disponibles en la carpeta `data/` del módulo IA y se justifica la selección del más apropiado para el entrenamiento del modelo.

## Datasets Disponibles

### 1. `incident_event_log.csv`
- **Descripción**: Este dataset contiene un log de eventos temporales de incidentes. Cada fila representa un cambio de estado en un incidente específico a lo largo del tiempo.
- **Columnas principales**: `number` (ID del incidente), `incident_state`, `active`, `reassignment_count`, `reopen_count`, `sys_mod_count`, `made_sla`, `caller_id`, `opened_by`, `opened_at`, `sys_created_by`, `sys_created_at`, `sys_updated_by`, `sys_updated_at`, `contact_type`, `location`, `category`, `subcategory`, `u_symptom`, `cmdb_ci`, `impact`, `urgency`, `priority`, `assignment_group`, `assigned_to`, `knowledge`, `u_priority_confirmation`, `notify`, `problem_id`, `rfc`, `vendor`, `caused_by`, `closed_code`, `resolved_by`, `resolved_at`, `closed_at`.
- **Ventajas**: Proporciona una vista temporal del ciclo de vida de los incidentes, útil para análisis de procesos y predicción de tiempos de resolución.
- **Desventajas**: Es un log de eventos, no un dataset estático por incidente. Para entrenamiento de IA, requiere agregación por incidente, lo que puede complicar el preprocesamiento. No incluye descripciones textuales detalladas de los incidentes.

### 2. `ITSM_data.csv`
- **Descripción**: Dataset de datos de IT Service Management (ITSM) con información estructurada por incidente.
- **Columnas principales**: `CI_Name`, `CI_Cat`, `CI_Subcat`, `WBS`, `Incident_ID`, `Status`, `Impact`, `Urgency`, `Priority`, `number_cnt`, `Category`, `KB_number`, `Alert_Status`, `No_of_Reassignments`, `Open_Time`, `Reopen_Time`, `Resolved_Time`, `Close_Time`, `Handle_Time_hrs`, `Closure_Code`, `No_of_Related_Interactions`, `Related_Interaction`, `No_of_Related_Incidents`, `No_of_Related_Changes`, `Related_Change`.
- **Ventajas**: Incluye campos clave para priorización como `Impact`, `Urgency` y `Priority`. También contiene tiempos de manejo, reasignaciones y códigos de cierre, lo que permite modelar la complejidad y duración de los incidentes. Es un dataset estático por incidente, facilitando el entrenamiento directo.
- **Desventajas**: No incluye descripciones textuales libres de los incidentes, lo que limita el uso de técnicas de procesamiento de lenguaje natural (NLP) para extraer características semánticas.

### 3. `all_tickets_processed_improved_v3.csv`
- **Descripción**: Dataset de tickets procesados con texto descriptivo y clasificación por tema.
- **Columnas principales**: `Document` (texto del ticket), `Topic_group` (clasificación como Hardware, Access, etc.).
- **Ventajas**: Proporciona texto rico para análisis NLP, permitiendo clasificar incidentes por tema y extraer características semánticas.
- **Desventajas**: No incluye campos de priorización estructurados como `Impact`, `Urgency` o `Priority`. Las clasificaciones son por tema, no por prioridad numérica o categórica.

## Análisis de Requisitos del Sistema

El sistema de priorización de incidentes IT busca asignar prioridades automáticas a nuevos incidentes basados en sus características. Los requisitos clave incluyen:
- Predicción de `Priority` basada en `Impact` y `Urgency`.
- Consideración de tiempos de resolución, reasignaciones y categorías.
- Potencial integración de texto descriptivo para mejorar la precisión mediante NLP.

Para el entrenamiento de IA, el dataset ideal debe contener:
- Etiquetas de prioridad (target variable).
- Características predictoras como impacto, urgencia, categoría, tiempos, etc.
- Opcionalmente, texto para modelos avanzados.

## Decisión de Selección

### Dataset Principal: `ITSM_data.csv`
- **Justificación**: Este dataset es el más adecuado para el entrenamiento inicial del modelo de priorización. Contiene directamente los campos esenciales para calcular o predecir prioridades (`Impact`, `Urgency`, `Priority`), así como métricas adicionales como `No_of_Reassignments`, `Handle_Time_hrs` y `Category`, que son indicadores de complejidad y severidad. La estructura tabular facilita el preprocesamiento y el entrenamiento de modelos supervisados como regresión logística, árboles de decisión o redes neuronales.
- **Razones**:
  - **Disponibilidad de Etiquetas**: `Priority` es la variable objetivo clara, con valores numéricos o categóricos que permiten evaluación directa.
  - **Características Relevantes**: Incluye factores determinantes de prioridad según estándares ITSM (e.g., ITIL), como impacto y urgencia.
  - **Escalabilidad**: Con miles de incidentes, proporciona un volumen suficiente para entrenamiento robusto.
  - **Facilidad de Uso**: Es un dataset estático, evitando la necesidad de agregación temporal compleja.

### Necesidad de Mezcla de Datasets
- **Evaluación**: Una mezcla con `all_tickets_processed_improved_v3.csv` sería beneficiosa para enriquecer el modelo con características textuales, permitiendo un enfoque híbrido (estructurado + NLP). Sin embargo, los IDs de incidentes no coinciden entre `ITSM_data.csv` (e.g., IM0000004) y `all_tickets_processed_improved_v3.csv` (sin IDs explícitos), lo que impide una fusión directa por clave.
- **Alternativas**:
  - Usar `all_tickets_processed_improved_v3.csv` para entrenar un modelo de clasificación de temas separado, y luego integrar las predicciones de tema como una característica adicional en el modelo de priorización basado en `ITSM_data.csv`.
  - Si se requiere texto, considerar la expansión futura del dataset o el uso de `incident_event_log.csv` para extraer descripciones de síntomas (`u_symptom`), aunque estas son limitadas.
- **Conclusión sobre Mezcla**: No es estrictamente necesaria para un modelo básico de priorización basado en metadatos. Para versiones avanzadas con NLP, se recomienda integrar texto si se obtiene correspondencia o se recopilan nuevos datos. Por ahora, `ITSM_data.csv` es suficiente y óptimo.

### Por Qué No los Otros Datasets como Principales
- `incident_event_log.csv`: Aunque útil para análisis predictivo de tiempos y estados, su naturaleza temporal requiere preprocesamiento adicional (e.g., pivoteo por incidente), y carece de una etiqueta de prioridad final clara por incidente. Es más adecuado para modelos de series temporales o análisis de procesos, no para priorización directa.
- `all_tickets_processed_improved_v3.csv`: Excelente para clasificación de temas, pero insuficiente para priorización ya que no incluye prioridades. Podría usarse como complemento, pero no como base.

## Recomendaciones para Entrenamiento
- **Preprocesamiento**: Limpiar valores faltantes en `ITSM_data.csv` (e.g., `Impact` y `Urgency` tienen valores como "NS" o "NA"). Convertir tiempos a formatos numéricos (e.g., duración en horas).
- **Modelo Inicial**: Usar algoritmos como Random Forest o Gradient Boosting para predecir `Priority` basado en `Impact`, `Urgency`, `Category`, etc.
- **Validación**: Dividir en train/test (80/20), usar métricas como accuracy, precision y recall para prioridades.
- **Mejoras Futuras**: Integrar NLP si se obtiene texto correspondiente, o usar embeddings de `Topic_group` de `all_tickets_processed_improved_v3.csv`.

## Conclusión

El dataset seleccionado es `ITSM_data.csv` como base principal para el entrenamiento de la IA, debido a su alineación directa con los requisitos de priorización. No se requiere una mezcla inmediata, pero se sugiere explorar integraciones para enriquecer el modelo. Esta selección asegura un entrenamiento eficiente y efectivo para el sistema de priorización de incidentes IT.