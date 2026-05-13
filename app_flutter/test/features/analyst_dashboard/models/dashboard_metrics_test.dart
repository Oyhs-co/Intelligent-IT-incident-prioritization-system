import 'package:flutter_test/flutter_test.dart';
import 'package:app_flutter/features/analyst_dashboard/models/dashboard_metrics.dart';

void main() {
  test('MetricsOverview.fromJson parses values', () {
    final json = {
      'total_incidents_today': 4,
      'total_incidents_week': 20,
      'total_incidents_month': 80,
      'incidents_open': 3,
      'incidents_in_progress': 2,
      'incidents_resolved': 5,
      'incidents_closed': 1,
      'avg_response_time_minutes': 12.5,
      'avg_resolution_time_minutes': 45.2,
      'sla_compliance_rate': 94.3,
      'sla_breach_count': 2,
      'model_accuracy': 0.91,
      'model_confidence_avg': 0.73,
      'ai_predictions_today': 7,
      'active_users': 10,
      'active_technicians': 3,
    };

    final overview = MetricsOverview.fromJson(json);

    expect(overview.totalIncidentsToday, 4);
    expect(overview.incidentsOpen, 3);
    expect(overview.avgResolutionTimeMinutes, 45.2);
    expect(overview.modelAccuracy, 0.91);
  });

  test('MetricsIncidents.fromJson maps nested data', () {
    final json = {
      'by_status': {'open': 3, 'resolved': 2},
      'by_priority': {'high': 1, 'low': 4},
      'by_category': {'hardware': 2},
      'avg_age_by_priority': {'high': 2.5},
      'resolution_rate_by_priority': {'high': 0.8},
    };

    final metrics = MetricsIncidents.fromJson(json);

    expect(metrics.byStatus['open'], 3);
    expect(metrics.byPriority['low'], 4);
    expect(metrics.avgAgeByPriority['high'], 2.5);
    expect(metrics.resolutionRateByPriority['high'], 0.8);
  });

  test('MetricsAI.fromJson defaults when missing', () {
    final metrics = MetricsAI.fromJson({});

    expect(metrics.totalPredictions, 0);
    expect(metrics.avgConfidence, 0.0);
    expect(metrics.confidenceDistribution, isEmpty);
  });

  test('SystemHealth.fromJson defaults when missing', () {
    final health = SystemHealth.fromJson({});

    expect(health.status, 'unknown');
    expect(health.database, 'unknown');
    expect(health.aiModel, 'unknown');
  });
}
