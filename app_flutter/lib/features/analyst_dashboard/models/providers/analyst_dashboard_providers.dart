import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:logger/logger.dart';
import '../../../../core/network/api_client.dart';
import '../../../../core/utils/app_constants.dart';
import '../dashboard_metrics.dart';

final logger = Logger();

class MetricsOverviewNotifier extends Notifier<MetricsOverview?> {
  final ApiClient _api = ApiClient();

  @override
  MetricsOverview? build() => null;

  Future<void> fetchOverview() async {
    try {
      final data = await _api.request('GET', ApiEndpoints.metricsOverview, auth: true);
      state = MetricsOverview.fromJson(data as Map<String, dynamic>);
    } catch (e) {
      logger.e('Failed to fetch metrics overview: $e');
    }
  }
}

final metricsOverviewProvider = NotifierProvider<MetricsOverviewNotifier, MetricsOverview?>(MetricsOverviewNotifier.new);

class MetricsIncidentsNotifier extends Notifier<MetricsIncidents?> {
  final ApiClient _api = ApiClient();

  @override
  MetricsIncidents? build() => null;

  Future<void> fetchIncidentsMetrics() async {
    try {
      final data = await _api.request('GET', ApiEndpoints.metricsIncidents, auth: true);
      state = MetricsIncidents.fromJson(data as Map<String, dynamic>);
    } catch (e) {
      logger.e('Failed to fetch incidents metrics: $e');
    }
  }
}

final metricsIncidentsProvider = NotifierProvider<MetricsIncidentsNotifier, MetricsIncidents?>(MetricsIncidentsNotifier.new);

class MetricsAINotifier extends Notifier<MetricsAI?> {
  final ApiClient _api = ApiClient();

  @override
  MetricsAI? build() => null;

  Future<void> fetchAIMetrics() async {
    try {
      final data = await _api.request('GET', ApiEndpoints.metricsAI, auth: true);
      state = MetricsAI.fromJson(data as Map<String, dynamic>);
    } catch (e) {
      logger.e('Failed to fetch AI metrics: $e');
    }
  }
}

final metricsAIProvider = NotifierProvider<MetricsAINotifier, MetricsAI?>(MetricsAINotifier.new);

class SystemHealthNotifier extends Notifier<SystemHealth?> {
  final ApiClient _api = ApiClient();

  @override
  SystemHealth? build() => null;

  Future<void> fetchHealth() async {
    try {
      final data = await _api.request('GET', ApiEndpoints.metricsHealth);
      state = SystemHealth.fromJson(data as Map<String, dynamic>);
    } catch (e) {
      logger.e('Failed to fetch system health: $e');
    }
  }
}

final systemHealthProvider = NotifierProvider<SystemHealthNotifier, SystemHealth?>(SystemHealthNotifier.new);
