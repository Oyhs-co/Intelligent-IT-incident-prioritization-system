import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../incident.dart';

// Gestiona el estado en memoria de los incidentes.
class IncidentNotifier extends Notifier<List<Incident>> {
  // Estado inicial de ejemplo.
  @override
  List<Incident> build() => [
    Incident(
      id: 'INC-1001',
      title: 'Mi pantalla no enciende',
      description: '',
      status: 'Siendo atendido',
    ),
    Incident(
      id: 'INC-1002',
      title: 'No puedo entrar al correo',
      description: '',
      status: 'Recibido',
    ),
  ];

  // Agrega un nuevo incidente al estado.
  void addIncident(String title, String description) {
    final newIncident = Incident(
      id: 'INC-${1000 + state.length + 1}', // ID simple para demo.
      title: title,
      description: description,
      status: 'Recibido',
    );

    state = [...state, newIncident];
  }
}

// Provider que expone el estado a las vistas.
final incidentProvider = NotifierProvider<IncidentNotifier, List<Incident>>(
  IncidentNotifier.new,
);
