# Estructura del Proyecto Flutter: `app_flutter`

Se define para que sirve cada carpeta y archivo importante dentro de `lib`, que es donde esta todo el codigo de la app en flutter

## `lib`
esta es la carpeta principal donde esta todo el codigo en dart de la aplicacion

- **`main.dart`**: es como el inicio de todo, aqui arranca la app, se configuran cosas basicas y se define el widget principal

## `lib/core`
esta carpeta tiene cosas que se usan en toda la app, no es de una sola parte sino que sirve para todo en general

- **`core/network`**: se encarga de conectarse con servicios externos como APIs  
  - **`api_client.dart`**: aqui se hacen las peticiones http al backend, o sea enviar y recibir datos

- **`core/router`**: sirve para manejar la navegacion  
  - **`app_router.dart`**: define las rutas y como se pasa de una pantalla a otra  
  - **`go_router_config.dart`**: es la configuracion del paquete go_router que ayuda a manejar mejor la navegacion

- **`core/theme`**: todo lo visual de la app  
  - **`app_theme.dart`**: aqui se definen colores, fuentes y estilos para que todo se vea igual en la app

- **`core/utils`**: cosas utiles que se usan en varias partes  
  - **`app_constants.dart`**: constantes globales como urls o valores fijos  
  - **`riverpod_providers.dart`**: aqui estan los providers globales para manejar estados en la app

## `lib/features`
esta carpeta organiza la app por funcionalidades, cada carpeta es una parte diferente

- **`features/analyst_dashboard`**: todo lo del panel del analista  
  - **`models`**: estructuras de datos  
    - **`dashboard_metrics.dart`**: datos como metricas del panel  
    - **`providers/analyst_dashboard_providers.dart`**: providers para manejar el estado del dashboard  
  - **`presentation`**: lo visual  
    - **`pages/dashboard_page.dart`**: pagina principal del panel  
    - **`widgets/ai_confidence_card.dart`**: tarjeta que muestra confianza de la IA

- **`features/auth`**: todo lo de autenticacion  
  - **`models`**:  
    - **`auth_user.dart`**: datos del usuario  
  - **`presentation`**:  
    - **`pages/login_page.dart`**: inicio de sesion  
    - **`pages/register_page.dart`**: registro  
    - **`widgets/auth_input_field.dart`**: campo de texto personalizado  
  - **`providers/auth_providers.dart`**: manejo del estado de login

- **`features/client_portal`**: lo que usa el cliente  
  - **`models`**:  
    - **`incident.dart`**: datos de un incidente  
    - **`providers/client_portal_providers.dart`**: estado de los incidentes  
  - **`presentation`**:  
    - **`pages/client_home.dart`**: inicio del cliente  
    - **`pages/incident_details.dart`**: detalles de un incidente  
    - **`pages/my_requests.dart`**: lista de solicitudes  
    - **`pages/new_report.dart`**: crear reporte nuevo  
    - **`widgets/status_badge.dart`**: muestra el estado del incidente

basicamente esta estructura ayuda a tener todo mas organizado y facil de entender aunque al inicio puede parecer confuso