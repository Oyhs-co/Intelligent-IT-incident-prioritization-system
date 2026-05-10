import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:logger/logger.dart';
import '../../../../core/network/api_client.dart';
import '../../../../core/utils/app_constants.dart';

final logger = Logger();

class IncidentCategory {
  final String value;
  final String label;

  IncidentCategory({required this.value, required this.label});

  factory IncidentCategory.fromJson(Map<String, dynamic> json) {
    return IncidentCategory(
      value: json['value'] as String,
      label: json['label'] as String,
    );
  }
}

class PriorityOption {
  final int value;
  final String label;

  PriorityOption({required this.value, required this.label});

  factory PriorityOption.fromJson(Map<String, dynamic> json) {
    return PriorityOption(
      value: json['value'] as int,
      label: json['label'] as String,
    );
  }
}

class MetadataState {
  final List<IncidentCategory> categories;
  final List<PriorityOption> priorities;
  final bool isLoading;

  const MetadataState({
    this.categories = const [],
    this.priorities = const [],
    this.isLoading = false,
  });
}

class MetadataNotifier extends Notifier<MetadataState> {
  final ApiClient _api = ApiClient();

  @override
  MetadataState build() => const MetadataState();

  Future<void> fetchMetadata() async {
    state = MetadataState(isLoading: true);
    try {
      final results = await Future.wait([
        _api.request('GET', ApiEndpoints.incidentCategories, auth: true),
        _api.request('GET', ApiEndpoints.incidentPriorities, auth: true),
      ]);

      final categoriesData = results[0] as List<dynamic>;
      final prioritiesData = results[1] as List<dynamic>;

      state = MetadataState(
        categories: categoriesData
            .map((e) => IncidentCategory.fromJson(e as Map<String, dynamic>))
            .toList(),
        priorities: prioritiesData
            .map((e) => PriorityOption.fromJson(e as Map<String, dynamic>))
            .toList(),
        isLoading: false,
      );
    } catch (e) {
      logger.e('Failed to fetch metadata: $e');
      state = const MetadataState();
    }
  }
}

final metadataProvider = NotifierProvider<MetadataNotifier, MetadataState>(MetadataNotifier.new);
