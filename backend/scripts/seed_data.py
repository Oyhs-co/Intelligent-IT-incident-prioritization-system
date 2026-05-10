"""Script para poblar la base de datos con datos de prueba masivos."""

import asyncio
import random
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path
from uuid import UUID

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.domain.entities.comment import Comment
from src.domain.entities.incident import Incident
from src.domain.entities.incident_event import IncidentEvent
from src.domain.entities.user import User, UserRole
from src.domain.value_objects import (
    EventType,
    IncidentCategory,
    IncidentSource,
    IncidentStatus,
    PriorityLevel,
)
from src.infrastructure.database import get_db_session
from src.infrastructure.database.models.incident_similarity_model import (
    IncidentSimilarityModel,
)
from src.infrastructure.database.models.metric_model import MetricModel
from src.infrastructure.database.repositories import (
    CommentRepository,
    EventRepository,
    IncidentRepository,
    UserRepository,
)
from src.shared.logging import get_logger

logger = get_logger("seed_data")

# Datos de prueba

USERS = [
    # (username, email, password, role, first_name, last_name, department)
    ("admin", "admin@example.com", "admin123", UserRole.ADMIN, "Admin", "User", "IT"),
    ("jperez", "jperez@example.com", "tech1234",
     UserRole.TECHNICIAN, "Juan", "Perez", "Support"),
    ("mlopez", "mlopez@example.com", "tech1234",
     UserRole.TECHNICIAN, "Maria", "Lopez", "Infrastructure"),
    ("rredes", "rredes@example.com", "tech1234",
     UserRole.TECHNICIAN, "Roberto", "Redes", "Network"),
    ("asegura", "asegura@example.com", "tech1234",
     UserRole.TECHNICIAN, "Ana", "Segura", "Security"),
    ("analista1", "analista1@example.com", "analyst1",
     UserRole.ANALYST, "Carlos", "Analisis", "Service Desk"),
    ("analista2", "analista2@example.com", "analyst2",
     UserRole.ANALYST, "Laura", "Analisis", "Service Desk"),
    ("cliente1", "cliente1@example.com", "client123",
     UserRole.USER, "Pedro", "Cliente", None),
    ("cliente2", "cliente2@example.com", "client456",
     UserRole.USER, "Sofia", "Cliente", None),
]

CATEGORIES = [
    (IncidentCategory.INFRASTRUCTURE, ["server", "storage", "backup", "power", "cooling"]),
    (IncidentCategory.APPLICATION, ["erp", "crm", "email", "office", "browser"]),
    (IncidentCategory.NETWORK, ["connectivity", "vpn", "wifi", "firewall", "dns"]),
    (IncidentCategory.SECURITY, ["access", "malware", "phishing", "authentication", "certificate"]),
    (IncidentCategory.DATABASE, ["query", "replication", "performance", "corruption", "backup"]),
    (IncidentCategory.HARDWARE, ["desktop", "laptop", "printer", "monitor", "server_hw"]),
    (IncidentCategory.SOFTWARE, ["os", "driver", "license", "update", "antivirus"]),
    (IncidentCategory.ACCESS, ["password", "account", "permissions", "vpn_access", "remote"]),
]

INCIDENT_TEMPLATES = [
    # (title, description, category_idx, subcategory_idx, urgency_min, urgency_max, impact_min, impact_max)
    ("Servidor {sub} fuera de servicio", "El servidor principal de {cat} ha dejado de responder. Se requiere intervención urgente para restaurar el servicio.", 0, 0, 4, 5, 4, 5),
    ("Problema de conectividad en {sub}", "Usuario reporta que no puede acceder a los recursos de red desde su estación de trabajo. La conexión se interrumpe intermitentemente.", 2, 0, 3, 5, 3, 4),
    ("Fallo en el sistema de {cat}", "El sistema de {cat} presenta errores al intentar procesar transacciones. Se necesita revisión inmediata.", 1, 0, 3, 4, 3, 4),
    ("Incidente de seguridad: {sub}", "Se ha detectado un intento de acceso no autorizado desde una dirección IP desconocida. Posible brecha de seguridad.", 3, 1, 4, 5, 4, 5),
    ("Lentitud en base de datos {sub}", "La base de datos principal presenta tiempos de respuesta elevados. Las consultas están tardando más de lo normal.", 4, 0, 3, 4, 3, 5),
    ("Equipo de {sub} no enciende", "El equipo de {sub} del usuario no enciende tras un corte de luz. Se reemplazó la fuente de poder pero persiste el problema.", 5, 0, 3, 4, 2, 3),
    ("Actualización de {cat} fallida", "La actualización del sistema de {cat} se interrumpió y ahora la aplicación no funciona correctamente.", 6, 0, 3, 4, 3, 4),
    ("Solicitud de acceso a {sub}", "Usuario solicita permisos de acceso al sistema de {sub} para realizar sus labores diarias.", 7, 2, 1, 2, 1, 2),
    ("Correo electrónico no funciona - {sub}", "El servicio de correo electrónico presenta intermitencias. Usuarios reportan que no pueden enviar ni recibir mensajes.", 1, 2, 4, 5, 4, 5),
    ("Respaldo de {cat} fallido", "El respaldo automático del sistema de {cat} ha fallado por tercera vez consecutiva. Se requiere revisión.", 0, 2, 2, 3, 3, 4),
    ("Alerta de capacidad en {sub}", "El almacenamiento {sub} ha alcanzado el 90% de su capacidad. Se necesita liberar espacio o ampliar.", 0, 1, 2, 3, 2, 3),
    ("VPN sin conexión - {sub}", "Usuarios remotos no pueden conectar a la VPN corporativa desde ubicaciones externas.", 2, 1, 4, 5, 3, 4),
    ("Ataque de phishing reportado - {sub}", "Varios usuarios han recibido correos sospechosos con enlaces maliciosos dirigidos a robar credenciales.", 3, 2, 4, 5, 4, 5),
    ("Impresora {sub} no responde", "La impresora del departamento no imprime y muestra error de conexión. Se intentó reiniciar sin éxito.", 5, 2, 2, 3, 1, 2),
    ("Error al generar reportes en {cat}", "El módulo de reportes del sistema {cat} genera errores al exportar datos en formato PDF.", 1, 0, 2, 3, 2, 3),
    ("Problema de licencia {sub}", "La licencia del software {sub} ha expirado y los usuarios no pueden acceder a funcionalidades críticas.", 6, 2, 3, 4, 3, 4),
    ("Caída del servicio de {cat}", "El servicio completo de {cat} se encuentra caído afectando a todos los usuarios. Prioridad máxima.", 1, 0, 5, 5, 5, 5),
    ("Migración de {sub} requiere asistencia", "Durante la migración del sistema {sub} se encontraron errores de compatibilidad que requieren atención.", 6, 0, 2, 3, 2, 3),
    ("Cuenta de usuario bloqueada - {sub}", "Usuario intentó acceder repetidamente y su cuenta fue bloqueada automáticamente por medidas de seguridad.", 7, 0, 2, 3, 2, 3),
    ("Congelamiento del sistema operativo", "Varios equipos del departamento presentan congelamiento del sistema operativo después del último parche.", 6, 0, 3, 4, 3, 4),
    ("Error de replicación en {sub}", "La replicación de datos hacia el servidor {sub} está fallando. Los datos no se están sincronizando.", 4, 1, 3, 4, 3, 5),
    ("Aumento de temperatura en sala de servidores", "La temperatura en el centro de datos ha superado el umbral seguro. Sistemas de cooling funcionando al máximo.", 0, 3, 4, 5, 4, 5),
    ("Problema de DNS - resolución de nombres", "Los usuarios no pueden resolver nombres de dominio internos. Servicios internos afectados.", 2, 4, 3, 4, 3, 4),
    ("Certificado SSL próximo a vencer", "El certificado SSL del sitio corporativo expirará en 48 horas. Se requiere renovación urgente.", 3, 4, 3, 4, 3, 4),
    ("Corrupción de índices en base de datos", "Se detectó corrupción en los índices de la base de datos principal. Se necesita reconstrucción.", 4, 3, 4, 5, 4, 5),
]


def _random_tags() -> list[str]:
    tags_pool = ["urgent", "recurring", "high_impact", "known_issue", "escalated",
                 "needs_review", "vendor", "internal", "customer_reported", "automated"]
    return random.sample(tags_pool, random.randint(0, 3))


# Seed functions

async def seed_users(user_repo: UserRepository) -> dict[str, UUID]:
    """Crea usuarios y devuelve {username: user_id}."""
    user_map = {}
    created = 0
    for username, email, password, role, first_name, last_name, department in USERS:
        existing = await user_repo.get_by_email(email)
        if existing:
            user_map[username] = existing.id
            continue
        user = User()
        user.email = email
        user.username = username
        user.set_password(password)
        user.role = role
        user.first_name = first_name
        user.last_name = last_name
        user.department = department
        user.is_verified = True
        created_user = await user_repo.create(user)
        user_map[username] = created_user.id
        created += 1
    logger.info(f"Created {created} users (total: {len(user_map)})")
    return user_map


async def seed_incidents(
    incident_repo: IncidentRepository,
    event_repo: EventRepository,
    user_map: dict[str, UUID],
) -> list[UUID]:
    """Crea incidentes con datos realistas y sus eventos. Devuelve lista de IDs."""
    tech_users = {name: uid for name, uid in user_map.items()}
    admins = [uid for name, uid in tech_users.items() if name == "admin"]
    technicians = [uid for name, uid in tech_users.items() if name in ("jperez", "mlopez", "rredes", "asegura")]
    analyst_users = [uid for name, uid in tech_users.items() if name in ("analista1", "analista2")]
    reporters = [uid for name, uid in tech_users.items() if name in ("cliente1", "cliente2", "admin")]
    incident_ids = []
    created = 0

    base_time = datetime.now(UTC) - timedelta(days=60)

    for _idx, (title_tpl, desc_tpl, cat_idx, sub_idx, urg_min, urg_max, imp_min, imp_max) in enumerate(INCIDENT_TEMPLATES):
        cat, subcats = CATEGORIES[cat_idx]
        sub = subcats[sub_idx]

        title = title_tpl.format(cat=cat.value.replace("_", " "), sub=sub.replace("_", " ").title())
        description = desc_tpl.format(cat=cat.value.replace("_", " "), sub=sub.replace("_", " ").title())

        # Determinar estado y fechas
        age_days = random.randint(1, 55)
        incident_time = base_time + timedelta(days=age_days, hours=random.randint(0, 23), minutes=random.randint(0, 59))

        # Elegir estado realista
        if age_days < 2:
            status = random.choice([IncidentStatus.NEW, IncidentStatus.OPEN, IncidentStatus.IN_PROGRESS])
        elif age_days < 7:
            status = random.choice([IncidentStatus.OPEN, IncidentStatus.IN_PROGRESS, IncidentStatus.ON_HOLD, IncidentStatus.RESOLVED])
        elif age_days < 30:
            status = random.choice([IncidentStatus.IN_PROGRESS, IncidentStatus.RESOLVED, IncidentStatus.ON_HOLD, IncidentStatus.CLOSED])
        else:
            status = random.choice([IncidentStatus.RESOLVED, IncidentStatus.CLOSED, IncidentStatus.REJECTED])

        # Asignar prioridad
        urgency = random.randint(urg_min, urg_max)
        impact = random.randint(imp_min, imp_max)
        priority = _urgency_impact_to_priority(urgency, impact)

        # Mapear categoría al técnico del área correspondiente
        _area_techs = {
            0: [uid for n, uid in tech_users.items() if n == "mlopez"],     # Infrastructure
            1: [uid for n, uid in tech_users.items() if n == "jperez"],     # Support
            2: [uid for n, uid in tech_users.items() if n == "rredes"],     # Network
            3: [uid for n, uid in tech_users.items() if n == "asegura"],    # Security
            4: [uid for n, uid in tech_users.items() if n == "mlopez"],     # Database → Infrastructure
            5: [uid for n, uid in tech_users.items() if n == "jperez"],     # Hardware → Support
            6: [uid for n, uid in tech_users.items() if n == "jperez"],     # Software → Support
            7: [uid for n, uid in tech_users.items() if n == "asegura"],    # Access → Security
        }

        assigned_to = None
        if status in (IncidentStatus.IN_PROGRESS, IncidentStatus.ON_HOLD, IncidentStatus.PENDING,
                      IncidentStatus.RESOLVED, IncidentStatus.CLOSED):
            area_techs = _area_techs.get(cat_idx, technicians)
            assigned_to = random.choice(area_techs) if area_techs else random.choice(technicians)

        # Resolución para cerrados
        resolution = None
        resolution_code = None
        resolved_at = None
        resolved_by = None
        closed_at = None
        closed_by = None
        sla_deadline = None

        if status in (IncidentStatus.RESOLVED, IncidentStatus.CLOSED):
            resolution = _random_resolution(priority)
            resolution_code = random.choice(["FIXED", "WORKAROUND", "BY_DESIGN", "DUPLICATE", "NOT_REPRODUCIBLE", "THIRD_PARTY", "USER_ERROR"])
            resolved_at = incident_time + timedelta(hours=random.randint(1, 48), minutes=random.randint(0, 59))
            resolved_by = assigned_to
            if status == IncidentStatus.CLOSED:
                closed_at = resolved_at + timedelta(hours=random.randint(1, 24))
                closed_by = random.choice(technicians)

        # SLA deadline
        sla_deadline = incident_time + timedelta(minutes=priority.sla_minutes)

        # Construir entidad
        inc = Incident()
        object.__setattr__(inc, "_title", title)
        object.__setattr__(inc, "_description", description)
        object.__setattr__(inc, "_category", cat)
        object.__setattr__(inc, "_subcategory", sub)
        object.__setattr__(inc, "_status", status)
        object.__setattr__(inc, "_priority", priority)
        object.__setattr__(inc, "_urgency", urgency)
        object.__setattr__(inc, "_impact", impact)
        object.__setattr__(inc, "_source", random.choice(list(IncidentSource)))
        object.__setattr__(inc, "_tags", _random_tags())
        object.__setattr__(inc, "_confidence_score", round(random.uniform(0.7, 0.99), 4))
        object.__setattr__(inc, "_explanation", f"Priorización basada en urgencia={urgency}, impacto={impact} y categoría {cat.value}")
        object.__setattr__(inc, "_sla_deadline", sla_deadline)
        object.__setattr__(inc, "_reporter_id", random.choice(reporters))
        object.__setattr__(inc, "_assigned_to", assigned_to)
        object.__setattr__(inc, "_resolution", resolution)
        object.__setattr__(inc, "_resolution_code", resolution_code)
        object.__setattr__(inc, "_resolved_at", resolved_at)
        object.__setattr__(inc, "_resolved_by", resolved_by)
        object.__setattr__(inc, "_closed_at", closed_at)
        object.__setattr__(inc, "_closed_by", closed_by)
        # Fechas de auditoría
        object.__setattr__(inc, "_created_at", incident_time)
        object.__setattr__(inc, "_updated_at", (closed_at or resolved_at or incident_time) + timedelta(minutes=random.randint(1, 120)))

        saved = await incident_repo.create(inc)
        incident_ids.append(saved.id)
        created += 1

        # Eventos según el flujo de vida
        await _create_incident_events(event_repo, saved.id, user_map, reporters, technicians,
                                      status, assigned_to, resolved_by, closed_by, incident_time,
                                      resolved_at, closed_at)

        if created % 20 == 0:
            logger.info(f"  Created {created} incidents...")

    logger.info(f"Created {created} incidents")
    return incident_ids


def _urgency_impact_to_priority(urgency: int, impact: int) -> PriorityLevel:
    score = urgency * impact
    if score <= 6:
        return PriorityLevel.P1_LOW
    elif score <= 10:
        return PriorityLevel.P2_MEDIUM
    elif score <= 16:
        return PriorityLevel.P3_HIGH
    else:
        return PriorityLevel.P4_CRITICAL


def _random_resolution(priority: PriorityLevel) -> str:
    resolutions = {
        PriorityLevel.P1_LOW: [
            "Se reinició el servicio y el problema quedó resuelto.",
            "Se aplicó el parche de seguridad correspondiente.",
            "Se liberó espacio en disco y el sistema respondió normalmente.",
            "Se actualizaron los controladores del dispositivo.",
        ],
        PriorityLevel.P2_MEDIUM: [
            "Se restauró la configuración desde backup y el servicio volvió a la normalidad.",
            "Se reemplazó el cable de red dañado y la conectividad se restableció.",
            "Se optimizaron las consultas a la base de datos mejorando los tiempos de respuesta.",
            "Se reinstaló la aplicación siguiendo el procedimiento estándar.",
        ],
        PriorityLevel.P3_HIGH: [
            "Se realizó failover al servidor secundario y se restauró el servicio completo.",
            "Se aplicó hotfix proporcionado por el vendor tras escalar el caso.",
            "Se reconstruyó el índice de la base de datos y se normalizó el rendimiento.",
            "Se reemplazó la fuente de poder dañada y el servidor quedó operativo.",
        ],
        PriorityLevel.P4_CRITICAL: [
            "Se ejecutó el plan de contingencia y se restauró el servicio en el DRP.",
            "Se parcheó la vulnerabilidad crítica y se realizó escaneo completo del sistema.",
            "Se revocaron accesos no autorizados y se fortaleció la autenticación multifactor.",
            "Se restauró la base de datos desde el backup más reciente con pérdida mínima de datos.",
        ],
    }
    return random.choice(resolutions.get(priority, resolutions[PriorityLevel.P1_LOW]))


async def _create_incident_events(
    event_repo: EventRepository,
    incident_id: UUID,
    user_map: dict[str, UUID],
    reporters: list[UUID],
    technicians: list[UUID],
    status: IncidentStatus,
    assigned_to: UUID | None,
    resolved_by: UUID | None,
    closed_by: UUID | None,
    created_at: datetime,
    resolved_at: datetime | None,
    closed_at: datetime | None,
):
    """Crea eventos de auditoría para un incidente según su ciclo de vida."""

    def make_event(event_type: EventType, user_id: UUID | None, when: datetime, old: str | None = None, new: str | None = None):
        ev = IncidentEvent()
        object.__setattr__(ev, "_incident_id", incident_id)
        object.__setattr__(ev, "_event_type", event_type)
        object.__setattr__(ev, "_user_id", user_id)
        object.__setattr__(ev, "_old_value", old)
        object.__setattr__(ev, "_new_value", new)
        object.__setattr__(ev, "_created_at", when)
        return ev

    reporter_id = random.choice(reporters)
    await event_repo.create(make_event(EventType.CREATED, reporter_id, created_at))

    # Asignación
    if assigned_to and status not in (IncidentStatus.NEW, IncidentStatus.REJECTED):
        assign_time = created_at + timedelta(minutes=random.randint(5, 180))
        await event_repo.create(make_event(EventType.ASSIGNED, assigned_to, assign_time))

    # Cambio de estado
    if status != IncidentStatus.NEW:
        status_time = created_at + timedelta(hours=random.randint(1, 12))
        await event_repo.create(make_event(EventType.STATUS_CHANGED, assigned_to or reporter_id, status_time, "new", status.value))

    # Resolución
    if resolved_at and resolved_by:
        await event_repo.create(make_event(EventType.RESOLVED, resolved_by, resolved_at))

    # Cierre
    if closed_at and closed_by:
        await event_repo.create(make_event(EventType.CLOSED, closed_by, closed_at))


async def seed_comments(
    comment_repo: CommentRepository,
    incident_ids: list[UUID],
    user_map: dict[str, UUID],
):
    """Añade comentarios realistas a los incidentes."""
    all_user_ids = list(user_map.values())
    total = 0

    comment_templates = [
        "Revisando el incidente. Solicito más información al usuario sobre los pasos para reproducir el problema.",
        "Se asignó al técnico de guardia para evaluación inicial.",
        "Contactando al usuario para obtener detalles adicionales.",
        "Se detectó que el problema está relacionado con una actualización reciente. Revirtiendo cambios.",
        "Escalando al equipo de infraestructura para revisión de servidores.",
        "Se identificó la causa raíz. Procediendo con la solución.",
        "El vendor fue contactado y está trabajando en un parche.",
        "Solución aplicada. Se monitorea el comportamiento del servicio.",
        "Usuario confirmó que el problema está resuelto.",
        "Se documentó la solución en la base de conocimiento.",
        "Agregando nota interna: Este es un problema recurrente, considerar análisis de tendencias.",
        "Se requiere aprobación del supervisor antes de proceder con el cambio.",
        "El problema persiste después del primer intento de solución. Re-evaluando enfoque.",
        "Backup realizado antes de proceder con la intervención.",
        "Programando ventana de mantenimiento para aplicar la corrección.",
        "Nota interna: Caso similar al INC-{ticket}, revisar historial.",
        "Verificando logs del sistema para identificar el momento exacto de la falla.",
        "Pruebas de conectividad realizadas. Se descarta problema de red.",
        "Se restauró desde backup y el servicio se recuperó completamente.",
        "Capacitación al usuario sobre el uso correcto de la aplicación.",
    ]

    for inc_id in random.sample(incident_ids, min(len(incident_ids), len(incident_ids))):
        num_comments = random.randint(1, 5)
        for _ in range(num_comments):
            comment = Comment()
            object.__setattr__(comment, "_incident_id", inc_id)
            object.__setattr__(comment, "_user_id", random.choice(all_user_ids))
            object.__setattr__(comment, "_content", random.choice(comment_templates))
            object.__setattr__(comment, "_is_internal", random.random() < 0.25)
            await comment_repo.create(comment)
            total += 1

    logger.info(f"Created {total} comments")


async def seed_similarities(session, incident_ids: list[UUID]):
    """Enlaza incidentes similares basados en categorías."""

    pairs = 0
    for i, inc_id in enumerate(incident_ids):
        # Buscar incidentes con misma categoría o similares
        candidates = [x for j, x in enumerate(incident_ids) if i != j and random.random() < 0.15]
        for similar_id in candidates[:3]:
            existing = await session.get(IncidentSimilarityModel, (str(inc_id), str(similar_id)))
            if not existing:
                session.add(IncidentSimilarityModel(
                    incident_id=str(inc_id),
                    similar_id=str(similar_id),
                    score=round(random.uniform(0.6, 0.98), 4),
                ))
                pairs += 1
    await session.commit()
    logger.info(f"Created {pairs} similarity links")


async def seed_metrics(session):
    """Crea métricas históricas realistas."""
    now = datetime.now(UTC)
    metrics_data = []

    for days_ago in range(0, 90, 1):
        day = now - timedelta(days=days_ago)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)

        metrics_data.append(MetricModel(
            name="incidents_created_daily",
            value=random.randint(3, 15),
            metric_type="counter",
            category="business",
            labels={"env": "production"},
            service="app",
            timestamp=day_start,
        ))
        metrics_data.append(MetricModel(
            name="incidents_resolved_daily",
            value=random.randint(2, 12),
            metric_type="counter",
            category="business",
            labels={"env": "production"},
            service="app",
            timestamp=day_start,
        ))
        metrics_data.append(MetricModel(
            name="sla_compliance_rate",
            value=round(random.uniform(0.85, 0.99), 4),
            metric_type="gauge",
            category="business",
            labels={"env": "production"},
            service="app",
            timestamp=day_start,
        ))
        metrics_data.append(MetricModel(
            name="avg_response_time_minutes",
            value=round(random.uniform(5, 120), 2),
            metric_type="gauge",
            category="technical",
            labels={"env": "production"},
            service="app",
            timestamp=day_start,
        ))
        metrics_data.append(MetricModel(
            name="avg_resolution_time_hours",
            value=round(random.uniform(1, 48), 2),
            metric_type="gauge",
            category="technical",
            labels={"env": "production"},
            service="app",
            timestamp=day_start,
        ))
        metrics_data.append(MetricModel(
            name="model_accuracy",
            value=round(random.uniform(0.80, 0.95), 4),
            metric_type="gauge",
            category="ai_ml",
            labels={"model": "priority_classifier_v1"},
            service="ai_service",
            timestamp=day_start,
        ))
        metrics_data.append(MetricModel(
            name="model_confidence_avg",
            value=round(random.uniform(0.75, 0.93), 4),
            metric_type="gauge",
            category="ai_ml",
            labels={"model": "priority_classifier_v1"},
            service="ai_service",
            timestamp=day_start,
        ))
        if days_ago % 7 == 0:
            metrics_data.append(MetricModel(
                name="active_users",
                value=random.randint(100, 350),
                metric_type="gauge",
                category="business",
                labels={"env": "production"},
                service="app",
                timestamp=day_start,
            ))
            metrics_data.append(MetricModel(
                name="total_incidents_monthly",
                value=random.randint(100, 300),
                metric_type="counter",
                category="business",
                labels={"env": "production"},
                service="app",
                timestamp=day_start,
            ))

    for m in metrics_data:
        session.add(m)
    await session.commit()
    logger.info(f"Created {len(metrics_data)} metric records")


# ── Main ──────────────────────────────────────────────────────────────

async def main():
    logger.info("Starting database seed...")

    async for session in get_db_session():
        try:
            incident_repo = IncidentRepository(session)
            user_repo = UserRepository(session)
            comment_repo = CommentRepository(session)
            event_repo = EventRepository(session)

            # 1. Users
            logger.info("Seeding users...")
            user_map = await seed_users(user_repo)
            await session.commit()

            # 2. Incidents + Events
            logger.info("Seeding incidents...")
            incident_ids = await seed_incidents(incident_repo, event_repo, user_map)
            await session.commit()

            # 3. Comments
            logger.info("Seeding comments...")
            await seed_comments(comment_repo, incident_ids, user_map)
            await session.commit()

            # 4. Similarities
            logger.info("Seeding incident similarities...")
            await seed_similarities(session, incident_ids)
            await session.commit()

            # 5. Metrics
            logger.info("Seeding metrics...")
            await seed_metrics(session)

            logger.info("Database seeded successfully!")
        except Exception as e:
            await session.rollback()
            logger.error(f"Seed failed: {e}")
            raise

    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
