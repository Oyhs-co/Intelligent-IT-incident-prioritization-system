import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../../core/network/api_client.dart';
import '../incident.dart';

final apiClient = ApiClient();

class IncidentNotifier extends Notifier<List<Incident>> {
  @override
  List<Incident> build() => [
    Incident(
      id: 'INC-1001',
      title: 'Mi pantalla no enciende',
      description: 'Ayuda',
      status: 'Pendiente',
    ),
    Incident(
      id: 'INC-1002',
      title: 'No puedo entrar al correo',
      description: 'Clave rota',
      status: 'En progreso',
    ),
  ];
  Future<void> addIncident(String title, String description) async {
    final newIncident = Incident(
      id: 'INC-${1000 + state.length + 1}',
      title: title,
      description: description,
      status: 'Enviando...',
    );
    state = [...state, newIncident];
    final enviadoConExito = await apiClient.enviarTicket(title, description);
    if (enviadoConExito) {
      print("El backend de FastAPI recibio el ticket.");
      state = state.map((incident) {
        if (incident.id == newIncident.id) {
          return Incident(
            id: incident.id,
            title: incident.title,
            description: incident.description,
            status: 'Recibido',
          );
        }
        return incident;
      }).toList();
    } else {
      print(
        " AVISO: El servidor Python está apagado. Se guardó solo en la memoria del celular.",
      );
    }
  }
}

final incidentProvider = NotifierProvider<IncidentNotifier, List<Incident>>(
  IncidentNotifier.new,
);
