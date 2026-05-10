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
    ),
    Incident(
      id: 'INC-1002',
      title: 'No puedo entrar al correo',
      description: 'Clave rota',
      status: 'En progreso',
      aiPriority: 'Alta',
      aiSuggestedArea: 'Cuentas y Accesos',
      assignedArea: 'Cuentas y Accesos',
    ),
  ];

  Future<bool> addIncident(String title, String description) async {
    final newIncident = Incident(
      id: 'INC-${1000 + state.length + 1}',
      title: title,
      description: description,
      status: 'Enviando...',
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
          aiPriority: priority,
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
        );
      }
      return incident;
    }).toList();
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

class AnalystFilterNotifier extends Notifier<String> {
  @override
  String build() => 'Todas';

  void setFilter(String filter) {
    state = filter;
  }
}

final analystFilterProvider = NotifierProvider<AnalystFilterNotifier, String>(AnalystFilterNotifier.new);
