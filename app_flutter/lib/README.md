# Documentacion detallada de lib/

Este documento describe la estructura completa de `lib/`, el rol de cada carpeta y el proposito de cada archivo actual. Esta organizado por capas y luego por feature.

## Estructura y flujo general

- Punto de entrada: `main.dart` inicializa Riverpod y crea la app Flutter.
- Capa `core/`: configuraciones globales, routing, red y utilidades compartidas.
- Capa `features/`: modulos de negocio con enfoque feature-first. Cada feature agrupa modelos, estado (Riverpod) y UI.

## Archivo raiz

### main.dart

- Crea `ProviderScope` para habilitar Riverpod en toda la app.
- Instancia `MaterialApp` con tema base y `home` apuntando al portal del cliente.
- Actualmente la pantalla inicial es `ClientHome` (portal del cliente).

## core/

### core/theme/

- `app_theme.dart`: punto central para definir el tema global de la app. Hoy solo contiene un comentario guia; se espera incluir `ThemeData`, paletas y tipografias.

### core/router/

- `app_router.dart`: contendra el router principal de la app. Planeado para exponer un objeto router reutilizable.
- `go_router_config.dart`: lugar para la configuracion concreta de rutas usando GoRouter (rutas, redirecciones, guards).

### core/network/

- `api_client.dart`: cliente HTTP compartido. Aqui deberian vivir configuraciones base, headers, interceptores y metodos comunes.

### core/utils/

- `app_constants.dart`: constantes globales (por ejemplo nombres de rutas, keys, endpoints).
- `riverpod_providers.dart`: providers compartidos de ambito transversal (por ejemplo servicios globales o configuraciones).

## features/

### auth/

#### auth/models/

- `auth_user.dart`: modelo de usuario autenticado. Actualmente es un placeholder; deberia guardar identidad, tokens, roles y metadata.

#### auth/providers/

- `auth_providers.dart`: providers de autenticacion (sesion, repositorios, notifiers). Hoy es un placeholder.

#### auth/presentation/pages/

- `login_page.dart`: pantalla de inicio de sesion. Es un placeholder con un texto de prueba.
- `register_page.dart`: pantalla de registro. Actualmente solo contiene un comentario guia.

#### auth/presentation/widgets/

- `auth_input_field.dart`: widget reutilizable para campos de autenticacion (email, password). Hoy es un placeholder.

### client_portal/

#### client_portal/models/

- `incident.dart`: modelo base de incidente con `id`, `title`, `description` y `status`.

#### client_portal/models/providers/

- `client_portal_providers.dart`: gestiona el estado de incidentes con Riverpod.
  - `IncidentNotifier`: mantiene una lista en memoria con datos de ejemplo.
  - `addIncident(...)`: agrega un nuevo incidente con un id generado.
  - `incidentProvider`: expone el estado a las pantallas.

#### client_portal/presentation/pages/

- `client_home.dart`: lista de incidentes del cliente.
  - Lee `incidentProvider` para poblar una lista.
  - Cada item muestra `id`, `title` y `status`.
  - El FAB navega a `NewReportPage`.
- `my_requests.dart`: placeholder para un historial de solicitudes. Aun sin implementacion.
- `new_report.dart`: formulario para crear un reporte.
  - Usa `TextEditingController` para titulo y descripcion.
  - Al enviar, llama a `addIncident` y regresa a la pantalla previa.

#### client_portal/presentation/widgets/

- `status_badge.dart`: widget para mostrar visualmente el estado del incidente. Actualmente es un placeholder.

### analyst_dashboard/

#### analyst_dashboard/models/

- `dashboard_metrics.dart`: modelo de metricas del dashboard. Placeholder.

#### analyst_dashboard/models/providers/

- `analyst_dashboard_providers.dart`: providers de Riverpod para el dashboard. Placeholder.

#### analyst_dashboard/presentation/pages/

- `dashboard_page.dart`: pantalla principal del analista. Placeholder.

#### analyst_dashboard/presentation/widgets/

- `ai_confidence_card.dart`: tarjeta para mostrar confianza de IA en las predicciones. Placeholder.

## Estado actual y pendientes

- Varios archivos estan creados como placeholders con comentarios guia. Esto ayuda a fijar la arquitectura mientras se completa la implementacion.
- Las unicas piezas funcionales hoy son el flujo de portal del cliente y su estado en memoria.
- Se recomienda implementar primero `app_theme.dart`, el router con GoRouter y los providers base de autenticacion.