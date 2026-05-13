import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:logger/logger.dart';
import '../../../../core/network/api_client.dart';
import '../../../../core/utils/app_constants.dart';
import '../incident.dart';

final logger = Logger();

class IncidentNotifier extends Notifier<List<Incident>> {
  final ApiClient _api = ApiClient();

  @override
  List<Incident> build() => [];

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
      state = (data['items'] as List<dynamic>).map((e) => Incident.fromJson(e as Map<String, dynamic>)).toList();
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
      return null;
    }
  }

  Future<Incident?> createIncident({
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
      return incident;
    } catch (e) {
      logger.e('Failed to create incident: $e');
      return null;
    }
  }

  Future<Map<String, dynamic>?> classifyIncident(String incidentId, {bool force = false}) async {
    try {
      final queryParams = <String, String>{'force': force.toString()};
      final data = await _api.request('POST', ApiEndpoints.classifyIncident(incidentId), queryParams: queryParams, auth: true);
      final result = data as Map<String, dynamic>;

      await updateIncident(incidentId, {'status': 'open'});

      state = state.map((incident) {
        if (incident.id == incidentId) {
          return incident.copyWith(
            priority: result['priority'] as int?,
            priorityLabel: result['priority_label'] as String?,
            confidenceScore: (result['confidence'] as num?)?.toDouble(),
            explanation: result['explanation'] as String?,
            status: 'open',
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

  Future<void> assignAndEditTicket(String incidentId, String categoryBackend, int priorityValue) async {
    try {
      await _api.request('PUT', ApiEndpoints.updateIncident(incidentId), body: {
        'category': categoryBackend,
        'status': 'in_progress',
        'priority': priorityValue,
      }, auth: true);

      final updated = await _api.request('GET', ApiEndpoints.incident(incidentId), auth: true);
      if (updated is Map<String, dynamic>) {
        state = state.map((inc) {
          if (inc.id == incidentId) {
            return Incident.fromJson(updated);
          }
          return inc;
        }).toList();
      }
    } catch (e) {
      logger.e('Failed to assign ticket: $e');
    }
  }

  Future<bool> updateIncident(String incidentId, Map<String, dynamic> fields) async {
    try {
      final data = await _api.request('PUT', ApiEndpoints.updateIncident(incidentId), body: fields, auth: true);
      if (data is Map<String, dynamic>) {
        final updated = Incident.fromJson(data);
        state = state.map((inc) => inc.id == incidentId ? updated : inc).toList();
      }
      return true;
    } catch (e) {
      logger.e('Failed to update incident $incidentId: $e');
      return false;
    }
  }

  Future<void> resolveIncident(String incidentId, String resolution) async {
    try {
      await _api.request('PUT', ApiEndpoints.updateIncident(incidentId), body: {
        'status': 'resolved',
        'resolution': resolution,
        'resolution_code': 'FIXED',
      }, auth: true);

      final updated = await _api.request('GET', ApiEndpoints.incident(incidentId), auth: true);
      if (updated is Map<String, dynamic>) {
        state = state.map((inc) {
          if (inc.id == incidentId) {
            return Incident.fromJson(updated);
          }
          return inc;
        }).toList();
        return;
      }
    } catch (e) {
      logger.e('Failed to resolve incident via API: $e');
    }
  }

  Future<bool> deleteIncident(String incidentId) async {
    try {
      await _api.request('DELETE', ApiEndpoints.incident(incidentId), auth: true);
      state = state.where((incident) => incident.id != incidentId).toList();
      return true;
    } catch (e) {
      logger.e('Failed to delete incident $incidentId: $e');
      return false;
    }
  }
}

final incidentProvider = NotifierProvider<IncidentNotifier, List<Incident>>(IncidentNotifier.new);

class ClientFilterNotifier extends Notifier<String> {
  @override
  String build() => 'Todos';
  void setFilter(String filter) => state = filter;
}

final clientFilterProvider = NotifierProvider<ClientFilterNotifier, String>(ClientFilterNotifier.new);


