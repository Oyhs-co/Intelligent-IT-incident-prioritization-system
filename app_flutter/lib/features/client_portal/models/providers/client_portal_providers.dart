import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:logger/logger.dart';
import '../../../../core/network/api_client.dart';
import '../incident.dart';

final apiClient = ApiClient();
final logger = Logger();

class IncidentNotifier extends Notifier<List<Incident>> {
  @override
  List<Incident> build() => [
    Incident(
      id: 'INC-1001',
      title: 'Mi pantalla no enciende',
      description: 'Ayuda',
      status: 'Pendiente',
      aiPriority: 'Baja',
      aiSuggestedArea: 'Soporte de Hardware',
      timeline: [
        IncidentEvent(title: 'Ticket Creado', description: 'El cliente reportó el problema.', date: DateTime.now().subtract(const Duration(hours: 2))),
        IncidentEvent(title: 'Análisis Preliminar', description: 'El sistema ha clasificado inicialmente el reporte.', date: DateTime.now().subtract(const Duration(hours: 1, minutes: 59))),
      ],
    ),
    Incident(
      id: 'INC-1002',
      title: 'No puedo entrar al correo',
      description: 'Clave rota',
      status: 'En progreso',
      aiPriority: 'Alta',
      aiSuggestedArea: 'Cuentas y Accesos',
      assignedArea: 'Cuentas y Accesos',
      timeline: [
        IncidentEvent(title: 'Ticket Creado', description: 'El cliente reportó el problema.', date: DateTime.now().subtract(const Duration(days: 1))),
        IncidentEvent(title: 'Análisis Preliminar', description: 'El sistema ha clasificado inicialmente el reporte.', date: DateTime.now().subtract(const Duration(days: 1, minutes: -1))),
        IncidentEvent(title: 'Asignado a Área', description: 'El analista asignó el ticket a Cuentas y Accesos.', date: DateTime.now().subtract(const Duration(hours: 5))),
      ],
    ),
  ];

  String _generateNextId() {
    if (state.isEmpty) return 'INC-1001';
    int maxId = 1000;
    for (final ticket in state) {
      if (ticket.id.startsWith('INC-')) {
        final numPart = int.tryParse(ticket.id.substring(4));
        if (numPart != null && numPart > maxId) {
          maxId = numPart;
        }
      }
    }
    return 'INC-${maxId + 1}';
  }

  Future<bool> addIncident(String title, String description) async {
    final newIncident = Incident(
      id: _generateNextId(),
      title: title,
      description: description,
      status: 'Enviando...',
      timeline: [
        IncidentEvent(title: 'Ticket Creado', description: 'El cliente reportó el incidente desde el portal.', date: DateTime.now()),
      ],
    );
    state = [...state, newIncident];
    final enviadoConExito = await apiClient.enviarTicket(title, description);
    if (enviadoConExito) {
      logger.i("El backend de FastAPI recibio el ticket.");
      state = state.map((incident) {
        if (incident.id == newIncident.id) {
          return incident.copyWith(status: 'Recibido');
        }
        return incident;
      }).toList();
      return true;
    } else {
      logger.w(
        "AVISO: El servidor Python esta apagado. Se guardó solo en la memoria del celular.",
      );
      state = state.map((incident) {
        if (incident.id == newIncident.id) {
          return incident.copyWith(
            status: 'Pendiente', 
            aiPriority: 'Alta', 
            aiSuggestedArea: 'Redes',
            timeline: [
              ...incident.timeline,
              IncidentEvent(title: 'Análisis Preliminar', description: 'Clasificación automática completada.', date: DateTime.now().add(const Duration(seconds: 1))),
            ],
          );
        }
        return incident;
      }).toList();
      return false;
    }
  }

  void assignAndEditTicket(String incidentId, String area, String priority) {
    state = state.map((incident) {
      if (incident.id == incidentId) {
        return incident.copyWith(
          status: 'En progreso',
          assignedArea: area,
          finalPriority: priority,
          timeline: [
            ...incident.timeline,
            IncidentEvent(title: 'Asignado a Área', description: 'El Analista asignó el caso a $area con prioridad $priority.', date: DateTime.now()),
          ],
        );
      }
      return incident;
    }).toList();
  }

  void resolveIncident(String incidentId, String resolution) {
    state = state.map((incident) {
      if (incident.id == incidentId) {
        return incident.copyWith(
          status: 'Resuelto',
          finalResolution: resolution,
          timeline: [
            ...incident.timeline,
            IncidentEvent(title: 'Ticket Resuelto', description: 'El Técnico registró la resolución final.', date: DateTime.now()),
          ],
        );
      }
      return incident;
    }).toList();
  }

  void deleteIncident(String incidentId) {
    state = state.where((incident) => incident.id != incidentId).toList();
  }
}

final incidentProvider = NotifierProvider<IncidentNotifier, List<Incident>>(
  IncidentNotifier.new,
);

class ClientFilterNotifier extends Notifier<String> {
  @override
  String build() => 'Todos';

  void setFilter(String filter) {
    state = filter;
  }
}

final clientFilterProvider = NotifierProvider<ClientFilterNotifier, String>(ClientFilterNotifier.new);

