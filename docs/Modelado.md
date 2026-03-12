# Modelado del Sistema Inteligente de Priorización de Incidentes IT

**curso:** Ingeniería de Software  
**profesor:** Aisner Marrugo  
**periodo:** 2026-1P  
**Fecha de Entrega:** 11 de marzo de 2026
**escuela** Escuela de Transformacion digital
**Estudiantes:**

- Omar Yesid Hernandez Sotelo
- Jorge Eliecer Martelo Martelo
- Jesus David Velazquez Mercado
- Jesus Manuel Mercado Machado

---

## 1. Introducción

Este documento presenta el modelado del Sistema Inteligente de Priorización de Incidentes IT. El objetivo es especificar la estructura funcional del sistema mediante diagramas UML y análisis detallado, demostrando la comprensión técnica del proyecto y la organización del trabajo del equipo de desarrollo.

---

## 2. Descripción del Problema

La empresa **TechSolutions Group S.A.S** recibe diariamente múltiples incidentes y tickets de soporte en su ambiente de trabajo. Actualmente, estos incidentes se clasifican y priorizan manualmente, lo que genera:

- **Demoras en la atención:** Los incidentes críticos no se atienden con la rapidez requerida
- **Inconsistencia:** Diferentes técnicos aplican criterios distintos de priorización
- **Alto costo operativo:** Requiere personal dedicado a tareas repetitivas de clasificación
- **Falta de escalabilidad:** El proceso no puede adaptarse al crecimiento de tickets

El sistema propuesto automatiza estos procesos utilizando inteligencia artificial para clasificar, asignar y priorizar incidentes de forma inteligente y consistente.

---

## 3. Usuarios del Sistema

| Usuario | Descripción | Interacción Principal |
|---------|------------|----------------------|
| **Reportador de Incidentes** | Empleados de TechSolutions que reportan problemas técnicos | Crear nuevos tickets describiendo el incidente |
| **Técnico de Soporte** | Personal encargado de resolver los incidentes | Recibir incidentes priorizados automáticamente y actualizar su estado |
| **Administrador de Sistema** | Gestor IT que supervisa el sistema | Configurar reglas de priorización, revisar decisiones de IA y generar reportes |
| **Supervisor de Incidentes** | Responsable de la calidad del servicio | Monitorear métricas, validar prioridades asignadas y ajustar criterios |

---

## 4. Funcionalidad Principal del Sistema

La funcionalidad central del sistema es **clasificar y priorizar incidentes de forma inteligente**. Cuando un nuevo incidente es reportado, el sistema:

1. Recibe la descripción del ticket
2. Analiza el contenido usando procesamiento de lenguaje natural (NLP)
3. Busca incidentes similares en el histórico usando embeddings semánticos
4. Aplica reglas de negocio y criterios SLA
5. Asigna automáticamente un nivel de prioridad (P1, P2, P3, P4)
6. Proporciona una justificación clara de la decisión

---

## 5. Modelado del Sistema

### 5.1 Diagrama de Casos de Uso

El sistema interactúa con cuatro actores principales que ejecutan las siguientes funcionalidades:

**Actores:**

- Reportador de Incidentes
- Técnico de Soporte
- Administrador del Sistema
- Supervisor de Incidentes

**Funcionalidades Principales (Casos de Uso):**

1. **Reportar Incidente:** El reportador crea un nuevo ticket describiendo el problema
2. **Clasificar y Priorizar Incidente:** El sistema analiza automáticamente el incidente y asigna prioridad
3. **Asignar Técnico:** El sistema sugiere automáticamente el técnico más adecuado
4. **Buscar Incidentes Similares:** El sistema busca en el histórico casos similares y sus resoluciones
5. **Actualizar Estado de Incidente:** El técnico modifica el estado (Abierto → En Progreso → Resuelto → Cerrado)
6. **Generar Reportes y Métricas:** El administrador obtiene análisis de rendimiento del sistema
7. **Reentrenar Modelo de IA:** El sistema aprende de validaciones manuales para mejorar futuras clasificaciones
8. **Configurar Reglas de Negocio:** El administrador define criterios de priorización personalizados

![Diagrama de casos de usos](/IMG/DiagramUseCases.png)

---

### 5.2 Diagrama de Clases / Modelo de Datos

**Entidades Principales y Relaciones:**

![Diagrama de Clases — Sistema Inteligente de Priorización de Incidentes IT](<Diagrama de Clases — Sistema Inteligente de Priorización de Incidentes IT.png>)

### 5.3 Diagrama de Actividad

Flujo principal desde la entrada del incidente hasta la asignación de prioridad:

![Diagrama de actividad](/IMG/DiagramActivity.jpg)

---

## 6. Análisis y Mejoras del Diseño

### 6.1 Aspectos Más Difíciles de Modelar

- **La toma de decisiones de IA:** Integrar múltiples componentes (NLP, embeddings, modelado, reglas) de forma coherente requirió definir claramente cuándo interviene cada uno
- **Balanceo entre automatización y control manual:** Determinar el nivel de confianza de la IA para actuar sin intervención humana fue complejo
- **Tratamiento de casos ambiguos:** Incidentes que podrían pertenecer a múltiples categorías o tener múltiples prioridades válidas

### 6.2 Aspectos que Podrían Mejorarse

- **Feedback circular automático:** Implementar un sistema donde el sistema aprenda automáticamente de las validaciones manuales sin intervención
- **Explicabilidad mejorada:** Usar técnicas de IA explicable (XAI) para justificar mejor las decisiones automáticas
- **Multiidioma:** Ampliar NLP para soportar múltiples idiomas en las descripciones de incidentes
- **Análisis predictivo:** Predecir tiempo de resolución y recursos necesarios antes de asignar

### 6.3 Riesgos si el Sistema Crece

- **Complejidad en mantenimiento:** Conforme se agreguen más reglas y actores, el sistema puede volverse difícil de mantener
- **Degradación de rendimiento:** Con millones de incidentes históricos, la búsqueda de similares podría volverse lenta
- **Sesgo en el modelo de IA:** Si el modelo no se reentren, podría producir prioridades incorrectas en nuevos tipos de incidentes
- **Sobrecarga del sistema:** Sin escalado horizontal, el procesamiento de IA podría convertirse en cuello de botella
- **Consistencia de datos:** Garantizar que todas las fuentes de incidentes tengan formato consistente es un desafío en crecimiento