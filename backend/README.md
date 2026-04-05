# Backend - Sistema de Priorización Inteligente de Incidentes IT

Backend completo del sistema de priorización de incidentes IT con FastAPI, SQLAlchemy (async) y arquitectura Clean Architecture.

## Características Principales

- **Sistema de Tickets Propio**: Gestión completa de incidentes con prioridades automáticas
- **Priorización con IA**: Clasificación usando el modelo de ML existente (`IA-module`)
- **Métricas Avanzadas**: Sistema de métricas para Prometheus/Grafana
- **Logging Estructurado**: Logs con trazabilidad y correlation IDs
- **Arquitectura Clean**: Estructura de microservicios (monolito modular)
- **Seguridad**: Autenticación JWT con refresh tokens

## Requisitos

- **Python**: 3.11+ (compatible con Python 3.14+)
- **Poetry**: Gestor de dependencias
- **Docker y Docker Compose**: Para producción
- **Redis**: Para caching, rate limiting y vector store
- **PostgreSQL**: Para producción (SQLite para desarrollo)

## Instalación Rápida

```bash
# 1. Entrar al directorio del backend
cd backend

# 2. Instalar dependencias
poetry install

# 3. Activar entorno virtual
poetry shell

# 4. Configurar variables de entorno
cp .env.example .env

# 5. Inicializar base de datos
python scripts/init_db.py

# 6. (Opcional) Cargar datos de prueba
python scripts/seed_data.py

# 7. Ejecutar el servidor
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## Configuración

El archivo `.env` contiene todas las configuraciones:

```bash
# Database
DATABASE_URL=sqlite+aiosqlite:///./data/itsm.db
# Para PostgreSQL en producción:
# DATABASE_URL=postgresql+asyncpg://user:pass@localhost:5432/itsm

# IA Module
MODEL_PATH=../IA-module/models
VECTORIZER_PATH=../IA-module/models

# Security
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS=7

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:8080

# Logging
LOG_LEVEL=INFO
```

## Estructura del Proyecto

```
backend/
├── src/
│   ├── domain/                    # Entidades y lógica de dominio
│   │   ├── entities/              # Entidades del negocio
│   │   │   ├── base.py            # BaseEntity con getters/setters
│   │   │   ├── incident.py        # Entidad Incident
│   │   │   ├── user.py            # Entidad User
│   │   │   ├── comment.py         # Entidad Comment
│   │   │   ├── incident_event.py  # Entidad IncidentEvent
│   │   │   └── metric.py          # Entidad Metric
│   │   ├── value_objects/          # Objetos de valor
│   │   │   └── priority_level.py   # PriorityLevel, IncidentStatus, etc.
│   │   └── repositories/          # Interfaces de repositorios
│   │
│   ├── application/               # Casos de uso y servicios
│   │   ├── use_cases/
│   │   │   ├── incidents/         # CRUD de incidentes
│   │   │   ├── users/            # CRUD de usuarios
│   │   │   ├── ai/               # Búsqueda de similares, recomendaciones
│   │   │   └── metrics/          # Métricas overview y SLA
│   │   ├── services/              # Servicios de aplicación
│   │   │   ├── ai_service.py     # Wrapper para el clasificador
│   │   │   ├── metrics_service.py # Recolección de métricas
│   │   │   └── auth_service.py   # Autenticación JWT
│   │   └── ports/                 # Interfaces abstratas
│   │
│   ├── infrastructure/            # Implementaciones externas
│   │   ├── database/              # SQLAlchemy async
│   │   │   ├── models/           # Modelos ORM
│   │   │   ├── repositories/     # Implementaciones de repositorios
│   │   │   └── session.py        # Configuración de sesión
│   │   ├── connectors/           # Integraciones externas
│   │   │   ├── jira_connector.py # Conector Jira
│   │   │   └── servicenow_connector.py
│   │   ├── messaging/             # Redis Pub/Sub
│   │   │   ├── redis_publisher.py
│   │   │   ├── redis_subscriber.py
│   │   │   └── event_handlers.py
│   │   └── ml/                    # Infraestructura ML
│   │       ├── embedding_adapter.py
│   │       └── vector_store.py
│   │
│   ├── presentation/               # Capa de presentación
│   │   ├── api/
│   │   │   ├── app.py            # Aplicación FastAPI
│   │   │   ├── routes/            # Rutas de la API
│   │   │   │   ├── incidents.py
│   │   │   │   ├── metrics.py
│   │   │   │   ├── auth.py
│   │   │   │   └── dependencies.py
│   │   │   └── middleware/        # Middlewares
│   │   │       ├── logging_middleware.py
│   │   │       ├── rate_limit_middleware.py
│   │   │       └── trace_middleware.py
│   │   └── schemas/               # Schemas Pydantic
│   │
│   └── shared/                     # Utilidades compartidas
│       ├── config.py              # Pydantic Settings
│       ├── logging.py            # Logging estructurado
│       └── exceptions.py          # Excepciones custom
│
├── tests/                          # Tests
│   ├── unit/
│   │   ├── domain/
│   │   └── application/
│   └── integration/
│
├── scripts/
│   ├── init_db.py                # Inicializar base de datos
│   └── seed_data.py              # Datos de prueba
│
├── docker/
│   ├── Dockerfile
│   ├── prometheus.yml
│   └── grafana/
│       └── dashboards/
│
├── pyproject.toml
├── docker-compose.yml
└── README.md
```

## Ejecución

### Desarrollo Local

```bash
# Con Poetry
poetry run uvicorn src.main:app --reload

# Con Python directo
python -m uvicorn src.main:app --reload
```

### Docker Compose (Completo con Prometheus y Grafana)

```bash
# Desarrollo con servicios básicos
docker-compose up -d

# Producción con monitoreo completo
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Verificación

Una vez iniciado, accede a:
- **API**: http://localhost:8000
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Prometheus**: http://localhost:9090
- **Grafana**: http://localhost:3001 (admin/admin)

## API Endpoints

### Salud y Raíz

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/` | Información del sistema |
| GET | `/health` | Health check básico |

### Incidentes

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/incidents/` | Crear incidente |
| GET | `/api/v1/incidents/` | Listar incidentes (con filtros) |
| GET | `/api/v1/incidents/{id}` | Obtener incidente por ID |
| POST | `/api/v1/incidents/{id}/classify` | Clasificar con IA |

### Métricas

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/api/v1/metrics/overview` | Métricas generales del sistema |
| GET | `/api/v1/metrics/incidents` | Métricas de incidentes |
| GET | `/api/v1/metrics/ai` | Métricas de IA/ML |
| GET | `/api/v1/metrics/health` | Health check detallado |

### Autenticación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Registrar usuario |
| POST | `/api/v1/auth/login` | Iniciar sesión |
| POST | `/api/v1/auth/refresh` | Refrescar token |
| GET | `/api/v1/auth/me` | Usuario actual |

## Testing

```bash
# Ejecutar todos los tests
poetry run pytest

# Con coverage
poetry run pytest --cov=src --cov-report=html

# Tests específicos
poetry run pytest tests/unit/
poetry run pytest tests/integration/

# Watch mode
poetry run pytest --watch
```

## Scripts Disponibles

```bash
# Inicializar base de datos
python scripts/init_db.py

# Cargar datos de prueba
python scripts/seed_data.py
```

## Integración con IA

El sistema utiliza el clasificador existente en `IA-module/`:

1. El modelo `priority_classifier_v1.pkl` clasifica incidentes
2. Genera explicaciones basadas en features
3. Calcula confianza de predicción

Para entrenar un nuevo modelo:
```bash
cd ../IA-module
python src/train.py
```

## Monitoreo

### Prometheus Metrics

El sistema expone métricas en `/metrics`:
- `itsm_incidents_created_total`
- `itsm_incidents_by_status`
- `itsm_incidents_by_priority`
- `itsm_ai_predictions_total`
- `itsm_model_avg_confidence`
- `itsm_model_avg_latency_ms`
- `itsm_sla_compliance_rate`
- `itsm_request_duration_seconds`

### Grafana Dashboards

Dashboards preconfigurados:
- **ITSM Dashboard**: Vista general de incidentes
- **AI Metrics Dashboard**: Métricas del modelo de ML

## Seguridad

- Contraseñas hasheadas con bcrypt
- Tokens JWT con expiración
- Rate limiting configurable
- CORS configurado
- Validación de datos con Pydantic

## Migración a Producción

1. Cambiar `DATABASE_URL` a PostgreSQL
2. Configurar `SECRET_KEY` seguro
3. Habilitar Redis
4. Configurar Prometheus y Grafana
5. Revisar variables de CORS
6. Configurar logs para producción

## Licencia

MIT
