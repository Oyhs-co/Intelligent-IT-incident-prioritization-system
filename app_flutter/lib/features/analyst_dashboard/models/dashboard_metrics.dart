class MetricsOverview {
  final int totalIncidentsToday;
  final int totalIncidentsWeek;
  final int totalIncidentsMonth;
  final int incidentsOpen;
  final int incidentsInProgress;
  final int incidentsResolved;
  final int incidentsClosed;
  final double avgResponseTimeMinutes;
  final double avgResolutionTimeMinutes;
  final double slaComplianceRate;
  final int slaBreachCount;
  final double modelAccuracy;
  final double modelConfidenceAvg;
  final int aiPredictionsToday;
  final int activeUsers;
  final int activeTechnicians;

  MetricsOverview({
    required this.totalIncidentsToday,
    required this.totalIncidentsWeek,
    required this.totalIncidentsMonth,
    required this.incidentsOpen,
    required this.incidentsInProgress,
    required this.incidentsResolved,
    required this.incidentsClosed,
    required this.avgResponseTimeMinutes,
    required this.avgResolutionTimeMinutes,
    required this.slaComplianceRate,
    required this.slaBreachCount,
    required this.modelAccuracy,
    required this.modelConfidenceAvg,
    required this.aiPredictionsToday,
    required this.activeUsers,
    required this.activeTechnicians,
  });

  factory MetricsOverview.fromJson(Map<String, dynamic> json) {
    return MetricsOverview(
      totalIncidentsToday: json['total_incidents_today'] as int? ?? 0,
      totalIncidentsWeek: json['total_incidents_week'] as int? ?? 0,
      totalIncidentsMonth: json['total_incidents_month'] as int? ?? 0,
      incidentsOpen: json['incidents_open'] as int? ?? 0,
      incidentsInProgress: json['incidents_in_progress'] as int? ?? 0,
      incidentsResolved: json['incidents_resolved'] as int? ?? 0,
      incidentsClosed: json['incidents_closed'] as int? ?? 0,
      avgResponseTimeMinutes: (json['avg_response_time_minutes'] as num?)?.toDouble() ?? 0.0,
      avgResolutionTimeMinutes: (json['avg_resolution_time_minutes'] as num?)?.toDouble() ?? 0.0,
      slaComplianceRate: (json['sla_compliance_rate'] as num?)?.toDouble() ?? 0.0,
      slaBreachCount: json['sla_breach_count'] as int? ?? 0,
      modelAccuracy: (json['model_accuracy'] as num?)?.toDouble() ?? 0.0,
      modelConfidenceAvg: (json['model_confidence_avg'] as num?)?.toDouble() ?? 0.0,
      aiPredictionsToday: json['ai_predictions_today'] as int? ?? 0,
      activeUsers: json['active_users'] as int? ?? 0,
      activeTechnicians: json['active_technicians'] as int? ?? 0,
    );
  }
}

class MetricsIncidents {
  final Map<String, int> byStatus;
  final Map<String, int> byPriority;
  final Map<String, int> byCategory;
  final Map<String, double> avgAgeByPriority;
  final Map<String, double> resolutionRateByPriority;

  MetricsIncidents({
    required this.byStatus,
    required this.byPriority,
    required this.byCategory,
    required this.avgAgeByPriority,
    required this.resolutionRateByPriority,
  });

  factory MetricsIncidents.fromJson(Map<String, dynamic> json) {
    return MetricsIncidents(
      byStatus: Map<String, int>.from((json['by_status'] as Map<String, dynamic>).map((k, v) => MapEntry(k, v as int))),
      byPriority: Map<String, int>.from((json['by_priority'] as Map<String, dynamic>).map((k, v) => MapEntry(k, v as int))),
      byCategory: Map<String, int>.from((json['by_category'] as Map<String, dynamic>).map((k, v) => MapEntry(k, v as int))),
      avgAgeByPriority: Map<String, double>.from((json['avg_age_by_priority'] as Map<String, dynamic>).map((k, v) => MapEntry(k, (v as num).toDouble()))),
      resolutionRateByPriority: Map<String, double>.from((json['resolution_rate_by_priority'] as Map<String, dynamic>).map((k, v) => MapEntry(k, (v as num).toDouble()))),
    );
  }
}

class MetricsAI {
  final int totalPredictions;
  final double accuracy;
  final double avgConfidence;
  final Map<String, int> confidenceDistribution;

  MetricsAI({
    required this.totalPredictions,
    required this.accuracy,
    required this.avgConfidence,
    required this.confidenceDistribution,
  });

  factory MetricsAI.fromJson(Map<String, dynamic> json) {
    return MetricsAI(
      totalPredictions: json['total_predictions'] as int? ?? 0,
      accuracy: (json['accuracy'] as num?)?.toDouble() ?? 0.0,
      avgConfidence: (json['avg_confidence'] as num?)?.toDouble() ?? 0.0,
      confidenceDistribution: Map<String, int>.from((json['confidence_distribution'] as Map<String, dynamic>?)?.map((k, v) => MapEntry(k, v as int)) ?? {}),
    );
  }
}

class SystemHealth {
  final String status;
  final String version;
  final String timestamp;
  final String database;
  final String aiModel;

  SystemHealth({
    required this.status,
    required this.version,
    required this.timestamp,
    required this.database,
    required this.aiModel,
  });

  factory SystemHealth.fromJson(Map<String, dynamic> json) {
    return SystemHealth(
      status: json['status'] as String? ?? 'unknown',
      version: json['version'] as String? ?? '',
      timestamp: json['timestamp'] as String? ?? '',
      database: json['database'] as String? ?? 'unknown',
      aiModel: json['ai_model'] as String? ?? 'unknown',
    );
  }
}
