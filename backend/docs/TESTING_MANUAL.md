# Manual de Prueba del Backend - Sistema de Priorización de Incidentes IT

Este manual describe paso a paso cómo probar completamente el backend del sistema.

## Prerrequisitos

1. Python 3.11+ instalado
2. Poetry instalado (`pip install poetry`)
3. (Opcional) Docker y Docker Compose para servicios externos

## 1. Instalación y Configuración Inicial

### 1.1 Clonar y Configurar

```bash
# Navegar al directorio del backend
cd backend

# Instalar dependencias
poetry install

# Activar entorno virtual
poetry shell

# Copiar archivo de configuración
cp .env.example .env

# Verificar que el archivo .env se creó correctamente
cat .env
```

### 1.2 Verificar Estructura del Proyecto

```bash
# Verificar estructura
ls -la src/

# Verificar que el módulo IA existe
ls -la ../IA-module/models/
```

## 2. Inicialización de la Base de Datos

### 2.1 Crear la Base de Datos

```bash
# Ejecutar script de inicialización
python scripts/init_db.py
```

Deberías ver:
```
INFO: Database initialized successfully
INFO: Tables created: users, incidents, comments, incident_events, metrics
```

### 2.2 Cargar Datos de Prueba (Opcional)

```bash
# Cargar datos de ejemplo
python scripts/seed_data.py
```

Esto creará:
- 3 usuarios de prueba
- 10 incidentes de ejemplo
- Eventos de prueba

## 3. Iniciar el Servidor

### 3.1 Opción A: Desarrollo Local (Recomendado)

```bash
# Iniciar con Uvicorn
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### 3.2 Opción B: Docker Compose (Servicios Completos)

```bash
# Iniciar todos los servicios
docker-compose up -d

# Ver logs
docker-compose logs -f backend

# Ver servicios activos
docker-compose ps
```

### 3.3 Verificar que el Servidor Está Corriendo

```bash
# Probar endpoint de salud
curl http://localhost:8000/health
```

Respuesta esperada:
```json
{"status": "healthy"}
```

## 4. Pruebas de la API

### 4.1 Documentación Interactiva

Accede a:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### 4.2 Pruebas con cURL

#### Health Check
```bash
# Health check básico
curl -X GET http://localhost:8000/health

# Info del sistema
curl -X GET http://localhost:8000/
```

#### Autenticación

```bash
# 1. Registrar un nuevo usuario
curl -X POST http://localhost:8000/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "username": "testuser",
    "password": "password123",
    "first_name": "Test",
    "last_name": "User",
    "department": "IT"
  }'

# Respuesta esperada:
# {
#   "id": "uuid-here",
#   "email": "test@example.com",
#   "username": "testuser",
#   "role": "user",
#   ...
# }

# 2. Iniciar sesión
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "password123"
  }'

# Respuesta esperada:
# {
#   "access_token": "eyJhbGciOi...",
#   "refresh_token": "eyJhbGciOi...",
#   "token_type": "bearer",
#   "expires_in": 1800
# }

# 3. Obtener usuario actual (reemplazar TOKEN con access_token)
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer TOKEN"
```

#### Incidentes

```bash
# 1. Crear un incidente
curl -X POST http://localhost:8000/api/v1/incidents/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Servidor de producción no responde",
    "description": "El servidor web principal no está respondiendo desde hace 30 minutos. Los usuarios reportan errores 500.",
    "category": "hardware",
    "urgency": 4,
    "impact": 5
  }'

# Respuesta:
# {
#   "id": "uuid-here",
#   "ticket_number": "INC-001",
#   "title": "Servidor de producción no responde",
#   "status": "new",
#   "priority": null,
#   ...
# }

# 2. Listar incidentes
curl -X GET "http://localhost:8000/api/v1/incidents/?skip=0&limit=10"

# 3. Listar incidentes con filtros
curl -X GET "http://localhost:8000/api/v1/incidents/?status=open&priority=1"

# 4. Obtener un incidente específico (reemplazar UUID)
curl -X GET http://localhost:8000/api/v1/incidents/{INCIDENT_UUID}

# 5. Clasificar un incidente con IA (reemplazar UUID)
curl -X POST http://localhost:8000/api/v1/incidents/{INCIDENT_UUID}/classify

# Respuesta:
# {
#   "incident_id": "uuid-here",
#   "priority": 1,
#   "priority_label": "Critical",
#   "confidence": 0.85,
#   "explanation": "High urgency and impact...",
#   "top_features": ["servidor", "no responde"],
#   "processing_time_ms": 45.2
# }
```

#### Métricas

```bash
# 1. Métricas generales
curl -X GET http://localhost:8000/api/v1/metrics/overview

# Respuesta:
# {
#   "total_incidents_today": 5,
#   "total_incidents_week": 25,
#   "total_incidents_month": 100,
#   "incidents_open": 15,
#   "incidents_in_progress": 5,
#   "incidents_resolved": 70,
#   "incidents_closed": 10,
#   "avg_response_time_minutes": 0.0,
#   "avg_resolution_time_minutes": 45.5,
#   "sla_compliance_rate": 95.5,
#   "sla_breach_count": 2,
#   "model_accuracy": 0.0,
#   "model_confidence_avg": 0.82,
#   "ai_predictions_today": 5,
#   "active_users": 10,
#   "active_technicians": 3
# }

# 2. Métricas de incidentes
curl -X GET http://localhost:8000/api/v1/metrics/incidents

# 3. Métricas de IA
curl -X GET http://localhost:8000/api/v1/metrics/ai

# 4. Health check detallado
curl -X GET http://localhost:8000/api/v1/metrics/health
```

## 5. Pruebas con Python (usando httpx)

### 5.1 Script de Prueba Completo

Crea un archivo `test_api.py`:

```python
import asyncio
import httpx
from httpx import AsyncClient

BASE_URL = "http://localhost:8000"

async def main():
    async with AsyncClient(base_url=BASE_URL, timeout=30.0) as client:
        
        # 1. Health Check
        print("=== 1. Health Check ===")
        response = await client.get("/health")
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}\n")
        
        # 2. Register User
        print("=== 2. Register User ===")
        user_data = {
            "email": "admin@example.com",
            "username": "admin",
            "password": "admin123",
            "first_name": "Admin",
            "last_name": "User"
        }
        response = await client.post("/api/v1/auth/register", json=user_data)
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}\n")
        
        # 3. Login
        print("=== 3. Login ===")
        login_data = {
            "email": "admin@example.com",
            "password": "admin123"
        }
        response = await client.post("/api/v1/auth/login", json=login_data)
        print(f"Status: {response.status_code}")
        tokens = response.json()
        print(f"Access Token: {tokens['access_token'][:50]}...")
        access_token = tokens["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}
        print()
        
        # 4. Create Incident
        print("=== 4. Create Incident ===")
        incident_data = {
            "title": "Database connection timeout",
            "description": "The main database is timing out during peak hours",
            "category": "database",
            "urgency": 4,
            "impact": 4
        }
        response = await client.post("/api/v1/incidents/", json=incident_data)
        print(f"Status: {response.status_code}")
        incident = response.json()
        incident_id = incident["id"]
        print(f"Created: {incident['ticket_number']} - {incident['title']}\n")
        
        # 5. Classify Incident
        print("=== 5. Classify Incident ===")
        response = await client.post(
            f"/api/v1/incidents/{incident_id}/classify",
            headers=headers
        )
        print(f"Status: {response.status_code}")
        classification = response.json()
        print(f"Priority: {classification['priority']} ({classification['priority_label']})")
        print(f"Confidence: {classification['confidence']:.2%}")
        print(f"Explanation: {classification['explanation']}\n")
        
        # 6. List Incidents
        print("=== 6. List Incidents ===")
        response = await client.get("/api/v1/incidents/")
        print(f"Status: {response.status_code}")
        incidents = response.json()
        print(f"Total: {incidents['total']} incidents\n")
        
        # 7. Get Metrics
        print("=== 7. Get Overview Metrics ===")
        response = await client.get("/api/v1/metrics/overview")
        print(f"Status: {response.status_code}")
        metrics = response.json()
        print(f"Incidents Today: {metrics['total_incidents_today']}")
        print(f"SLA Compliance: {metrics['sla_compliance_rate']:.2f}%")
        print(f"AI Predictions: {metrics['ai_predictions_today']}\n")
        
        # 8. Get AI Metrics
        print("=== 8. Get AI Metrics ===")
        response = await client.get("/api/v1/metrics/ai")
        print(f"Status: {response.status_code}")
        ai_metrics = response.json()
        print(f"Total Predictions: {ai_metrics['total_predictions']}")
        print(f"Avg Confidence: {ai_metrics['avg_confidence']:.2%}\n")
        
        print("=== All Tests Passed! ===")

if __name__ == "__main__":
    asyncio.run(main())
```

Ejecutar:
```bash
python test_api.py
```

## 6. Pruebas de Carga con Apache Bench

```bash
# 100 requests concurrentemente 10 a la vez
ab -n 100 -c 10 http://localhost:8000/health

# Probar endpoint de métricas
ab -n 50 -c 5 http://localhost:8000/api/v1/metrics/overview
```

## 7. Verificar Métricas de Prometheus

```bash
# Ver métricas en formato Prometheus
curl http://localhost:8000/metrics

# Ver métricas específicas
curl http://localhost:8000/metrics | grep itsm_
```

Métricas disponibles:
- `itsm_incidents_created_total` - Total de incidentes creados
- `itsm_incidents_resolved_total` - Total de incidentes resueltos
- `itsm_ai_predictions_total` - Total de predicciones de IA
- `itsm_model_avg_confidence` - Confianza promedio del modelo
- `itsm_request_duration_seconds` - Duración de requests
- `itsm_sla_compliance_rate` - Tasa de cumplimiento SLA

## 8. Pruebas de Integración con Docker

```bash
# Iniciar servicios completos
docker-compose up -d

# Ver logs del backend
docker-compose logs -f backend

# Ver logs de Prometheus
docker-compose logs -f prometheus

# Ver logs de Grafana
docker-compose logs -f grafana

# Ver todos los contenedores
docker-compose ps
```

## 9. Verificar en Grafana

1. Abrir http://localhost:3001
2. Login con admin/admin
3. Ir a Dashboards > ITSM Dashboard
4. Verificar que las métricas se muestran correctamente

## 10. Pruebas de Unitarias

```bash
# Ejecutar todos los tests
poetry run pytest

# Tests con verbose
poetry run pytest -v

# Tests con coverage
poetry run pytest --cov=src --cov-report=term-missing

# Tests específicos
poetry run pytest tests/unit/domain/
poetry run pytest tests/unit/application/
poetry run pytest tests/integration/

# Tests en watch mode
poetry run pytest --watch
```

## 11. Troubleshooting

### Error: "ModuleNotFoundError"

```bash
# Reinstalar dependencias
poetry install
poetry shell
```

### Error: "Database locked"

```bash
# Cerrar conexiones existentes
# Cambiar a modo de desarrollo con SQLite en memoria
# O reiniciar el servidor
```

### Error: "AI Model not found"

```bash
# Verificar que el modelo existe
ls -la ../IA-module/models/

# Si no existe, copiar desde IA-module
cp ../IA-module/models/*.pkl ./models/ 2>/dev/null || echo "Model files need to be trained"
```

### Verificar estado de Redis

```bash
# Con Docker
docker-compose exec redis redis-cli ping

# Local
redis-cli ping
```

## 12. Resumen de Comandos Rápidos

```bash
# Iniciar servidor
poetry run uvicorn src.main:app --reload

# Inicializar DB
python scripts/init_db.py

# Datos de prueba
python scripts/seed_data.py

# Tests
poetry run pytest

# Con Docker
docker-compose up -d

# Ver API docs
open http://localhost:8000/docs
```

## Checklist de Prueba

- [ ] Servidor inicia correctamente
- [ ] Health check responde
- [ ] Registro de usuario funciona
- [ ] Login funciona y retorna token
- [ ] Crear incidente funciona
- [ ] Listar incidentes funciona
- [ ] Clasificar incidente con IA funciona
- [ ] Métricas overview se calculan
- [ ] Métricas AI se muestran
- [ ] Tests unitarios pasan
- [ ] Docker Compose funciona
- [ ] Métricas Prometheus disponibles
- [ ] Grafana muestra dashboards
