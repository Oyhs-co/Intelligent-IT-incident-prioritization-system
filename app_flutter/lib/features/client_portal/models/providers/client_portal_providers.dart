import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:logger/logger.dart';
import '../../../../core/network/api_client.dart';
import '../../../../core/utils/app_constants.dart';
import '../incident.dart';

final logger = Logger();

class IncidentNotifier extends Notifier<List<Incident>> {
  final ApiClient _api = ApiClient();

  @override
  List<Incident> build() => [
    Incident(
      id: 'INC-1001',
      ticketNumber: 'INC-1001',
      title: 'Mi pantalla no enciende',
      description: 'Ayuda',
      status: 'Pendiente',
      priorityLabel: 'Baja',
      category: 'Soporte de Hardware',
      createdAt: DateTime.now().toIso8601String(),
      updatedAt: DateTime.now().toIso8601String(),
      timeline: [
        IncidentEvent(title: 'Ticket Creado', description: 'El cliente reportó el problema.', date: DateTime.now().subtract(const Duration(hours: 2))),
        IncidentEvent(title: 'Análisis Preliminar', description: 'El sistema ha clasificado inicialmente el reporte.', date: DateTime.now().subtract(const Duration(hours: 1, minutes: 59))),
      ],
    ),
    Incident(
      id: 'INC-1002',
      ticketNumber: 'INC-1002',
      title: 'No puedo entrar al correo',
      description: 'Clave rota',
      status: 'En progreso',
      priorityLabel: 'Alta',
      category: 'Cuentas y Accesos',
      assignedTo: 'Cuentas y Accesos',
      createdAt: DateTime.now().subtract(const Duration(days: 1)).toIso8601String(),
      updatedAt: DateTime.now().toIso8601String(),
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
        if (numPart != null && numPart > maxId) maxId = numPart;
      }
    }
    return 'INC-${maxId + 1}';
  }

  Future<void> fetchIncidents({
    int skip = 0,
    int limit = 100,
    String? status,
    int? priority,
    String? category,
  }) async {
    try {
      final queryParams = <String, String>{
        'skip': skip.toString(),
        'limit': limit.toString(),
      };
      if (status != null) queryParams['status'] = status;
      if (priority != null) queryParams['priority'] = priority.toString();
      if (category != null) queryParams['category'] = category;

      final data = await _api.request('GET', ApiEndpoints.incidents, queryParams: queryParams, auth: true) as Map<String, dynamic>;
      final items = (data['items'] as List<dynamic>).map((e) => Incident.fromJson(e as Map<String, dynamic>)).toList();
      state = items.isNotEmpty ? items : state;
    } catch (e) {
      logger.e('Failed to fetch incidents: $e');
    }
  }

  Future<Incident?> getIncident(String id) async {
    try {
      final data = await _api.request('GET', ApiEndpoints.incident(id), auth: true);
      return Incident.fromJson(data as Map<String, dynamic>);
    } catch (e) {
      logger.e('Failed to fetch incident $id: $e');
      return state.where((i) => i.id == id).firstOrNull;
    }
  }

  Future<bool> createIncident({
    required String title,
    required String description,
    String? category,
    String? subcategory,
    int urgency = 3,
    int impact = 3,
  }) async {
    try {
      final body = <String, dynamic>{
        'title': title,
        'description': description,
        'urgency': urgency,
        'impact': impact,
      };
      if (category != null && category.isNotEmpty) body['category'] = category;
      if (subcategory != null && subcategory.isNotEmpty) body['subcategory'] = subcategory;

      final data = await _api.request('POST', ApiEndpoints.incidents, body: body, auth: true);
      final incident = Incident.fromJson(data as Map<String, dynamic>);
      state = [...state, incident];
      return true;
    } catch (e) {
      logger.e('Failed to create incident: $e');
      final newIncident = Incident(
        id: _generateNextId(),
        ticketNumber: _generateNextId(),
        title: title,
        description: description,
        status: 'Pendiente',
        createdAt: DateTime.now().toIso8601String(),
        updatedAt: DateTime.now().toIso8601String(),
        category: category,
        urgency: urgency,
        impact: impact,
        timeline: [IncidentEvent(title: 'Ticket Creado', description: 'El cliente reportó el incidente desde el portal.', date: DateTime.now())],
      );
      state = [...state, newIncident];
      return false;
    }
  }

  Future<Map<String, dynamic>?> classifyIncident(String incidentId, {bool force = false}) async {
    try {
      final queryParams = <String, String>{'force': force.toString()};
      final data = await _api.request('POST', ApiEndpoints.classifyIncident(incidentId), queryParams: queryParams, auth: true);
      final result = data as Map<String, dynamic>;

      state = state.map((incident) {
        if (incident.id == incidentId) {
          return incident.copyWith(
            priority: result['priority'] as int?,
            priorityLabel: result['priority_label'] as String?,
            confidenceScore: (result['confidence'] as num?)?.toDouble(),
            explanation: result['explanation'] as String?,
          );
        }
        return incident;
      }).toList();

      return result;
    } catch (e) {
      logger.e('Failed to classify incident $incidentId: $e');
      return null;
    }
  }

  void assignAndEditTicket(String incidentId, String area, String priorityStr) {
    state = state.map((incident) {
      if (incident.id == incidentId) {
        return incident.copyWith(
          status: 'En progreso',
          category: area,
          priorityLabel: priorityStr,
          finalPriority: priorityStr,
          timeline: [
            ...incident.timeline,
            IncidentEvent(title: 'Asignado a Área', description: 'El Analista asignó el caso a $area con prioridad $priorityStr.', date: DateTime.now()),
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

final incidentProvider = NotifierProvider<IncidentNotifier, List<Incident>>(IncidentNotifier.new);

class ClientFilterNotifier extends Notifier<String> {
  @override
  String build() => 'Todos';
  void setFilter(String filter) => state = filter;
}

final clientFilterProvider = NotifierProvider<ClientFilterNotifier, String>(ClientFilterNotifier.new);


