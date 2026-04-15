# Justificación técnica de la selección de datasets

## Objetivo

Seleccionar datasets adecuados para entrenar un modelo de priorización de incidentes IT. El modelo debe poder clasificar tickets de soporte en niveles de prioridad y generalizar a distintos tipos de incidentes, tanto en lenguaje natural como en contextos de soporte técnico.

## Dataset seleccionado

### `it_tickets_merged.csv`

- **Contenido**: 45,988 tickets de incidentes IT con descripciones textuales reales
- **Columnas**: `text`, `priority`, `department`, `type`, `tags`, `source`
- **Prioridades**: 
  - P1 (Critical) - 17,857 tickets
  - P2 (Medium) - 18,744 tickets
  - P3 (Low) - 9,387 tickets
- **Idioma**: Predominantemente inglés, con texto descriptivo real

### Ventajas del dataset

1. **Texto real**: A diferencia de datasets anteriores que requerían generar texto a partir de metadatos, este incluye descripciones textuales completas de incidentes
2. **Distribución realista**: Los datos reflejan patrones reales de tickets de soporte IT
3. **Contexto adicional**: Incluye `department`, `type`, `tags` que enriquecen el análisis
4. **Volumen adecuado**: 45,988 tickets permiten un entrenamiento robusto

## Estructura del dataset

| Columna | Descripción |
|---------|-------------|
| `text` | Descripción textual del incidente |
| `priority` | Nivel de prioridad (1, 2, 3) |
| `department` | Departamento asociado |
| `type` | Tipo de ticket (Incident, Request, Problem, Change) |
| `tags` | Etiquetas relacionadas |
| `source` | Origen del ticket |

## Uso en el entrenamiento

- **Preprocesamiento**: 
  - Limpieza de valores inválidos
  - Filtrado de textos vacíos
  - Validación de prioridades (1-3)
- **Vectorización**: TF-IDF con 1000 features
- **División**: 70% train, 10% validation, 20% test (estratificada)

## Conclusión

El dataset `it_tickets_merged.csv` es técnicamente adecuado porque:
- Contiene texto descriptivo real de incidentes IT
- Tiene etiquetas de prioridad bien definidas (1-3)
- Proporciona metadatos adicionales útiles
- Tiene volumen suficiente para un entrenamiento robusto

**Fecha de integración**: Abril 2026