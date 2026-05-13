# Intelligent IT Incident Prioritization System

Sistema integral para la gestion, clasificacion y priorizacion inteligente de incidentes IT. Combina un backend en Python con inteligencia artificial y una aplicacion movil/escritorio en Flutter para ofrecer una plataforma completa de ITSM (IT Service Management).

## Arquitectura

```
/
├── backend/        API REST con FastAPI, IA, y monitoreo
└── app_flutter/    Aplicacion multiplataforma (movil, web, escritorio)
```

El backend expone una API REST que la app Flutter consume. La comunicacion es via HTTP con autenticacion JWT.

---

## Backend

API REST construida con FastAPI y Python, usando Clean Architecture y Machine Learning para la priorizacion automatica de incidentes.

### Tecnologias

- **Framework:** FastAPI (Python 3.11+)
- **Base de datos:** SQLAlchemy 2.0 async (SQLite en desarrollo, PostgreSQL en produccion)
- **Migraciones:** Alembic
- **Autenticacion:** JWT con refresh tokens, bcrypt
- **ML/AI:** LightGBM, sentence-transformers (all-MiniLM-L6-v2), SHAP, scikit-learn
- **Cache/Mensajeria:** Redis
- **Monitoreo:** Prometheus + Grafana
- **Contenedores:** Docker + docker-compose
- **Testing:** pytest, httpx AsyncClient

### Funcionalidades

- CRUD completo de incidentes, usuarios, comentarios
- Clasificacion automatica de incidentes con IA (LightGBM + embeddings)
- Explicaciones SHAP para cada prediccion
- Busqueda de incidentes similares
- Sistema de roles: admin, technician, analyst, client
- Trazabilidad completa (audit events por cada cambio)
- Metricas de negocio, SLA, y rendimiento del modelo
- Integracion con Jira y ServiceNow (conectores)
- Rate limiting, logging estructurado, correlation IDs
- Documentacion interactiva (Swagger, ReDoc)

### Como ejecutar

```bash
cd backend
poetry install
cp .env.example .env
python scripts/init_db.py
python scripts/seed_data.py           # opcional
poetry run uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

O con Docker:

```bash
cd backend
docker-compose up -d
```

Accesos:
- API: http://localhost:8000
- Swagger: http://localhost:8000/docs
- Grafana: http://localhost:3001 (admin/admin)

---

## App Flutter (SIPIIT)

Aplicacion multiplataforma (Android, iOS, Web, Windows, Linux, macOS) para la gestion de incidentes IT, construida con Flutter.

### Tecnologias

- **Framework:** Flutter SDK ^3.11.4, Dart
- **Estado:** Riverpod (flutter_riverpod ^3.3.1)
- **Ruteo:** go_router ^15.0.0
- **HTTP:** http ^1.6.0
- **Almacenamiento local:** shared_preferences
- **Tipografia:** Google Fonts (Inter)
- **Diseno:** Material Design 3

### Funcionalidades por rol

- **Client:** Reportar incidentes, ver estado de sus solicitudes, historial
- **Analyst:** Revisar incidentes, clasificar con IA, asignar prioridad, metricas
- **Technician:** Ver tickets asignados, tomar y resolver incidentes
- **Admin:** Gestion de usuarios, tickets globales, configuracion de IA, auditoria

### Como ejecutar

```bash
cd app_flutter
flutter pub get
flutter run
```

Requiere el backend corriendo en la direccion configurada en `lib/core/utils/app_constants.dart`.

---

## Estructura del proyecto

```
backend/
  src/
    domain/              Entidades y reglas de negocio
    application/         Casos de uso y servicios
    infrastructure/      Base de datos, ML, conectores, mensajeria
    presentation/        API routes, middleware, schemas
    shared/              Configuracion, logging, excepciones
  tests/                 Tests unitarios y de integracion
  migrations/            Migraciones de base de datos (Alembic)
  scripts/               Scripts de inicializacion y datos de prueba
  docker/                Configuracion Docker, Prometheus, Grafana

app_flutter/
  lib/
    core/                Red, tema, ruteo, utilidades compartidas
    features/
      auth/              Login, registro
      client_portal/     Vista de cliente (reportar, ver incidentes)
      analyst_dashboard/ Vista de analista (revisar, clasificar, metricas)
      technician_dashboard/ Vista de tecnico (resolver incidentes)
      admin/             Vista de administrador (usuarios, tickets, IA)
  test/                  Tests unitarios y de widgets
```

## Licencia

MIT
