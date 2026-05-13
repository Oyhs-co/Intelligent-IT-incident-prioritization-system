class IncidentEvent {
  final String title;
  final String description;
  final DateTime date;

  IncidentEvent({required this.title, required this.description, required this.date});
}

class Incident {
  final String id;
  final String ticketNumber;
  final String title;
  final String description;
  final String? category;
  final String? subcategory;
  final String status;
  final int? priority;
  final String? priorityLabel;
  final int urgency;
  final int impact;
  final double? confidenceScore;
  final String? explanation;
  final String? slaDeadline;
  final String source;
  final List<String> tags;
  final String? reporterId;
  final String? assignedTo;
  final String createdAt;
  final String updatedAt;
  final bool isSlaBreached;
  final String? finalPriority;
  final String? finalResolution;
  final String? resolution;
  final String? resolutionCode;
  final String? resolvedAt;
  final List<IncidentEvent> timeline;

  Incident({
    required this.id,
    required this.ticketNumber,
    required this.title,
    required this.description,
    this.category,
    this.subcategory,
    required this.status,
    this.priority,
    this.priorityLabel,
    this.urgency = 3,
    this.impact = 3,
    this.confidenceScore,
    this.explanation,
    this.slaDeadline,
    this.source = 'web',
    this.tags = const [],
    this.reporterId,
    this.assignedTo,
    required this.createdAt,
    required this.updatedAt,
    this.isSlaBreached = false,
    this.finalPriority,
    this.finalResolution,
    this.resolution,
    this.resolutionCode,
    this.resolvedAt,
    this.timeline = const [],
  });

  factory Incident.fromJson(Map<String, dynamic> json) {
    return Incident(
      id: json['id'] as String,
      ticketNumber: json['ticket_number'] as String,
      title: json['title'] as String,
      description: json['description'] as String,
      category: json['category'] as String?,
      subcategory: json['subcategory'] as String?,
      status: json['status'] as String,
      priority: json['priority'] as int?,
      priorityLabel: json['priority_label'] as String?,
      urgency: json['urgency'] as int? ?? 3,
      impact: json['impact'] as int? ?? 3,
      confidenceScore: (json['confidence_score'] as num?)?.toDouble(),
      explanation: json['explanation'] as String?,
      slaDeadline: json['sla_deadline'] as String?,
      source: json['source'] as String? ?? 'web',
      tags: (json['tags'] as List<dynamic>?)?.map((e) => e as String).toList() ?? [],
      reporterId: json['reporter_id'] as String?,
      assignedTo: json['assigned_to'] as String?,
      createdAt: json['created_at'] as String,
      updatedAt: json['updated_at'] as String,
      isSlaBreached: json['is_sla_breached'] as bool? ?? false,
      resolution: json['resolution'] as String?,
      resolutionCode: json['resolution_code'] as String?,
      resolvedAt: json['resolved_at'] as String?,
    );
  }

  Incident copyWith({
    String? id,
    String? ticketNumber,
    String? title,
    String? description,
    String? category,
    String? subcategory,
    String? status,
    int? priority,
    String? priorityLabel,
    int? urgency,
    int? impact,
    double? confidenceScore,
    String? explanation,
    String? slaDeadline,
    String? source,
    List<String>? tags,
    String? reporterId,
    String? assignedTo,
    String? createdAt,
    String? updatedAt,
    bool? isSlaBreached,
    String? finalPriority,
    String? finalResolution,
    String? resolution,
    String? resolutionCode,
    String? resolvedAt,
    List<IncidentEvent>? timeline,
  }) {
    return Incident(
      id: id ?? this.id,
      ticketNumber: ticketNumber ?? this.ticketNumber,
      title: title ?? this.title,
      description: description ?? this.description,
      category: category ?? this.category,
      subcategory: subcategory ?? this.subcategory,
      status: status ?? this.status,
      priority: priority ?? this.priority,
      priorityLabel: priorityLabel ?? this.priorityLabel,
      urgency: urgency ?? this.urgency,
      impact: impact ?? this.impact,
      confidenceScore: confidenceScore ?? this.confidenceScore,
      explanation: explanation ?? this.explanation,
      slaDeadline: slaDeadline ?? this.slaDeadline,
      source: source ?? this.source,
      tags: tags ?? this.tags,
      reporterId: reporterId ?? this.reporterId,
      assignedTo: assignedTo ?? this.assignedTo,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
      isSlaBreached: isSlaBreached ?? this.isSlaBreached,
      finalPriority: finalPriority ?? this.finalPriority,
      finalResolution: finalResolution ?? this.finalResolution,
      resolution: resolution ?? this.resolution,
      resolutionCode: resolutionCode ?? this.resolutionCode,
      resolvedAt: resolvedAt ?? this.resolvedAt,
      timeline: timeline ?? this.timeline,
    );
  }
}
