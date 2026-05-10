class Incident {
  final String id;
  final String title;
  final String description;
  final String status;
  final String aiPriority;
  final String aiSuggestedArea;
  final String? assignedArea;
  final String? finalResolution;

  Incident({
    required this.id,
    required this.title,
    required this.description,
    required this.status,
    this.aiPriority = 'Media', 
    this.aiSuggestedArea = 'Soporte General', 
    this.assignedArea,
    this.finalResolution,
  });

  Incident copyWith({
    String? id,
    String? title,
    String? description,
    String? status,
    String? aiPriority,
    String? aiSuggestedArea,
    String? assignedArea,
    String? finalResolution,
  }) {
    return Incident(
      id: id ?? this.id,
      title: title ?? this.title,
      description: description ?? this.description,
      status: status ?? this.status,
      aiPriority: aiPriority ?? this.aiPriority,
      aiSuggestedArea: aiSuggestedArea ?? this.aiSuggestedArea,
      assignedArea: assignedArea ?? this.assignedArea,
      finalResolution: finalResolution ?? this.finalResolution,
    );
  }
}

