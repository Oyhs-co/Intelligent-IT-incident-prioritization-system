# Documentación de la API - Sistema de Priorización de Incidentes IT

Este documento describe detalladamente cada ruta de la API REST del sistema.

## Base URL

```
Desarrollo: http://localhost:8000
Producción: https://api.tu-dominio.com
```

## Formato de Respuestas

Todas las respuestas siguen el formato JSON. Los errores incluyen:
```json
{
  "detail": "Mensaje de error descriptivo"
}
```

---

## 1. Endpoints de Sistema

### GET /
Obtiene información general del sistema.

**Respuesta (200 OK):**
```json
{
  "name": "Incident Prioritization System",
  "version": "1.0.0",
  "status": "running"
}
```

---

### GET /health
Health check básico del sistema.

**Respuesta (200 OK):**
```json
{
  "status": "healthy"
}
```

---

### GET /metrics
Métricas de Prometheus para monitoreo.

**Respuesta (200 OK):**
```
# HELP itsm_incidents_created_total Total incidents created
# TYPE itsm_incidents_created_total counter
itsm_incidents_created_total 150

# HELP itsm_model_avg_confidence AI model average confidence
# TYPE itsm_model_avg_confidence gauge
itsm_model_avg_confidence 0.85
```

---

## 2. Endpoints de Incidentes

### Prefix: `/api/v1/incidents`

---

### POST /api/v1/incidents/
Crea un nuevo incidente en el sistema.

**Headers:**
```
Content-Type: application/json
Authorization: Bearer <token>  (opcional)
```

**Request Body:**
```json
{
  "title": "string (requerido, 1-200 caracteres)",
  "description": "string (requerido, 1-5000 caracteres)",
  "category": "string (opcional) - ej: hardware, software, red",
  "subcategory": "string (opcional)",
  "urgency": "integer (1-5, default: 3)",
  "impact": "integer (1-5, default: 3)"
}
```

**Ejemplo:**
```bash
curl -X POST http://localhost:8000/api/v1/incidents/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Servidor de producción no responde",
    "description": "El servidor principal no está respondiendo desde hace 30 minutos",
    "category": "hardware",
    "urgency": 5,
    "impact": 4
  }'
```

**Respuesta (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "ticket_number": "INC-001",
  "title": "Servidor de producción no responde",
  "description": "El servidor principal no está respondiendo desde hace 30 minutos",
  "category": "hardware",
  "subcategory": null,
  "status": "new",
  "priority": null,
  "priority_label": null,
  "urgency": 5,
  "impact": 4,
  "confidence_score": null,
  "explanation": null,
  "sla_deadline": "2024-01-15T10:30:00",
  "source": "web",
  "tags": [],
  "reporter_id": null,
  "assigned_to": null,
  "created_at": "2024-01-15T09:30:00",
  "updated_at": "2024-01-15T09:30:00",
  "is_sla_breached": false
}
```

**Códigos de Error:**
- `422 Unprocessable Entity`: Validación fallida

---

### GET /api/v1/incidents/
Lista incidentes con paginación y filtros.

**Query Parameters:**
| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| skip | integer | 0 | Número de registros a omitir |
| limit | integer | 100 | Límite de registros (máx 1000) |
| status | string | - | Filtrar por estado |
| priority | integer | - | Filtrar por prioridad (1-4) |
| category | string | - | Filtrar por categoría |

**Valores posibles para status:**
- `new`
- `open`
- `in_progress`
- `pending`
- `resolved`
- `closed`

**Ejemplo:**
```bash
# Listar primeros 10 incidentes
curl "http://localhost:8000/api/v1/incidents/?skip=0&limit=10"

# Filtrar por estado y prioridad
curl "http://localhost:8000/api/v1/incidents/?status=open&priority=1"

# Filtrar por categoría
curl "http://localhost:8000/api/v1/incidents/?category=hardware"
```

**Respuesta (200 OK):**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "ticket_number": "INC-001",
      "title": "Servidor de producción no responde",
      "description": "...",
      "category": "hardware",
      "status": "new",
      "priority": 1,
      "priority_label": "Critical",
      "urgency": 5,
      "impact": 4,
      "confidence_score": 0.92,
      "explanation": "...",
      "sla_deadline": "2024-01-15T10:30:00",
      "source": "web",
      "tags": [],
      "reporter_id": null,
      "assigned_to": null,
      "created_at": "2024-01-15T09:30:00",
      "updated_at": "2024-01-15T09:30:00",
      "is_sla_breached": false
    }
  ],
  "total": 150,
  "skip": 0,
  "limit": 10
}
```

---

### GET /api/v1/incidents/{incident_id}
Obtiene un incidente específico por su ID.

**Path Parameters:**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| incident_id | UUID | ID único del incidente |

**Ejemplo:**
```bash
curl http://localhost:8000/api/v1/incidents/550e8400-e29b-41d4-a716-446655440000
```

**Respuesta (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "ticket_number": "INC-001",
  "title": "Servidor de producción no responde",
  "description": "El servidor principal no está respondiendo...",
  "category": "hardware",
  "subcategory": null,
  "status": "in_progress",
  "priority": 1,
  "priority_label": "Critical",
  "urgency": 5,
  "impact": 4,
  "confidence_score": 0.92,
  "explanation": "High urgency and impact values indicate critical issue",
  "sla_deadline": "2024-01-15T10:30:00",
  "source": "web",
  "tags": ["critical", "production"],
  "reporter_id": "123e4567-e89b-12d3-a456-426614174000",
  "assigned_to": "123e4567-e89b-12d3-a456-426614174001",
  "created_at": "2024-01-15T09:30:00",
  "updated_at": "2024-01-15T09:45:00",
  "is_sla_breached": false
}
```

**Códigos de Error:**
- `404 Not Found`: Incidente no encontrado

---

### POST /api/v1/incidents/{incident_id}/classify
Clasifica un incidente usando el modelo de IA.

**Path Parameters:**
| Parámetro | Tipo | Descripción |
|-----------|------|-------------|
| incident_id | UUID | ID del incidente a clasificar |

**Query Parameters:**
| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| force | boolean | false | Forzar re-clasificación |

**Headers:**
```
Authorization: Bearer <token>  (opcional)
```

**Ejemplo:**
```bash
# Clasificar incidente
curl -X POST http://localhost:8000/api/v1/incidents/550e8400-e29b-41d4-a716-446655440000/classify

# Forzar re-clasificación
curl -X POST "http://localhost:8000/api/v1/incidents/550e8400-e29b-41d4-a716-446655440000/classify?force=true"
```

**Respuesta (200 OK):**
```json
{
  "incident_id": "550e8400-e29b-41d4-a716-446655440000",
  "priority": 1,
  "priority_label": "Critical",
  "confidence": 0.92,
  "explanation": "Based on high urgency (5) and impact (4) values, combined with keywords 'servidor', 'no responde', this incident requires immediate attention.",
  "top_features": [
    "servidor",
    "responde",
    "producción",
    "usuarios",
    "errores"
  ],
  "processing_time_ms": 45.23
}
```

**Niveles de Prioridad:**

| Priority | Label | Descripción |
|----------|-------|-------------|
| 1 | Critical | Resolución inmediata requerida |
| 2 | High | Alta prioridad, resolver ASAP |
| 3 | Medium | Prioridad normal |
| 4 | Low | Baja prioridad |

**Códigos de Error:**
- `404 Not Found`: Incidente no encontrado

---

## 3. Endpoints de Métricas

### Prefix: `/api/v1/metrics`

---

### GET /api/v1/metrics/overview
Obtiene métricas generales del sistema.

**Ejemplo:**
```bash
curl http://localhost:8000/api/v1/metrics/overview
```

**Respuesta (200 OK):**
```json
{
  "total_incidents_today": 15,
  "total_incidents_week": 75,
  "total_incidents_month": 320,
  "incidents_open": 25,
  "incidents_in_progress": 10,
  "incidents_resolved": 275,
  "incidents_closed": 10,
  "avg_response_time_minutes": 0.0,
  "avg_resolution_time_minutes": 45.5,
  "sla_compliance_rate": 95.5,
  "sla_breach_count": 3,
  "model_accuracy": 0.0,
  "model_confidence_avg": 0.82,
  "ai_predictions_today": 15,
  "active_users": 12,
  "active_technicians": 5
}
```

**Descripción de Campos:**

| Campo | Descripción |
|-------|-------------|
| total_incidents_today | Incidentes creados hoy |
| total_incidents_week | Incidentes creados esta semana |
| total_incidents_month | Incidentes creados este mes |
| incidents_open | Incidentes abiertos |
| incidents_in_progress | Incidentes en progreso |
| incidents_resolved | Incidentes resueltos |
| incidents_closed | Incidentes cerrados |
| avg_resolution_time_minutes | Tiempo promedio de resolución |
| sla_compliance_rate | Porcentaje de cumplimiento SLA |
| sla_breach_count | Número de SLAs violados |
| model_confidence_avg | Confianza promedio del modelo IA |
| ai_predictions_today | Predicciones de IA hoy |
| active_users | Usuarios activos |
| active_technicians | Técnicos activos |

---

### GET /api/v1/metrics/incidents
Obtiene métricas detalladas de incidentes.

**Ejemplo:**
```bash
curl http://localhost:8000/api/v1/metrics/incidents
```

**Respuesta (200 OK):**
```json
{
  "by_status": {
    "new": 5,
    "open": 20,
    "in_progress": 10,
    "resolved": 250,
    "closed": 15
  },
  "by_priority": {
    "1": 25,
    "2": 50,
    "3": 150,
    "4": 75
  },
  "by_category": {
    "hardware": 80,
    "software": 120,
    "network": 60,
    "security": 40
  },
  "avg_age_by_priority": {
    "1": 2.5,
    "2": 8.3,
    "3": 24.0,
    "4": 72.0
  },
  "resolution_rate_by_priority": {
    "1": 0.95,
    "2": 0.88,
    "3": 0.75,
    "4": 0.60
  }
}
```

---

### GET /api/v1/metrics/ai
Obtiene métricas del modelo de IA.

**Ejemplo:**
```bash
curl http://localhost:8000/api/v1/metrics/ai
```

**Respuesta (200 OK):**
```json
{
  "total_predictions": 320,
  "accuracy": 0.0,
  "avg_confidence": 0.82,
  "confidence_distribution": {
    "high": 180,
    "medium": 100,
    "low": 40
  }
}
```

**Distribución de Confianza:**
- **high**: confidence >= 0.8
- **medium**: 0.5 <= confidence < 0.8
- **low**: confidence < 0.5

---

### GET /api/v1/metrics/health
Health check detallado del sistema.

**Ejemplo:**
```bash
curl http://localhost:8000/api/v1/metrics/health
```

**Respuesta (200 OK):**
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "timestamp": "2024-01-15T10:30:00",
  "database": "connected",
  "ai_model": "loaded"
}
```

**Estados posibles:**
- `ai_model`: `loaded` | `not_loaded` | `error`

---

## 4. Endpoints de Autenticación

### Prefix: `/api/v1/auth`

---

### POST /api/v1/auth/register
Registra un nuevo usuario en el sistema.

**Request Body:**
```json
{
  "email": "string (requerido, email válido)",
  "username": "string (requerido, 3-50 caracteres)",
  "password": "string (requerido, 8-100 caracteres)",
  "first_name": "string (opcional, máx 100)",
  "last_name": "string (opcional, máx 100)",
  "department": "string (opcional)"
}
```

**Ejemplo:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@ejemplo.com",
    "username": "usuario1",
    "password": "contraseña123",
    "first_name": "Juan",
    "last_name": "Pérez",
    "department": "IT"
  }'
```

**Respuesta (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "usuario@ejemplo.com",
  "username": "usuario1",
  "role": "user",
  "first_name": "Juan",
  "last_name": "Pérez",
  "full_name": "Juan Pérez",
  "department": "IT",
  "is_active": true,
  "is_verified": false,
  "last_login": null,
  "created_at": "2024-01-15T10:30:00"
}
```

**Códigos de Error:**
- `400 Bad Request`: Email o username ya existe

---

### POST /api/v1/auth/login
Inicia sesión y obtiene tokens JWT.

**Request Body:**
```json
{
  "email": "string (requerido)",
  "password": "string (requerido)"
}
```

**Ejemplo:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@ejemplo.com",
    "password": "contraseña123"
  }'
```

**Respuesta (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Códigos de Error:**
- `401 Unauthorized`: Credenciales inválidas

---

### POST /api/v1/auth/refresh
Refresca el token de acceso usando un refresh token.

**Request Body:**
```json
{
  "refresh_token": "string (requerido)"
}
```

**Ejemplo:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/refresh \
  -H "Content-Type: application/json" \
  -d '{
    "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
  }'
```

**Respuesta (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Códigos de Error:**
- `401 Unauthorized`: Refresh token inválido o expirado

---

### GET /api/v1/auth/me
Obtiene información del usuario autenticado.

**Headers:**
```
Authorization: Bearer <access_token>  (requerido)
```

**Ejemplo:**
```bash
curl http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
```

**Respuesta (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "email": "usuario@ejemplo.com",
  "username": "usuario1",
  "role": "user",
  "first_name": "Juan",
  "last_name": "Pérez",
  "full_name": "Juan Pérez",
  "department": "IT",
  "is_active": true,
  "is_verified": false,
  "last_login": "2024-01-15T10:30:00",
  "created_at": "2024-01-10T08:00:00"
}
```

**Códigos de Error:**
- `401 Unauthorized`: Token no proporcionado o inválido

---

## 5. Códigos de Estado HTTP

| Código | Descripción |
|--------|-------------|
| 200 | OK - Request exitosa |
| 201 | Created - Recurso creado |
| 400 | Bad Request - Datos inválidos |
| 401 | Unauthorized - Autenticación requerida |
| 403 | Forbidden - Sin permisos |
| 404 | Not Found - Recurso no encontrado |
| 422 | Unprocessable Entity - Validación fallida |
| 429 | Too Many Requests - Rate limit excedido |
| 500 | Internal Server Error - Error del servidor |

---

## 6. Rate Limiting

El API implementa rate limiting:
- **60 requests por minuto** por IP
- **1000 requests por hora** por IP

Headers en respuesta:
```
X-RateLimit-Remaining: 45
X-RateLimit-Limit: 60
```

Si se excede el límite:
```json
{
  "error": "Too Many Requests",
  "detail": "Rate limit: max 60 requests per minute",
  "retry_after": 30
}
```

---

## 7. Autenticación

El API usa JWT (JSON Web Tokens):

1. **Obtener token** via `/auth/login`
2. **Usar token** en header `Authorization: Bearer <token>`
3. **Refrescar token** cuando expire via `/auth/refresh`

**Tiempo de expiración:**
- Access Token: 30 minutos
- Refresh Token: 7 días

---

## 8. Ejemplos Completos

### Flujo Completo: Crear y Clasificar Incidente

```bash
# 1. Registrar usuario
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","username":"admin","password":"admin123"}'

# 2. Login
TOKEN=$(curl -s -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"admin123"}' | jq -r '.access_token')

# 3. Crear incidente
INCIDENT=$(curl -s -X POST http://localhost:8000/api/v1/incidents/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $TOKEN" \
  -d '{"title":"App no carga","description":"La aplicación principal muestra pantalla en blanco","urgency":4,"impact":3}')

INCIDENT_ID=$(echo $INCIDENT | jq -r '.id')

# 4. Clasificar incidente
curl -X POST "http://localhost:8000/api/v1/incidents/$INCIDENT_ID/classify" \
  -H "Authorization: Bearer $TOKEN"

# 5. Ver métricas actualizadas
curl http://localhost:8000/api/v1/metrics/overview
```

---

## 9. Swagger UI

La documentación interactiva está disponible en:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

Estas interfaces permiten:
- Explorar todos los endpoints
- Probar requests directamente
- Ver ejemplos de request/response
- Descargar OpenAPI spec
